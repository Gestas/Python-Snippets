from Utils import Utils
import json
import logging
import configparser

utils = Utils

logger = logging.getLogger(__name__)


class INIConfiguration:
    def __init__(self, config_path, normalize=False):
        """Get or update an INI formatted configuration.

        :param config_path: Path to a INI formatted file.
        :type config_path: [Path, str]
        :param normalize: Capitalized keys are lowercased and spaces in keys are replaced with '_'.
        :type normalize: bool
        """
        self.config = {}
        _config_dict = {}
        self._config_path = Utils.expand_path(config_path)
        self.update = None
        self.normalize = normalize

    def _format_keys(self, str_):
        if not self.normalize:
            return str_
        if self.update:
            str_ = str_.upper()
            return str_.replace("_", " ")
        str_ = str_.lower()
        return str_.replace(" ", "_")

    @staticmethod
    def _format_values(v):
        if v.lower() in ["1", "yes", "true", "on"]:
            return True
        if v.lower() in ["0", "no", "false", "off"]:
            return False
        return v

    def get(self):
        """Get and return the configuration from disk as a dict
        :return: The configuration as a dict
        :rtype: dict
        """
        _config_file = None
        _parsed_config = configparser.ConfigParser()
        try:
            _config_file = open(self._config_path, "r")
        except OSError as e:
            logger.error(str(e))
            Utils.exiter(1)
        try:
            _parsed_config.read_file(_config_file)
        except configparser.ParsingError as e:
            logger.error(str(e))
            Utils.exiter(1)

        _defaults = _parsed_config.defaults()
        _t = {}
        for (_k, _v) in _defaults:
            _t[self._format_keys(_k)] = self._format_values(_v)
        self.config[self._format_keys("defaults")] = _t

        for _s in _parsed_config.sections():
            _t = {}
            for (_k, _v) in _parsed_config.items(_s):
                _t[self._format_keys(_k)] = self._format_values(_v)
            self.config[self._format_keys(_s)] = _t
        logger.debug(f"Got config: {json.dumps(self.config, indent=2)}")
        return self.config

    def update(self, update: dict):
        # TODO
        pass
