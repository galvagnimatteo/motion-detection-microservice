# motion-detection-microservice (gotta find a better name)
A (very) simple, non-bullshit motion detection service that lets you subscribe to a motion detection event given a camera URL (tested with RTSP but should work with other protocols too as it uses OpenCv) and that performs a callback on a given endpoint when movement is found.

## Build with Docker
```
docker build -t motion-detection-microservice .
docker run -d -e USE_PORT=9669 --name motion-detection-microservice --network host motion-detection-microservice
```

The only thing worthy of an explanation is the `--network host`: simply put, the service needs to be on same network of the host to reach the cameras and to be reachable from outside the host.
The service will start on the port passed in `USE_PORT`.

## How to use
The service exposes endpoints to subscribe to motion detection events. 
Once subscribed (with the camera URL as the identifier for your subscription), a separate thread will constantly search for movement with that camera.
If found, a POST request with a blob representing an image of the movement will be sent to a callback endpoint of yours (also provided when creating the subscription).

Every subscription has a cooldown period between every movement detection where this request will not be sent, this is needed because if movement is found and your service
has been notified of it, it probably doesn't need to be notified for every other frame of movement.
With every subscription you can also specify the min value of contour area the movement needs to be to
trigger the callback, this is used to increase or decrease the camera sensibility to movement; every frame is resized as an
image with a fixed width of 500 so keep in mind this when deciding what min contour area to use.
A cooldown of 120s and a min contour of 5000 should be good default values but adjust as you like.

This service has NO persistence, so if shut down it will lose all saved subscriptions.

If the thread crashes for some reason, an empty POST request will be sent to another endpoint of yours to inform you about the crash.

You can go to [localhost:USE_PORT/docs] or use the provided OpenApi schema to learn more about the available endpoints.

## Subscription statuses
If you perform a GET request passing the camera URL used for subscription, a subscription object will be returned with
your configuration and a "status" value.
This list briefly explain what every status means:
- STARTING: The motion detection thread has just started. Camera connection has already been checked and is working, but motion is still not being detected.
This typically last less than a second and will be returned only on subscription creation.
- CRASHED: The thread has crashed for some reason. A POST request (with the camera URL as data) to your specified crash endpoint 
has been performed so you can decide what to do. You still need to unsubscribe if you want to create a new subscription.
- ACTIVE: Thread is running and searching for movement (or has already detected it and is waiting the cooldown period). Note that
if movement is found the relative thread still remains active (there is no special state, just the callback POST request with
an image blob to your specified callback url).
- RETRYING: Thread has received a bad frame from camera. Sometimes it happens and it's no big deal. You can still consider this as ACTIVE,
though if some thread is often in this state something might be wrong.
- DELETING: When a subscription is deleted the motion detection thread is lazily stopped (meaning it isn't immediately killed, just 
given a signal to stop itself). This status reflects the short period of time (again less than a second) between the 
thread stopping signal and the subscription deletion.

## Typical use flow
- Subscribe with camera RTSP URL to start detection
- Get subscription to check if active
- A camera detects movement, your callback URL is called and the cooldown period starts
    - If camera still detects movement it will not call the callback URL until cooldown period is finished
- Unsubscribe with camera URL to stop detection