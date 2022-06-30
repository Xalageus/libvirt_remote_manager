from flask import jsonify
from flask.wrappers import Response
from typing import List
import libvirt_remote_manager._vm_md as vm_md

class VMList():
    def __init__(self, vm_list: List[vm_md.VMMetadata]):
        self.vm_list = vm_list

    def toJSON(self) -> Response:
        data = []

        for vm in self.vm_list:
            state = vm_md.VMState(vm.state)
            shutoff_reason = vm_md.VMShutoffReason(vm.shutoff_reason)

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
