from libvirt_remote_manager import app
from flask import request, abort
from libvirt_remote_manager._response_data import ResultBool
from libvirt_remote_manager.host_power import HostPower

@app.route('/api/host/pom/shutdown', methods=['POST'])
def host_shutdown():
    hp = HostPower()
    done = hp.host_shutdown()
    return ResultBool(done, '').toJSON()

@app.route('/api/host/pom/reboot', methods=['POST'])
def host_reboot():
    hp = HostPower()
    done = hp.host_reboot()
    return ResultBool(done, '').toJSON()

@app.route('/api/host/pom/ping')
def ping():
    return "pong"