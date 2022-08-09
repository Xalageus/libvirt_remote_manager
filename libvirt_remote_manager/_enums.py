import enum

class PowerType(enum.Enum):
    shutdown = 0
    reboot = 1

class PowerMethod(enum.Enum):
    classic = 0
    systemd = 1

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
