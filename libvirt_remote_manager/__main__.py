import argparse, logging, signal, traceback, sys
from libvirt_remote_manager import __name__ as lrm_name
from libvirt_remote_manager import __version__ as lrm_version
from waitress import serve
from libvirt_remote_manager import app

def unhandled_exception(*exc_info):
    logging.critical("An unhandled exception has occurred! Stopping!\n{0}".format("".join(traceback.format_exception(*exc_info))))
    exit(1)

# Gracefull way of stopping thread with a wait
def shutdown(sig, frame):
    libvirt_remote_manager.server_objs.pairh.cleanup()
    exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=lrm_name)
    parser.add_argument('--pom', help='Power only mode', action='store_true')
    parser.add_argument('--port', help="Set port (doesn't affect POM)", type=int)
    parser.add_argument('--pair', help="Pair device", action='store_true')
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
    if log_level == logging.DEBUG:
        fmt = '[%(asctime)s] [%(levelname)s] [%(module)s] [%(threadName)s] %(message)s'
        print(lrm_name + " " + lrm_version)
    else:
        fmt = '[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s'
    logging.basicConfig(level=log_level, format=fmt, datefmt='%Y-%m-%d %H:%M:%S')

    sys.excepthook = unhandled_exception

    if(args.pom):
        import libvirt_remote_manager.utils as utils
        if utils.check_if_root():
            import libvirt_remote_manager.pom_server
            serve(app, host="127.0.0.1", port=18965)
        else:
            logging.critical("Root is required for POM to work! Exiting...")
            exit(1)
    elif(args.pair):
        pass
    else:
        from libvirt_remote_manager.virt_api import VirtAPI
        from libvirt_remote_manager.pair_host import PairHost
        import libvirt_remote_manager.server_objs
        libvirt_remote_manager.server_objs.api = VirtAPI()
        libvirt_remote_manager.server_objs.pairh = PairHost("data.db")
        import libvirt_remote_manager.server
        signal.signal(signal.SIGINT, shutdown)
        serve(app, host="0.0.0.0", port=args.port or 18964)
