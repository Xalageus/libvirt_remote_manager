import libvirt_remote_manager._enums as enums

class OSNames():
    def __init__(self, name: str, long_id: str, short_id: str, family: str, distro: str):
        self.name = name
        self.long_id = long_id
        self.short_id = short_id
        self.family = family
        self.distro = distro

class VMMetadata():
    def __init__(self, name: str, state: enums.VMState, shutoff_reason: enums.VMShutoffReason, uuid: str, os_names: OSNames):
        self.name = name
        self.state = state
        self.shutoff_reason = shutoff_reason
        self.uuid = uuid
        self.os_names = os_names
