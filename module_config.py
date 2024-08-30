from dotenv import load_dotenv
import os


class ConfigManager:
    __instance = None
    __initialized = False

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if ConfigManager.__initialized:
            return
        load_dotenv()
        self.broker_host = os.getenv('MESSAGE_BROKER_HOST', '127.0.0.1')
        self.broker_login = os.getenv('MESSAGE_BROKER_LOGIN')
        self.broker_password = os.getenv('MESSAGE_BROKER_PASSWORD')
        self.folder_with_converted_files = os.getenv('CONVERTER_FOLDER_CONVERTED_FILES')
