#!/usr/bin/env python
from __future__ import print_function

import argparse
import logging
import os
import sys

import sh

LOG_FORMAT = '%(asctime)-14s %(name)-10s %(levelname)-7s %(message)s'

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--src-dir', default='.',
                        help="Directory to load photos from")
    args = parser.parse_args(argv[1:])
    if not os.path.isdir(args.src_dir):
        parser.error("--src-dir {} must exist".format(args.src_dir))
    return args

def make_vid(args):
    # ffmpeg -f image2 -framerate 25 -r 30
    # -pattern_type glob -i '*.jpg' -s 720x540 movie.mp4
    ffmpeg = sh.Command('/usr/bin/ffmpeg')
    ffmpeg(
        '-f', 'image2',
        '-framerate', 25,
        '-r', 30,
        '-pattern_type', 'glob',
        '-i', os.path.join(args.src_dir, '*.jpg'),
        '-s', '720x540',
        'movie.mp4',
        _out=sys.stdout,
        _err=sys.stderr,
#        _piped='err',
    )

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    args = parse_args(sys.argv)
    make_vid(args)
