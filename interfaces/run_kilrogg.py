#! /usr/bin/env python3

import argparse
import sys

from ModelInterface import ModelInterface

def main(argv):
    arg_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, prog='kilrogg')
    arg_parser.description = 'Performs a cutout operation on the input image'
    arg_parser.add_argument('path', nargs='+', help="Path for input images or directory", metavar='input')
    args = arg_parser.parse_args(argv)

    print("Input paths:")
    for f in args.path:
        print(f)

    model = ModelInterface()
    saved_files = model.run_inference(args.path)
    print("Inference successful, files saved to:")
    for f in saved_files:
        print(f)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
