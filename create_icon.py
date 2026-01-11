#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的图标生成脚本
如果没有 icon.ico 文件，可以运行此脚本生成一个默认图标
"""
import os

try:
    from PIL import Image, ImageDraw, ImageFont
    
    def create_default_icon():
        """创建默认的应用图标"""
        print("正在生成默认图标...")
        
        # 创建图标 - 使用蓝色背景
        size = 256
        img = Image.new('RGB', (size, size), color='#0078d4')
        draw = ImageDraw.Draw(img)
        
        # 绘制音乐符号 ♪
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("arial.ttf", 150)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 150)
            except:
                # 如果找不到字体，使用默认字体
                font = ImageFont.load_default()
                print("警告: 无法加载 TrueType 字体，使用默认字体")
        
        # 绘制 "M" 代表 Music
        text = "♪"
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
        except:
            # 旧版本的 Pillow 使用 textsize
            bbox = (0, 0) + draw.textsize(text, font=font)
        
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) / 2
        y = (size - text_height) / 2 - 10  # 稍微向上移动
        
        draw.text((x, y), text, fill='white', font=font)
        
        # 添加圆角效果
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), (size, size)], radius=30, fill=255)
        
        # 应用圆角
        output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        
        # 保存为 ICO 格式，包含多个尺寸
        output.save('icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        print("✅ 图标已生成: icon.ico")
        print("   包含尺寸: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256")
        return True
    
    if __name__ == '__main__':
        if os.path.exists('icon.ico'):
            response = input("icon.ico 已存在，是否覆盖？ (y/N): ")
            if response.lower() != 'y':
                print("取消生成")
                exit(0)
        
        create_default_icon()

except ImportError:
    print("❌ 错误: 需要安装 Pillow 库")
    print("   请运行: pip install Pillow")
    print("\n或者您可以:")
    print("1. 使用在线工具创建图标: https://www.icoconverter.com/")
    print("2. 从其他来源获取图标文件")
    print("3. 不使用图标（程序将使用默认图标）")
    exit(1)
except Exception as e:
    print(f"❌ 生成图标时出错: {e}")
    exit(1)
