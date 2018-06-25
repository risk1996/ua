# import RPi.GPIO as GPIO
# import time

# GPIO.setmode(GPIO.BCM)

# GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)#Button to GPIO23
# GPIO.setup(24, GPIO.OUT)  #LED to GPIO24

# i=0

# try:
#     while True:
#          button_state = GPIO.input(23)
#          if button_state == False:
#             GPIO.output(24, True)
#             i += 1
#             print('Button Pressed ' + str(i) + " times.")
#             time.sleep(0.2)
#          else:
#             GPIO.output(24, False)
# except:
#     GPIO.cleanup()

import RPLCD
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
try:
    lcd = RPLCD.CharLCD(numbering_mode=GPIO.BOARD, cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33, 31, 29, 23])
    lcd.write_string(u'Hello World')
    time.sleep(1.5)
    def lcd_write(row, col, str):
        lcd.cursor_pos = (row, col)
        lcd.write_string(str)
        return
    
    lcd_write(0, 0, u'UrineAnalyzerV.1')
    lcd_write(1, 0, u'-- Booting Up --')
    x=42
    time.sleep(3)
    while True:
        if GPIO.input(11) == False:
            x = x+1
            time.sleep(0.2)
        elif GPIO.input(13) == False:
            x = x-1
            time.sleep(0.2)
        # lcd_write(1,0,"Clk: %s" %time.strftime("%H:%M:%S:%f"))
        lcd_write(1,0,'{:>3}%            '.format(x))
    GPIO.cleanup()
except:
    GPIO.cleanup()

# import picamera
# import time

# CAMERA_SHARPNESS             = 0
# CAMERA_CONTRAST              = 0
# CAMERA_BRIGHTNESS            = 50
# CAMERA_SATURATION            = 0
# CAMERA_ISO                   = 400
# CAMERA_EXPOSURE_COMPENSATION = 0
# CAMERA_EXPOSURE_MODE         = 'auto'
# CAMERA_METER_MODE            = 'average'
# CAMERA_AWB_MODE              = 'auto'
# CAMERA_AWB_GAINS             = (0,0)

# # Camera Initialization
# def camera_init():
#     global camera
#     camera = picamera.PiCamera()
#     camera.resolution = (800, 600)
#     camera.video_stabilization = False
#     camera.image_effect = 'none'
#     camera.color_effects = None
#     camera.rotation = 0
#     camera.hflip = False
#     camera.vflip = False
#     camera.crop = (0.0, 0.0, 1.0, 1.0)
#     # picamera.PiRenderer(camera, fullscreen=False, window=(0,0,2592, 1944))
#     camera.annotate_text = '|'
#     return

# # Camera load adjustments
# def camera_reload():
#     camera.sharpness = CAMERA_SHARPNESS
#     camera.contrast = CAMERA_CONTRAST
#     camera.brightness = CAMERA_BRIGHTNESS
#     camera.saturation = CAMERA_SATURATION
#     camera.ISO = CAMERA_ISO
#     camera.exposure_compensation = CAMERA_EXPOSURE_COMPENSATION
#     camera.exposure_mode = CAMERA_EXPOSURE_MODE
#     camera.meter_mode = CAMERA_METER_MODE
#     camera.awb_mode = CAMERA_AWB_MODE
#     camera.awb_gains = CAMERA_AWB_GAINS

# # Camera take picture
# def take_picture(filename):
#     camera_init()
#     camera_reload()
#     camera.start_preview()
#     time.sleep(.25)
#     camera.capture(filename)
#     camera.stop_preview()
#     camera.close()
#     return

# camera_init()
# # camera_reload()
# camera.led = False
# camera.start_preview()
# camera.led = False
# time.sleep(5)
# camera.capture("aft.jpg", use_video_port=True)
# camera.stop_preview()
# camera.close()

# import cv2
# import numpy
# BEFORE_IMAGE_FILENAME        = "bef.jpg"
# AFTER_IMAGE_FILENAME         = "aft.jpg"
# DIFFERENCE_IMAGE_FILENAME    = "dif.jpg"
# IMAGE_WIDTH                  = 800
# IMAGE_HEIGHT                 = 600
# bef = cv2.imread(BEFORE_IMAGE_FILENAME)
# aft = cv2.imread(AFTER_IMAGE_FILENAME)
# diff = cv2.absdiff(aft, bef)
# diff = cv2.bitwise_not(diff)
# cv2.imwrite(DIFFERENCE_IMAGE_FILENAME, diff)
# diff_l = diff[0:IMAGE_HEIGHT, 0              :IMAGE_WIDTH/2]
# diff_r = diff[0:IMAGE_HEIGHT, IMAGE_WIDTH/2+1:IMAGE_WIDTH  ]
# diff_l_avg = numpy.round(numpy.average(numpy.average(diff_l, axis=0), axis=0))
# diff_r_avg = numpy.round(numpy.average(numpy.average(diff_r, axis=0), axis=0))
# print(diff_l_avg)
# print(diff_r_avg)

# import webcolors # https://stackoverflow.com/questions/9694165/convert-rgb-color-to-english-color-name-like-green-with-python

# def closest_colour(requested_colour):
#     min_colours = {}
#     for key, name in webcolors.css3_hex_to_names.items():
#         r_c, g_c, b_c = webcolors.hex_to_rgb(key)
#         rd = (r_c - requested_colour[0]) ** 2
#         gd = (g_c - requested_colour[1]) ** 2
#         bd = (b_c - requested_colour[2]) ** 2
#         min_colours[(rd + gd + bd)] = name
#     return min_colours[min(min_colours.keys())]

# def get_colour_name(requested_colour):
#     try:
#         closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
#     except ValueError:
#         closest_name = closest_colour(requested_colour)
#         actual_name = None
#     return actual_name, closest_name

# requested_colour = (151, 223, 172)
# actual_name, closest_name = get_colour_name(requested_colour)

# print "Actual colour name:", actual_name, ", closest colour name:", closest_name
