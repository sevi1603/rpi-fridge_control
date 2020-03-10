import board, busio, adafruit_ssd1306, time, adafruit_dht
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
from tinydb import TinyDB
from datetime import datetime, timedelta

# Setup I/O and sensors
i2c = busio.I2C(board.SCL, board.SDA)
display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
dht11 = adafruit_dht.DHT11(board.D4)

# Setup Relay Board
relayboardpin = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(relayboardpin, GPIO.OUT)

# Clear display
display.fill(0)
display.show()

# Create Pillow image and setup
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
#font = ImageFont.load_default()
image = Image.new('1', (display.width, display.height))
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0)

# Setup database
db = TinyDB('./db_sensordata.json')
table = db.table('dht11')

# Setup timer for timed database writes
committime = datetime.now() + timedelta(seconds=10)

# Temperature Control values
tempThresholdHigh = 24

# main loop
while True:
    try:
        # Reset screen
        draw.rectangle((0,0, display.width, display.height), outline=0, fill=0)

        # Get DHT11 sensor data
        if dht11.temperature < 100 and dht11.temperature > -100:
            temperature_c = dht11.temperature
            humidity = dht11.humidity
        else:
            continue
        line1 = 'Temperature: {t}C'.format(t=temperature_c)
        line2 = 'Humidity: {h}%'.format(h=humidity)

        draw.text((5, 5), line1, font=font, fill=255)
        draw.text((5, 20), line2, font=font, fill=255)

        # Switch Relay
        #print('get pinmode: ' + str(GPIO.getmode()))
        if GPIO.getmode() is not 11:    # 11 = GPIO.BCM / 10 = GPIO.BOARD
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(relayboardpin, GPIO.OUT)
        if tempThresholdHigh < temperature_c:
            GPIO.output(relayboardpin, GPIO.LOW)
        else:
            GPIO.output(relayboardpin, GPIO.HIGH)

        # Display image
        display.image(image)
        display.show()

        # Write to database, every 10 seconds
        if committime < datetime.now():
            table.insert({'temp': temperature_c, 'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
            table.insert({'humi': humidity, 'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
            committime = datetime.now() + timedelta(seconds=10)

    except RuntimeError as error:
        print(error.args[0])
    except KeyboardInterrupt:
        print('exiting')
        GPIO.cleanup()
        sys.exit()

    time.sleep(0.5)
