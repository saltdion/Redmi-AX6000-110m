"""根据真实 Release 附件生成下载表；只替换 README 标记区间。"""
import argparse
import base64
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from cleanup_releases import PREFIXES

REPO = 'saltdion/Redmi-AX6000-110m'
START = '<!-- firmware-downloads:start -->'
END = '<!-- firmware-downloads:end -->'


def gh_api(endpoint, payload=None):
    args = ['gh', 'api', endpoint]
    if payload is not None:
        args += ['--method', 'PUT', '--input', '-']
    result = subprocess.run(args, input=json.dumps(payload) if payload is not None else None,
                            capture_output=True, text=True, encoding='utf-8', check=True)
    return json.loads(result.stdout)


def read_releases():
    releases = []
    page = 1
    while True:
        batch = gh_api(f'repos/{REPO}/releases?per_page=100&page={page}')
        releases.extend(batch)
        if len(batch) < 100:
            return releases
        page += 1


def render(releases):
    latest = {}
    for release in releases:
        if release.get('draft') or not release.get('published_at'):
            continue
        for variant, prefix in PREFIXES.items():
            match = re.fullmatch(re.escape(prefix) + r'(\d{8}-\d{6})', release.get('name') or '')
            if not match:
                continue
            try:
                built = datetime.strptime(match[1], '%Y%m%d-%H%M%S')
            except ValueError:
                break
            # 只为实际存在且上传完成的附件生成链接，不猜测文件地址。
            links = []
            for suffix, label in [('squashfs-sysupgrade.bin', 'sysupgrade'), ('initramfs-kernel.bin', 'initramfs')]:
                assets = sorted((a for a in release.get('assets', []) if
                                 a.get('state') == 'uploaded' and 'xiaomi_redmi-router-ax6000' in a['name'] and
                                 a['name'].endswith(suffix)), key=lambda a: a['name'])
                for asset in assets:
                    url = f'https://github.com/{REPO}/releases/download/{quote(release["tag_name"], safe="")}/{quote(asset["name"], safe="")}'
                    links.append(f'[{label}]({url})')
            release_url = f'https://github.com/{REPO}/releases/tag/{quote(release["tag_name"], safe="")}'
            row = f'| {built:%Y-%m-%d %H:%M:%S} | `{variant}` | {" · ".join(links) or "暂无指定镜像"} | [Release]({release_url}) |'
            # 每个版本仅展示最新的已发布记录，不能依赖 API 返回顺序。
            candidate = (built, release['id'], row)
            if variant not in latest or candidate[:2] > latest[variant][:2]:
                latest[variant] = candidate
            break
    rows = list(latest.values())
    rows.sort(key=lambda row: (row[0], row[1]), reverse=True)
    lines = ['| 构建时间（北京时间） | 固件版本 | 镜像下载 | 发布详情 |', '| --- | --- | --- | --- |']
    lines.extend(row[2] for row in rows)
    if not rows:
        lines.append('| — | 暂无已发布固件 | — | — |')
    return '\n'.join(lines)


def replace_section(text, table):
    assert text.count(START) == text.count(END) == 1, 'README 下载列表标记缺失或重复'
    begin = text.index(START) + len(START)
    end = text.index(END)
    assert begin < end
    return text[:begin] + '\n\n' + table + '\n\n' + text[end:]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--from-json')
    args = parser.parse_args()
    if args.from_json:
        data = json.loads(Path(args.from_json).read_text(encoding='utf-8-sig'))
        releases = [r for page in data for r in page] if data and isinstance(data[0], list) else data
    else:
        releases = read_releases()
    table = render(releases)
    if not args.publish:
        path = Path('README.md')
        path.write_bytes(replace_section(path.read_text(encoding='utf-8'), table).encode('utf-8'))
        return
    # 使用文件 SHA 乐观锁提交，冲突时重读，避免覆盖人工修改。
    for attempt in range(3):
        current = gh_api(f'repos/{REPO}/contents/README.md?ref=main')
        old = base64.b64decode(current['content']).decode('utf-8')
        new = replace_section(old, table)
        if old == new:
            print('下载列表没有变化，无需提交。')
            return
        try:
            gh_api(f'repos/{REPO}/contents/README.md', dict(
                message='docs: refresh firmware download list', branch='main', sha=current['sha'],
                content=base64.b64encode(new.encode('utf-8')).decode('ascii')))
            print('已更新 README 固件下载列表。')
            return
        except subprocess.CalledProcessError as error:
            if '(HTTP 409)' not in error.stderr or attempt == 2:
                raise


if __name__ == '__main__':
    main()
