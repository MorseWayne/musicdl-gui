# 快速开始指南 - 应用发布

本指南帮助你快速了解如何发布 MusicdlGUI 应用的 Windows 版本。

## 🚀 最快速的方式：使用 GitHub Actions 自动发布

### 第一步：推送代码到 GitHub

```bash
git add .
git commit -m "feat: 添加应用发布配置

1. 新增 PyInstaller 构建配置
2. 添加本地构建脚本
3. 配置 GitHub Actions 自动构建
4. 支持 Win32 和 Win64 双架构发布"
git push
```

### 第二步：创建发布标签

```bash
# 创建版本标签
git tag v1.0.0

# 推送标签到 GitHub（这会自动触发构建）
git push origin v1.0.0
```

### 第三步：等待自动构建

1. 访问你的 GitHub 仓库
2. 点击 "Actions" 标签
3. 查看 "Build Release" 工作流的运行状态
4. 大约 5-10 分钟后构建完成

### 第四步：查看发布

1. 进入 "Releases" 标签
2. 找到新创建的 v1.0.0 版本
3. 下载并测试生成的应用：
   - `MusicdlGUI-Windows-x64.zip` (64位版本)
   - `MusicdlGUI-Windows-x86.zip` (32位版本)

## 💻 本地构建方式

如果你想在本地构建：

### 安装依赖

```bash
pip install pyinstaller
pip install -r requirements.txt
```

### 生成图标（可选）

```bash
# 如果有 Pillow
pip install Pillow
python create_icon.py

# 或者手动放置 icon.ico 文件到项目根目录
```

### 构建 64位版本

```bash
python build.py x64
```

### 构建 32位版本

需要 32位 Python 环境：

```bash
# 使用 32位 Python
C:\Python311-32\python.exe build.py x86
```

### 查看输出

构建成功后，在 `dist` 目录下可以找到：
- `dist/MusicdlGUI-x64/MusicdlGUI.exe` - 可执行文件
- `dist/MusicdlGUI-Windows-x64.zip` - 发布压缩包

## 📋 发布检查清单

在发布新版本前，请确认：

- [ ] 所有功能正常工作
- [ ] 代码已经提交到 GitHub
- [ ] 更新了版本号（如果需要）
- [ ] README.md 中的信息是最新的
- [ ] 测试了本地构建（可选）
- [ ] 创建了合适的版本标签（如 v1.0.0）

## 🔄 持续发布流程

后续发布新版本：

```bash
# 1. 开发和测试新功能
# 2. 提交所有更改
git add .
git commit -m "feat: 添加新功能"
git push

# 3. 创建新版本标签
git tag v1.1.0
git push origin v1.1.0

# 4. GitHub Actions 自动构建并发布
```

## ❓ 遇到问题？

1. **构建失败**：查看 Actions 日志，找到具体错误
2. **依赖问题**：确保 requirements.txt 包含所有依赖
3. **Python 架构问题**：32位版本需要 32位 Python
4. **详细文档**：查看 [BUILD.md](BUILD.md)

## 📚 更多信息

- **详细构建文档**：[BUILD.md](BUILD.md)
- **图标制作说明**：[ICON.md](ICON.md)
- **项目说明**：[README.md](README.md)

---

**提示**：第一次发布建议先在本地测试构建，确认没有问题后再使用 GitHub Actions 自动发布。
