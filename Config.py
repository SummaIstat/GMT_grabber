import os
import sys
import logging
import logging_config

logging_config.setup_logger()
logger = logging.getLogger(__name__)
logger.debug(__name__ + ' logger initialized')


class Config:

    def __init__(self, argv):
        external_settings = Config.load_external_configuration(argv)
        try:
            self.PROGRAM_NAME = "GMT_grabber"
            self.INPUT_FILE_PATH = str(external_settings['INPUT_FILE_PATH']).strip()
            self.OUTPUT_FOLDER_PATH = str(external_settings['OUTPUT_FOLDER_PATH']).strip()
            self.MAPS_FOLDER_PATH = str(external_settings['MAPS_FOLDER_PATH']).strip()
            self.NEGATIVES_FOLDER_PATH = str(external_settings['NEGATIVES_FOLDER_PATH']).strip()
            self.LOG_FOLDER_PATH = str(external_settings['LOG_FOLDER_PATH']).strip()
            self.LOG_LEVEL = str(external_settings['LOG_LEVEL']).strip()
            self.PROXY_HOST = external_settings.get('PROXY_HOST', None)
            self.PROXY_PORT = external_settings.get('PROXY_PORT', None)
            if (self.PROXY_HOST is not None) and (self.PROXY_PORT is not None):
                self.PROXY_HOST = self.PROXY_HOST.strip()
                self.PROXY_PORT = self.PROXY_PORT.strip()
            elif (self.PROXY_HOST) or (self.PROXY_PORT):
                logger.error("Invalid proxy configuration parameters: both PROXY_HOST and PROXY_PORT must be valid or both must be commented")
                raise Exception("Invalid proxy configuration parameters")

            self.check_existence("INPUT_FILE_PATH", self.INPUT_FILE_PATH)
            self.check_existence("OUTPUT_FOLDER_PATH", self.OUTPUT_FOLDER_PATH)
            self.check_existence("MAPS_FOLDER_PATH", self.MAPS_FOLDER_PATH)
            self.check_existence("NEGATIVES_FOLDER_PATH", self.NEGATIVES_FOLDER_PATH)
            self.check_existence("LOG_FOLDER_PATH", self.LOG_FOLDER_PATH)

        except Exception as e:
            sys.exit("Missing parameters and/or Invalid parameter values in configuration file")


    def check_existence(self, var_name, var_value):
        if not os.path.exists(var_value):
            error_message = "The " + var_name + " provided in the config.cfg configuration file does not exist!"
            logger.error(error_message)
            sys.exit(error_message)

    @staticmethod
    def load_external_configuration(argv):
        if len(argv) != 1:
            sys.exit("USAGE: python GMT_grabber.py my_path/config.cfg")

        config_file_path = argv[0]
        if not os.path.exists(config_file_path):
            sys.exit("The provided configuration file " + config_file_path + " does not exist !")

        external_settings = dict()
        with open(config_file_path, "rt") as f:
            for line in f.readlines():
                if not line.startswith("#"):
                    tokens = line.split("=")
                    if len(tokens) == 2:
                        external_settings[tokens[0].strip()] = tokens[1].strip()

        return external_settings
