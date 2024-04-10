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

There is a cooldown period beetween every movement detection where this request will not be sent, this is needed because if movement is found and your service
has been notified of it, it probably doesn't need to be notified for every other frame of movement; this cooldown is by default 120 seconds but it can be customized
with the appropriated `/updateEnv` endpoint.
Speaking of env variables, there also is a `MIN_CONTOUR_AREA` variable that can be modified to increase or decrease the camera sensibility to movement; again, this 
can be customized with `/updateEnv`.

This service has NO persistence other than the env variables, so if shutted down it will lose all saved subscriptions.

If the thread crashes for some reason, an empty POST request will be sent to another endpoint of yours to inform you about the crash.
There also is an utility endpoint (`/checkCameraConnection`), mainly used to check if the camera url is working correctly.

You can go to [localhost:USE_PORT/docs] or use the provided OpenApi schema to learn more about the available endpoints.

## Typical use flow
- Check camera connection given its RTSP URL
- Subscribe with camera RTSP URL to start detection
- Get subscription to check if active
- A camera detects movement, your callback URL is called and the cooldown period starts
    - If camera still detects movement it will not call the callback URL until cooldown period is finished
- Unsubscribe with camera URL to stop detection
- Update camera sensibility or cooldown period