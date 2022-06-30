from waitress import serve
from libvirt_remote_manager import app
from libvirt_remote_manager.virt_api import VirtAPI

if __name__ == "__main__":
    import libvirt_remote_manager.server
    libvirt_remote_manager.server._api = VirtAPI()
    serve(app, host="0.0.0.0", port=18964)