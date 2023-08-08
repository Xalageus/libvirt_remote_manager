import os, uuid, random, string, socket
import libvirt_remote_manager._exceptions as ex

def check_if_root() -> bool:
    if os.getuid() == 0:
        return True
    else:
        return False

def generate_uuid4() -> str:
    return str(uuid.uuid4())

def str_to_uuid4(uuid_str: str) -> uuid.UUID:
    if(is_valid_uuid4(uuid_str)):
        return uuid.UUID(uuid_str, version=4)
    else:
        raise ex.UUIDException()

def _validate_uuid4(uuid_str: str) -> uuid.UUID | None:
    try:
        validate = uuid.UUID(uuid_str, version=4)
    except Exception:
        return None
    
    return validate

def is_valid_uuid4(uuid_str: str) -> bool:
    if(_validate_uuid4(uuid_str)):
        return True
    
    return False

def generate_rand_4_digits() -> str:
    return str(random.randint(0, 9999)).zfill(4)

def generate_device_key() -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for i in range(32))

def check_if_local_addr(addr: str) -> bool:
    if addr == "127.0.0.1" or addr == "localhost":
        return True
    
    return False

def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip
