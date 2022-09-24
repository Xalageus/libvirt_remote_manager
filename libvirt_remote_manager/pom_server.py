from libvirt_remote_manager import app
from flask import request, abort
from libvirt_remote_manager._response_data import ResultBool
from libvirt_remote_manager.host_power import HostPower
import libvirt_remote_manager.utils as utils

debug = False

@app.route('/api/host/pom/shutdown', methods=['POST'])
def host_shutdown():
    if debug:
        utils.debug_print_request(request.url)
    hp = HostPower()
    done = hp.host_shutdown()
    return ResultBool(done, '').toJSON()

@app.route('/api/host/pom/reboot', methods=['POST'])
def host_reboot():
    if debug:
        utils.debug_print_request(request.url)
    hp = HostPower()
    done = hp.host_reboot()
    return ResultBool(done, '').toJSON()

@app.route('/api/host/pom/ping')
def ping():
    if debug:
        utils.debug_print_request(request.url)
    return "pong"
