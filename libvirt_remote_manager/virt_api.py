import libvirt, re
import libvirt_remote_manager._vm_md as vm_md
from typing import List
import xml.etree.ElementTree as ET

import gi
gi.require_version('Libosinfo', '1.0')
from gi.repository import Libosinfo

class VirtAPI():
    def __init__(self):
        pass

    def _open(self) -> libvirt.virConnect:
        return libvirt.open(None)

    def _open_read_only(self) -> libvirt.virConnect:
        return libvirt.openReadOnly(None)

    def _find_element_with_regex(self, element: ET.Element, tag_name: str) -> ET.Element | None:
        for el in list(element.iter()):
            if re.match("{.+}" + tag_name, el.tag):
                return el
        
        return None

    def _get_os_names_from_id(self, id: str) -> vm_md.OSNames:
        loader = Libosinfo.Loader()
        loader.process_default_path()
        osdb = loader.get_db()

        os = osdb.get_os(id)
        return vm_md.OSNames(os.get_name(), id, os.get_short_id(), os.get_family(), os.get_distro())

    def _get_os_from_xml(self, xml: str) -> vm_md.OSNames:
        root = ET.fromstring(xml)
        
        metadata = root.find("metadata")
        if metadata != None:
            os_el = self._find_element_with_regex(metadata, "os")
            if os_el != None:
                return self._get_os_names_from_id(os_el.get("id"))

        return vm_md.OSNames("Generic OS", "generic", "generic", "generic", "generic")

    def list_vms(self, simple: bool) -> List[vm_md.VMMetadata]:
        conn = self._open_read_only()
        domains = conn.listAllDomains()
        vms = []
        for domain in domains:
            state = domain.state()
            if simple:
                vms.append(vm_md.VMMetadata(domain.name(), state[0], state[1], domain.UUIDString()))
            else:
                vms.append(vm_md.VMMetadata(domain.name(), state[0], state[1], domain.UUIDString(), self._get_os_from_xml(domain.XMLDesc())))

        conn.close()
        return vms

    def get_vm(self, vm_uuid: str, simple: bool) -> vm_md.VMMetadata:
        conn = self._open_read_only()
        domain = conn.lookupByUUIDString(vm_uuid)
        state = domain.state()
        if simple:
            return vm_md.VMMetadata(domain.name(), state[0], state[1], domain.UUIDString())
        else:
            return vm_md.VMMetadata(domain.name(), state[0], state[1], domain.UUIDString(), self._get_os_from_xml(domain.XMLDesc()))

    def start_vm(self, vm_uuid: str):
        conn = self._open()
        domain = conn.lookupByUUIDString(vm_uuid)
        domain.create()
        conn.close()

    def shutdown_vm(self, vm_uuid: str):
        conn = self._open()
        domain = conn.lookupByUUIDString(vm_uuid)
        domain.shutdown()
        conn.close()

    def poweroff_vm(self, vm_uuid: str):
        conn = self._open()
        domain = conn.lookupByUUIDString(vm_uuid)
        domain.destroy()
        conn.close()

    def get_libvirt_version(self):
        conn = self._open_read_only()
        ver = conn.getLibVersion()
        conn.close()

        maj_ver = int(ver / 1000000)
        min_ver = int((ver - (maj_ver * 1000000)) / 1000)
        rel_ver = int((ver - (maj_ver * 1000000)) - (min_ver * 1000))

        return str(maj_ver) + "." + str(min_ver) + "." + str(rel_ver)
