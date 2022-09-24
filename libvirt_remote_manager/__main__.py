import argparse
from libvirt_remote_manager import __name__ as lrm_name
from waitress import serve
from libvirt_remote_manager import app
from libvirt_remote_manager.virt_api import VirtAPI

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=lrm_name)
    parser.add_argument('--pom', help='Power only mode', action='store_true')
    parser.add_argument('--debug', help='Enable debug mode', action='store_true')
    args = parser.parse_args()

    if(args.pom):
        import libvirt_remote_manager.utils as utils
        if utils.check_if_root():
            import libvirt_remote_manager.pom_server
            libvirt_remote_manager.pom_server.debug = args.debug
            serve(app, host="127.0.0.1", port=18965)
        else:
            print("Root is required for POM to work! Exiting...")
            exit(1)
    else:
        import libvirt_remote_manager.server
        libvirt_remote_manager.server.debug = args.debug
        libvirt_remote_manager.server._api = VirtAPI()
        serve(app, host="0.0.0.0", port=18964)
