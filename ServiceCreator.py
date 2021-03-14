# Service creators for SystemD, macOS, Windows
import logging
from pathlib import Path
from Utils import Utils
from SubProcessor import SubProcessor

logger = logging.getLogger(__name__)

utils = Utils
subprocessor = SubProcessor()


class SystemD(object):
    def __init__(self, service_mode, service_name, description, executable_path, wanted_by, documentation=""):
        self.service_mode = service_mode
        self.service_name = service_name
        self.description = description
        self.documentation = documentation
        self.executable_path = str(executable_path)
        self.wanted_by = wanted_by
        self.service_path = Path("/etc/systemd/system/")
        self.service_path = self.service_path.joinpath(self.service_name)
        self.reload_daemon = "systemctl daemon-reload"

    def disable(self):
        """ Disable the service if it exists """
        logger.debug(f"Disabling {self.service_name}")
        _disable = "systemctl disable " + self.service_name
        if subprocessor.run_subprocess([_disable]):
            logger.info(f"{self.service_name} disabled.")
            return True
        logger.warning(f"Unable to disable {self.service_name}.")
        return False

    def remove(self):
        """ Delete the service if it exists """
        logger.debug(f"Removing existing {self.service_name} service.")
        _reset_failed = "systemctl reset-failed"
        _stop = "systemctl stop " + self.service_name

        self.disable()
        subprocessor.run_subprocess([_stop])
        self.service_path.unlink(missing_ok=True)
        lib_systemd = Path("/usr/lib/systemd/system/")
        lib_systemd = lib_systemd.joinpath(self.service_name)
        lib_systemd.unlink(missing_ok=True)
        subprocessor.run_subprocess([self.reload_daemon, _reset_failed])
        logger.info("Automatic start disabled")

    def _check_service(self):
        """ Return true if the service is active """
        _is_active = "systemctl is-active " + self.service_name
        status = subprocessor.run_subprocess([_is_active])
        return status == "active"

    def _make_systemd_service_file(self):
        service = (
            f"[Unit]\n"
            f"Description={self.description}\n"
            f"Documentation={self.documentation}\n"
            f"StartLimitIntervalSec=0\n"
            f"\n"
            f"[Service]\n"
            f"Type=simple\n"
            f"Restart=always\n"
            f"RestartSec=2\n"
            f"User=root\n"
            f"ExecStart={self.executable_path}\n"
            f"\n"
            f"[Install]\n"
            f"WantedBy={self.wanted_by}"
        )
        logger.debug(f"Creating service file {self.service_path}")
        try:
            with open(self.service_path, "w") as f:
                f.write(service)
        except OSError as err:
            logger.error(f'Error creating service file; {self.service_path}' 
                         f'ERROR: {str(err)}')

    def create(self) -> bool:
        """ Create a systemd service """
        _start = "systemctl start " + self.service_name
        _enable = "systemctl enable " + self.service_name
        _chmod = "chmod " + str(self.service_mode) + " " + str(self.service_path)
        _exists = "systemctl list-unit-files | grep " + self.service_name
        _service = subprocessor.run_subprocess([_exists])
        if _service:
            self.remove()
        self._make_systemd_service_file()
        # Activate the service
        subprocessor.run_subprocess([_chmod, self.reload_daemon, _enable, _start])
        if self._check_service():
            logger.info(f"Automatic start enabled, {self.service_name} is running.")
            return True
        else:
            logger.error(
                f"Service failed to start. Check `systemctl status {self.service_name}` for details.")
            return False


class LaunchD(object):
    """ Create a MacOS service """

    def __init__(self, service_name, executable_path):
        self._service_name = service_name
        self._executable_path = executable_path
        self._service_path = Path("/System/Library/LaunchDaemons")
        self._service_path = Path(self._service_path.joinpath(self._service_name))
        self._service_path = Path(self._service_path.joinpath(".plist"))

    def _is_active(self):
        """ Return true if the service is active """
        _is_active = "launchctl list | grep " + self._service_name
        _status = subprocessor.run_subprocess([_is_active])
        return bool(_status)

    def _make_plist_file(self):
        _plist = (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
            f'<plist version="1.0">\n'
            f"  <dict>\n"
            f"    <key>EnvironmentVariables</key>\n"
            f"    <dict>\n"
            f"      <key>PATH</key>\n"
            f"<string>/usr/local/opt/icu4c/sbin:/usr/local/opt/icu4c/bin:/usr/local/sbin:/usr/local/bin:/usr/bin:/bin"
            f":/usr/sbin:/sbin:/Users/admin/go/bin\n "
            f"      </string>\n"
            f"    </dict>\n"
            f"    <key>Label</key>\n"
            f"      <string>{self._service_name}</string>\n"
            f"    <key>Program</key>\n"
            f"      <string>{self._executable_path}</string>\n"
            f"    <key>ProgramArguments</key>\n"
            f"      <string>monitor</string>\n"
            f"    <key>RunAtLoad</key>\n"
            f"      <true/>\n"
            f"    <key>KeepAlive</key>\n"
            f"      <false/>\n"
            f"    <key>LaunchOnlyOnce</key>\n"
            f"      <true/>\n"
            f"  </dict>\n"
            f"</plist>"
        )

        logger.debug(f"Creating plist file {self._service_path}")
        with open(self._service_path, "w") as f:
            f.write(_plist)

    def disable(self):
        """ Disable the service without changing its current state """
        if self._is_active():
            _disable = "launchctl load -w " + self._service_path
            subprocessor.run_subprocess([_disable])
            logging.info(
                f"Automatic start disabled, {self._service_name} is still running.")
        else:
            _disable = "launchctl unload -w " + self._service_path
            subprocessor.run_subprocess([_disable])
            logging.info(
                f"Automatic start disabled, {self._service_name} is not running.")

    def remove(self):
        if self._service_path.is_file():
            _unload = "launchctl unload " + self._service_path
            _remove = "launchctl remove" + self._service_name
            subprocessor.run_subprocess([_unload, _remove])
            self._service_path.unlink(missing_ok=True)
            logger.info(f"{self._service_name} removed.")
            return True

    def create(self):
        """ Create a LaunchD service"""
        _load = "launchctl load " + self._service_path
        _start = "launchctl start " + self._service_name
        # Delete the service if it exists
        if self._service_path.is_file():
            self.remove()
        self._make_plist_file()
        subprocessor.run_subprocess([_load, _start])
        # Check to make sure it's running
        if self._is_active():
            logger.info("Automatic start enabled, %s is running.", self._service_name)
            return True
        else:
            logger.error("%s failed to start.", self._service_name)
            return False


class WindowsService(object):
    def __init__(self, service_name, description, executable_path):
        self.service_name = service_name
        self.description = description
        self.executable_path = str(executable_path)
        self.service_path = Path("/etc/systemd/system/")
        self.service_path = self.service_path.joinpath(self.service_name)

    def _make_service(self):
        """ Create a Windows service"""
        _service = (
            f"$credentials = new-object -typename System.Management.Automation.PSCredential "
            f'-argumentlist "NT AUTHORITY\\LOCAL SYSTEM"\n'
            f'New-Service -Name "{self.service_name}" -BinaryPathName "{self.executable_path} monitor" '
            f'-DisplayName "{self.service_name}" -Description "{self.description}" '
            f'-Credential $credentials -StartupType "Automatic"'
        )
        subprocessor.run_subprocess([_service])

    def _is_running(self):
        # TODO
        return True

    def remove(self):
        # TODO
        return True

    def create(self):
        self._make_service()
        if self._is_running():
            logger.info(f"Automatic start enabled, {self.service_name} is running.")
            return True
        else:
            logger.error(f"{self.service_name} failed to start.")
            return False
