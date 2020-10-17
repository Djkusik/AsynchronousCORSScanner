import logging
import json

from datetime import datetime


class Statistics:
    data = {
        'excepted': [],
        'redirected': [],
        'status_400': [],
        'worked': [],
        'mirrored_vuln': [],
        'credentials_vuln': []
    }

    def print_results(self):
        logging.info("\n--------------------------------------------")
        logging.info("Exception during connection:")
        logging.info(len(self.data['excepted']))
        logging.info("400 returned:")
        logging.info(len(self.data['status_400']))
        logging.info("Redirected to another domain:")
        logging.info(len(self.data['redirected']))
        logging.info("Working examples:")
        logging.info(len(self.data['worked']))
        logging.info("Mirrored origins:")
        logging.info(len(self.data['mirrored_vuln']))
        logging.info("Vulnerable examples:")
        logging.info(len(self.data['credentials_vuln']))
        logging.info("--------------------------------------------")

    def save_json(self):
        filename = self.get_filename()
        with open(filename, 'w+') as json_file:
            json.dump(self.data, json_file)

    def get_filename(self):
        now = datetime.now()
        return now.strftime('%Y%m%d_%H%M%S_cors.json')