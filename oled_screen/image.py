import psutil
import time
import datetime
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont
from PIL import Image, ImageDraw
import os
import subprocess
# 要终止的进程名称
process_name = "sys_info.py"

# 使用subprocess执行终止进程的命令
subprocess.call(["pkill", "-f", process_name])

# OLED配置
i2c_bus_number = 3
width = 128
height = 64

def main():
    serial = i2c(port=i2c_bus_number, address=0x3C)
    device = ssd1306(serial)
    

    # 加载图像
    image_path = "1.png"
    image_to_display = Image.open(image_path).convert("1")  # 转换为单色模式

    # 缩放图像以适应屏幕大小
    image_to_display = image_to_display.resize((width, height))

    device.display(image_to_display)

    # 等待一段时间
    time.sleep(50)  # 这里可以调整显示图像的时间



if __name__ == "__main__":
    main()
  