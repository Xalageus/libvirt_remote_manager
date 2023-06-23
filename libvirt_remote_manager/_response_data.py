from flask import jsonify
from flask.wrappers import Response
from typing import List
import libvirt_remote_manager._vm_md as vm_md
import libvirt_remote_manager._enums as enums
import libvirt_remote_manager._db_types as db_types

class JSONResponse():
    def __init__(self):
        self.data = {}

    def toJSON(self) -> Response:
        return jsonify(self.data)

class VMData(JSONResponse):
    def __init__(self, vm: vm_md.VMMetadata):
        super().__init__()
        self.vm = vm

        state = enums.VMState(vm.state)
        shutoff_reason = enums.VMShutoffReason(vm.shutoff_reason)
        self.data = {
            'name': vm.name,
            'state': state.name,
            'shutoff_reason': shutoff_reason.name,
            'uuid': vm.uuid,
            'raw': {
                'state': vm.state,
                'shutoff_reason': vm.shutoff_reason
            }
        }

        if hasattr(vm, 'os_names'):
            self.data['os_names'] = {
                'name': vm.os_names.name,
                'long_id': vm.os_names.long_id,
                'short_id': vm.os_names.short_id,
                'family': vm.os_names.family,
                'distro': vm.os_names.distro
            }

class VMList(JSONResponse):
    def __init__(self, vm_list: List[vm_md.VMMetadata]):
        super().__init__()
        self.vm_list = vm_list

        self.data = []

        for vm in self.vm_list:
            self.data.append(VMData(vm).data)

class Result(JSONResponse):
    def __init__(self, status: str, message: str):
        super().__init__()
        self.status = status
        self.message = message

        self.data = {
            'status': self.status,
            'msg': self.message
        }

class ResultBool(JSONResponse):
    def __init__(self, status: bool, message: str):
        super().__init__()
        self.status = status
        self.message = message

        self.data = {
            'status': self.status,
            'msg': self.message
        }

class HostInfo(JSONResponse):
    def __init__(self, lrm_name: str, lrm_version: str, hostname: str, libvirt_version: str, hypervisor_version: str, host_uuid: str):
        super().__init__()
        self.lrm_name = lrm_name
        self.lrm_version = lrm_version
        self.hostname = hostname
        self.libvirt_version = libvirt_version
        self.hypervisor_version = hypervisor_version
        self.host_uuid = host_uuid

        self.data = {
            'lrm_name': self.lrm_name,
            'lrm_version': self.lrm_version,
            'hostname': self.hostname,
            'libvirt_version': self.libvirt_version,
            'hypervisor_version': self.hypervisor_version,
            'host_uuid': self.host_uuid
        }

class PairInfo(JSONResponse):
    def __init__(self, pair_key: str, pair_time: int, status: enums.PairKeyStatus = enums.PairKeyStatus.not_paired):
        super().__init__()
        self.pair_key = pair_key
        self.pair_time = pair_time
        self.status = status

        self.data = {
            'pair_key': self.pair_key,
            'pair_time': self.pair_time,
            'status': self.status.value
        }

class PairSuccessInfo(JSONResponse):
    def __init__(self, device_uuid: str, device_key: str, host_uuid: str):
        super().__init__()
        self.device_uuid = device_uuid
        self.device_key = device_key
        self.host_uuid = host_uuid

        self.data = {
            'device_uuid': self.device_uuid,
            'device_key': self.device_key,
            'host_uuid': self.host_uuid
        }

class DeviceData(JSONResponse):
    def __init__(self, device: db_types.Device):
        super().__init__()
        self.device = device

        self.data = {
            'device_uuid': self.device.device_uuid,
            'trusted': self.device.trusted
        }

class DeviceList(JSONResponse):
    def __init__(self, devices: List[db_types.Device]):
        super().__init__()
        self.devices = devices

        self.data = []

        for device in self.devices:
            self.data.append(DeviceData(device).data)
