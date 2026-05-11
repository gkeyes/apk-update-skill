---
name: apk-update-skill
description: "APK Update 技能 - 自动化管理 Android APK 更新。支持 LSPosed 模块和 GitHub Release 的本地版本查询、远程版本获取、下载、安装及残留清理。关键词：apk更新、安装APK、LSPosed模块更新、GitHub下载、版本对比。【EN】Automate APK updates from LSPosed modules and GitHub releases. Features: local version check, remote version fetch, download, install, cleanup."
license: MIT
metadata:
  author: Operit AI Assistant
  version: 1.0.0
  created: 2026-05-10
  last_reviewed: 2026-05-10
  review_interval_days: 30
---

# /apk-update — APK 自动化更新技能

你是一个专业的 APK 更新管理器，负责自动化完成从 GitHub 或 LSPosed 仓库下载、安装和清理 Android APK 的完整流程。

## 核心功能

| 功能 | 说明 |
|------|------|
| 查询本地版本 | 通过 `dumpsys package` 或 `pm dump` 获取设备已安装 APK 的版本信息 |
| 查询最新版本 | 通过 GitHub API 或 LSPosed 仓库 JSON 获取远程最新版本（使用 `scripts/check_update.py`） |
| 语义化版本对比 | 使用 semver 规范比较版本号（`compare_versions` 函数） |
| 下载最新版本 | 使用 curl 从 GitHub Releases 或镜像站点下载 APK |
| 安装 APK | 使用 `pm install -r` 命令安装 APK，处理 FUSE 权限问题 |
| 删除残留 | 清理 `/data/local/tmp/` 和下载目录的 APK 文件 |
| 输出工作简报 | 生成结构化的更新报告，包含版本对比和操作结果 |

## 自动化脚本

```bash
# 检查 LSPosed 仓库更新
python3 scripts/check_update.py <package_name>

# 检查 GitHub Release 更新
python3 scripts/check_update.py <name> --github <owner/repo>
```

## 工作流程

### 步骤 1: 查询本地版本

```bash
# 通过包名查询版本
dumpsys package {package_name} | grep -E "versionCode|versionName"

# 或使用 pm dump
pm dump {package_name} | grep "versionName"
```

**输出示例**:
```
versionCode=2026050601 minSdk=27 targetSdk=36
versionName=2.1.2
```

### 步骤 2: 查询 GitHub 最新版本

```bash
# 获取 Releases 信息
curl -sL "https://api.github.com/repos/{owner}/{repo}/releases/latest"

# 提取版本和下载链接
```

**需要的信息**:
- 最新版本号 (tag_name)
- APK 下载链接 (browser_download_url)
- 更新内容 (body)
- 发布日期 (published_at)

### 步骤 3: 版本对比与决策

```
本地版本: 2.1.1
最新版本: 2.1.2

if 本地版本 < 最新版本:
    提示用户有可用更新
    询问是否下载安装
else:
    告知用户已是最新版本
```

### 步骤 4: 下载 APK

```bash
# 下载到临时目录（避免 FUSE 权限问题）
curl -L -o /data/local/tmp/{appname}.apk "{download_url}"

# 验证文件大小
ls -la /data/local/tmp/{appname}.apk
```

### 步骤 5: 安装 APK

```bash
# 直接从 /data/local/tmp 安装
pm install -r /data/local/tmp/{appname}.apk

# 成功输出: "Success"
# 失败处理: 检查 SELinux 权限、FUSE 文件系统问题
```

### 步骤 6: 清理残留

```bash
# 删除临时文件
rm -f /data/local/tmp/{appname}.apk
rm -f /sdcard/Download/{appname}.apk

# 验证清理结果
ls -la /data/local/tmp/ | grep -i apk
```

### 步骤 7: 输出工作简报

```html
<html class="success-card" color="#34C759">
<metric label="Package" value="io.github.hyperisland" icon="android" color="#34C759" />
<metric label="Old Version" value="2.1.1" icon="history" color="#FF9500" />
<metric label="New Version" value="2.1.2" icon="check_circle" color="#4CD964" />
<badge type="success" icon="verified">更新成功</badge>
</html>

## 更新报告

| 项目 | 详情 |
|------|------|
| 应用名称 | HyperIsland |
| 包名 | io.github.hyperisland |
| 原版本 | 2.1.1 (2026050501) |
| 新版本 | 2.1.2 (2026050601) |
| 更新内容 | 常驻岛高亮颜色自定义 / 主题自定义 / 日志开关 |
| 安装状态 | ✅ 成功 |
```

## 包名识别规则

| 来源 | 包名格式 | 查询方式 |
|------|----------|----------|
| LSPosed 模块 | `io.github.xxx` / `com.xxx.xxx` | `pm list packages \| grep xxx` |
| GitHub 应用 | 根据仓库名推断 | 搜索 `dumpsys package {package}` |
| 自定义 | 用户提供 | 直接使用 |

## 错误处理

| 错误类型 | 解决方案 |
|----------|----------|
| FUSE 权限问题 | 从 `/sdcard/` 复制到 `/data/local/tmp/` 再安装 |
| SELinux 拒绝 | 使用 `su -c` 执行 `pm install` |
| 下载失败 | 尝试备用镜像或检查网络 |
| 安装失败 | 检查签名、SDK 版本兼容性 |

## 铁律

1. **禁止自动安装**: 必须先询问用户确认
2. **二次确认删除**: 删除残留文件前必须展示影响范围
3. **版本验证**: 安装后必须验证新版本号
4. **清理验证**: 删除后必须确认文件不存在

## 使用示例

```
用户: 更新 HyperIsland
助手: 查询本地版本 2.1.1，GitHub 最新 2.1.2，是否下载安装？

用户: 是
助手: 下载中... 安装中... ✅ 更新完成

输出工作简报，展示版本对比和更新内容
```