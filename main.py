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


def main(source, *args, **kwargs):
    capture = cv2.VideoCapture(source)
    while cv2.waitKey(1) == -1:
        rv, img = capture.read()
        if rv:
            cv2.imshow('raw', img)
            thresholds = threshold(img, kwargs['low'] if 'low' in kwargs else None)
            for title, image in thresholds:
                cv2.imshow(title, image)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default=0)
    parser.add_argument('-l', '--low', type=int, default=127)

    args = parser.parse_args()

    print args
    main(source=args.input, low=args.low)