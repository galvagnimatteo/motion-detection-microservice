from pydantic import BaseModel
from model.enums.ThreadStatus import ThreadStatus


class SubscriptionOutputDto(BaseModel):
    camera_url: str
    movement_callback_url: str
    crash_callback_url: str
    min_contour_area: int
    cooldown_seconds: int
    status: ThreadStatus
