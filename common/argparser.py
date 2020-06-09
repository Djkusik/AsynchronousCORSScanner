import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list', help='Path to file with domain list', type=str)
    parser.add_argument('-d', '--domain', help='Domain', type=str)
    parser.add_argument('-v', '--verbose', help="Turn on logging", action="store_true")

    args = parser.parse_args()
    is_path = True if args.list is not None else False
    value = args.list if is_path else args.domain

    return is_path, value, args.verbose