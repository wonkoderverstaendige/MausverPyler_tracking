#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 12/06/14 16:34
@author: <'Ronny Eichler'> ronny.eichler@gmail.com

"""

import cv2
import argparse
import os
import numpy as np
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


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
    mog = None
    mog2 = True
    capture = cv2.VideoCapture(source)

    fgbg = cv2.BackgroundSubtractorMOG() if mog else None
    fgbg2 = cv2.BackgroundSubtractorMOG2(history=500, varThreshold=128, bShadowDetection=False) if mog2 else None

    # Generate start image for background subtraction
    video_folder = os.path.dirname(source) if os.path.exists(source) else None
    print source, video_folder
    print os.path.join(video_folder, 'empty_arena.png')

    arena_mask = None if video_folder is None else cv2.imread(os.path.join(video_folder, 'arena_mask.png'))
    if arena_mask is not None:
        rv, arena_mask = cv2.threshold(cv2.cvtColor(arena_mask, cv2.COLOR_BGR2GRAY), 1, 255, cv2.THRESH_BINARY_INV)
        #cv2.imshow("Mask", arena_mask)

    empty_img = None if video_folder is None else cv2.imread(os.path.join(video_folder, 'empty_arena.png'))
    if empty_img is not None:
        empty_img = mask(empty_img, arena_mask)
        if mog is not None:
            fgbg.apply(empty_img)
        if mog2 is not None:
            fgbg2.apply(empty_img)

    detect_count = []

    total_frames = capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
    ##capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, total_frames-2000)  # jump to end of file

    delay = 1
    frame_skip = 25
    fps = None
    tick_freq = cv2.getTickFrequency()
    tick_last = cv2.getTickCount()
    current_frame_pos = 0.0
    while capture.isOpened():
        rv, img = capture.read()
        if rv:
            current_frame_pos = capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
            img = mask(img, arena_mask)

            # THRESHOLDED IMAGES
            # thresholds = threshold(img, kwargs['low'] if 'low' in kwargs else None)
            # for title, image in thresholds:
            #     cv2.imshow(title, image)

            # BACKGROUND SUBTRACTION
            mog = fgbg.apply(img) if mog is not None else None
            mog2 = fgbg2.apply(img) if mog2 is not None else None

            eroded = cv2.erode(mog2, None, iterations=10)
            dilated = cv2.dilate(eroded, None, iterations=10)

            #call function to find contours
            contours, hierarchy = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            min_area = 500

            passed = [cnt for cnt in contours if cv2.contourArea(cnt.astype(int)) > min_area]
            n_shapes = len(passed)
            detect_count.append(n_shapes)

            if current_frame_pos % frame_skip == 0 and current_frame_pos > 0:  # reduce display burden

                # RAW IMAGE
                if mog is not None:
                    cv2.imshow('MOG()', mog)
                if mog2 is not None:
                    cv2.imshow('MOG2()', mog2)

                cv2.imshow('MOGx.erode()', eroded)
                cv2.imshow('MOGx.erode().dilate()', dilated)
                cv2.imshow("Masked raw gray", cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)*arena_mask)

                #draw found contours into new image
                contour_img = np.zeros_like(arena_mask)
                cv2.drawContours(contour_img, passed, -1, 255)

                for n, cnt in enumerate(passed):
                    color = (0, 0, 255) if len(passed) == 1 else ((255, 0, 0) if n == 1 else (0, 255, 0))
                    rect = cv2.minAreaRect(cnt)
                    box = cv2.cv.BoxPoints(rect)
                    box = np.int0(box)
                    cv2.drawContours(img, [box], 0, color, 2)
                cv2.imshow('Contours', contour_img)

                elapsed = (cv2.getTickCount() - tick_last) / tick_freq
                fps = 0.8*fps + 0.2*(frame_skip/elapsed) if fps is not None else frame_skip/elapsed
                #print "Processed {0} frames in {1:.2f}s".format(frame_skip, elapsed)
                tick_last = cv2.getTickCount()
                cv2.putText(img, "{0:.1f}% done.".format((current_frame_pos*100)/total_frames),
                            (700, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
                cv2.putText(img, "fps: {0:.2f}".format(fps),
                            (10, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
                cv2.putText(img, "frame: {0:.0f}/{1:.0f}".format(current_frame_pos, total_frames),
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
                cv2.imshow('raw', img)

                key = cv2.waitKey(10) - 0x100000
                if key > -1:
                    print key
                if key in (27, 113):  # ESC or 'q'
                    capture.release()
                    cv2.destroyAllWindows()
                elif key == 32:
                    delay = 1 if delay != 1 else 0
                elif key == 115:  # 's' for slow
                    delay = 500 if delay != 500 else 1

        if current_frame_pos == total_frames:
            print len(detect_count), detect_count.count(1),\
                "{0:.2f}%".format(detect_count.count(1)*100./len(detect_count))
            print "Starting Over!"
            capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 0.0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default=0)
    parser.add_argument('-l', '--low', type=int, default=127)

    args = parser.parse_args()

    print args
    main(source=args.input, low=args.low)