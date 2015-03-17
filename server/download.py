#!/usr/bin/env python
from __future__ import print_function

import argparse
import logging
import sys
import time

import pysftp

LOG_FORMAT = '%(asctime)-15s %(name)-10s %(levelname)-7s %(message)s'

# max number of files to download per sftp connection - not getting them all at
# once helps avoid lockups/hangs on the android side.
MAX_PER_CONN = 10

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('ip', help="IP address of camera")
    parser.add_argument('port', type=int,
                        help="Port number of ssh server on camera")
    parser.add_argument('username', help="Username for ssh server")
    parser.add_argument('password', help="Password for ssh server")
    return parser.parse_args(argv[1:])

def download_some(args):
    some_downloaded = False
    logger.info("Connecting")
    with pysftp.Connection(args.ip, port=args.port,
                           username=args.username,
                           password=args.password) as sftp:
        logger.info("Listing files")
        file_names = sftp.listdir()
        logger.info("Found %d files", len(file_names))
        for i, file_name in enumerate(file_names[:MAX_PER_CONN]):
            logger.info("Downloading %d/%d: %s", i+1, len(file_names), file_name)
            sftp.get(file_name)
            logger.info("Removing %s", file_name)
            sftp.unlink(file_name)
            some_downloaded = True
    return some_downloaded

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    args = parse_args(sys.argv)
    while download_some(args):
        pass