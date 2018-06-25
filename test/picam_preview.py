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
CAMERA_METER_MODE            = 'backlit'
CAMERA_AWB_MODE              = 'auto'   # Range: 'auto' or 'off'
CAMERA_AWB_GAINS             = (0,0)    # Range: (0.0 .. 8.0, 0.0 .. 8.0)
CAMERA_ANNOTATE_TEXT         = '|'
CAMERA_DELAY                 = 1
CAMERA_USE_VIDEO_PORT        = True

# HSV Color Bounds of Reaction Results
BIURET_POSITIVE_LOWER_BOUND  = np.array([140,  80,  40])
BIURET_POSITIVE_UPPER_BOUND  = np.array([155, 255, 255])
BIURET_NEGATIVE_LOWER_BOUND  = np.array([105,  20,  40])
BIURET_NEGATIVE_UPPER_BOUND  = np.array([120, 255, 255])
BENEDICT_POSITIVE_LOWER_BOUND= np.array([  5,  80,  40])
BENEDICT_POSITIVE_UPPER_BOUND= np.array([ 30, 255, 255])
BENEDICT_NEGATIVE_LOWER_BOUND= np.array([ 85,  80,  40])
BENEDICT_NEGATIVE_UPPER_BOUND= np.array([ 95, 255, 255])

######################################
## Functions                        ##
######################################

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
    
    i=-100
    while True:
        camera.sharpness = CAMERA_SHARPNESS + i#change
        print i
        camera.start_preview()
        time.sleep(0.5)
        camera.stop_preview()
        i+=10
   
    #time.sleep(1)
    time.sleep(5*60)
    camera.resolution = (IMAGE_WIDTH, IMAGE_HEIGHT)
    #camera.capture("tes backlit.jpg", use_video_port=CAMERA_USE_VIDEO_PORT)

    camera.contrast = CAMERA_CONTRAST
    camera.brightness = CAMERA_BRIGHTNESS
    camera.saturation = CAMERA_SATURATION #change
    camera.ISO = CAMERA_ISO
    camera.exposure_compensation = CAMERA_EXPOSURE_COMPENSATION
    camera.exposure_mode = CAMERA_EXPOSURE_MODE
    camera.meter_mode = CAMERA_METER_MODE
    camera.awb_mode = CAMERA_AWB_MODE
    camera.annotate_text = CAMERA_ANNOTATE_TEXT
    camera.stop_preview()


######################################
## Boot Up                          ##
######################################
# GPIO Setup
RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setup(BUTTON_PIN_CALIBRATION, RPi.GPIO.IN )

######################################
## Loop                             ##
######################################
# Main process
camera_init()
camera_reload()