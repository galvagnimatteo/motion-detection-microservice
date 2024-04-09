from fastapi import FastAPI, HTTPException, Response
from motion_detection import start_motion_detection
from entities import *
import cv2
from dotenv import set_key

app = FastAPI()
threads = {} #camera url -> thread
subscriptionItems = {} #camera url -> subscription

@app.post("/subscribe")
async def subscribe(item: SubscribeItem):
    if item.camera_url in threads:
        raise HTTPException(status_code=400, detail="a thread is already running, unsubscribe first")
    t = CameraThread(target=start_motion_detection, args=(item.camera_url, item.movement_callback_url, item.crash_callback_url))
    t.start()
    threads[item.camera_url] = t
    subscriptionItems[item.camera_url] = item
    
    subscriptionToReturn = Subscription(camera_url=item.camera_url, status=ThreadStatus.STARTING, movement_callback_url=item.movement_callback_url, crash_callback_url=item.crash_callback_url)
    return subscriptionToReturn

@app.post("/unsubscribe")
async def unsubscribe(item: UnsubscribeItem):
    if item.camera_url in threads:
        threads[item.camera_url].do_run = False
        del threads[item.camera_url]
        del subscriptionItems[item.camera_url]
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404, detail="thread not found for this url")

@app.get("/getSubscription")
async def get_subscription(camera_url: str):
    if camera_url in threads:
        subscriptionToReturn = Subscription(camera_url=camera_url, status=threads[camera_url].status, movement_callback_url=subscriptionItems[camera_url].movement_callback_url, crash_callback_url=subscriptionItems[camera_url].crash_callback_url)
        return subscriptionToReturn
    else:
        raise HTTPException(status_code=404, detail="thread not found for this url")
    
@app.get("/checkCameraConnection")
def connect_camera(camera_url: str):
    cap = cv2.VideoCapture(camera_url)
    if cap.isOpened():
        return Response(status_code=204)
    else:
        return {"camera_url": camera_url}
    
@app.put("/updateEnv")
async def update_env(item: EnvItem):
    set_key('.env', 'MIN_CONTOUR_AREA', str(item.min_contour_area))
    set_key('.env', 'COOLDOWN_SECONDS', str(item.cooldown_seconds))
    for camera_url in threads:
        threads[camera_url].do_update_env = True
    return Response(status_code=204)