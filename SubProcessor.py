import logging
import subprocess
from Utils import Utils
logger = logging.getLogger(__name__)

utils = Utils


class SubProcessor(object):
    def __init__(self):
        pass

    @staticmethod
    def run_subprocess(command: list, **kwargs):
        result = None
        env = kwargs.get("env", {})
        timeout = kwargs.get("timeout", 30)
        ignore_error = kwargs.get("ignore_error", True)
        logger.debug(f'Running {command}.')
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=True,
                timeout=timeout,
                env=env,
            )
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out at {timeout} seconds.")
            raise subprocess.TimeoutExpired
        except subprocess.SubprocessError as err:
            logger.error(f"Subprocess error: {err}")
        if result.returncode == 0 or ignore_error:
            return result
        return False
