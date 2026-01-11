#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
本地构建脚本 - 用于打包 Windows 应用程序
支持 win32 和 win64 架构
"""
import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


def clean_build():
    """清理之前的构建文件"""
    print("🧹 清理旧的构建文件...")
    dirs_to_clean = ['build', 'dist']
    files_to_clean = ['musicdlgui.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   ✓ 删除 {dir_name}/")
    
    print()


def check_dependencies():
    """检查必要的依赖是否已安装"""
    print("📦 检查依赖...")
    required_packages = {
        'PyInstaller': 'pyinstaller',
        'PyQt5': 'PyQt5',
        'musicdl': 'musicdl',
        'requests': 'requests',
    }
    
    missing_packages = []
    for display_name, package_name in required_packages.items():
        try:
            __import__(package_name)
            print(f"   ✓ {display_name}")
        except ImportError:
            print(f"   ✗ {display_name} 未安装")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n❌ 缺少依赖包: {', '.join(missing_packages)}")
        print(f"请运行: pip install {' '.join(missing_packages)}")
        return False
    
    print()
    return True


def create_icon_if_missing():
    """如果不存在图标文件，创建一个简单的图标"""
    if not os.path.exists('icon.ico'):
        print("⚠️  未找到 icon.ico，将使用默认图标")
        print("   提示: 您可以将自定义的 icon.ico 文件放在项目根目录")
    print()


def build_exe(architecture='x64'):
    """
    使用 PyInstaller 构建可执行文件
    
    Args:
        architecture: 'x86' (32位) 或 'x64' (64位)
    """
    print(f"🔨 开始构建 Windows {architecture} 版本...")
    
    # 根据架构设置输出目录
    dist_dir = f'dist/MusicdlGUI-{architecture}'
    
    # PyInstaller 命令
    cmd = [
        'pyinstaller',
        '--name=MusicdlGUI',
        '--onefile',  # 打包成单个文件
        '--windowed',  # 不显示控制台窗口
        '--clean',
        f'--distpath={dist_dir}',
        '--add-data=components.py;.',
        '--add-data=dialogs.py;.',
        '--add-data=styles.py;.',
        '--add-data=workers.py;.',
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=musicdl',
        '--hidden-import=requests',
    ]
    
    # 如果有图标文件，添加图标参数
    if os.path.exists('icon.ico'):
        cmd.append('--icon=icon.ico')
    
    cmd.append('musicdlgui.py')
    
    print(f"   执行命令: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        print(f"\n✅ 构建成功!")
        print(f"   输出目录: {dist_dir}/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 构建失败: {e}")
        return False


def create_release_package(architecture='x64'):
    """创建发布包（包含 README 等文件）"""
    print(f"\n📦 创建发布包...")
    
    dist_dir = Path(f'dist/MusicdlGUI-{architecture}')
    if not dist_dir.exists():
        print(f"   ✗ 输出目录不存在: {dist_dir}")
        return False
    
    # 复制必要的文件到发布目录
    files_to_copy = [
        ('README.md', 'README.md'),
        ('LICENSE', 'LICENSE'),
    ]
    
    for src, dst in files_to_copy:
        if os.path.exists(src):
            shutil.copy2(src, dist_dir / dst)
            print(f"   ✓ 复制 {src}")
    
    # 创建使用说明
    usage_guide = """MusicdlGUI 使用说明
==================

运行方式：
双击 MusicdlGUI.exe 即可启动程序

首次使用：
1. 选择音乐平台（建议选择 2-3 个）
2. 输入搜索关键词
3. 在搜索结果中右键选择要下载的歌曲
4. 点击 "Settings" 可以配置下载目录和 Cookies

注意事项：
- 下载的音乐文件默认保存在程序目录下的 musicdl_outputs 文件夹
- 可以在设置中配置各平台的 Cookies 以获取更高音质
- 本程序仅供学习和教育使用，请勿用于商业用途

更多信息请参考 README.md
"""
    
    with open(dist_dir / '使用说明.txt', 'w', encoding='utf-8') as f:
        f.write(usage_guide)
    print(f"   ✓ 创建 使用说明.txt")
    
    # 创建压缩包
    archive_name = f'MusicdlGUI-Windows-{architecture}'
    archive_path = Path('dist') / archive_name
    
    print(f"\n   正在创建压缩包: {archive_name}.zip")
    shutil.make_archive(str(archive_path), 'zip', dist_dir)
    print(f"   ✓ 压缩包已创建: {archive_path}.zip")
    
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("MusicdlGUI 构建脚本")
    print("=" * 60)
    print()
    
    # 检查 Python 版本
    python_version = sys.version_info
    print(f"Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    print(f"平台: {platform.system()} {platform.machine()}")
    print()
    
    # 清理旧文件
    clean_build()
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查图标
    create_icon_if_missing()
    
    # 确定架构
    if len(sys.argv) > 1:
        arch = sys.argv[1].lower()
        if arch not in ['x86', 'x64', 'both']:
            print(f"❌ 无效的架构参数: {arch}")
            print("   用法: python build.py [x86|x64|both]")
            sys.exit(1)
    else:
        # 根据当前 Python 架构自动选择
        arch = 'x64' if platform.machine().endswith('64') else 'x86'
        print(f"ℹ️  未指定架构，使用当前环境架构: {arch}")
        print()
    
    # 构建
    if arch == 'both':
        print("⚠️  注意: 'both' 选项需要分别在 32位 和 64位 Python 环境中运行")
        print("   当前将构建: {}\n".format('x64' if platform.machine().endswith('64') else 'x86'))
        arch = 'x64' if platform.machine().endswith('64') else 'x86'
    
    success = build_exe(arch)
    
    if success:
        create_release_package(arch)
        print("\n" + "=" * 60)
        print("✅ 构建完成!")
        print("=" * 60)
        print(f"\n可执行文件位置: dist/MusicdlGUI-{arch}/MusicdlGUI.exe")
        print(f"发布包位置: dist/MusicdlGUI-Windows-{arch}.zip")
    else:
        print("\n" + "=" * 60)
        print("❌ 构建失败")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
