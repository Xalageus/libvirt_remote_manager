import logging
from functools import wraps
from flask import request
from libvirt_remote_manager.server_objs import pairh
import libvirt_remote_manager.server_utils as s_utils
import libvirt_remote_manager.utils as utils
import libvirt_remote_manager._exceptions as ex
import libvirt_remote_manager._response_data as responses

def debug_log_url(f):
    @wraps(f)
    def d(*args, **kwargs):
        logging.debug(request.url)
        return f(*args, **kwargs)
    return d

def pair_required(f):
    @wraps(f)
    def d(*args, **kwargs):
        try:
            device_uuid, _ = s_utils.get_device_creds(request)
            if(s_utils.paired(request, pairh)):
                # Device is paired but I don't want to catch exceptions inside f
                pass
            else:
                raise ex.CMDAttemptException(str(device_uuid), request.remove_addr, "paired")
        except Exception as err:
            return responses.Result('failure', str(err)).toJSON()
        return f(*args, **kwargs)
    return d

def trusted_or_localhost_required(f):
    @wraps(f)
    def d(*args, **kwargs):
        try:
            device_uuid, _ = s_utils.get_device_creds(request)
            if(s_utils.paired(request, pairh) or utils.check_if_local_addr(request.remote_addr)):
                if(utils.check_if_local_addr(request.remote_addr) or pairh.trusted(str(device_uuid))):
                    # Device is paired and trusted or localhost but I don't want to catch exceptions inside f
                    pass
                else:
                    raise ex.CMDAttemptException(str(device_uuid), request.remove_addr, "trusted")
            else:
                raise ex.CMDAttemptException(str(device_uuid), request.remove_addr, "trusted")
        except Exception as err:
            return responses.Result('failure', str(err)).toJSON()
        return f(*args, **kwargs)
    return d

def trusted_required(f):
    @wraps(f)
    def d(*args, **kwargs):
        try:
            device_uuid, _ = s_utils.get_device_creds(request)
            if(s_utils.paired(request, pairh) and pairh.trusted(str(device_uuid))):
                # Device is paired and trusted but I don't want to catch exceptions inside f
                pass
            else:
                raise ex.CMDAttemptException(str(device_uuid), request.remove_addr, "trusted")
        except Exception as err:
            return responses.Result('failure', str(err)).toJSON()
        return f(*args, **kwargs)
    return d
