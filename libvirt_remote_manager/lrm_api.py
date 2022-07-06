import socket
from libvirt_remote_manager import __name__ as lrm_name
from libvirt_remote_manager import __version__ as lrm_version

def get_hostname() -> str:
    return socket.gethostname()

def get_lrm_name() -> str:
    return lrm_name

def get_lrm_version() -> str:
    return lrm_version
