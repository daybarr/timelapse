#!/usr/bin/env python
from __future__ import print_function

import argparse
import datetime
import logging
import os
import sys
import time

import pysftp

LOG_FORMAT = '%(asctime)-15s %(name)-10s %(levelname)-7s %(message)s'

# max number of files to download per sftp connection - not getting them all at
# once helps avoid lockups/hangs on the android side.
MAX_PER_CONN = 20

DEFAULT_SRC_DIR = "/mnt/sdcard/timelapse"
DEFAULT_DEST_DIR = os.path.expanduser("~/timelapse")
DEFAULT_PRIVATE_KEY = os.path.expanduser("~/.ssh/id_rsa")

LOG_FILE_NAME = 'battery.txt'

def parse_args(argv):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('ip', help="IP address of camera")
    parser.add_argument('port', type=int,
                        help="Port number of ssh server on camera")
    parser.add_argument('--username', default=os.getlogin(),
                        help="Username for ssh server")
    parser.add_argument('--password', default=None,
                        help="Password for ssh server")
    parser.add_argument('--private-key', default=DEFAULT_PRIVATE_KEY,
                        help="Private key for ssh connection")
    parser.add_argument('--dest-dir', default=DEFAULT_DEST_DIR,
                        help="Directory to download photos to")
    parser.add_argument('--src-dir', default=DEFAULT_SRC_DIR,
                        help="Directory to download photos from")
    args = parser.parse_args(argv[1:])
    if not os.path.isdir(args.dest_dir):
        parser.error("--dest-dir {} must exist".format(args.dest_dir))
    return args

def download_some(args):
    some_downloaded = False
    logger.info("Connecting")
    with pysftp.Connection(args.ip, port=args.port,
                           username=args.username,
                           password=args.password,
                           private_key=args.private_key) as sftp, \
        sftp.cd(args.src_dir):

        logger.info("Listing files")
        file_names = sftp.listdir()
        logger.info("Found %d files", len(file_names))

        images = [name for name in file_names if name.endswith('.jpg')]
        for i, file_name in enumerate(images[:MAX_PER_CONN]):
            dest_file_name = os.path.join(args.dest_dir, file_name)
            logger.info("Downloading image %d/%d: %s => %s", i+1, len(images),
                        file_name, dest_file_name)
            sftp.get(file_name, dest_file_name)
            logger.info("Removing %s", file_name)
            sftp.unlink(file_name)
            some_downloaded = True

        suffix = datetime.datetime.now().strftime('.%Y%m%d-%H%M%S')
        if LOG_FILE_NAME in file_names:
            remote_name = LOG_FILE_NAME + suffix
            dest_file_name = os.path.join(args.dest_dir, remote_name)
            logger.info("Renaming log => %s", remote_name)
            sftp.rename(LOG_FILE_NAME, remote_name)
            time.sleep(1)
            logger.info("Downloading log => %s", dest_file_name)
            sftp.get(remote_name, dest_file_name)
            logger.info("Removing %s", remote_name)
            sftp.unlink(file_name)

        # Failed logs
        logs = [name for name in file_names if name.startswith(LOG_FILE_NAME)
                and len(name) > len(LOG_FILE_NAME)]
        for i, file_name in enumerate(logs):
            dest_file_name = os.path.join(args.dest_dir, file_name)
            logger.info("Downloading %d/%d: %s => %s", i+1, len(logs),
                        file_name, dest_file_name)
            sftp.get(file_name, dest_file_name)
            logger.info("Removing %s", file_name)
            sftp.unlink(file_name)

    return some_downloaded

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    args = parse_args(sys.argv)
    while download_some(args):
        pass
