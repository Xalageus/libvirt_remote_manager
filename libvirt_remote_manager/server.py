from libvirt_remote_manager import app
from flask import request, abort
from libvirt_remote_manager.virt_api import VirtAPI
from libvirt_remote_manager._response_data import VMList, Result

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
