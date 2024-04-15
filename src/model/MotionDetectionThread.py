from threading import Thread


class MotionDetectionThread(Thread):
    def __init__(self, *args, **kwargs):
        super(MotionDetectionThread, self).__init__(*args, **kwargs)
        self.status = None