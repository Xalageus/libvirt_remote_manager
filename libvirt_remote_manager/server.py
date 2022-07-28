from libvirt_remote_manager import app
from flask import request, abort
from libvirt_remote_manager.virt_api import VirtAPI
from libvirt_remote_manager._response_data import VMList, Result, HostInfo, ResultBool
import libvirt_remote_manager.lrm_api as lrm_api
from libvirt_remote_manager.host_power import HostPower

_api: VirtAPI

@app.route('/api/get_vms')
def get_vms():
    try:
        vms = _api.list_vms()
        return VMList(vms).toJSON()
    except Exception as err:
        return Result('failure', err).toJSON()

@app.route('/api/<uuid>/start', methods=['POST'])
def start_vm(uuid):
    if request.method == 'POST':
        try:
            _api.start_vm(uuid)
            return Result('success', '').toJSON()
        except Exception as err:
            return Result('failure', str(err)).toJSON()

@app.route('/api/<uuid>/shutdown', methods=['POST'])
def shutdown_vm(uuid):
    if request.method == 'POST':
        try:
            _api.shutdown_vm(uuid)
            return Result('success', '').toJSON()
        except Exception as err:
            return Result('failure', str(err)).toJSON()

@app.route('/api/<uuid>/poweroff', methods=['POST'])
def poweroff_vm(uuid):
    if request.method == 'POST':
        try:
            _api.poweroff_vm(uuid)
            return Result('success', '').toJSON()
        except Exception as err:
            return Result('failure', str(err)).toJSON()

@app.route('/api/get_device_info')
def get_device_info():
    try:
        return HostInfo(lrm_api.get_lrm_name(), lrm_api.get_lrm_version(), str(lrm_api.get_hostname()), str(_api.get_libvirt_version())).toJSON()
    except Exception as err:
        return Result('failure', err).toJSON()

@app.route('/api/host/shutdown', methods=['POST'])
def host_shutdown():
    hp = HostPower()
    done = hp.host_shutdown()
    return ResultBool(done, '').toJSON()

@app.route('/api/host/reboot', methods=['POST'])
def host_reboot():
    hp = HostPower()
    done = hp.host_reboot()
    return ResultBool(done, '').toJSON()
