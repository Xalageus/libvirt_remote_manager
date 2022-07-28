import os, psutil
from time import sleep
from threading import Thread
from libvirt_remote_manager._enums import PowerType, PowerMethod

class HostPower():
    def __init__(self):
        pass

    def _check_systemctl(self) -> bool:
        if(os.path.exists('/usr/bin/systemctl') or os.path.exists('/bin/systemctl')):
            return True
        else:
            return False

    def _check_if_local(self) -> bool:
        if not os.getenv('SSH_CLIENT') and not os.getenv('SSH_CONNECTION'):
            return True
        else:
            return False

    def _check_if_root(self) -> bool:
        if os.getuid() == 0:
            return True
        else:
            return False

    def _have_tty(self) -> bool:
        try:
            os.getlogin()
            return True
        except:
            return False

    def _check_if_only_user_logged_in(self) -> bool:
        only = True
        current = psutil.Process(os.getpid()).username()
        #current = os.getlogin()
        users = psutil.users()

        for user in users:
            if user.name != current:
                only = False

        return only

    def host_shutdown(self) -> bool:
        ptype = PowerType.shutdown
        method: PowerMethod

        if self._check_if_root():
            if self._check_systemctl():
                method = PowerMethod.systemd
            else:
                method = PowerMethod.classic

            ThreadedHostPower(ptype, method)
            return True
        else:
            if self._check_if_local() and self._check_if_only_user_logged_in() and self._have_tty():
                if self._check_systemctl():
                    method = PowerMethod.systemd
                else:
                    method = PowerMethod.classic

                ThreadedHostPower(ptype, method)
                return True
            else:
                return False

    def host_reboot(self) -> bool:
        ptype = PowerType.reboot
        method: PowerMethod

        if self._check_if_root():
            if self._check_systemctl():
                method = PowerMethod.systemd
            else:
                method = PowerMethod.classic

            ThreadedHostPower(ptype, method)
            return True
        else:
            if self._check_if_local() and self._check_if_only_user_logged_in() and self._have_tty():
                if self._check_systemctl():
                    method = PowerMethod.systemd
                else:
                    method = PowerMethod.classic

                ThreadedHostPower(ptype, method)
                return True
            else:
                return False

class ThreadedHostPower:
    _WAITTIME = 5

    def _shutdown_systemctl(self):
        os.system("systemctl poweroff")

    def _shutdown_shutdown(self):
        os.system("shutdown -h now")

    def _reboot_systemctl(self):
        os.system("systemctl reboot")

    def _reboot_shutdown(self):
        os.system("shutdown -r now")

    def _choose(self, ptype: PowerType, method: PowerMethod):
        sleep(self._WAITTIME)

        if ptype == PowerType.shutdown:
            if method == PowerMethod.classic:
                self._shutdown_shutdown()
            elif method == PowerMethod.systemd:
                self._shutdown_systemctl()
        elif ptype == PowerType.reboot:
            if method == PowerMethod.classic:
                self._reboot_shutdown()
            elif method == PowerMethod.systemd:
                self._reboot_systemctl()

    def __init__(self, ptype: PowerType, method: PowerMethod):
        self._t = Thread(target=self._choose, args=(ptype, method))
        self._t.start()
