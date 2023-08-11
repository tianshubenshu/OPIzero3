# stop_script.py
# 在服务停止时执行的清理操作，比如关闭屏幕等
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306

i2c_bus_number = 3  # 定义i2c总线

def main():
    serial = i2c(port=i2c_bus_number, address=0x3C)  # 设置 OLED I2C 地址
    device = ssd1306(serial)

    # 关闭屏幕
    device.clear()
    device.hide()
    serial.cleanup()

if __name__ == "__main__":
    main()