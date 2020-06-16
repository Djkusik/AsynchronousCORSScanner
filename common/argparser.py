import argparse

from common.logger import log_level


class Args:
    def __init__(self):
        self.is_path = None
        self.value = None
        self.log_level = None
        self.log_filename = None


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list', help='Path to file with domain list', type=str)
    parser.add_argument('-d', '--domain', help='Domain', type=str)
    parser.add_argument('-v', '--verbosity', help="Logging level", type=int, choices=range(1,6), default=4)
    parser.add_argument('-f', '--file', help='Path to log file', type=str)
    args = parser.parse_args()

    cmd_args = Args()
    cmd_args.is_path = True if args.list is not None else False
    cmd_args.value = args.list if cmd_args.is_path else args.domain
    cmd_args.log_level = log_level(args.verbosity)
    cmd_args.log_filename = args.file

    return cmd_args