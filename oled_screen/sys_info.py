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
process_name = "1.py"

# 使用subprocess执行终止进程的命令
subprocess.call(["pkill", "-f", process_name])



i2c_bus_number = 3 #定义i2c总线
first_run = True  # 标记是否第一次运行脚本
serial = i2c(port=i2c_bus_number, address=0x3C)  # 设置 OLED I2C 地址
device = ssd1306(serial)


# 获取系统信息
def get_system_info():
    cmd = "top -bn2 -d 0.1 | grep %Cpu | awk 'NR==2{printf \"CPU: %.2f%%\",100-$8}'"
    CPU = subprocess.check_output(cmd, shell=True).decode('utf-8')
    cmd = "free -m | awk 'NR==2{printf \"Mem: %.1f/%.1f GB %.1f%%\", $3/1024,$2/1024,$3*100/$2 }'"
    MemUsage = os.popen(cmd).read().strip()
    cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB %s", $3,$2,$5}\''
    Disk = os.popen(cmd).read().strip()
    cmd = "hostname -I | cut -d' ' -f1"
    IP = os.popen(cmd).read().strip()
    cmd = "cat /sys/class/thermal/thermal_zone0/temp | awk '{printf \"%.1f\", $0/1000}'"
    cput = subprocess.check_output(cmd, shell=True).decode('utf-8')
    return CPU, MemUsage, Disk, IP, cput


# 格式化运行时间
def format_uptime(uptime):
    total_seconds = int(uptime.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# 显示开机欢迎信息
def show_poweron_text(draw, font_Big, width, height):
    font_path = "apple-M.ttf"  # 替换为实际的字体文件路径
    font_size = 15  # 指定字体大小
    font = ImageFont.truetype(font_path, font_size)

    # 加载图像
    image_path = "1.png"
    image_to_display = Image.open(image_path).convert("1")  # 转换为单色模式

    # 缩放图像以适应屏幕大小
    image_to_display = image_to_display.resize((width, height))

    # 创建一个可以在图像上绘制文本的 Draw 对象
    draw = ImageDraw.Draw(image_to_display)

    # 在图像下方绘制文本 "Hello"
    draw.text((40, 44), "HELLO", font=font, fill=255)
    # 在屏幕上显示图像
    device.display(image_to_display)


def main():
    global first_run

    width = 128
    height = 64
    # 创建一个黑色背景的空白图像
    image = Image.new("1", (width, height))
    draw = ImageDraw.Draw(image)

    # 定义字体大小
    font_size_Big = 18  # 大字体大小
    font_size_large = 14  # 中字体大小
    font_size_small = 10  # 小字体大小
    font_Big = ImageFont.truetype("apple-M.ttf", font_size_Big)
    font_large = ImageFont.truetype("apple-M.ttf", font_size_large)
    font_small = ImageFont.truetype("apple-M.ttf", font_size_small)

    last_switch_time = time.time()# 获取当前时间
    showing_system_info = True    # 是否显示系统信息
    poweron_displayed = False    # 是否已显示开机信息

    # 获取系统启动时间
    boot_time = psutil.boot_time()
    boot_time_datetime = datetime.datetime.fromtimestamp(boot_time)

    # 主循环
    while True:
        if not poweron_displayed:       # 如果尚未显示开机信息
            show_poweron_text(draw, font_Big, width, height)
            poweron_displayed = True
            time.sleep(3)
            device.display(image)


        if poweron_displayed and time.time() - last_switch_time >= 3:  # 等待3秒后开始切换显示内容
            # 如果显示系统信息
            if showing_system_info:
               CPU, MemUsage, Disk, IP, cput = get_system_info()

               # 清除之前的内容
               draw.rectangle((0, 0, width - 1, height - 1), outline=0, fill=0)
               top = 0
               # 绘制 OrangePi Zero 3 字样
               draw.text((0, top), "OrangePi Zero 3", font=font_large, fill=255)
               top += 18
               # 重新绘制数据
               draw.text((0, top), CPU, font=font_small, fill=255)
               draw.text((80, top), cput + " °C", font=font_small, fill=255)
               top += 12
               draw.text((0, top), MemUsage.replace('%', '% '), font=font_small, fill=255)
               top += 12
               draw.text((0, top), Disk, font=font_small,fill=255)
               top += 12
               draw.text((0, top), "IP: " + IP, font=font_small, fill=255)
               # 绘制分隔线
               draw.line((0, 17.5, width, 17.5), fill=255)
               pass
            else:
               current_time = datetime.datetime.now().strftime("%H:%M:%S")
               # 计算开机运行时间
               uptime = datetime.datetime.now() - boot_time_datetime

               draw.rectangle((0, 0, width - 1, height - 1), outline=0, fill=0)
               top = 0
               draw.text((0, top), "OrangePi Zero 3", font=font_large, fill=255)
               top += 18
               draw.text((0, top), "Local Time: " + current_time, font=font_small, fill=255)
               top += 12
               draw.text((0, top), f"Uptime: {format_uptime(uptime)}", font=font_small, fill=255)
               draw.line((0, 17.5, width, 17.5), fill=255)
               top += 16
               draw.text((32, top), f"田鼠本鼠", font=font_large, fill=255)
               pass
        # 如果距离上次切换时间超过10秒，切换状态
        if time.time() - last_switch_time >= 10:
            showing_system_info = not showing_system_info
            last_switch_time = time.time()



        # 在 OLED 屏幕上显示图像
        device.display(image)
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("An error occurred:", str(e))
        serial.cleanup()  # 如果需要，确保在发生异常时进行清理操作




