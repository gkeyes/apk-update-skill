# LSPosed Module Update Skill

自动化管理 LSPosed 模块更新的 AI Skill。

## 功能

- 查询本地已安装 LSPosed 模块版本
- 通过 modules.lsposed.org API 获取最新版本信息
- 语义化版本对比（支持多种格式）
- 自动定位 GitHub 仓库
- 下载并安装最新版本 APK
- 自动清理残留文件
- 输出结构化更新简报

## 使用方法

```bash
python3 scripts/check_update.py com.sevtinge.hyperceiler
```

## License

MIT