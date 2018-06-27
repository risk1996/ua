import RPi
import RPLCD        # http://www.circuitbasics.com/raspberry-pi-lcd-set-up-and-programming-in-python/
import picamera     # https://picamera.readthedocs.io/en/release-1.13/recipes1.html
import time
import cv2
import subprocess
import numpy as np
import pygame

######################################
## Variable & Constants             ##
######################################
# GPIO Pins Declarations
BUTTON_PIN_CALIBRATION       = 11
BUTTON_PIN_START             = 13

# LED Pins Declarations
LED_PIN_READY                = 24

# LCD Pins & Constants Declarations
LCD_NUMBERING_MODE           = RPi.GPIO.BOARD
LCD_COLUMNS                  = 16
LCD_ROWS                     = 2
LCD_PIN_RESET                = 37
LCD_PIN_ENABLED              = 35
LCD_PINS_DATA                = [33, 31, 29, 23]

# Image Constants Declarations
BEFORE_IMAGE_FILENAME        = "bef.jpg"
AFTER_IMAGE_FILENAME         = "aft.jpg"
DIFFERENCE_IMAGE_FILENAME    = "dif.jpg"
IMAGE_WIDTH                  = 800
IMAGE_HEIGHT                 = 600

# Global Camera Adjustment Variable Declarations
CAMERA_SHARPNESS             = 0        # Range: -100 .. 100
CAMERA_CONTRAST              = 0        # Range: -100 .. 100
CAMERA_BRIGHTNESS            = 50       # Range:    0 .. 100
CAMERA_SATURATION            = 0        # Range: -100 .. 100
CAMERA_ISO                   = 0        # Range:    0 .. 800
CAMERA_EXPOSURE_COMPENSATION = 0        # Range: - 25 ..  25
CAMERA_EXPOSURE_MODE         = 'auto'   # Range: 'auto' or 'off'
CAMERA_METER_MODE            = 'average'
CAMERA_AWB_MODE              = 'auto'   # Range: 'auto' or 'off'
CAMERA_AWB_GAINS             = (0,0)    # Range: (0.0 .. 8.0, 0.0 .. 8.0)
CAMERA_ANNOTATE_TEXT         = '|'
CAMERA_DELAY                 = 1
CAMERA_USE_VIDEO_PORT        = True

# HSV Color Bounds of Reaction Results
BIURET_POSITIVE_LOWER_BOUND  = numpy.array([140,  80,  40])
BIURET_POSITIVE_UPPER_BOUND  = numpy.array([155, 255, 255])
BIURET_NEGATIVE_LOWER_BOUND  = numpy.array([105,  20,  40])
BIURET_NEGATIVE_UPPER_BOUND  = numpy.array([120, 255, 255])
BENEDICT_POSITIVE_LOWER_BOUND= numpy.array([  5,  80,  40])
BENEDICT_POSITIVE_UPPER_BOUND= numpy.array([ 30, 255, 255])
BENEDICT_NEGATIVE_LOWER_BOUND= numpy.array([ 85,  80,  40])
BENEDICT_NEGATIVE_UPPER_BOUND= numpy.array([ 95, 255, 255])

######################################
## Functions                        ##
######################################
# LCD Initialization
def lcd_init():
    global lcd
    lcd = RPLCD.CharLCD(numbering_mode=LCD_NUMBERING_MODE, cols=LCD_COLUMNS, rows=LCD_ROWS, pin_rs=LCD_PIN_RESET, pin_e=LCD_PIN_ENABLED, pins_data=LCD_PINS_DATA)
    return

# LCD Write
def lcd_write(row, col, str):
    lcd.cursor_pos = (row, col)
    lcd.write_string(str)
    return

#LCD Exit (GPIO cleanup)
def lcd_exit():
    RPi.GPIO.cleanup()
    return

# Camera Initialization
def camera_init():
    global camera
    camera = picamera.PiCamera()
    camera.video_stabilization = False
    camera.image_effect = 'none'
    camera.color_effects = None
    camera.rotation = 0
    camera.hflip = False
    camera.vflip = False
    camera.crop = (0.0, 0.0, 1.0, 1.0)
    camera.led = False
    return

# Camera load adjustments
def camera_reload():
    camera.resolution = (IMAGE_WIDTH, IMAGE_HEIGHT)
    camera.sharpness = CAMERA_SHARPNESS
    camera.contrast = CAMERA_CONTRAST
    camera.brightness = CAMERA_BRIGHTNESS
    camera.saturation = CAMERA_SATURATION
    camera.ISO = CAMERA_ISO
    camera.exposure_compensation = CAMERA_EXPOSURE_COMPENSATION
    camera.exposure_mode = CAMERA_EXPOSURE_MODE
    camera.meter_mode = CAMERA_METER_MODE
    camera.awb_mode = CAMERA_AWB_MODE
    camera.annotate_text = CAMERA_ANNOTATE_TEXT

# Camera take picture
def take_picture(filename):
    camera_init()
    camera_reload()
    camera.start_preview()
    time.sleep(CAMERA_DELAY)
    camera.capture(filename, use_video_port=CAMERA_USE_VIDEO_PORT)
    camera.stop_preview()
    camera.close()
    return

# Sigmoid function
def sigmoid(x):
    return 1/(1+numpy.exp(-x))

# Accuracy function
def accuracy(x):
    return int(round(2*(sigmoid(x)-.5)*100))

# Play audio function
def play_audio(x):
    pygame.mixer.init()
    pygame.mixer.music.load(x)
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass

######################################
## Boot Up                          ##
######################################
# GPIO Setup
RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setup(BUTTON_PIN_CALIBRATION, RPi.GPIO.IN )
RPi.GPIO.setup(BUTTON_PIN_START      , RPi.GPIO.IN )
RPi.GPIO.setup(LED_PIN_READY         , RPi.GPIO.OUT)
# LCD Setup
lcd_init()
lcd_write(0, 0, u'UrineAnalyzerV.1')
lcd_write(1, 0, u'~~ Booting Up ~~')

######################################
## Loop                             ##
######################################
# Main process
while True:
    # Wait for user input
    if RPi.GPIO.input(BUTTON_CALIBRATION):

    else if RPi.GPIO.input(BUTTON_START):
        # Take before-image
        take_picture(BEFORE_IMAGE_FILENAME)

        # Drop reagents
        # something()

        # Wait for reactions
        time.sleep(5) # Supposed to be 5 minutes

        # Take after-image
        take_picture(AFTER_IMAGE_FILENAME)

        # Calculate differences in before-image and after-image
        bef = cv2.imread(BEFORE_IMAGE_FILENAME)
        aft = cv2.imread(AFTER_IMAGE_FILENAME)
        diff = cv2.absdiff(aft, bef)
        diff = cv2.bitwise_not(diff)
        cv2.imwrite(DIFFERENCE_IMAGE_FILENAME, diff)

        # Split left and right image
        diff_l = diff[0:IMAGE_HEIGHT, 0              :IMAGE_WIDTH/2]
        diff_r = diff[0:IMAGE_HEIGHT, IMAGE_WIDTH/2+1:IMAGE_WIDTH  ]

        # Convert to HSV
        diff_l_hsv = cv2.cvtColor(diff_l, cv2.COLOR_BGR2HSV)
        diff_r_hsv = cv2.cvtColor(diff_r, cv2.COLOR_BGR2HSV)

        # Process left and right image seperately
        # diff_l_avg = numpy.round(numpy.average(numpy.average(diff_l, axis=0), axis=0))
        # diff_r_avg = numpy.round(numpy.average(numpy.average(diff_r, axis=0), axis=0))
        # print(diff_l_avg)
        # print(diff_r_avg)
        diff_l_pos = cv2.inRange(diff_l_hsv,   BIURET_POSITIVE_LOWER_BOUND,   BIURET_POSITIVE_UPPER_BOUND)
        diff_l_neg = cv2.inRange(diff_l_hsv,   BIURET_NEGATIVE_LOWER_BOUND,   BIURET_NEGATIVE_UPPER_BOUND)
        diff_r_pos = cv2.inRange(diff_r_hsv, BENEDICT_POSITIVE_LOWER_BOUND, BENEDICT_POSITIVE_UPPER_BOUND)
        diff_r_neg = cv2.inRange(diff_r_hsv, BENEDICT_NEGATIVE_LOWER_BOUND, BENEDICT_NEGATIVE_UPPER_BOUND)
        diff_l_pos[0,0] = 255
        diff_l_neg[0,0] = 255
        diff_r_pos[0,0] = 255
        diff_r_neg[0,0] = 255
        temp, diff_l_cnt_pos = numpy.unique(diff_l_pos, return_counts=True)
        temp, diff_l_cnt_neg = numpy.unique(diff_l_neg, return_counts=True)
        temp, diff_r_cnt_pos = numpy.unique(diff_r_pos, return_counts=True)
        temp, diff_r_cnt_neg = numpy.unique(diff_r_neg, return_counts=True)

        # Obtain test result
        biuret_test_result   = accuracy(5*(diff_l_cnt_pos[1]-diff_l_cnt_neg[1])/(numpy.sum(diff_l_cnt_pos)))
        benedict_test_result = accuracy(5*(diff_r_cnt_pos[1]-diff_r_cnt_neg[1])/(numpy.sum(diff_r_cnt_pos)))

        # Output test result
        lcd_write(1, 0, u'Analisa Selesai!')
        play_audio("sls.mp3")
        lcd_write(1, 0, u'  Hasil Tes...  ')
        play_audio("hsl.mp3")
        # lcd_write(1, 0, u'  Hasil Tes...  ')

        # Remove residual files
        # subprocess.check_output(["bash", "-c", "rm -f " + BEFORE_IMAGE_FILENAME])
        # subprocess.check_output(["bash", "-c", "rm -f " + AFTER_IMAGE_FILENAME])
        # subprocess.check_output(["bash", "-c", "rm -f " + DIFFERENCE_IMAGE_FILENAME])