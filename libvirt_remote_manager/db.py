import sqlite3, logging, os, threading, queue
import libvirt_remote_manager.utils as utils
import libvirt_remote_manager._exceptions as ex
from libvirt_remote_manager._enums import DBFunction

DB_VERSION = 1
DB_TIMEOUT = 80 # 20 seconds

class DatabaseThread(threading.Thread):
    def __init__(self, dbFile: str):
        self._dbFile = dbFile
        self._db = None

        self.q_call = queue.Queue()
        self.q_return = queue.Queue()
        self.q_lf = queue.Queue()
        super().__init__()
        self.setName("DBThread")
        self._resume = threading.Event()
        self._done = threading.Event()
        self._running = True
        self._call_lock = False
        self._ready = threading.Event()

    def wait_till_ready(self):
        loading = True
        while loading:
            self._ready.wait(1)
            if self._ready.is_set():
                loading = False
            if not self.is_alive():
                raise ex.DBThreadDiedException()

    def on_thread(self, function: DBFunction, *args, **kwargs):
        call_num = int(utils.generate_rand_4_digits())
        self.q_call.put((call_num, function, args, kwargs))
        self._resume.set()
        self._call_lock = True
        self._call_lock_timeout = 0
        result = None

        while self._call_lock:
            try:
                self._done.wait(0.25)
                self._call_lock_timeout += 1
                if self._call_lock_timeout > DB_TIMEOUT:
                    raise ex.DBTimeoutException()

                try:
                    r_call_num, result = self.q_return.get(timeout=1)
                    if(r_call_num == call_num):
                        if result == "INVALIDFUNCTION":
                            raise ex.DBThreadInvalidFuncException()
                        self._call_lock = False
                        self._done.clear()
                    else:
                        self.q_lf.put((r_call_num, result))
                        # Check lost and found
                        r_call_num, result = self.lf.get(timeout=1)
                        if(r_call_num == call_num):
                            if result == "INVALIDFUNCTION":
                                raise ex.DBThreadInvalidFuncException()
                            self._call_lock = False
                            self._done.clear()
                        self.q_lf.put((r_call_num, result))
                except ex.DBThreadInvalidFuncException:
                    result = None
                    self._call_lock = False
                    self._done.clear()
                except queue.Empty:
                    # Assume we don't need to receive anything
                    result = None
                    self._call_lock = False
                    self._done.clear()
            except ex.DBTimeoutException:
                result = None
                self._call_lock = False
                self._done.clear()

        return result

    def run(self):
        logging.debug("Starting DB thread")
        self._db = Database(self._dbFile)
        while self._running:
            if self.q_call.qsize() > 0:
                try:
                    function: DBFunction
                    call_num, function, args, kwargs = self.q_call.get(timeout=1)
                    match function.value:
                        case 0:
                            result = self._db.get_host_uuid()
                        case 1:
                            self._db.add_device_pair(args[0], args[1], args[2])
                            result = "DONE"
                        case 2:
                            self._db.set_device_trusted(args[0])
                            result = "DONE"
                        case 3:
                            result = self._db.get_devices()
                        case 4:
                            self._db.set_device_untrusted(args[0])
                            result = "DONE"
                        case 5:
                            result = self._db.get_device_data(args[0])
                        case _:
                            result = "INVALIDFUNCTION"
                    if result != None:
                        self.q_return.put((call_num, result))
                    self._done.set()
                except queue.Empty:
                    self._resume.wait()
            else:
                self._ready.set()
                self._resume.wait()

            self._resume.clear()
        
        self._db.cleanup()

    def stop(self):
        logging.debug("Stopping DB thread")
        self._running = False
        self._resume.set()

class Database():
    def __init__(self, dbFile: str):
        if self._verify_db_file(dbFile):
            self._con = sqlite3.connect(dbFile)
            self._cur = self._con.cursor()

            if not self._verify_db_tables():
                self._create_db()
        else:
            raise ex.DBCorruptionException()

    def _verify_db_file(self, dbFile: str) -> bool:
        if os.path.isfile(dbFile):
            if os.path.getsize(dbFile) > 100:
                with open(dbFile, 'r', encoding='ISO-8859-1') as file:
                    header = file.read(100)
                    if header.startswith('SQLite format 3'):
                        return True
        else:
            # DB not created?
            return True
        
        return False
    
    def _verify_db_tables(self) -> bool:
        self._cur.execute('SELECT count(name) FROM sqlite_master WHERE type=\'table\' AND name=\'lrmData\';')
        self._cur.execute('SELECT count(name) FROM sqlite_master WHERE type=\'table\' AND name=\'DevicePairs\';')

        for row in self._cur.fetchall():
            if row[0] == 0:
                return False
            
        return True
    
    def _create_db(self):
        logging.info("Creating database")

        self._cur.execute('CREATE TABLE lrmData (DBVERSION INTEGER NOT NULL, HostUUID TEXT NOT NULL);')
        self._cur.execute('CREATE TABLE DevicePairs (DeviceID INTEGER PRIMARY KEY AUTOINCREMENT, DeviceName TEXT NOT NULL, DeviceUUID TEXT NOT NULL, DeviceKey TEXT NOT NULL, Trusted BOOLEAN NOT NULL);')
        self._cur.execute('INSERT INTO lrmData Values(?, ?);', (str(DB_VERSION), str(utils.generate_uuid4())))
        self._con.commit()

    def cleanup(self):
        logging.debug("Closing database")
        self._con.close()

    def get_host_uuid(self):
        self._cur.execute('SELECT HostUUID FROM lrmData;')
        row = self._cur.fetchone()

        return row
    
    def add_device_pair(self, device_name: str, device_uuid: str, device_key: str):
        self._cur.execute('INSERT INTO DevicePairs Values(null, ?, ?, ?, ?)', (device_name, device_uuid, device_key, str(False)))
        self._con.commit()

    def set_device_trusted(self, device_uuid: str):
        self._cur.execute('UPDATE DevicePairs SET Trusted=? WHERE DeviceUUID=?;', (str(True), device_uuid))
        self._con.commit()

    def get_devices(self):
        self._cur.execute('SELECT DeviceName, DeviceUUID, Trusted FROM DevicePairs;')
        rows = self._cur.fetchall()

        return rows
    
    def set_device_untrusted(self, device_uuid: str):
        self._cur.execute('UPDATE DevicePairs SET Trusted=? WHERE DeviceUUID=?;', (str(False), device_uuid))
        self._con.commit()

    def get_device_data(self, device_uuid: str):
        self._cur.execute('SELECT DeviceName, DeviceKey, Trusted FROM DevicePairs WHERE DeviceUUID=?;', (device_uuid,))
        row = self._cur.fetchone()

        return row
    
    def delete_device_pair(self, device_uuid: str):
        self._cur.execute('DELETE FROM DevicePairs WHERE DeviceUUID=?;', (device_uuid,))
        self._con.commit()
