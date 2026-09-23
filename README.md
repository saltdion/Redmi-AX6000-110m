<h1 align="center">云编译红米AX6000 uboot 110M 大分区</h1>


---

## 项目背景

目前主要使用 ImmortalWrt `24.10` 和 `25.12` 两个版本。

### 背景一：使用 110M 大分区

已经根据[相关讨论帖](https://www.right.com.cn/forum/thread-8265832-1-1.html)刷入 hanwckf 大佬的不死 uboot，希望使用 uboot 的 110M UBI 大分区。


### 背景二：支持较新的系统版本

hanwckf 大佬的仓库目前主要支持 OpenWrt `21.02`：

[hanwckf/immortalwrt-mt798x](https://github.com/hanwckf/immortalwrt-mt798x)

为了使用 OpenWrt `24.10` 及以上版本，本项目基于 ImmortalWrt 官方源码的 `openwrt-24.10` 和 `openwrt-25.12` 分支进行构建：

[immortalwrt/immortalwrt](https://github.com/immortalwrt/immortalwrt)

### 背景三：尽可能保留 overlay 空间

下载的一些 `110m-squashfs-factory.bin` 固件大小约为 45 MB。按照 100 MB 分区计算，刷入后 overlay 大约只剩 55 MB，安装较大的插件时往往不够用。

例如：

- `luci-app-openclash`：约 26–32 MB
- `luci-app-daed`：约 65 MB
- `luci-app-ssr-plus`：约 66 MB

目前已经同时准备了 OpenClash 和 DAE 所需的内核支持，但相关 luci-app 仍需要手动下载。通过压缩固件，固件大小约为 16 MB，overlay 空间最多可保留约 80 MB。


## 固件配置

### 固件下载列表

每个固件版本仅列出最近一次成功发布的记录，最多六行，按 Release 名称记录的构建时间倒序排列。时间为北京时间（在编译及 Artifact 上传后生成，接近编译完成时间）。下载列表仅提供实际存在的 sysupgrade 镜像；发布和历史清理后自动更新。更多历史版本请查看 [Releases](https://github.com/saltdion/Redmi-AX6000-110m/releases)。

<!-- firmware-downloads:start -->

| 构建时间（北京时间） | 固件版本 | 镜像下载 | 发布详情 |
| --- | --- | --- | --- |
| 2026-09-24 05:06:20 | `immortalwrt_110m_compact_25.12` | [sysupgrade](https://github.com/saltdion/Redmi-AX6000-110m/releases/download/20260924-050620/immortalwrt-mediatek-filogic-xiaomi_redmi-router-ax6000-110m-squashfs-sysupgrade.bin) | [Release](https://github.com/saltdion/Redmi-AX6000-110m/releases/tag/20260924-050620) |
| 2026-09-24 05:05:40 | `LEDE_110m` | [sysupgrade](https://github.com/saltdion/Redmi-AX6000-110m/releases/download/LEDE_110m_20260924-050540_35909121267/openwrt-mediatek-filogic-xiaomi_redmi-router-ax6000-squashfs-sysupgrade.bin) | [Release](https://github.com/saltdion/Redmi-AX6000-110m/releases/tag/LEDE_110m_20260924-050540_35909121267) |
| 2026-09-23 08:19:13 | `immortalwrt_110m` | [sysupgrade](https://github.com/saltdion/Redmi-AX6000-110m/releases/download/immortalwrt_110m_20260923-081913_35773794934/immortalwrt-mediatek-filogic-xiaomi_redmi-router-ax6000-110m-squashfs-sysupgrade.bin) | [Release](https://github.com/saltdion/Redmi-AX6000-110m/releases/tag/immortalwrt_110m_20260923-081913_35773794934) |
| 2026-09-23 07:16:50 | `immortalwrt_237_golang_110m` | [sysupgrade](https://github.com/saltdion/Redmi-AX6000-110m/releases/download/immortalwrt_237_golang_110m_20260923-071650_35773914011/immortalwrt-mediatek-filogic-xiaomi_redmi-router-ax6000-110m-squashfs-sysupgrade.bin) | [Release](https://github.com/saltdion/Redmi-AX6000-110m/releases/tag/immortalwrt_237_golang_110m_20260923-071650_35773914011) |
| 2026-09-23 07:11:30 | `immortalwrt_237_110m` | [sysupgrade](https://github.com/saltdion/Redmi-AX6000-110m/releases/download/immortalwrt_237_110m_20260923-071130_35774923735/immortalwrt-mediatek-filogic-xiaomi_redmi-router-ax6000-110m-squashfs-sysupgrade.bin) | [Release](https://github.com/saltdion/Redmi-AX6000-110m/releases/tag/immortalwrt_237_110m_20260923-071130_35774923735) |
| 2026-09-23 06:06:38 | `immortalwrt_110m_compact_24.10` | [sysupgrade](https://github.com/saltdion/Redmi-AX6000-110m/releases/download/20260923-060638/immortalwrt-mediatek-filogic-xiaomi_redmi-router-ax6000-110m-squashfs-sysupgrade.bin) | [Release](https://github.com/saltdion/Redmi-AX6000-110m/releases/tag/20260923-060638) |

<!-- firmware-downloads:end -->

### 自动编译与 Release 保留规则

六个版本每天北京时间 **00:00** 开始定时编译（GitHub 实际调度可能延迟）。

历史 Release 按版本分别管理：每个版本最多保留最新 **7 个**，同时删除发布时间超过 **7 天（168 小时）** 的 Release；满足任一条件即清理，因此某版本可能不足 7 个。每天北京时间 00:00 以及各版本成功编译后执行清理。

清理会删除对应 Release 及其附件，但保留 Git 标签；草稿和不符合六个版本命名规则的发布不处理。可在 Actions 的“清理历史固件 Release”中手动预览。此规则不改变 Artifact 的保留设置。

### ImmortalWrt 24.10

使用脚本 `immortalwrt_110m_compact_24.10.yml`。

编译适用于 OpenWrt 24.10 分支的 ImmortalWrt 110M 大分区 uboot 固件。

### ImmortalWrt 25.12

使用脚本 `immortalwrt_110m_compact_25.12.yml`。

编译适用于 OpenWrt 25.12 分支的 ImmortalWrt 110M 大分区 uboot 固件。



默认配置如下：

| 项目 | 配置 |
| --- | --- |
| 管理地址 | `192.168.16.1` |
| 用户名 | `root` |
| 默认密码 | 无 |
| 2.4G Wi-Fi | `Redmi-2.4G` |
| 5G Wi-Fi | `Redmi-5G` |
| Wi-Fi 密码 | `qwer1234` |

首次登录后请及时修改管理密码和 Wi-Fi 密码。


---

### LEDE 110M 大分区（未充分测试）

使用脚本 `LEDE_110m.yml`。

编译适用于 hanwckf 大佬 uboot / ImmortalWrt 110M 大分区的固件。

### ImmortalWrt 237 厂商无线驱动版（未充分测试）

使用脚本 `immortalwrt_237_110m.yml` 或 `immortalwrt_237_golang_110m.yml`。

`237` 为沿用的命名，目前两个脚本实际使用 `padavanonly/immortalwrt-mt798x-6.6` 的 `openwrt-24.10-6.6` 分支，并非 ImmortalWrt 23.07。Golang 版本额外升级 Go 工具链，无线驱动方案相同。

编译适用于 hanwckf 大佬 uboot / ImmortalWrt 110M 大分区的固件。

## 六个版本主要差异

以下根据当前 workflow、设备定义和构建配置整理：六个版本中，四个使用开源 mt76 无线驱动，两个使用联发科厂商 mt_wifi 无线驱动方案（社区通常称为“闭源版”）。

| 固件 / workflow 名称 | 源码仓库与分支 | Wi-Fi 驱动方案 | 主要选择的 LuCI 应用 | 定位 |
| --- | --- | --- | --- | --- |
| `LEDE_110m` | `coolsnowwolf/lede` · `master`（滚动更新） | 开源 mt76，`kmod-mt7915e` | OpenClash、PassWall、SSR Plus+、msd_lite | 插件较多，偏向功能齐全 |
| `immortalwrt_110m` | `immortalwrt/immortalwrt` · `openwrt-24.10` | 开源 mt76，`kmod-mt7915e` | OpenClash、PassWall、msd_lite、定时重启、ARP 绑定 | 官方源码的常用插件版 |
| `immortalwrt_110m_compact_24.10` | `immortalwrt/immortalwrt` · `openwrt-24.10` | 开源 mt76，`kmod-mt7915e` | 定时重启、ARP 绑定 | 精简版，代理软件按需安装 |
| `immortalwrt_110m_compact_25.12` | `immortalwrt/immortalwrt` · `openwrt-25.12` | 开源 mt76，`kmod-mt7915e` | 定时重启、ARP 绑定 | 较新系统分支的精简版 |
| `immortalwrt_237_110m` | `padavanonly/immortalwrt-mt798x-6.6` · `openwrt-24.10-6.6` | 厂商 mt_wifi（通常称“闭源版”），`kmod-mt_wifi`、`kmod-warp` | OpenClash、PassWall、msd_lite、定时重启，以及上游 MTK 无线管理、网络加速、限速和流量统计组件 | 厂商无线驱动版 |
| `immortalwrt_237_golang_110m` | 同上，额外升级 Go 工具链 | 同上 | 与普通 `237` 版本相同 | 解决部分插件对新版 Go 的编译要求 |

### 插件、地址和版本说明

- 两个 compact 版本不内置 OpenClash、PassWall、DAE 本体，仅保留 OpenClash 和 DAE 所需的部分底层依赖；固件体积和剩余空间以实际构建及设备运行结果为准。
- 四个非 compact 版本选择了 OpenClash 插件，但 workflow 没有明确预装 Clash/Mihomo 内核的步骤；PassWall 则配置了 Sing-Box、Xray 和 Geoview。
- `237` 是沿用的命名，并不表示当前系统为 23.07。Golang 版本主要改变编译工具链，不代表无线驱动不同或网络性能更高。
- 当前定制配置将 LEDE 和两个 `237` 版本的管理地址设为 `192.168.2.1`，官方 ImmortalWrt 三个版本设为 `192.168.16.1`；保留旧配置升级时地址可能沿用原设置。
- LEDE 当前选择上游普通 AX6000 目标，workflow 没有像官方 ImmortalWrt 三个版本一样显式添加 110M 设备补丁；不能仅凭文件名认定分区兼容，刷机前需单独核实。
- 独立仓库 [chasey 25.12 厂商驱动精简版 Fork](https://github.com/saltdion/immortalwrt-mt798x-rebase) 不属于本表六个版本，使用独立的每周五北京时间 01:00 更新检查和按需编译计划。

<a id="网络驱动说明"></a>

### 适用范围

- 上述“开源 / 闭源”主要指 **Wi-Fi 无线驱动方案**，不代表整个固件或有线 WAN/LAN 驱动的开源属性。有线以太网、交换机及硬件加速组件需分别核对，不能直接套用此分类。
- 开源 mt76 驱动仍会加载联发科提供的二进制无线固件（firmware）；驱动源码开源，不等于芯片运行的全部固件均开源。
- 此表说明的是构建配置，并非逐一检查已发布固件后的结果。实际安装包以对应构建的 `.manifest` 清单和设备运行状态为准；上游分支更新也可能改变默认配置。

### 核对依据

- [LEDE Filogic 默认软件包](https://github.com/coolsnowwolf/lede/blob/master/target/linux/mediatek/filogic/target.mk)包含 `kmod-mt7915e`；[mt76 软件包定义](https://github.com/coolsnowwolf/lede/blob/master/package/kernel/mt76/Makefile)声明 GPLv2 许可证。
- ImmortalWrt 的 AX6000 设备定义包含 `kmod-mt7915e`，本项目三个官方源码版本继承该设备定义：[24.10 设备定义](https://github.com/immortalwrt/immortalwrt/blob/openwrt-24.10/target/linux/mediatek/image/filogic.mk)、[25.12 设备定义](https://github.com/immortalwrt/immortalwrt/blob/openwrt-25.12/target/linux/mediatek/image/filogic.mk)。
- 两个 237 版本使用的 [AX6000 上游配置](https://github.com/padavanonly/immortalwrt-mt798x-6.6/blob/openwrt-24.10-6.6/defconfig/mt7986-ax6000.config)启用了 `kmod-mt_wifi`、`kmod-warp` 和 `mtwifi-cfg`。

## 刷机注意事项

1. 刷机前请确认设备已经刷入支持 110M UBI 分区的不死 uboot。
2. 请确认固件型号与设备分区布局匹配，并提前备份重要分区。
3. 刷机存在变砖风险，请准备好 uboot 恢复或串口救砖方案。
