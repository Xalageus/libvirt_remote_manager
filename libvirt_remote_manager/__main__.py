import argparse, logging
from libvirt_remote_manager import __name__ as lrm_name
from waitress import serve
from libvirt_remote_manager import app
from libvirt_remote_manager.virt_api import VirtAPI

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=lrm_name)
    parser.add_argument('--pom', help='Power only mode', action='store_true')
    parser.add_argument('--port', help="Set port (doesn't affect POM)", type=int)
    parser.add_argument('--log', help="Set logging level (Debug, Info, Warning, Error, Critical)", type=str, default='INFO')
    args = parser.parse_args()

    #Setup logger
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    log_level = log_levels.get(args.log.upper())
    if log_level is None:
        raise ValueError('Invalid log level: %s' % args.log)
    logging.basicConfig(level=log_level, format='[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    if(args.pom):
        import libvirt_remote_manager.utils as utils
        if utils.check_if_root():
            import libvirt_remote_manager.pom_server
            serve(app, host="127.0.0.1", port=18965)
        else:
            logging.critical("Root is required for POM to work! Exiting...")
            exit(1)
    else:
        import libvirt_remote_manager.server
        libvirt_remote_manager.server._api = VirtAPI()
        serve(app, host="0.0.0.0", port=args.port or 18964)
