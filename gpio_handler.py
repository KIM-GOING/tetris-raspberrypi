import spidev
import RPi.GPIO as GPIO

JOYSTICK = 17
SWITCH = 22

spi = spidev.SpiDev()

def initialize_gpio():
    try:
        print("Initializing GPIO and SPI...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(JOYSTICK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        spi.open(0,0)
        spi.max_speed_hz=1350000
        print("SPI and GPIO initialized successfully.")
    except Exception as e:
        print(f"Error initializing GPIO or SPI: {e}")
        raise

def cleanup_gpio():
    spi.close()
    GPIO.cleanup()
    print("GPIO clean up.")
    
def read_adc(channel):
    if channel < 0 or channel > 7:
        raise ValueError("Invalid ADC Channel")
    adc = spi.xfer2([1, (8+channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data
    

def get_joystick_input():
    print(2)
    x = read_adc(0)
    y = read_adc(1)
    sw = GPIO.input(JOYSTICK)
    print(x, y, sw)
    return x, y, sw

def is_switch_pressed():
    return GPIO.input(SWITCH) == GPIO.LOW