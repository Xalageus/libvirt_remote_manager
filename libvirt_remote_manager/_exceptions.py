import logging, inspect, uuid
from typing import List

# Setup LogException logger
_logger = logging.getLogger("LogException")
_logger.propagate = False
_lsh = logging.StreamHandler()
_lsh.setLevel(logging.root.level)
if _lsh.level == logging.DEBUG:
    _fmt = '[%(asctime)s] [%(levelname)s] [%(off_module)s] [%(threadName)s] %(message)s'
else:
    _fmt = '[%(asctime)s] [%(levelname)s] [%(off_module)s] %(message)s'
_lfmt = logging.Formatter(fmt=_fmt, datefmt='%Y-%m-%d %H:%M:%S')
_lsh.setFormatter(_lfmt)
_logger.addHandler(_lsh)
logging.debug("LogException is ready")

class LoggerException(Exception):
    def __init__(self, msg="Failed to find offending module!"):
        self.msg = msg
        super().__init__(self.msg)

        logging.critical(msg)

class LogException(Exception):
    class _LogExceptionFilter(logging.Filter):
        def _find_module(self, frames: List[inspect.FrameInfo]):
            for f in frames:
                module = inspect.getmodule(f.frame)
                namelen = len(module.__name__.split("."))
                name = module.__name__.split(".")[namelen - 1]
                if name != '_exceptions' and name != 'logging':
                    return module
                
            return None

        def filter(self, record):
            off_modules = inspect.getouterframes(inspect.currentframe())
            off_module = self._find_module(off_modules)
            if off_module:
                namelen = len(off_module.__name__.split("."))
                record.off_module = off_module.__name__.split(".")[namelen - 1]
            else:
                raise LoggerException()
            
            return True

    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    def __init__(self, msg: str, log_level: str):
        self.msg = msg
        super().__init__(self.msg)

        filt = self._LogExceptionFilter()
        _logger.addFilter(filt)
        _logger.log(level=self.log_levels.get(log_level), msg=self.msg)
        _logger.removeFilter(filt)

class UUIDException(LogException):
    def __init__(self, msg="Received invalid UUID", log_level="WARNING"):
        self.msg = msg
        self.log_level = log_level
        super().__init__(self.msg, self.log_level)

class DBCorruptionException(LogException):
    def __init__(self, msg="Database is corrupted!"):
        self.msg = msg
        self.log_level = "CRITICAL"
        super().__init__(self.msg, self.log_level)

class DBThreadInvalidFuncException(LogException):
    def __init__(self, msg="Invalid function passed to thread!"):
        self.msg = msg
        self.log_level = "ERROR"
        super().__init__(self.msg, self.log_level)

class DBTimeoutException(LogException):
    def __init__(self, msg="Timed out waiting for a response from db thread!"):
        self.msg = msg
        self.log_level = "WARNING"
        super().__init__(self.msg, self.log_level)

class PairFailException(LogException):
    def __init__(self, device_uuid: str, pin: str, paired: bool):
        self.device_uuid = device_uuid
        self.pin = pin
        if paired:
            self.msg = "Device with uuid " + self.device_uuid + " is already paired"
        else:
            self.msg = "Device with uuid " + self.device_uuid + " used invalid pin " + self.pin
        self.log_level = "WARNING"
        super().__init__(self.msg, self.log_level)

class DeviceTrustException(LogException):
    def __init__(self, device_uuid: str, trusted: bool):
        self.device_uuid = device_uuid
        self.trusted = trusted
        if self.trusted:
            self.msg = "Device with uuid " + self.device_uuid + " is already trusted"
        else:
            self.msg = "Device with uuid " + self.device_uuid + " is not trusted"
        self.log_level = "ERROR"
        super().__init__(self.msg, self.log_level)

class DeviceMissingException(LogException):
    def __init__(self, device_uuid: str):
        self.device_uuid = device_uuid
        self.msg = "Device with uuid " + self.device_uuid + " does not exist"
        self.log_level = "ERROR"
        super().__init__(self.msg, self.log_level)

class CMDAttemptException(LogException):
    def __init__(self, device_uuid: uuid.UUID, addr: str, cmd: str):
        self.device_uuid = device_uuid
        if self.device_uuid:
            self.msg = "Device with uuid " + str(device_uuid) + " (" + addr + ") attempted to use a " + cmd + " command"
        else:
            self.msg = "Device at " + addr + " attempted to use a " + cmd + " command"
        self.log_level = "WARNING"
        super().__init__(self.msg, self.log_level)

class DBThreadDiedException(LogException):
    def __init__(self, msg="DBThread died!"):
        self.msg = msg
        self.log_level = "CRITICAL"
        super().__init__(self.msg, self.log_level)

class MissingCredentialsException(LogException):
    def __init__(self, msg="Device did not send required credentials!"):
        self.msg = msg
        self.log_level = "WARNING"
        super().__init__(self.msg, self.log_level)

class SendAPICallException(LogException):
    def __init__(self, msg="Failed to call API endpoint!"):
        self.msg = msg
        self.log_level = "ERROR"
        super().__init__(self.msg, self.log_level)
