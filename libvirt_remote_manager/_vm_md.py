import enum

class VMState(enum.Enum):
    nostate = 0
    running = 1
    blocked = 2
    paused = 3
    shutdown = 4
    shutoff = 5
    crashed = 6
    pm_suspended = 7
    last = 8

class VMShutoffReason(enum.Enum):
    unknown = 0
    shutdown = 1
    destroyed = 2
    crashed = 3
    migrate = 4
    saved = 5
    failed = 6
    from_snapshot = 7
    daemon = 8
    last = 9

class OSNames():
    def __init__(self, name: str, long_id: str, short_id: str, family: str, distro: str):
        self.name = name
        self.long_id = long_id
        self.short_id = short_id
        self.family = family
        self.distro = distro

class VMMetadata():
    def __init__(self, name: str, state: VMState, shutoff_reason: VMShutoffReason, uuid: str, os_names: OSNames):
        self.name = name
        self.state = state
        self.shutoff_reason = shutoff_reason
        self.uuid = uuid
        self.os_names = os_names
