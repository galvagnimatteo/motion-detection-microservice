from enum import Enum


class ThreadStatus(Enum):
    STARTING = "STARTING"
    CRASHED = "CRASHED"
    ACTIVE = "ACTIVE"
    RETRYING = "RETRYING"
    DELETING = "DELETING"
