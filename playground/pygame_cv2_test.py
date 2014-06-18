# -*- coding: utf-8 -*-
"""
Created on 18/06/14 17:23
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

"""

import pygame
import cv2
import numpy as np

screen_width = 640
screen_height = 360
delay = 1

capture = cv2.VideoCapture(0)
capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, screen_width)
capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, screen_height)

# OpenCV window
cv2.namedWindow("Raw", cv2.CV_WINDOW_AUTOSIZE)

# pygame window
screen = pygame.display.set_mode((screen_width, screen_height), 0, 24)
screen.fill(0)
surface = pygame.Surface((screen_width, screen_height), depth=24)
pygame.init()


def show_cv2(img):
    global delay
    cv2.imshow("Raw", img)
    key = cv2.waitKey(delay) - 0x100000
    if key > -1:
        print "Pressed key {0:d}".format(key)
    if key in (27, 113):  # ESC or 'q'
        capture.release()
        cv2.destroyAllWindows()
    elif key == 32:
        delay = 1 if delay != 1 else 0
    elif key == 115:  # 's' for slow
        delay = 500 if delay != 500 else 1


def blit_frame(surface, img):
    return pygame.surfarray.blit_array(surface, cv2.cvtColor(np.rot90(img), cv2.COLOR_BGR2RGB))


while capture.isOpened():
    rv, img = capture.read()
    if rv:
        show_cv2(img)
    blit_frame(surface, img)
    screen.blit(surface, (0, 0))
    pygame.display.flip()
    for e in pygame.event.get():
        print e
        if e.type == pygame.QUIT:
            print "Exiting"
            capture.release()
