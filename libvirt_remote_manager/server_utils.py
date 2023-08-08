import flask, uuid
import libvirt_remote_manager.utils as utils
from libvirt_remote_manager.pair_host import PairHost
import libvirt_remote_manager._exceptions as ex

def get_device_creds(req: flask.Request) -> tuple[uuid.UUID, str]:
    if('X-Device-Uuid' in req.headers and 'X-Device-Key' in req.headers):
        return (utils.str_to_uuid4(req.headers['X-Device-Uuid']), req.headers['X-Device-Key'])
    else:
        raise ex.MissingCredentialsException()
    
def get_sent_device_uuid(req: flask.Request) -> uuid.UUID or None:
    if('X-Device-Uuid') in req.headers:
        return utils.str_to_uuid4(req.headers['X-Device-Uuid'])
    else:
        return None

def paired(req: flask.Request, ph: PairHost) -> bool:
    if get_sent_device_uuid(req):
        device_uuid, device_key = get_device_creds(req)
        return ph.check_device(str(device_uuid), device_key)
    else:
        return False
