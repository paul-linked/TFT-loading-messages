
import os
import random
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735  
import praw
import string
import urllib.request
import time

# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D22)
reset_pin = digitalio.DigitalInOut(board.D27)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()


# Create the display:
disp = st7735.ST7735R(spi, rotation=270, x_offset=0, y_offset=0,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)


# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height
image = Image.new("RGB", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill="#800080")
disp.image(image)

# Load default font.
font = ImageFont.truetype("arial.ttf", 20)


#scrape images from reddit 
def get_image():
    # Authenticate with Reddit API
    reddit = praw.Reddit(client_id='5jcQTiciPInnU9is21oVvw',
                        client_secret='z8dCQ8l5yU-UqfCKGuccGfl_XFUb-w',
                        user_agent='CLOCK')

    # Get the top 10 posts from the "hot" category of the day
    subreddit = reddit.subreddit('ProgrammerHumor')
    hot_posts = subreddit.hot(limit=30)

    # Delete all files in the "images" folder
    folder_path = './images'
    

    # Download the images
    for i, post in enumerate(hot_posts):
        if post.url.endswith('.jpg') or post.url.endswith('.png'):
            image_url = post.url
            image_name = str(i) + '.' + image_url.split('.')[-1]
            image_path = os.path.join(folder_path, image_name)
            urllib.request.urlretrieve(image_url, image_path)




# Define function to get a random image file name from the folder
def get_random_image():
    folder = "/home/paul/RB-TFT1.8_Codeexample_RaspberryPi/images"
    files = os.listdir(folder)
    image_files = [f for f in files if f.endswith(".jpg") or f.endswith(".png")]
    if image_files:
        return os.path.join(folder, random.choice(image_files))
    else:
        get_image()
        get_random_image()


def display_image():
    # Get a random image file name
    # Display a random image for a short time
    image_file = get_random_image()
    if image_file:
        # Load the image file and display it on the screen
        image = Image.open(image_file)
        # Scale the image to the smaller screen dimension
        image_ratio = image.width / image.height
        screen_ratio = width / height
        if screen_ratio < image_ratio:
            scaled_width = image.width * height // image.height
            scaled_height = height
        else:
            scaled_width = width
            scaled_height = image.height * width // image.width
        image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

        # Crop and center the image
        x = scaled_width // 2 - width // 2
        y = scaled_height // 2 - height // 2
        image = image.crop((x, y, x + width, y + height))
        disp.image(image)
        # Wait for 30 seconds
        time.sleep(60)
        # Delete the image file
        os.remove(image_file)


# Open file and read list of strings
with open("/home/paul/RB-TFT1.8_Codeexample_RaspberryPi/strings.txt", "r", encoding="latin-1") as file:
    strings = [rline.strip() for rline in file.readlines()]


# Define initial index
index = 0

while True:
    while index < 10:
        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
        
        # Get current string from list
        string = random.choice(strings)
        
        # Wrap text to the next line if it exceeds the width of the display
        lines = []
        line = ""
        for word in string.split():
            if draw.textsize(line + " " + word, font=font)[0] < width:
                line += " " + word
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        y = (height - font.getsize(lines[0])[1] * len(lines)) // 2
        for line in lines:
            text_width, text_height = draw.textsize(line, font)
            x = (width - text_width) // 2
            draw.text((x, y), line, font=font, fill=(255, 255, 255))
            y += font.getsize(line)[1]
        
        # Display image.
        disp.image(image)
        
        # Increment index
        index += 1
        
        # Wait for some time
        time.sleep(5)
    
    # Get current time
    current_date = time.strftime("%d.%m.%Y")
    current_time = time.strftime("%H:%M:%S")

    # Display current time on the TFT display
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    text_width, text_height = draw.textsize(current_date + "\n\n" + current_time, font)
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.text((x, y), current_time + "\n\n" + current_date, font=font, fill=(255, 255, 255))
    disp.image(image)

    if int(time.strftime("%M")) % 15 == 0:
        display_image()

