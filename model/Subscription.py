from model.MotionDetectionThread import MotionDetectionThread


class Subscription:
    def __init__(
            self,
            camera_url: str,
            movement_callback_url: str,
            crash_callback_url: str,
            min_contour_area: int,
            cooldown_seconds: int,
            motion_detection_thread: MotionDetectionThread,
    ):
        self.camera_url = camera_url
        self.movement_callback_url = movement_callback_url
        self.crash_callback_url = crash_callback_url
        self.min_contour_area = min_contour_area
        self.cooldown_seconds = cooldown_seconds
        self.motion_detection_thread = motion_detection_thread
