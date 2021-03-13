"""A generally generic set of utilities."""
import logging
import math
import os
import sys
from pathlib import Path
from typing import Union
from logging import handlers

from DateTimeFormatter import DateTimeFormatter

dtf = DateTimeFormatter()

logger = logging.getLogger(__name__)


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def setup_logging(loglevel, logs_dir, log_filename, log_retention, console_loglevel=None):
        """Setup the logger. Uses f-string formatting for log messages.
        :param loglevel: Level for the logger
        :type loglevel: int, str
        :param logs_dir: Directory to store the logs in
        :type logs_dir: str, Path
        :param log_filename: filename for log
        :type log_filename: str
        :param log_retention: Number of old logs to retain
        :type log_retention: int
        :param console_loglevel: Optional console loglevel
        :type console_loglevel: int, str
        """

        logger = logging.getLogger()
        logger.setLevel(loglevel)

        logs_dir = Path(logs_dir)
        logs_dir = logs_dir.expanduser()
        logs_dir.mkdir(exist_ok=True)

        log_path = logs_dir.joinpath(log_filename)
        # Logs are rotated whenever the app is restarted
        rollover_required = log_path.exists()
        # file_formatter = logging.Formatter("{asctime}: {message}", style="{")
        file_formatter = logging.Formatter("{dtf.r3339}: {message}", style="{")
        file = logging.handlers.RotatingFileHandler(filename=log_path, backupCount=log_retention)
        file.setFormatter(file_formatter)
        logger.addHandler(file)
        if rollover_required:
            logger.critical(f'\n--------- Log closed {dtf.r3339} ---------')
            file.doRollover()
        logger.critical(f'--------- Log started {dtf.r3339} ---------')

        # Logs are output to console only if a console loglevel is supplied.
        if console_loglevel:
            console_formatter = logging.Formatter("{levelname}: {message}", style="{")
            console = logging.StreamHandler()
            console.setFormatter(console_formatter)
            console.setLevel(console_loglevel)
            logger.addHandler(console)

    @staticmethod
    def expand_path(path: Union[Path, str]) -> Path:
        """User and variable expansion for paths.

        :param path: A Path or path-like string
        :type path: Path, str
        :return: A path
        :rtype: Path
        """
        return Path(os.path.expandvars(Path(path).expanduser()))

    @staticmethod
    def format_bytes(bytes_: int) -> str:
        """Format bytes into a pretty string.

        :param bytes_: bytes
        :type bytes_: int
        :return: A pretty string
        :rtype: str
        """
        if bytes_ is None:
            return "N/A"
        if isinstance(bytes_, str):
            _bytes = float(bytes_)
        exponent = 0 if bytes_ == 0.0 else int(math.log(bytes_, 1024.0))
        suffix = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"][exponent]
        converted = float(bytes_) / float(1024 ** exponent)
        return f"{converted:.2f}{suffix}"

    @staticmethod
    def exiter(level, message=None, **kwargs):
        """Cleanup and exit the application.

        :param level: Exit code
        :type level: int
        :param message: Exit message
        :type message: str
        """
        # Insert cleanup tasks here
        if level != 0 and message:
            logger.error(f"{message}")
        elif message:
            logger.debug(f"{message}")
        sys.exit(level)

    @staticmethod
    def image_format_converter(
            source_path: [str, Path],
            target_format: [str],
            destination_path=None,
            delete_original=False,
    ):
        """Creates a new image of the requested format. Optionally deletes the original.

        :param source_path: Source file
        :param target_format: Target format. Must be supported by Pillow.
        :param destination_path: Optional destination path.
        :param delete_original: Delete the original if conversion succeeds.
        """
        from PIL import Image

        if not destination_path:
            _destination_path = source_path.with_suffix("." + target_format)
        else:
            _destination_path = Path(destination_path).expanduser()
        try:
            _file = open(_destination_path, "w")
        except OSError as e:
            logger.error(
                f"Unable to create thumbnail file {str(_destination_path)}, {str(e)}."
            )
            return
        try:
            _image = Image.open(source_path).convert("RGB")
            _image.save(_file, target_format)
        except Exception as e:
            raise e
        if delete_original:
            source_path.unlink()

    def signal_handler(self, sig, frame, **kwargs):
        """Catch signals.

        :param sig: A signal
        :type sig: Signal
        :param frame:
        :type frame:
        :param kwargs:
        :type kwargs:
        """
        # Put this somewhere at the start of your program ->
        # signal.signal(signal.SIGINT, utils.signal_handler)
        _ = frame
        self.exiter(1, message=f"Caught Signal: {sig}", **kwargs)
