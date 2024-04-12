from fastapi import FastAPI, HTTPException, Response

from model.MotionDetectionThread import MotionDetectionThread
from model.Subscription import Subscription
from model.dtos.input.SubscriptionInputDto import SubscriptionInputDto
from model.dtos.output.SubscriptionOutputDto import SubscriptionOutputDto
from utils.motion_detection import start_motion_detection
import cv2

app = FastAPI()

subscriptions = {}  #camera url -> subscription


@app.post("/")
async def create_subscription(item: SubscriptionInputDto):
    if item.camera_url in subscriptions:
        raise HTTPException(status_code=400, detail="a subscription with this url is already running, delete it first")

    cap = cv2.VideoCapture(item.camera_url)
    if not cap.isOpened():
        raise HTTPException(status_code=400, detail="can't connect to camera (check if url is valid)")

    thread = MotionDetectionThread(target=start_motion_detection,
                                   args=(item,))
    thread.start()
    subscriptions[item.camera_url] = Subscription(camera_url=item.camera_url,
                                                  movement_callback_url=item.movement_callback_url,
                                                  crash_callback_url=item.crash_callback_url,
                                                  min_contour_area=item.min_contour_area,
                                                  cooldown_seconds=item.cooldown_seconds,
                                                  motion_detection_thread=thread)

    return SubscriptionOutputDto(camera_url=item.camera_url,
                                 movement_callback_url=item.movement_callback_url,
                                 crash_callback_url=item.crash_callback_url,
                                 min_contour_area=item.min_contour_area,
                                 cooldown_seconds=item.cooldown_seconds,
                                 status=thread.status)


@app.get("/")
async def get_subscription(camera_url: str):
    if camera_url in subscriptions:
        subscription = subscriptions[camera_url]
        return SubscriptionOutputDto(camera_url=subscription.camera_url,
                                     movement_callback_url=subscription.movement_callback_url,
                                     crash_callback_url=subscription.crash_callback_url,
                                     min_contour_area=subscription.min_contour_area,
                                     cooldown_seconds=subscription.cooldown_seconds,
                                     status=subscription.motion_detection_thread.status)
    else:
        raise HTTPException(status_code=404, detail="subscription not found for this url")


@app.delete("/")
async def cancel_subscription(camera_url: str):
    if camera_url in subscriptions:
        subscriptions[camera_url].motion_detection_thread.do_run = False
        del subscriptions[camera_url]
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404, detail="subscription not found for this url")
