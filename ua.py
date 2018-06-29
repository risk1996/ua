import RPi
import RPLCD        # http://www.circuitbasics.com/raspberry-pi-lcd-set-up-and-programming-in-python/
import picamera     # https://picamera.readthedocs.io/en/release-1.13/recipes1.html
import time
import cv2
import subprocess
import numpy
import pygame

######################################
## Variable & Constants             ##
######################################
# GPIO Pins Declarations
BUTTON_PIN_SHUTDOWN          = 11
BUTTON_PIN_START             = 13
LED_PIN_READY                = 24
PUMP_BIURET_PIN_DRIVE        = 16
PUMP_BENEDICT_PIN_DRIVE      = 18

# LCD Pins & Constants Declarations
LCD_NUMBERING_MODE           = RPi.GPIO.BOARD
LCD_COLUMNS                  = 16
LCD_ROWS                     = 2
LCD_PIN_RESET                = 37
LCD_PIN_ENABLED              = 35
LCD_PINS_DATA                = [33, 31, 29, 23]

# Image Constants Declarations
IMAGE_FILENAME               = "img.jpg"
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

# HSV Color Bounds of Urine
URINE_LOWER_BOUND            = numpy.array([20,  40,  40])
URINE_UPPER_BOUND            = numpy.array([30, 255, 255])

# HSV Color Bounds of Reaction Results
BIURET_POSITIVE_LOWER_BOUND  = numpy.array([140,  80,  40])
BIURET_POSITIVE_UPPER_BOUND  = numpy.array([155, 255, 255])
BIURET_NEGATIVE_LOWER_BOUND  = numpy.array([105,  20,  40])
BIURET_NEGATIVE_UPPER_BOUND  = numpy.array([120, 255, 255])
BENEDICT_POSITIVE_LOWER_BOUND= numpy.array([  5,  80,  40])
BENEDICT_POSITIVE_UPPER_BOUND= numpy.array([ 30, 255, 255])
BENEDICT_NEGATIVE_LOWER_BOUND= numpy.array([ 85,  80,  40])
BENEDICT_NEGATIVE_UPPER_BOUND= numpy.array([ 95, 255, 255])

# Test bounds
TEST_SUCCESS_LOWER_BOUND     = 20

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

# Accuracy function
def accuracy(x):
    # Sigmoid function
    def sigmoid(x):
        return 1/(1+numpy.exp(-x))
    return int(round(2*(sigmoid(5*x)-.5)*100))

# Play audio function
def play_audio(x):
    pygame.mixer.init()
    pygame.mixer.music.load(x)
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass

# Run reagent pump for t seconds
def drop_reagent(t):
    RPi.GPIO.output(PUMP_BIURET_PIN_DRIVE  , RPi.GPIO.HIGH)
    RPi.GPIO.output(PUMP_BENEDICT_PIN_DRIVE, RPi.GPIO.HIGH)
    time.sleep(t)
    RPi.GPIO.output(PUMP_BIURET_PIN_DRIVE  , RPi.GPIO.LOW)
    RPi.GPIO.output(PUMP_BENEDICT_PIN_DRIVE, RPi.GPIO.LOW)

# Image masking withon bounds
def mask_within_bounds(img, low, up):
    mask = cv2.inRange(img, low, up)
    mask[0,0] = 255
    temp, count = numpy.unique(img_l_pos, return_counts=True)
    return count

######################################
## Boot Up                          ##
######################################
# GPIO Setup
RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setup(BUTTON_PIN_SHUTDOWN    , RPi.GPIO.IN , pull_up_down=RPi.GPIO.PUD_UP)
RPi.GPIO.setup(BUTTON_PIN_START       , RPi.GPIO.IN , pull_up_down=RPi.GPIO.PUD_UP)
RPi.GPIO.setup(LED_PIN_READY          , RPi.GPIO.OUT)
RPi.GPIO.setup(PUMP_BIURET_PIN_DRIVE  , RPi.GPIO.OUT)
RPi.GPIO.setup(PUMP_BENEDICT_PIN_DRIVE, RPi.GPIO.OUT)
# LCD Setup
lcd_init()
lcd_write(0, 0, u'UrineAnalyzerV.1')
lcd_write(1, 0, u'-- Booting Up --')

######################################
## Loop                             ##
######################################
# Main process
while True:
    # Output system status as ready
    lcd_write(0, 0, u'UrineAnalyzerV.1')
    lcd_write(1, 0, u'  -- Ready! --  ')

    # Wait for user input
    if RPi.GPIO.input(BUTTON_PIN_SHUTDOWN):
        # Output system status as busy
        lcd_write(1, 0, u'Shutting down...')

        # Shutdown Raspberry Pi
        subprocess.check_output(["bash", "-c", "shutdown -t 5"])

    elif RPi.GPIO.input(BUTTON_PIN_START):

        # Output system status as busy
        lcd_write(1, 0, u'   Testing...   ')

        # Drop reagents
        drop_reagent(3)

        # Wait for reactions
        time.sleep(5) # Supposed to be 5 minutes

        # Take and load image
        take_picture(IMAGE_FILENAME)
        img = cv2.imread(IMAGE_FILENAME)

        # Split left and right image
        img_l = img[0:IMAGE_HEIGHT, 0              :IMAGE_WIDTH/2]
        img_r = img[0:IMAGE_HEIGHT, IMAGE_WIDTH/2+1:IMAGE_WIDTH  ]

        # Convert to HSV
        img_l_hsv = cv2.cvtColor(img_l, cv2.COLOR_BGR2HSV)
        img_r_hsv = cv2.cvtColor(img_r, cv2.COLOR_BGR2HSV)

        # Process left and right image
        img_l_cnt_pos = mask_within_bounds(img_l_hsv,   BIURET_POSITIVE_LOWER_BOUND,   BIURET_POSITIVE_UPPER_BOUND)
        img_l_cnt_neg = mask_within_bounds(img_l_hsv,   BIURET_NEGATIVE_LOWER_BOUND,   BIURET_NEGATIVE_UPPER_BOUND)
        img_r_cnt_pos = mask_within_bounds(img_r_hsv, BENEDICT_POSITIVE_LOWER_BOUND, BENEDICT_POSITIVE_UPPER_BOUND)
        img_r_cnt_neg = mask_within_bounds(img_r_hsv, BENEDICT_NEGATIVE_LOWER_BOUND, BENEDICT_NEGATIVE_UPPER_BOUND)

        # Obtain test result
        biuret_test_result   = accuracy((img_l_cnt_pos[1]-img_l_cnt_neg[1])/numpy.sum(img_l_cnt_pos))
        benedict_test_result = accuracy((img_r_cnt_pos[1]-img_r_cnt_neg[1])/numpy.sum(img_r_cnt_pos))
        biuret_test_result_is_pos   = biuret_test_result   > 0
        benedict_test_result_is_pos = benedict_test_result > 0
        biuret_test_result_pct      = abs(biuret_test_result)
        benedict_test_result_pct    = abs(benedict_test_result)
        if biuret_test_result_pct < TEST_SUCCESS_LOWER_BOUND:
            biuret_test_result_str    = "GGL"
            biuret_test_result_sym    = "X"
        else if biuret_test_result_is_pos:
            biuret_test_result_str    = "POS"
            biuret_test_result_sym    = "+"
        else:
            biuret_test_result_str    = "NEG"
            biuret_test_result_sym    = "-"
        if benedict_test_result_pct < TEST_SUCCESS_LOWER_BOUND:
            benedict_test_result_str  = "GGL"
            benedict_test_result_sym  = "X"
        else if benedict_test_result_is_pos:
            benedict_test_result_str  = "POS"
            benedict_test_result_sym  = "+"
        else:
            benedict_test_result_str  = "NEG"
            benedict_test_result_sym  = "-"

        # Output test result
        lcd_write(1, 0, u'Analisa Selesai!')
        play_audio("sls.mp3")
        lcd_write(1, 0, u'  Hasil Tes...  ')
        play_audio("hsl.mp3")
        lcd_write(0, 0, u'Biuret  : ' + biuret_test_result_sym   + '{:>3}%'.format(biuret_test_result_pct))
        lcd_write(1, 0, u'Benedict: ' + benedict_test_result_sym + '{:>3}%'.format(benedict_test_result_pct))
        play_audio("bi.mp3")
        play_audio(biuret_test_result_str.lower() + ".mp3")
        if biuret_test_result_str != "GGL":
            play_audio("ta.mp3")
            play_audio("{}".format(biuret_test_result_pct) + ".mp3")
        play_audio("be.mp3")
        play_audio(benedict_test_result_str.lower() + ".mp3")
        if benedict_test_result_str != "GGL":
            play_audio("ta.mp3")
            play_audio("{}".format(benedict_test_result_pct) + ".mp3")

        # Remove residual files
        # subprocess.check_output(["bash", "-c", "rm -f " + IMAGE_FILENAME])