import enum

class PowerType(enum.Enum):
    shutdown = 0
    reboot = 1

class PowerMethod(enum.Enum):
    classic = 0
    systemd = 1