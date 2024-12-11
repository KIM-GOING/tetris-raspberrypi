import spidev
import RPi.GPIO as GPIO
import time

# mcp3008 and GPIO setting
spi = spidev.SpiDev()

# joystick and switch pin numbering
JOYSTICKS = [
    {"VRX": 1, "VRY": 3, "SW": 27},
    {"VRX": 0, "VRY": 2, "SW": 17},
]
SWITCHES = [23,22]

# GPIO initialize function
def initialize_gpio():
    try:
        print("Initializing GPIO and SPI...")
        GPIO.setmode(GPIO.BCM)
        
        # GPIO pin setting
        for joystick in JOYSTICKS:
            GPIO.setup(joystick["SW"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        for switch in SWITCHES:
            GPIO.setup(switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # SPI setting
        spi.open(0,0)
        spi.max_speed_hz=1350000
        print("SPI and GPIO initialized successfully.")
    except Exception as e:
        print(f"Error initializing GPIO or SPI: {e}")
        raise

# exit function
def cleanup_gpio():
    spi.close()
    GPIO.cleanup()
    print("GPIO and SPI cleaned up.")

# MCP3008 analog reading function
def read_adc(channel):
    if channel < 0 or channel > 7:
        raise ValueError("Invalid ADC Channel")
    adc = spi.xfer2([1, (8+channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data
    
# joystick reading function
def get_joystick_input(player_index):
    try:
        joystick = JOYSTICKS[player_index]
        x = read_adc(joystick["VRX"])
        y = read_adc(joystick["VRY"])
        sw = GPIO.input(joystick["SW"]) == GPIO.LOW
        return x, y, sw
    except Exception as e:
        print("Error in get_joystick_input: {e}")
        raise

# switch reading function
switch_states = [False, False]
last_switch_states = [False, False]
def is_switch_pressed(player_index):
    global switch_states, last_switch_states
    current_state = GPIO.input(SWITCHES[player_index]) == GPIO.LOW
        
    if current_state and not last_switch_states[player_index]:
        switch_states[player_index] = True
    else:
        switch_states[player_index] = False
    
    last_switch_states[player_index] = current_state
    
    return switch_states[player_index]
