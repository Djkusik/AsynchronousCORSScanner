import json
import os

from datetime import datetime
from common.logger import get_logger


class Statistics:

    data = {
        'excepted': [],
        'redirected': [],
        'status_400': [],
        'worked': [],
        'mirrored_vuln': [],
        'credentials_vuln': []
    }

    def __init__(self, save_path='./report/'):
        self.save_path = save_path
        if not os.path.isdir(self.save_path):
            os.mkdir(self.save_path)

        self.logger = get_logger()

    def print_results(self):
        self.logger.info("\n--------------------------------------------")
        self.logger.info("Exception during connection:")
        self.logger.info(len(self.data['excepted']))
        self.logger.info("400 returned:")
        self.logger.info(len(self.data['status_400']))
        self.logger.info("Redirected to another domain:")
        self.logger.info(len(self.data['redirected']))
        self.logger.info("Working examples:")
        self.logger.info(len(self.data['worked']))
        self.logger.info("Mirrored origins:")
        self.logger.info(len(self.data['mirrored_vuln']))
        self.logger.info("Vulnerable examples:")
        self.logger.info(len(self.data['credentials_vuln']))
        self.logger.info("--------------------------------------------")

    def save_json(self):
        filename = self.get_fullpath()
        with open(filename, 'w+') as json_file:
            json.dump(self.data, json_file)

    def get_fullpath(self):
        now = datetime.now()
        today_folder = self.get_today_folder(now)
        return f"{today_folder}/{now.strftime('%H%M%S_cors.json')}"

    def get_today_folder(self, now):
        today_folder = f"{self.save_path}/{now.strftime('%Y%m%d')}"
        if not os.path.isdir(today_folder):
            os.mkdir(today_folder)
        return today_folder