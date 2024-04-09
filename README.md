# motion-detection-microservice (gotta find a better name)
A (very) simple, non-bullshit motion detection service that lets you subscribe to a motion detection event given a camera URL and performs a callback on a given endpoint when movement is found.

## Build with Docker
`docker build -t motion-detection-microservice .`

`docker run -d --name motion-detection-microservice --network host motion-detection-microservice`

The only thing worthy of an explanation is the `--network host`: simply put, the service needs to be on same network of the host to reach the cameras and to be reachable from outside the host.
The service will start on port 8000.

## Build with Docker
