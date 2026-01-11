#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
依赖检查脚本 - 验证所有必需的包是否已正确安装
"""
import sys
import platform

def check_python_version():
    """检查 Python 版本"""
    print("=" * 60)
    print("Python 环境检查")
    print("=" * 60)
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    print(f"平台: {platform.system()} {platform.machine()}")
    print(f"架构: {'64位' if platform.machine().endswith('64') else '32位'}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("❌ Python 版本过低，需要 Python 3.6 或更高版本")
        return False
    else:
        print("✅ Python 版本满足要求")
    return True

def check_dependencies():
    """检查依赖包"""
    print("\n" + "=" * 60)
    print("依赖包检查")
    print("=" * 60)
    
    required_packages = {
        'PyQt5': {
            'import_name': 'PyQt5',
            'description': 'GUI 框架',
            'required': True
        },
        'requests': {
            'import_name': 'requests',
            'description': 'HTTP 请求库',
            'required': True
        },
        'musicdl': {
            'import_name': 'musicdl',
            'description': '音乐下载核心库',
            'required': True
        },
        'PyInstaller': {
            'import_name': 'PyInstaller',
            'description': '打包工具（构建时需要）',
            'required': False
        },
        'PIL': {
            'import_name': 'PIL',
            'description': '图像处理库（生成图标时需要）',
            'required': False
        }
    }
    
    all_ok = True
    missing_required = []
    missing_optional = []
    
    for name, info in required_packages.items():
        try:
            module = __import__(info['import_name'])
            version = getattr(module, '__version__', '未知')
            status = "✅"
            desc = info['description']
            print(f"{status} {name:15s} {version:10s} - {desc}")
        except ImportError:
            if info['required']:
                status = "❌"
                missing_required.append(name)
                all_ok = False
            else:
                status = "⚠️ "
                missing_optional.append(name)
            desc = info['description']
            print(f"{status} {name:15s} {'未安装':10s} - {desc}")
    
    print("\n" + "=" * 60)
    print("检查结果")
    print("=" * 60)
    
    if missing_required:
        print(f"\n❌ 缺少必需的依赖包: {', '.join(missing_required)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_required)}")
    
    if missing_optional:
        print(f"\n⚠️  缺少可选的依赖包: {', '.join(missing_optional)}")
        print("这些包不是运行程序必需的，但在某些场景下需要:")
        if 'PyInstaller' in missing_optional:
            print("  - PyInstaller: 构建可执行文件时需要")
        if 'PIL' in missing_optional:
            print("  - PIL (Pillow): 生成图标时需要")
        print(f"安装命令: pip install {' '.join(missing_optional)}")
    
    if not missing_required:
        print("\n✅ 所有必需的依赖包都已安装")
        print("程序可以正常运行！")
    
    return all_ok

def check_files():
    """检查关键文件是否存在"""
    import os
    
    print("\n" + "=" * 60)
    print("文件检查")
    print("=" * 60)
    
    critical_files = [
        ('musicdlgui.py', '主程序文件', True),
        ('components.py', '组件模块', True),
        ('dialogs.py', '对话框模块', True),
        ('styles.py', '样式模块', True),
        ('workers.py', '工作线程模块', True),
        ('requirements.txt', '依赖列表', True),
        ('build.py', '构建脚本', False),
        ('musicdlgui.spec', 'PyInstaller 配置', False),
        ('icon.ico', '应用图标', False),
    ]
    
    all_ok = True
    for filename, desc, required in critical_files:
        if os.path.exists(filename):
            print(f"✅ {filename:20s} - {desc}")
        else:
            if required:
                print(f"❌ {filename:20s} - {desc} (必需)")
                all_ok = False
            else:
                print(f"⚠️  {filename:20s} - {desc} (可选)")
    
    return all_ok

def main():
    """主函数"""
    print("\n🔍 MusicdlGUI 环境检查工具\n")
    
    # 检查 Python 版本
    python_ok = check_python_version()
    
    # 检查依赖
    deps_ok = check_dependencies()
    
    # 检查文件
    files_ok = check_files()
    
    # 总结
    print("\n" + "=" * 60)
    print("总结")
    print("=" * 60)
    
    if python_ok and deps_ok and files_ok:
        print("\n✅ 所有检查通过！")
        print("\n你可以:")
        print("1. 运行程序: python musicdlgui.py")
        print("2. 构建应用: python build.py x64")
        return 0
    else:
        print("\n❌ 检查未通过，请解决上述问题")
        print("\n建议:")
        if not python_ok:
            print("- 升级 Python 到 3.6 或更高版本")
        if not deps_ok:
            print("- 安装缺失的必需依赖: pip install -r requirements.txt")
        if not files_ok:
            print("- 确保所有必需的文件都存在")
        return 1

if __name__ == '__main__':
    exit_code = main()
    print("\n按回车键退出...")
    input()
    sys.exit(exit_code)
