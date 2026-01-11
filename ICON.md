# 图标文件说明

## 关于 icon.ico

本项目需要一个应用程序图标文件 `icon.ico`，用于：
- Windows 可执行文件的图标
- 应用程序窗口的图标

## 如何添加图标

### 方法一：准备自己的图标

1. 准备一个图片文件（PNG、JPG 等）
2. 使用在线工具转换为 ICO 格式：
   - https://www.icoconverter.com/
   - https://convertio.co/zh/png-ico/
   - https://www.favicon-generator.org/

3. 推荐图标尺寸：
   - 256x256 像素（主要尺寸）
   - 也可以包含多个尺寸：16x16, 32x32, 48x48, 256x256

4. 将生成的文件命名为 `icon.ico`，放在项目根目录

### 方法二：使用 Python 生成简单图标

如果没有图标文件，可以运行以下脚本生成一个简单的默认图标：

```python
from PIL import Image, ImageDraw, ImageFont

# 创建图标
size = 256
img = Image.new('RGB', (size, size), color='#0078d4')
draw = ImageDraw.Draw(img)

# 绘制文字
try:
    font = ImageFont.truetype("arial.ttf", 100)
except:
    font = ImageFont.load_default()

text = "M"
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (size - text_width) / 2
y = (size - text_height) / 2
draw.text((x, y), text, fill='white', font=font)

# 保存为 ICO 格式
img.save('icon.ico', format='ICO', sizes=[(256, 256)])
print("图标已生成: icon.ico")
```

需要安装 Pillow：
```bash
pip install Pillow
```

### 方法三：不使用图标

如果暂时不需要自定义图标：
- 构建脚本会自动检测图标是否存在
- 如果不存在，将使用 Windows 默认图标
- 程序功能不受影响

## 图标设计建议

- 使用简洁的设计，避免过于复杂
- 使用与应用主题相关的图标（例如音乐符号）
- 确保在小尺寸（16x16）下仍然清晰可辨
- 建议使用透明背景
- 颜色与应用界面风格保持一致

## 示例图标资源

可以从以下网站获取免费图标：
- https://www.flaticon.com/
- https://icons8.com/
- https://www.iconfinder.com/
- https://iconmonstr.com/

**注意**：使用时请注意版权和许可证要求。

---

如果你有设计好的图标，欢迎通过 Pull Request 贡献到项目中！
