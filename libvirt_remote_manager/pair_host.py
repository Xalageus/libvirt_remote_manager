import logging, datetime
from typing import List
from libvirt_remote_manager.db import DatabaseThread
import libvirt_remote_manager.utils as utils
import libvirt_remote_manager._enums as enums
import libvirt_remote_manager._db_types as db_types
import libvirt_remote_manager._exceptions as ex

PAIR_TIME = 60

class PairKey():
    def __init__(self, pair_time: int):
        self._created_time = datetime.datetime.now()
        self.key = utils.generate_rand_4_digits()
        self.pair_time = pair_time
        self.done = False

    def check_valid(self) -> bool:
        return (datetime.datetime.now() - self._created_time).seconds < self.pair_time
    
    def time_remaining(self) -> int:
        return self.pair_time - (datetime.datetime.now() - self._created_time).seconds
    
    def old(self) -> bool:
        if self.done:
            if (datetime.datetime.now() - self._created_time).seconds > (self.pair_time * 2):
                return True
            
        return False

class PairHost():
    def __init__(self, dbFile: str):
        self._db = DatabaseThread(dbFile)
        self._db.start()
        self._db.wait_till_ready()
        self._pairkeys: List[PairKey] = []

    def _check_db_thread(self):
        if not self._db.is_alive():
            raise ex.DBThreadDied()

    def _cleanup_keys(self):
        for key in self._pairkeys:
            if not key.done and not key.check_valid():
                self._pairkeys.remove(key)

            if key.old():
                self._pairkeys.remove(key)

    def start_pair(self, pair_time=PAIR_TIME) -> tuple[int, int]:
        self._check_db_thread()
        self._cleanup_keys()

        key = PairKey(pair_time)
        self._pairkeys.append(key)
        return (key.key, key.pair_time)
    
    def pair_attempt(self, device_name: str, device_uuid: str, pin: str) -> str:
        self._check_db_thread()
        self._cleanup_keys()

        for key in self._pairkeys:
            if key.key == pin and not key.done:
                logging.info("Pair success with " + device_uuid)
                key.done = True
                device_key = utils.generate_device_key()
                self._db.on_thread(enums.DBFunction.add_device_pair, device_name, device_uuid, device_key)
                return device_key
            
        raise ex.PairFailException(device_uuid, pin)

    def check_pair(self, pin: str) -> tuple[int, enums.PairKeyStatus]:
        self._cleanup_keys()

        for key in self._pairkeys:
            if key.key == pin:
                return (key.time_remaining(), enums.PairKeyStatus(key.done))
        
        return (0, enums.PairKeyStatus.expired)
    
    def trust_device(self, device_uuid: str):
        self._check_db_thread()

        devices = self._db.on_thread(enums.DBFunction.get_devices)
        for device in devices:
            if device[1] == device_uuid:
                if device[2]:
                    raise ex.DeviceTrustException(device_uuid, True)
                self._db.on_thread(enums.DBFunction.set_device_trusted, device_uuid)
            
        raise ex.DeviceMissingException(device_uuid)
    
    def untrust_device(self, device_uuid: str):
        self._check_db_thread()

        devices = self._db.on_thread(enums.DBFunction.get_devices)
        for device in devices:
            if device[1] == device_uuid:
                if not device[2]:
                    raise ex.DeviceTrustException(device_uuid, False)
                self._db.on_thread(enums.DBFunction.set_device_untrusted, device_uuid)
            
        raise ex.DeviceMissingException(device_uuid)
    
    def check_device(self, device_uuid: str, device_key: str) -> bool:
        self._check_db_thread()

        device = self._db.on_thread(enums.DBFunction.get_device_data, device_uuid)
        if device:
            if device[1] == device_key:
                return True
        
        return False
    
    def trusted(self, device_uuid: str) -> bool:
        self._check_db_thread()

        if not device_uuid:
            return False
        
        device = self._db.on_thread(enums.DBFunction.get_device_data, device_uuid)
        return device[2]
    
    def get_devices(self) -> List[db_types.Device]:
        self._check_db_thread()

        device_list = []
        db_devices = self._db.on_thread(enums.DBFunction.get_devices)
        for device in db_devices:
             device_list.append(db_types.Device(device[0], device[1], device[2]))

        return device_list
    
    def get_device(self, device_uuid: str) -> db_types.Device | None:
        self._check_db_thread()

        db_device = self._db.on_thread(enums.DBFunction.get_device_data, device_uuid)
        if db_device:
            return db_types.Device(db_device[0], device_uuid, db_device[2])
        
        logging.debug(device_uuid + " not in db")
        return None
    
    def unpair(self, device_uuid: str) -> bool:
        self._check_db_thread()

        db_device = self._db.on_thread(enums.DBFunction.get_device_data, device_uuid)
        if db_device:
            self._db.on_thread(enums.DBFunction.delete_device_pair)

        raise ex.DeviceMissingException()

    def get_host_uuid(self):
        self._check_db_thread()

        try:
            uuid_str = self._db.on_thread(enums.DBFunction.get_host_uuid)[0]
            return utils.str_to_uuid4(uuid_str)
        except Exception as e:
            raise ex.UUIDException(msg="Invalid UUID from database, this may indicate db corruption!", log_level="ERROR")

    def cleanup(self):
        self._db.stop()