import logging
from libvirt_remote_manager import app
from flask import request, abort
import libvirt_remote_manager._response_data as responses
import libvirt_remote_manager.lrm_api as lrm_api
from libvirt_remote_manager.host_power import HostPower
import libvirt_remote_manager._exceptions as ex
import libvirt_remote_manager.utils as utils
import libvirt_remote_manager.server_utils as s_utils
from libvirt_remote_manager.server_dec import debug_log_url, pair_required, trusted_or_localhost_required, trusted_required
from libvirt_remote_manager.server_objs import api, pairh

@app.route('/api/get_vms')
@debug_log_url
@pair_required
def get_vms():
    try:
        simple = request.args.get('simple', default=False, type=lambda v: v.lower() == 'true')
        vms = api.list_vms(simple)
        return responses.VMList(vms).toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()

@app.route('/api/vm/<uuid>')
@debug_log_url
@pair_required
def get_vm(uuid):
    try:
        simple = request.args.get('simple', default=False, type=lambda v: v.lower() == 'true')
        vm = api.get_vm(uuid, simple)
        return responses.VMData(vm).toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()

@app.route('/api/vm/<uuid>/start', methods=['POST'])
@debug_log_url
@pair_required
def start_vm(uuid):
    try:
        api.start_vm(uuid)
        return responses.Result('success', '').toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()

@app.route('/api/vm/<uuid>/shutdown', methods=['POST'])
@debug_log_url
@pair_required
def shutdown_vm(uuid):
    try:
        api.shutdown_vm(uuid)
        return responses.Result('success', '').toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()

@app.route('/api/vm/<uuid>/poweroff', methods=['POST'])
@debug_log_url
@pair_required
def poweroff_vm(uuid):
    try:
        api.poweroff_vm(uuid)
        return responses.Result('success', '').toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()

@app.route('/api/vm/<uuid>/resume', methods=['POST'])
@debug_log_url
@pair_required
def resume_vm(uuid):
    try:
        api.resume_vm(uuid)
        return responses.Result('success', '').toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()

@app.route('/api/vm/<uuid>/pause', methods=['POST'])
@debug_log_url
@pair_required
def pause_vm(uuid):
    try:
        api.pause_vm(uuid)
        return responses.Result('success', '').toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()

@app.route('/api/get_host_info')
@debug_log_url
def get_host_info():
    try:
        return responses.HostInfo(lrm_api.get_lrm_name(), lrm_api.get_lrm_version(), lrm_api.get_hostname(), api.get_libvirt_version(), api.get_hypervisor_version(), str(pairh.get_host_uuid())).toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()

@app.route('/api/host/shutdown', methods=['POST'])
@debug_log_url
@pair_required
def host_shutdown():
    try:
        hp = HostPower()
        done = hp.host_shutdown()
        return responses.ResultBool(done, '').toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()

@app.route('/api/host/reboot', methods=['POST'])
@debug_log_url
@pair_required
def host_reboot():
    try:
        hp = HostPower()
        done = hp.host_reboot()
        return responses.ResultBool(done, '').toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()

@app.route('/api/host/ping')
@debug_log_url
def ping():
    return "pong"

@app.route('/api/pair/start')
@debug_log_url
@trusted_or_localhost_required
def pair_start():
    try:
        pair_time = request.args.get('pair_time')
        logging.info("Starting pair using " + request.remote_addr)
        if(pair_time):
            return responses.PairInfo(pair_key=pairh.start_pair(pair_time)).toJSON()
        else:
            return responses.PairInfo(pair_key=pairh.start_pair()).toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()

@app.route('/api/pair/pair', methods=['POST'])
@debug_log_url
def pair():
    try:
        device_name = request.args.get('device_name')
        device_uuid = request.args.get('device_uuid')
        pin = request.args.get('pin', type=str)
        logging.info("Pair attempt from " + request.remote_addr + " (" + device_uuid + ")")
        device_key = pairh.pair_attempt(device_name, device_uuid, pin)
        return responses.PairSuccessInfo(device_uuid, device_key, str(pairh.get_host_uuid())).toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()
    
@app.route('/api/pair/unpair', methods=['POST'])
@debug_log_url
@pair_required
def unpair():
    try:
        device_uuid, _ = s_utils.get_device_creds(request)
        device_name = pairh.get_device(str(device_uuid)).device_name
        logging.info("Unpairing " + device_name + " (" + str(device_uuid) + ")")
        pairh.unpair(str(device_uuid))
        return responses.Result('success', '').toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()

@app.route('/api/pair/unpair_device', methods=['POST'])
@debug_log_url
@trusted_or_localhost_required
def unpair_device():
    try:
        unpairing_device_uuid = request.args.get('device_uuid')
        logging.info("Unpairing " + unpairing_device_uuid)
        pairh.unpair(unpairing_device_uuid)
        return responses.Result('success', '').toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()

@app.route('/api/pair/check')
@debug_log_url
@trusted_or_localhost_required
def pair_check():
    try:
        pair_key = request.args.get('pair_key', type=str)
        return responses.PairInfo(pair_key, pairh.check_pair(pair_key)).toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()

@app.route('/api/pair/trust_device', methods=['POST'])
@debug_log_url
@trusted_or_localhost_required
def pair_trust_device():
    try:
        device_uuid = request.args.get('device_uuid')
        logging.warning("Trusting device " + device_uuid)
        pairh.trust_device(device_uuid)
        return responses.Result('success', '').toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()

@app.route('/api/pair/untrust', methods=['POST'])
@debug_log_url
@trusted_required
def pair_untrust():
    try:
        device_uuid, _ = s_utils.get_device_creds(request)
        logging.warning("Untrusting device " + device_uuid)
        pairh.untrust_device(device_uuid)
        return responses.Result('success', '').toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()
    
@app.route('/api/pair/untrust_device', methods=['POST'])
@debug_log_url
@trusted_or_localhost_required
def pair_untrust_device():
    try:
        device_uuid = request.args.get('device_uuid')
        logging.warning("Untrusting device " + device_uuid)
        pairh.untrust_device(device_uuid)
        return responses.Result('success', '').toJSON()
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()

@app.route('/api/pair/get_devices')
@debug_log_url
@trusted_or_localhost_required
def pair_get_devices():
    try:
        return responses.DeviceList(pairh.get_devices())
    except Exception as err:
        return responses.Result('failure', str(err)).toJSON()
