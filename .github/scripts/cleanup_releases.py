"""按固件版本保留最多七个 Release，并清理发布超过七天的记录。"""
import argparse
import json
import os
import re
import urllib.request
from datetime import datetime, timedelta, timezone

PREFIXES = {
    'LEDE_110m': 'RedmiAX6000_LEDE_110m_',
    'immortalwrt_110m': 'RedmiAX6000_immortalwrt_110m_',
    'immortalwrt_237_110m': 'RedmiAX6000_immortalwrt_237_110m_',
    'immortalwrt_237_golang_110m': 'RedmiAX6000_immortalwrt_237_golang_110m_',
    'immortalwrt_110m_compact_24.10': 'RedmiAX6000_110m_Compact_24.10_',
    'immortalwrt_110m_compact_25.12': 'RedmiAX6000_110m_Compact_25.12_',
}


def select_releases(releases, now):
    groups = {key: [] for key in PREFIXES}
    for release in releases:
        # 只处理这六个版本的已发布记录；草稿及未知命名保持不动。
        if release.get('draft') or not release.get('published_at'):
            continue
        for variant, prefix in PREFIXES.items():
            if re.fullmatch(re.escape(prefix) + r'\d{8}-\d{6}', release.get('name') or ''):
                published = datetime.fromisoformat(release['published_at'].replace('Z', '+00:00'))
                groups[variant].append((published, release))
                break
    selected = []
    cutoff = now - timedelta(days=7)
    for variant, entries in groups.items():
        entries.sort(key=lambda item: (item[0], item[1]['id']), reverse=True)
        for index, (published, release) in enumerate(entries):
            reasons = []
            if index >= 7:
                reasons.append('该版本超出最新7个')
            if published < cutoff:
                reasons.append('发布时间超过7天')
            if reasons:
                selected.append((variant, release, '；'.join(reasons)))
    return selected


def api(repo, suffix, method='GET'):
    request = urllib.request.Request(
        f'https://api.github.com/repos/{repo}/{suffix}', method=method,
        headers={'Authorization': f'Bearer {os.environ["GH_TOKEN"]}',
                 'Accept': 'application/vnd.github+json',
                 'X-GitHub-Api-Version': '2022-11-28',
                 'User-Agent': 'ax6000-release-retention'})
    with urllib.request.urlopen(request, timeout=60) as response:
        content = response.read()
        return json.loads(content) if content else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='实际删除；默认只预览')
    args = parser.parse_args()
    repo = os.environ['GITHUB_REPOSITORY']
    assert repo == 'saltdion/Redmi-AX6000-110m', '仅允许清理指定六版本仓库'
    releases = []
    page = 1
    while True:
        batch = api(repo, f'releases?per_page=100&page={page}')
        releases.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    selected = select_releases(releases, datetime.now(timezone.utc))
    lines = [f'扫描 {len(releases)} 个 Release，待清理 {len(selected)} 个；模式：' + ('实际清理' if args.apply else '预览')]
    for variant, release, reason in selected:
        lines.append(f'- {variant} / {release["tag_name"]}：{reason}')
    report = '\n'.join(lines) + '\n'
    print(report, flush=True)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as output:
            output.write(report)
    if args.apply:
        for _, release, _ in selected:
            # 每次删除前重新核对记录，避免预览后被编辑的 Release 被误删。
            current = api(repo, f'releases/{release["id"]}')
            for field in ('name', 'tag_name', 'published_at', 'draft'):
                assert current[field] == release[field], f'Release 已改变，停止清理：{release["id"]}'
            api(repo, f'releases/{release["id"]}', method='DELETE')
            print(f'已删除 Release：{release["tag_name"]}（Git 标签保留）', flush=True)


if __name__ == '__main__':
    main()
