import os

def check_if_root() -> bool:
    if os.getuid() == 0:
        return True
    else:
        return False

def debug_print_request(req: str):
    print("[Debug] " + req)
