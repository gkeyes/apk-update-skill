# LSPosed Module Update Skill

自动化管理 LSPosed 模块更新的 AI Skill。

## 功能

- 查询本地已安装 LSPosed 模块版本
- 通过 modules.lsposed.org API 获取最新版本信息
- 语义化版本对比（支持多种格式：semver、X.Y.Z-YYYYMMDD、buildcode-X.Y.Z）
- 自动定位 GitHub 仓库（支持 Xposed-Modules-Repo）
- 下载并安装最新版本 APK（自动处理 FUSE 权限问题）
- 安装后自动清理残留文件
- 输出结构化更新简报

## 使用方法

```bash
# 检查模块更新
python3 scripts/check_update.py com.sevtinge.hyperceiler

# 指定 GitHub 仓库
python3 scripts/check_update.py hyperisland --github Xposed-Modules-Repo/io.github.hyperisland
```

## 支持的模块

- HyperIsland (io.github.hyperisland)
- HyperCeiler (com.sevtinge.hyperceiler)
- KernelSU-Next (com.rifsxd.ksunext)
- 净址AdBlock (com.close.hook.ads)
- 任何发布在 Xposed-Modules-Repo 的模块

## 工作流程

1. 查询本地已安装版本
2. 通过 modules.lsposed.org 获取模块元数据
3. 解析版本号（支持多种格式）
4. 版本对比
5. 下载最新 APK
6. 安装 APK（/data/local/tmp 中转）
7. 验证安装
8. 清理残留文件
9. 输出更新简报

## License

MIT
