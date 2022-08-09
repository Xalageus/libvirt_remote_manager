from flask import jsonify
from flask.wrappers import Response
from typing import List
import libvirt_remote_manager._vm_md as vm_md
import libvirt_remote_manager._enums as enums

class VMList():
    def __init__(self, vm_list: List[vm_md.VMMetadata]):
        self.vm_list = vm_list

    def toJSON(self) -> Response:
        data = []

        for vm in self.vm_list:
            state = enums.VMState(vm.state)
            shutoff_reason = enums.VMShutoffReason(vm.shutoff_reason)

            vm_data = {
                'name': vm.name,
                'state': state.name,
                'shutoff_reason': shutoff_reason.name,
                'uuid': vm.uuid,
                'raw': {
                    'state': vm.state,
                    'shutoff_reason': vm.shutoff_reason
                },
                'os_names': {
                    'name': vm.os_names.name,
                    'long_id': vm.os_names.long_id,
                    'short_id': vm.os_names.short_id,
                    'family': vm.os_names.family,
                    'distro': vm.os_names.distro
                }
            }

            data.append(vm_data)

        return jsonify(data)

class Result():
    def __init__(self, status: str, message: str):
        self.status = status
        self.message = message

    def toJSON(self) -> Response:
        data = {
            'status': self.status,
            'msg': self.message
        }

        return jsonify(data)

class ResultBool():
    def __init__(self, status: bool, message: str):
        self.status = status
        self.message = message

    def toJSON(self) -> Response:
        data = {
            'status': self.status,
            'msg': self.message
        }

        return jsonify(data)

class HostInfo():
    def __init__(self, lrm_name: str, lrm_version: str, hostname: str, libvirt_version: str):
        self.lrm_name = lrm_name
        self.lrm_version = lrm_version
        self.hostname = hostname
        self.libvirt_version = libvirt_version

    def toJSON(self) -> Response:
        data = {
            'lrm_name': self.lrm_name,
            'lrm_version': self.lrm_version,
            'hostname': self.hostname,
            'libvirt_version': self.libvirt_version
        }

        return jsonify(data)
