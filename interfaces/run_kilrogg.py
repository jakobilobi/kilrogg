#! /usr/bin/env python3

import argparse
import sys

from ModelInterface import ModelInterface

def main(argv):
    arg_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, prog='kilrogg')
    arg_parser.description = 'Performs a cutout operation on the input image'
    arg_parser.add_argument('filepath', nargs='+', help="Filepath for input image", metavar='input')
    args = arg_parser.parse_args(argv)

    model = ModelInterface()
    saved_files = model.run_inference(args.filepath)
    print("Inference successful, files saved to:")
    for f in saved_files:
        print(f)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
