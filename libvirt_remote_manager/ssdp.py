import logging, select, threading
from ssdpy import SSDPServer
from libvirt_remote_manager import lrm_api as lrm_api
import libvirt_remote_manager.utils as utils

class ThreadedSSDP(threading.Thread):
    def run(self):
        logging.debug("Starting SSDP thread")
        server = SSDPServer("uuid:" + self._host_uuid + "::ssdp:" + lrm_api.get_lrm_name(), location="http://" + utils.get_local_ip() + ":" + str(self._port) + "/", device_type="ssdp:" + lrm_api.get_lrm_name())
        server.sock.setblocking(0)

        while self._running:
            try:
                ready = select.select([server.sock], [], [], 2)
                if ready[0]:
                    data, address = server.sock.recvfrom(1024)
                    server.on_recv(data, address)
            except Exception:
                pass

        server.sock.close()

    def __init__(self, host_uuid: str, port: int):
        self._host_uuid = host_uuid
        self._port = port
        self._running = True
        super().__init__()
        self.setName("SSDPThread")

    def stop(self):
        self._running = False