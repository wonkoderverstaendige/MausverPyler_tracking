#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 12/06/14 16:34
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

"""

import cv2
import argparse
import logging
import os
import numpy as np


def threshold(img, low=None, high=None):
    low = low if low is not None else 127
    high = high if high is not None else 255

    return_images = []

    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rv1, th1 = cv2.threshold(grey, low, high, cv2.THRESH_TOZERO_INV)
    return_images.append(('to_zero {0:d}'.format(low), th1))

    # Otsu's thresholding after Gaussian filtering
    blur = cv2.GaussianBlur(grey, (5, 5), 0)
    rv2, th2 = cv2.threshold(blur, 200, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    return_images.append(("Otsu's", th2))

    return return_images


def mask(img, mask):
    return cv2.add(np.zeros_like(img), img, mask=mask)


def main(source, *args, **kwargs):
    capture = cv2.VideoCapture(source)

    fgbg = cv2.BackgroundSubtractorMOG()
    fgbg2 = cv2.BackgroundSubtractorMOG2(history=500, varThreshold=128, bShadowDetection=False)

    # Generate start image for background subtraction
    video_folder = os.path.dirname(source) if os.path.exists(source) else None
    print source, video_folder
    print os.path.join(video_folder, 'empty_arena.png')

    arena_mask = None if video_folder is None else cv2.imread(os.path.join(video_folder, 'arena_mask.png'))
    if arena_mask is not None:
        rv, arena_mask = cv2.threshold(cv2.cvtColor(arena_mask, cv2.COLOR_BGR2GRAY), 1, 255, cv2.THRESH_BINARY_INV)
        cv2.imshow("Mask", arena_mask)

    empty_img = None if video_folder is None else cv2.imread(os.path.join(video_folder, 'empty_arena.png'))
    if empty_img is not None:
        empty_img = mask(empty_img, arena_mask)
        fgbg.apply(empty_img)
        fgbg2.apply(empty_img)

    delay = 1
    while capture.isOpened():
        rv, img = capture.read()
        if rv:
            img = mask(img, arena_mask)
            # RAW IMAGE
            cv2.imshow('raw', img)

            # THRESHOLDED IMAGES
            # thresholds = threshold(img, kwargs['low'] if 'low' in kwargs else None)
            # for title, image in thresholds:
            #     cv2.imshow(title, image)

            # BACKGROUND SUBTRACTION
            mog = fgbg.apply(img)
            cv2.imshow('MOG()', mog)
            mog2 = fgbg2.apply(img)
            cv2.imshow('MOG2()', mog2)

            eroded = cv2.erode(mog, None, iterations=1)
            cv2.imshow('MOG2().erode()', eroded)
            dilated = cv2.dilate(eroded, None, iterations=2)
            cv2.imshow('MOG2().erode().dilate()', dilated)

            #call function to find contours
            contours, hierarchy = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            min_area = 2000

            passed = [cnt for cnt in contours if cv2.contourArea(cnt.astype(int)) > min_area]

            #draw found contours into new image
            contour_img = np.zeros_like(mog2)
            cv2.drawContours(contour_img, passed, -1, 255)
            cv2.imshow('Contours', contour_img)


            cv2.imshow("Masked raw greyscale", cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)*arena_mask)

        key = cv2.waitKey(delay) - 0x100000
        if key > -1:
            print key
        if key in (27, 113):  # ESC or 'q'
            capture.release()
            cv2.destroyAllWindows()
        elif key == 32:
            delay = 1 if delay != 1 else 0
        elif key == 115:  # 's' for slow
            delay = 500 if delay != 500 else 1



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default=0)
    parser.add_argument('-l', '--low', type=int, default=127)

    args = parser.parse_args()

    print args
    main(source=args.input, low=args.low)