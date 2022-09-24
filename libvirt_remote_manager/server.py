from libvirt_remote_manager import app
from flask import request, abort
from libvirt_remote_manager.virt_api import VirtAPI
from libvirt_remote_manager._response_data import VMList, Result, HostInfo, ResultBool, VMData
import libvirt_remote_manager.lrm_api as lrm_api
from libvirt_remote_manager.host_power import HostPower
import libvirt_remote_manager.utils as utils

_api: VirtAPI
debug = False

@app.route('/api/get_vms')
def get_vms():
    if debug:
        utils.debug_print_request(request.url)
    simple = request.args.get('simple', default=False, type=lambda v: v.lower() == 'true')
    try:
        vms = _api.list_vms(simple)
        return VMList(vms).toJSON()
    except Exception as err:
        return Result('failure', str(err)).toJSON()

@app.route('/api/vm/<uuid>', methods=['GET'])
def get_vm(uuid):
    if request.method == 'GET':
        if debug:
            utils.debug_print_request(request.url)
        simple = request.args.get('simple', default=False, type=lambda v: v.lower() == 'true')
        try:
            vm = _api.get_vm(uuid, simple)
            return VMData(vm).toJSON()
        except Exception as err:
            return Result('failure', str(err)).toJSON()

@app.route('/api/vm/<uuid>/start', methods=['POST'])
def start_vm(uuid):
    if request.method == 'POST':
        if debug:
            utils.debug_print_request(request.url)
        try:
            _api.start_vm(uuid)
            return Result('success', '').toJSON()
        except Exception as err:
            return Result('failure', str(err)).toJSON()

@app.route('/api/vm/<uuid>/shutdown', methods=['POST'])
def shutdown_vm(uuid):
    if request.method == 'POST':
        if debug:
            utils.debug_print_request(request.url)
        try:
            _api.shutdown_vm(uuid)
            return Result('success', '').toJSON()
        except Exception as err:
            return Result('failure', str(err)).toJSON()

@app.route('/api/vm/<uuid>/poweroff', methods=['POST'])
def poweroff_vm(uuid):
    if request.method == 'POST':
        if debug:
            utils.debug_print_request(request.url)
        try:
            _api.poweroff_vm(uuid)
            return Result('success', '').toJSON()
        except Exception as err:
            return Result('failure', str(err)).toJSON()

@app.route('/api/get_device_info')
def get_device_info():
    if debug:
        utils.debug_print_request(request.url)
    try:
        return HostInfo(lrm_api.get_lrm_name(), lrm_api.get_lrm_version(), str(lrm_api.get_hostname()), str(_api.get_libvirt_version())).toJSON()
    except Exception as err:
        return Result('failure', str(err)).toJSON()

@app.route('/api/host/shutdown', methods=['POST'])
def host_shutdown():
    if debug:
        utils.debug_print_request(request.url)
    hp = HostPower()
    done = hp.host_shutdown()
    return ResultBool(done, '').toJSON()

@app.route('/api/host/reboot', methods=['POST'])
def host_reboot():
    if debug:
        utils.debug_print_request(request.url)
    hp = HostPower()
    done = hp.host_reboot()
    return ResultBool(done, '').toJSON()

@app.route('/api/host/ping')
def ping():
    if debug:
        utils.debug_print_request(request.url)
    return "pong"