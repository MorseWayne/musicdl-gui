# MusicdlGUI

基于 [musicdl](https://github.com/CharlesPikachu/musicdl) 和 PyQt5 的音乐搜索、下载桌面工具。

## 从源码运行

需要 Python 3.10+，建议使用 Python 3.11 / 3.12 x64。本项目当前适配并固定 `musicdl==2.14.0`、`PyQt5==5.15.11`。
旧版安装包内置的音乐源接口可能已失效；更新仓库不会更新旧的 exe，需要使用下面的源码运行方式，或重新构建。

```bash
python -m venv .venv
```

Linux / macOS：

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python check_env.py
.venv/bin/python musicdlgui.py
```

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe check_env.py
.\.venv\Scripts\python.exe musicdlgui.py
```

Linux 需要可用的图形桌面与 Qt 系统运行库。如果报 `xcb` 插件错误，请先检查系统图形依赖。

## 使用

1. 选择音乐来源，输入歌名、歌手或专辑，按 Enter 搜索。默认选择酷我、咪咕、网易云；也支持 QQ、酷狗、千千。
2. 各来源独立搜索，最多三个同时运行，结果陆续显示。默认每个来源最多 5 首、60 秒时限，可在设置中调整。
3. 点击列头排序，用“筛选当前结果”缩小范围。勾选歌曲后点击“下载选中”；未勾选时可下载高亮选中的行，也可以右键下载单首。
4. 下载状态逐首更新，失败后可重试。下载完成后用“打开下载目录”查看文件。

搜索时点击“取消搜索”，下载时点击“取消下载”。Esc 取消当前任务，Ctrl+L 聚焦搜索框。
取消搜索保留已有结果；取消下载清理当前临时文件，并停止后续队列。关闭窗口会先停止后台任务再退出。

“全选可见结果”只勾选筛选后可见的歌曲；已勾选的歌曲即使被筛选隐藏，仍计入“下载选中”的数量。

## 设置与文件保存

- 下载目录支持平铺、按来源、按来源/日期和关键词分类，新安装默认保存到用户音乐目录下的 `Musicdl`。
- 同名文件自动追加编号，不覆盖已有音乐；下载通过完整性检查后才保存正式文件。
- Cookie 按平台配置，下载 Cookie 留空时沿用搜索 Cookie。修改后重新搜索才能应用。仅能访问账号已有权限内的内容。
- 设置保存在系统用户配置目录的 `MusicdlGUI/settings.json`，日志在系统用户数据目录的 `MusicdlGUI/logs/`，可从设置中打开。
- 首次启动会读取并迁移程序旁的旧 `settings.json`，保留原文件和下载目录。旧相对路径按旧设置文件所在目录解析。
- 设置中的 Cookie 是本机明文凭据，请勿分享该文件。旧夸克 Cookie 值会保留；当前六个来源没有夸克入口，界面不再显示这一无效配置项。

## 搜索失败时

界面会保留每个来源的错误说明，并允许只重试失败来源。没有可下载结果与请求失败分别显示。
部分平台会受网络、登录状态或上游接口变化影响；默认时限包含该来源初始化和音乐地址解析的时间。

可运行限时联网诊断（不读取个人 Cookie，不下载歌曲）：

```bash
python check_env.py --search "晴天" --timeout 60 --limit 5
python check_env.py --search "晴天" --sources MiguMusicClient,KuwoMusicClient
```

请使用前面创建的虚拟环境中的 Python。诊断退出码：`0` 环境正常且搜索有结果，`1` 环境或参数错误，`2` 搜索未得到可用结果。
如果只有某一个来源超时，可以先切换其他来源，或在设置中延长时限。下载链接过期时应重新搜索后下载。

## 开发与验证

```bash
python -m pip install -r requirements.txt pytest
python -m pytest -q
```

测试覆盖 musicdl 数据适配、真实子进程取消和超时、Cookie 传递、无效下载响应、完整文件保存、设置迁移、排序选择与批量队列。
Qt 测试使用 offscreen 模式，不需要显示器；联网平台可用性由上述诊断命令单独验证。

核心模块：`backend.py` 负责平台适配和文件传输，`workers.py` 管理限时子进程，`musicdlgui.py` 管理界面与队列，`app_config.py` 管理设置和用户目录。
目前支持六个平台的 HTTP 直链音频；不支持 HLS 播放列表、DRM 解密或音频预览。

Windows 构建见 [BUILD.md](BUILD.md)。源码测试不代表 Windows 打包产物已经验收。

## 免责声明与许可证

本项目仅供学习和教育使用，不得用于商业用途。不托管或分发任何受版权保护的内容。
如需访问付费曲目，请购买或订阅相关音乐服务，请勿绕过付费限制或 DRM。

本仓库代码采用 MIT License；依赖 musicdl 的使用与分发须遵守其自身许可证。
感谢 musicdl 作者 Charles 的皮卡丘。
