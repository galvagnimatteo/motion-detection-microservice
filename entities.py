from pydantic import BaseModel
from threading import Thread
from enum import Enum

class SubscribeItem(BaseModel):
    movement_callback_url: str
    crash_callback_url: str
    camera_url: str

class UnsubscribeItem(BaseModel):
    camera_url: str

class CameraThread(Thread):
    def __init__(self, *args, **kwargs):
        super(CameraThread, self).__init__(*args, **kwargs)
        self.status = None
        self.do_update_env = False

class ThreadStatus(Enum):
    STARTING = "STARTING"
    CRASHED = "CRASHED"
    ACTIVE = "ACTIVE"
    RETRYING = "RETRYING"
    STOPPED = "STOPPED"

class EnvItem(BaseModel):
    min_contour_area: int
    cooldown_seconds: int

class Subscription(BaseModel):
    camera_url: str
    status : ThreadStatus
    movement_callback_url: str
    crash_callback_url: str
