class Device():
    def __init__(self, device_name: str, device_uuid: str, trusted: bool):
        self.device_name = device_name
        self.device_uuid = device_uuid
        self.trusted = trusted
