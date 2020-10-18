import argparse
import sys

from common.logger import log_level


class Args:
    def __init__(self):
        self.is_path = None
        self.value = None
        self.log_level = None
        self.log_filename = None
        self.headers = None
        self.char_mode = None
        self.if_report = False
        self.report_path = None


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list', help='Path to file with domain list', type=str)
    parser.add_argument('-d', '--domain', help='Domain', type=str)
    parser.add_argument('-v', '--verbosity', help="Logging level", type=int, choices=range(1,6), default=4)
    parser.add_argument('-f', '--file', help='Path to log file', type=str)
    parser.add_argument('-c', '--char', help='Bigger number will result in wider tests which uses special characters', type=int, choices=range(0,3), default=0)
    parser.add_argument('-r', '--report', help='Create report', action='store_true')
    parser.add_argument('-rp', '--report-path', help='Path where to create a report', type=str, default='./report/')
    args = parser.parse_args()

    cmd_args = Args()
    cmd_args.is_path = True if args.list is not None else False
    cmd_args.value = args.list if cmd_args.is_path else args.domain
    if cmd_args.value is None:
        parser.print_help()
        sys.exit(1)
    cmd_args.log_level = log_level(args.verbosity)
    cmd_args.log_filename = args.file
    cmd_args.char_mode = args.char
    cmd_args.if_report = args.report
    cmd_args.report_path = args.report_path

    return cmd_args