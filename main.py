from machine import Pin, I2C, ADC, PWM
from ssd1306 import SSD1306_I2C
import time
import math

# Right potentiometer
r_adc = ADC(Pin(26))

# Left potentiometer
l_adc = ADC(Pin(27))

# I2C connection to the display
i2c = I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)

# Setup display
oled = SSD1306_I2C(128, 64, i2c)

# Buzzer pin
buzzer = PWM(Pin(16))

# Switch pin
switch = Pin(15, Pin.IN)

buzzer.duty_u16(0)

old_wartosc = (0, 0)

mode = 1
        

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

while True:
    oled.fill(0)
    
    if switch():
        mode = 2
    else:
        mode = 1
    prawy_y = int(translate(round(r_adc.read_u16(), -3), 256, 65535, 5, 50))
    lewy_x = int(translate(round(l_adc.read_u16(), -2), 256, 65535, 5, 105))
    
#    print(f"{lewy_x} | {old_wartosc[0]}")
    
    # improve this
    if abs(lewy_x - old_wartosc[0]) >= 3 or abs(prawy_y - old_wartosc[1]) >= 3:
        buzzer.duty_u16(1000)
        time.sleep(0.01)
        buzzer.duty_u16(0)
        old_wartosc = (lewy_x, prawy_y)
    
#    old_wartosc = (lewy_x, prawy_y)
    
    # Draw the triangle
    oled.line(112, 56, 112, prawy_y, 1)
    oled.line(112, 56, lewy_x, 56, 1)
    oled.line(lewy_x, 56, 112, prawy_y, 1)
    
    # Calculate length
    bok_prawy = 56 - prawy_y
    bok_dolny = 112 - lewy_x
    bok_gorny = math.sqrt((bok_prawy ** 2) + (bok_dolny ** 2))
    
    
    # Draw the symbols
    if mode == 1:
        oled.text("a", lewy_x, 56)
        
        tga = bok_prawy / bok_dolny
        ctga = bok_dolny / bok_prawy
        sina = bok_prawy / bok_gorny
        cosa = bok_dolny / bok_gorny
        
        oled.text(f"sin: {sina:.4f}", 0, 0)
        oled.text(f"cos: {cosa:.4f}", 0, 8)
        oled.text(f"tg:  {tga:.4f}", 0, 16)
        oled.text(f"ctg: {ctga:.4f}", 0, 24)
        
    elif mode == 2:
        oled.text("b", 112 + 2, prawy_y)
        
        sinb =  bok_dolny / bok_gorny
        cosb = bok_prawy / bok_gorny
        tgb = bok_dolny / bok_prawy
        ctgb = bok_prawy / bok_dolny
        
        oled.text(f"sin: {sinb:.4f}", 0, 0)
        oled.text(f"cos: {cosb:.4f}", 0, 8)
        oled.text(f"tg:  {tgb:.4f}", 0, 16)
        oled.text(f"ctg: {ctgb:.4f}", 0, 24)
    else:
        print("something is wrong")
    
#    print(f"bok_prawy: {bok_prawy} | bok_dolny: {bok_dolny} | bok_gorny: {bok_gorny}")
        
#    oled.text(f"Prawy: {bok_prawy}", 0, 0)
#    oled.text(f"Dolny: {bok_dolny}", 0, 8)
#    oled.text(f"Górny: {bok_gorny}", 0, 16)
    
    if bok_dolny >= 20:
        oled.text(f"{bok_dolny}", int(bok_dolny/2)+lewy_x - 2, 56+1)
    if bok_prawy >= 10:
        oled.text(f"{bok_prawy}", 112+1, int(bok_prawy/2)+prawy_y)

    oled.show()
    time.sleep(0.01)

