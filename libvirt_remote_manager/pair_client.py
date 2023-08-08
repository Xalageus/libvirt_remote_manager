import requests, time, curses, uuid
from typing import List
import libvirt_remote_manager.utils as utils
import libvirt_remote_manager._enums as enums
import libvirt_remote_manager._exceptions as ex
import libvirt_remote_manager._db_types as db_types
from libvirt_remote_manager.pair_menu import PairMenu

_localhost = 'http://127.0.0.1'

class PairClient():
    def __init__(self, port: int):
        self.port = port

    def _send_pair_start(self) -> tuple[str, int, enums.PairKeyStatus]:
        try:
            r = requests.get(_localhost + ':' + str(self.port) + '/api/pair/start')

            if r.status_code == 200:
                data = r.json()
                return (data['pair_key'], data['pair_time'], enums.PairKeyStatus(data['status']))
        except:
            raise ex.SendAPICallException("Failed to call pair_start on host!")
        
    def _send_pair_check(self, pair_key: str) -> tuple[int, enums.PairKeyStatus]:
        try:
            r = requests.get(_localhost + ':' + str(self.port) + '/api/pair/check?pair_key=' + str(pair_key))

            if r.status_code == 200:
                data = r.json()
                return (data['pair_time'], enums.PairKeyStatus(data['status']))
        except:
            raise ex.SendAPICallException("Failed to call pair_check on host!")
        
    def _send_unpair_device(self, device_uuid: uuid.UUID) -> bool:
        try:
            r = requests.post(_localhost + ':' + str(self.port) + '/api/pair/unpair_device?device_uuid=' + str(device_uuid))

            if r.status_code == 200:
                data = r.json()
                if data['status'] == 'success':
                    return True
                
            return False
        except:
            raise ex.SendAPICallException("Failed to call unpair_device on host!")
        
    def _send_trust_device(self, device_uuid: uuid.UUID) -> bool:
        try:
            r = requests.post(_localhost + ':' + str(self.port) + '/api/pair/trust_device?device_uuid=' + str(device_uuid))

            if r.status_code == 200:
                data = r.json()
                if data['status'] == 'success':
                    return True
                
            return False
        except:
            raise ex.SendAPICallException("Failed to call trust_device on host!")
        
    def _send_untrust_device(self, device_uuid: uuid.UUID) -> bool:
        try:
            r = requests.post(_localhost + ':' + str(self.port) + '/api/pair/untrust_device?device_uuid=' + str(device_uuid))

            if r.status_code == 200:
                data = r.json()
                if data['status'] == 'success':
                    return True
                
            return False
        except:
            raise ex.SendAPICallException("Failed to call untrust_device on host!")
        
    def _get_devices(self) -> List[db_types.Device]:
        try:
            r = requests.get(_localhost + ':' + str(self.port) + '/api/pair/get_devices')

            if r.status_code == 200:
                device_list = []
                data = r.json()
                for obj in data:
                    device_list.append(db_types.Device(obj['device_name'], obj['device_uuid'], obj['trusted']))
                return device_list
        except:
            raise ex.SendAPICallException("Failed to call pair_get_devices on host!")

    def start_pair(self):
        screen = curses.initscr()
        curses.curs_set(0)

        try:
            pair_key, pair_time, status = self._send_pair_start()
            while status == enums.PairKeyStatus.not_paired:
                screen.clear()
                screen.addstr(1, 1, "Pair code: " + str(pair_key))
                screen.addstr(2, 1, "Time remaining: " + str(pair_time))
                screen.refresh()
                time.sleep(2)
                pair_time, status = self._send_pair_check(pair_key)

            curses.curs_set(1)
            curses.endwin()

            if status == enums.PairKeyStatus.paired:
                print("Device successfully paired")
            elif status == enums.PairKeyStatus.expired:
                print("Pair code expired")
        except:
            if not curses.isendwin():
                curses.endwin()
            print("Pair failed")

    def unpair_device(self, device_uuid: str):
        if utils.is_valid_uuid4(device_uuid):
            if self._send_unpair_device(utils.str_to_uuid4(device_uuid)):
                print("Device successfully unpaired")
            else:
                print("Failed to unpair device")
        else:
            print("Received invalid UUID")

    def unpair_device_interactive(self):
        devices = self._get_devices()
        if len(devices) > 0:
            pm = PairMenu(devices, "unpair")
            result = pm.select()
            if result != -1:
                self.unpair_device(devices[result].device_uuid)
        else:
            print("No devices paired")

    def trust_device(self, device_uuid: str):
        if utils.is_valid_uuid4(device_uuid):
            if self._send_trust_device(utils.str_to_uuid4(device_uuid)):
                print("Device successfully trusted")
            else:
                print("Failed to trust device")
        else:
            print("Received invalid UUID")

    def trust_device_interactive(self):
        devices = self._get_devices()
        for device in devices:
            if device.trusted:
                devices.remove(device)

        if len(devices) > 0:
            pm = PairMenu(devices, "trust")
            result = pm.select()
            if result != -1:
                self.trust_device(devices[result].device_uuid)
        else:
            print("No untrusted devices")

    def untrust_device(self, device_uuid: str):
        if utils.is_valid_uuid4(device_uuid):
            if self._send_untrust_device(utils.str_to_uuid4(device_uuid)):
                print("Device successfully untrusted")
            else:
                print("Failed to untrust device")
        else:
            print("Received invalid UUID")

    def untrust_device_interactive(self):
        devices = self._get_devices()
        for device in devices:
            if not device.trusted:
                devices.remove(device)

        if len(devices) > 0:
            pm = PairMenu(devices, "untrust")
            result = pm.select()
            if result != -1:
                self.untrust_device(devices[result].device_uuid)
        else:
            print("No trusted devices")

    def list_devices(self):
        devices = self._get_devices()
        print(str(len(devices)) + " total devices paired\n")

        for device in devices:
            print("Name: " + device.device_name + ", UUID: " + device.device_uuid + ", Trusted: " + ("Yes" if device.trusted else "No"))
