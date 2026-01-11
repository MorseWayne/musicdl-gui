# musicdl-gui

MusicDL 的图形用户界面程序 - 一个美观易用的音乐下载工具

## 简介

musicdl-gui 是基于 [musicdl](https://github.com/CharlesPikachu/musicdl) 开发的桌面图形界面程序，提供了友好的用户界面，让音乐搜索和下载变得更加简单。

## ⚠️ 免责声明

本项目仅供学习和教育使用，不得用于商业用途。

本项目通过公开的网络接口进行交互，不托管或分发任何受版权保护的内容。

如需访问付费曲目，请购买或订阅相关音乐服务——请勿使用本项目绕过付费限制或 DRM。

如果您是版权方并认为本项目侵犯了您的权利，请通过 Issue 联系我，我将及时处理。

## 特性

- 🎵 支持多个音乐平台搜索：QQ音乐、酷我音乐、咪咕音乐、千千音乐、酷狗音乐、网易云音乐
- 🎨 现代化的图形界面，操作简单直观
- ⚙️ 灵活的下载配置
  - 自定义下载目录
  - 三种目录组织方式：扁平结构、按音乐源分类、按日期分类
- 🔑 支持配置 Cookies 获取 VIP 音质
- 💾 支持夸克网盘 Cookies 下载分享网站的无损音乐
- ⚡ 优化的搜索速度和下载体验

## 安装

### 依赖要求

- Python 3.6+
- PyQt5
- musicdl
- requests

### 安装步骤

1. 克隆仓库

```bash
git clone https://github.com/MorseWayne/musicdl-gui.git
cd musicdl-gui
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 方式一：直接运行 Python 脚本

1. 运行程序

```bash
python musicdlgui.py
```

2. 选择音乐平台（建议选择 2-3 个）

3. 输入搜索关键词，点击 "Search" 按钮

4. 在搜索结果中右键点击要下载的歌曲，选择 "Download"

### 方式二：使用编译后的可执行文件（推荐）

1. 从 [Releases](https://github.com/MorseWayne/musicdl-gui/releases) 页面下载对应系统的版本：
   - `MusicdlGUI-Windows-x64.zip` - 64位 Windows 系统
   - `MusicdlGUI-Windows-x86.zip` - 32位 Windows 系统

2. 解压后双击 `MusicdlGUI.exe` 即可运行

3. 无需安装 Python 环境，开箱即用

## 设置说明

点击 "Settings - 设置" 按钮可以配置：

### 下载目录

- **Directory**: 选择音乐下载保存的位置
- **Directory Structure**: 选择文件组织方式
  - **Flat**: 所有音乐文件直接保存到设置目录
  - **By Source**: 在设置目录下按音乐平台创建子文件夹
  - **By Date**: 按日期和搜索关键词创建子文件夹（原有结构）

### Cookies 配置

为了获取更高音质或下载 VIP 音乐，可以配置各个平台的 Cookies：

1. 登录对应的音乐平台网页版
2. 打开浏览器开发者工具（F12）
3. 在 Network 标签页找到请求，复制 Cookie
4. 粘贴到对应平台的 Cookies 配置框

### 夸克网盘 Cookies

用于下载米兔音乐、歌曲宝、音乐岛、布谷音乐等分享网站的无损音乐：

1. 登录 https://pan.quark.cn/
2. 从浏览器开发者工具获取 Cookie
3. 粘贴到夸克网盘 Cookies 配置框

## 截图

（待添加）

## 开发计划

- [ ] 添加播放预览功能
- [ ] 支持批量下载
- [ ] 添加下载历史记录
- [ ] 支持更多音乐平台
- [ ] 优化界面设计

## 开发者指南

### 构建发布版本

如果你想自己构建应用程序，请参考 [BUILD.md](BUILD.md) 文档，里面详细说明了：
- 本地构建步骤
- 如何构建 32位 和 64位版本
- 使用 GitHub Actions 自动发布
- 常见问题解决方案

## 贡献

欢迎提交 Issue 和 Pull Request！

## 致谢

本项目基于 [musicdl](https://github.com/CharlesPikachu/musicdl) 开发，感谢原作者 Charles的皮卡丘。

## 许可证

MIT License
