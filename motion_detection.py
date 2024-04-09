import cv2
import requests
import time
import threading
from entities import ThreadStatus
import imutils
import os
from dotenv import load_dotenv

def start_motion_detection(camera_url, movement_callback_url, crash_callback_url):
    t = threading.currentThread()
    t.status = ThreadStatus.STARTING

    load_dotenv()
    min_contour_area = int(os.getenv('MIN_CONTOUR_AREA'))
    cooldown_seconds = int(os.getenv('COOLDOWN_SECONDS'))

    try:
        cap = cv2.VideoCapture(camera_url)
        fgbg = cv2.createBackgroundSubtractorMOG2()

        last_detection_time = 0

        while getattr(t, "do_run", True):

            if t.do_update_env:
                #reload env when is changed instead of reading from file for every frame
                load_dotenv()
                min_contour_area = int(os.getenv('MIN_CONTOUR_AREA'))
                cooldown_seconds = int(os.getenv('COOLDOWN_SECONDS'))
                t.do_update_env = False

            ret, frame = cap.read()
            if ret:
                t.status = ThreadStatus.ACTIVE
                frame = imutils.resize(frame, width=500)
                fgmask = fgbg.apply(frame)
                contours, _ = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours[1:]:
                    if cv2.contourArea(contour) > min_contour_area:
                        current_time = time.time()
                        if current_time - last_detection_time > cooldown_seconds:
                            last_detection_time = time.time()
                            (x, y, w, h) = cv2.boundingRect(contour)
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                            _, jpeg = cv2.imencode('.jpg', frame)
                            blob = jpeg.tobytes()
                            requests.post(movement_callback_url, data=blob)
            else:
                #bad frame, no big deal, probably doesn't even need a status for this
                t.status = ThreadStatus.RETRYING

        cap.release()
        #thread stopped, will be deleted, probably doesn't need this status but ynk
        t.status = ThreadStatus.STOPPED

    except Exception as e:
        print(e)
        requests.post(crash_callback_url) #useful for detecting a crashed thread
        t.status = ThreadStatus.CRASHED
