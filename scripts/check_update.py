#!/usr/bin/env python3
"""
APK Update Checker v1.1
支持 modules.lsposed.org 和 GitHub Releases
"""

import json
import re
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def fetch_json(url: str, retries: int = 3) -> dict:
    """获取 JSON 数据，支持重试"""
    headers = {"User-Agent": "ApkUpdateScript/1.1"}
    for attempt in range(retries):
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (URLError, HTTPError) as e:
            if attempt == retries - 1:
                print(f"[ERROR] 获取 {url} 失败: {e}")
                return {}


def parse_version_with_suffix(version: str) -> tuple:
    """
    解析版本号，支持多种格式：
    - X.Y.Z-YYYYMMDD (如 2.1.4-20260510)
    - buildcode-X.Y.Z (如 4571-2.10.166)
    - X.Y.Z alone (如 2.1.4)
    返回: (main_version, suffix)
    """
    if "-" not in version:
        return version, None
    
    parts = version.split("-", 1)
    prefix = parts[0]
    suffix = parts[1] if len(parts) > 1 else None
    
    # 判断格式
    # 如果 prefix 是纯数字(版本码)，则后缀是完整版本号
    if prefix.isdigit():
        return suffix, prefix  # main_ver, build_code
    # 如果 prefix 包含数字(如 2.10)，则前缀是版本号
    elif re.match(r"^\d+\.", prefix):
        return prefix, suffix
    # 其他情况返回原始
    return version, None


def parse_semver(version: str) -> tuple:
    """解析语义化版本号，返回 (major, minor, patch)"""
    main_ver, _ = parse_version_with_suffix(version)
    match = re.match(r"(\d+)\.(\d+)\.?(\d*)", main_ver)
    if match:
        return tuple(map(int, (match.group(1), match.group(2), match.group(3) or 0)))
    return (0, 0, 0)


def compare_versions(v1: str, v2: str) -> int:
    """比较两个版本号，返回: 1(v1>v2), -1(v1<v2), 0(相等)"""
    ver1 = parse_semver(v1)
    ver2 = parse_semver(v2)
    if ver1 > ver2:
        return 1
    elif ver1 < ver2:
        return -1
    return 0


def check_lsposed_module(package_name: str) -> dict:
    """
    检查 LSPosed 仓库模块版本
    模块 JSON: https://modules.lsposed.org/module/{package}.json
    返回: {version, download_url, releases, ...}
    """
    url = f"https://modules.lsposed.org/module/{package_name}.json"
    data = fetch_json(url)
    
    if not data:
        return {"error": "无法获取 LSPosed 数据", "source": "lsposed"}
    
    # 提取版本信息
    latest_release = data.get("latestRelease", "")
    main_version, date_suffix = parse_version_with_suffix(latest_release)
    
    # 获取 releases 中的第一个（最新版本）详情
    releases = data.get("releases", [])
    latest_info = releases[0] if releases else {}
    assets = latest_info.get("releaseAssets", [])
    
    # 选择合适的 APK（优先 OS3/HyperOS3）
    download_url = None
    apk_name = None
    for asset in assets:
        name = asset.get("name", "")
        if "OS3" in name or "Android16" in name:
            download_url = asset.get("downloadUrl")
            apk_name = name
            break
    if not download_url and assets:
        download_url = assets[0].get("downloadUrl")
        apk_name = assets[0].get("name")
    
    return {
        "source": "lsposed",
        "module_url": data.get("url", ""),
        "name": data.get("name", package_name),
        "description": data.get("description", ""),
        "version": main_version,
        "full_release": latest_release,
        "date_suffix": date_suffix,
        "published_at": latest_info.get("publishedAt", ""),
        "update_body": latest_info.get("descriptionHTML", ""),
        "download_url": download_url,
        "apk_name": apk_name,
        "downloads": assets[0].get("downloadCount", 0) if assets else 0,
        "apk_size": assets[0].get("size", 0) if assets else 0
    }


def check_github_release(owner: str, repo: str) -> dict:
    """检查 GitHub Release 最新版本"""
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    data = fetch_json(url)
    
    if not data or "message" in data:
        return {"error": "GitHub API 请求失败", "source": "github"}
    
    tag_name = data.get("tag_name", "")
    main_version, _ = parse_version_with_suffix(tag_name)
    
    # 提取 APK 下载链接
    assets = data.get("assets", [])
    apk_url = None
    for asset in assets:
        if asset.get("name", "").endswith(".apk"):
            apk_url = asset.get("browser_download_url")
            break
    
    return {
        "source": "github",
        "owner": owner,
        "repo": repo,
        "version": main_version,
        "full_tag": tag_name,
        "name": data.get("name", ""),
        "body": data.get("body", ""),
        "published_at": data.get("published_at", ""),
        "download_url": apk_url
    }


def main():
    if len(sys.argv) < 2:
        print("用法:\n  LSPosed模块: python3 check_update.py <package_name>\n  GitHub仓库:  python3 check_update.py <name> --github <owner/repo>\n示例:\n  python3 check_update.py com.sevtinge.hyperceiler\n  python3 check_update.py hyperisland --github Xposed-Modules-Repo/io.github.hyperisland")
        sys.exit(1)
    
    package = sys.argv[1]
    use_github = "--github" in sys.argv
    
    if use_github:
        idx = sys.argv.index("--github")
        if idx + 1 < len(sys.argv):
            owner_repo = sys.argv[idx + 1]
            if "/" not in owner_repo:
                print("[ERROR] GitHub 仓库格式应为: owner/repo")
                sys.exit(1)
            owner, repo = owner_repo.split("/")
            result = check_github_release(owner, repo)
        else:
            print("[ERROR] 需要指定 GitHub 仓库，格式: owner/repo")
            sys.exit(1)
    else:
        # 优先使用 LSPosed API
        result = check_lsposed_module(package)
    
    if result:
        if "error" in result:
            print(f"[{result['source'].upper()}] {result['error']}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("[INFO] 未找到更新信息")


if __name__ == "__main__":
    main()