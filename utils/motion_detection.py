import cv2
import requests
import time
import threading
import imutils

from model.enums.ThreadStatus import ThreadStatus


#precondition: camera url is valid and works
def start_motion_detection(subscription_input_dto):
    t = threading.currentThread()
    t.status = ThreadStatus.STARTING

    try:
        cap = cv2.VideoCapture(subscription_input_dto.camera_url)
        fgbg = cv2.createBackgroundSubtractorMOG2()

        last_detection_time = 0

        while getattr(t, "do_run", True):
            ret, frame = cap.read()
            if ret:
                t.status = ThreadStatus.ACTIVE
                frame = imutils.resize(frame, width=500)
                fgmask = fgbg.apply(frame)
                contours, _ = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours[1:]:
                    if cv2.contourArea(contour) > subscription_input_dto.min_contour_area:
                        current_time = time.time()
                        if current_time - last_detection_time > subscription_input_dto.cooldown_seconds:
                            last_detection_time = time.time()
                            (x, y, w, h) = cv2.boundingRect(contour)
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                            _, jpeg = cv2.imencode('.jpg', frame)
                            blob = jpeg.tobytes()
                            requests.post(subscription_input_dto.movement_callback_url, data=blob)
            else:
                #bad frame, no big deal, probably doesn't even need a status for this
                t.status = ThreadStatus.RETRYING

        cap.release()
        #thread stopped, will be deleted, probably doesn't need this status but ynk
        t.status = ThreadStatus.DELETING

    except Exception as e:
        print(e)
        requests.post(subscription_input_dto.crash_callback_url, data=subscription_input_dto.camera_url)  #useful for detecting a crashed thread
        t.status = ThreadStatus.CRASHED
