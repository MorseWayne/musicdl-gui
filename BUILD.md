# 构建和发布指南

本文档说明如何构建 MusicdlGUI 的 Windows 发布版本（支持 32位 和 64位）。

## 目录

- [前置要求](#前置要求)
- [本地构建](#本地构建)
- [自动化构建（GitHub Actions）](#自动化构建github-actions)
- [发布流程](#发布流程)
- [常见问题](#常见问题)

## 前置要求

### 本地构建需要

1. **Python 环境**
   - Python 3.6 或更高版本
   - 推荐使用 Python 3.11

2. **必需的 Python 包**
   ```bash
   pip install pyinstaller
   pip install -r requirements.txt
   ```

3. **图标文件（可选）**
   - 在项目根目录放置 `icon.ico` 文件
   - 如果没有图标文件，程序将使用默认图标

### 架构说明

- **x64 (64位)**：适用于 64位 Windows 系统（主流）
- **x86 (32位)**：适用于 32位 Windows 系统（较老系统）

⚠️ **重要提示**：
- 构建 64位版本需要 64位 Python
- 构建 32位版本需要 32位 Python

## 本地构建

### 方法一：使用构建脚本（推荐）

1. **构建 64位版本**
   ```bash
   python build.py x64
   ```

2. **构建 32位版本**
   ```bash
   python build.py x86
   ```

3. **自动检测当前架构**
   ```bash
   python build.py
   ```

### 方法二：直接使用 PyInstaller

```bash
# 64位版本
pyinstaller --name=MusicdlGUI --onefile --windowed --clean ^
    --distpath=dist/MusicdlGUI-x64 ^
    --add-data=components.py;. ^
    --add-data=dialogs.py;. ^
    --add-data=styles.py;. ^
    --add-data=workers.py;. ^
    --icon=icon.ico ^
    musicdlgui.py
```

### 构建输出

构建完成后，会在 `dist` 目录下生成：

```
dist/
├── MusicdlGUI-x64/
│   ├── MusicdlGUI.exe          # 可执行文件
│   ├── README.md               # 说明文档
│   ├── LICENSE                 # 许可证
│   └── 使用说明.txt            # 使用说明
├── MusicdlGUI-Windows-x64.zip  # 发布压缩包
└── MusicdlGUI-Windows-x86.zip  # 发布压缩包（如果构建了 32位）
```

## 自动化构建（GitHub Actions）

本项目配置了 GitHub Actions 自动构建工作流，可以自动构建 32位 和 64位版本。

### 触发方式

#### 方式一：创建版本标签（推荐）

1. **创建并推送标签**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. GitHub Actions 会自动：
   - 构建 32位 和 64位版本
   - 创建 GitHub Release
   - 上传构建的安装包到 Release

#### 方式二：手动触发

1. 进入 GitHub 仓库
2. 点击 "Actions" 标签
3. 选择 "Build Release" 工作流
4. 点击 "Run workflow" 按钮
5. 选择分支并运行

### 查看构建结果

构建完成后：

- **成功**：在 Actions 页面可以看到绿色的✓标记
- **产物下载**：点击构建任务，在 "Artifacts" 部分可以下载生成的文件
- **Release**：如果是标签触发，会自动创建 Release

## 发布流程

### 完整的发布步骤

1. **准备发布**
   ```bash
   # 确保所有更改已提交
   git status
   
   # 更新版本号（可选）
   # 编辑相关文件中的版本号
   ```

2. **创建版本标签**
   ```bash
   # 创建标签（例如 v1.0.0）
   git tag -a v1.0.0 -m "Release version 1.0.0"
   
   # 推送标签到 GitHub
   git push origin v1.0.0
   ```

3. **等待自动构建**
   - 访问 GitHub Actions 页面
   - 查看构建进度
   - 等待构建完成（通常需要 5-10 分钟）

4. **检查 Release**
   - 进入 GitHub 仓库的 "Releases" 页面
   - 找到新创建的 Release
   - 验证附件文件：
     - `MusicdlGUI-Windows-x64.zip`
     - `MusicdlGUI-Windows-x86.zip`

5. **编辑 Release 说明（可选）**
   - 添加更新日志
   - 说明新功能和修复的问题
   - 添加使用说明

### 发布版本号规范

建议使用语义化版本号（Semantic Versioning）：

- `v1.0.0` - 主版本号.次版本号.修订号
- `v1.0.0-beta` - 测试版本
- `v1.0.0-rc1` - 候选发布版本

示例：
- `v1.0.0` - 首次正式发布
- `v1.1.0` - 新增功能
- `v1.1.1` - 修复问题
- `v2.0.0` - 重大更新

## 常见问题

### Q1: 构建失败，提示找不到模块

**问题**：`ModuleNotFoundError: No module named 'xxx'`

**解决方案**：
```bash
# 安装缺失的依赖
pip install -r requirements.txt
```

### Q2: 32位版本构建失败

**问题**：需要构建 32位版本，但当前是 64位 Python

**解决方案**：
1. 下载并安装 32位 Python（从 python.org）
2. 使用 32位 Python 运行构建脚本：
   ```bash
   C:\Python311-32\python.exe build.py x86
   ```

### Q3: 生成的 exe 文件很大

**说明**：PyInstaller 会将所有依赖打包到一个文件中，所以文件较大是正常的。

**优化方案**：
- 使用 `--onedir` 代替 `--onefile`（文件分散但总大小更小）
- 使用 UPX 压缩（已在配置中启用）

### Q4: 运行 exe 时报毒或被阻止

**原因**：PyInstaller 打包的程序可能被杀毒软件误报

**解决方案**：
- 添加到杀毒软件白名单
- 使用代码签名证书签名（推荐，但需要购买证书）

### Q5: GitHub Actions 构建失败

**检查步骤**：
1. 查看 Actions 日志，找到具体错误信息
2. 检查 `requirements.txt` 是否完整
3. 确认 `build.py` 脚本没有语法错误
4. 检查工作流配置文件 `.github/workflows/build-release.yml`

### Q6: 如何添加自定义图标？

**步骤**：
1. 准备一个 `.ico` 格式的图标文件
2. 将其命名为 `icon.ico`
3. 放在项目根目录
4. 重新构建

**在线工具推荐**：
- https://www.icoconverter.com/
- https://convertio.co/zh/png-ico/

### Q7: 如何测试构建的应用？

**测试清单**：
- [ ] 程序能正常启动
- [ ] 界面显示正常
- [ ] 搜索功能正常
- [ ] 下载功能正常
- [ ] 设置保存和加载正常
- [ ] 在不同 Windows 版本上测试（Win10, Win11）

## 技术细节

### PyInstaller 配置说明

关键参数：
- `--onefile`: 打包成单个 exe 文件
- `--windowed`: 不显示控制台窗口（GUI 应用）
- `--clean`: 清理临时文件
- `--add-data`: 添加额外的数据文件
- `--hidden-import`: 添加隐式导入的模块
- `--icon`: 设置应用图标

### GitHub Actions 工作流

工作流配置位于 `.github/workflows/build-release.yml`

特点：
- 使用矩阵构建同时构建 32位 和 64位版本
- 自动上传构建产物
- 标签推送时自动创建 Release
- 使用最新的 GitHub Actions（v4/v5）

## 参考资源

- [PyInstaller 官方文档](https://pyinstaller.org/en/stable/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)

## 支持

如有问题，请：
1. 查看本文档的常见问题部分
2. 在 GitHub 提交 Issue
3. 查看 PyInstaller 官方文档

---

最后更新：2026-01-11
