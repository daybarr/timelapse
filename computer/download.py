#!/usr/bin/env python
from __future__ import print_function

import argparse
import datetime
import errno
import logging
import os
import re
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

PHOTO_RE = re.compile(
    r'^timelapse.(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)-(?P<hour>\d\d)-(?P<minute>\d\d)-(?P<second>\d\d).jpg$'
)

LOG_FILE_NAME = 'battery.txt'

def getlogin():
    try:
        login = os.getlogin()
    except OSError:
        login = os.environ.get('USER', 'day')
    return login

def parse_args(argv):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('ip', help="IP address of camera")
    parser.add_argument('port', type=int,
                        help="Port number of ssh server on camera")
    parser.add_argument('--username', default=getlogin(),
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

def mkdir(dir_name):
    """Version of os.mkdir that silently does nothing if dir already exists"""
    try:
        os.mkdir(dir_name)
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise

def download_and_remove(sftp, remote_file_name, local_file_name):
    logger.info("Downloading %s => %s", remote_file_name, local_file_name)
    sftp.get(remote_file_name, local_file_name)
    logger.info("Removing %s", remote_file_name)
    sftp.unlink(remote_file_name)

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

        images = [name for name in file_names if PHOTO_RE.match(name)]
        for i, remote_file_name in enumerate(images[:MAX_PER_CONN]):
            logger.info("Image %d/%d", i+1, len(images))
            match = PHOTO_RE.match(remote_file_name)
            assert match
            day_dir_name = '{year:04d}-{month:02d}-{day:02d}'.format(
                **{k: int(v) for k, v in match.groupdict().items()}
            )
            local_dir_name = os.path.join(args.dest_dir, day_dir_name)
            mkdir(local_dir_name)
            local_file_name = os.path.join(local_dir_name, remote_file_name)
            download_and_remove(sftp, remote_file_name, local_file_name)
            some_downloaded = True

        if LOG_FILE_NAME in file_names:
            suffix = datetime.datetime.now().strftime('.%Y%m%d-%H%M%S')
            remote_file_name = LOG_FILE_NAME + suffix
            logger.info("Renaming log => %s", remote_file_name)
            sftp.rename(LOG_FILE_NAME, remote_file_name)

            time.sleep(1)

            local_file_name = os.path.join(args.dest_dir, remote_file_name)
            download_and_remove(sftp, remote_file_name, local_file_name)

        # Failed log downloads
        logs = [name for name in file_names if name.startswith(LOG_FILE_NAME)
                and len(name) > len(LOG_FILE_NAME)]
        for i, remote_file_name in enumerate(logs):
            local_file_name = os.path.join(args.dest_dir, remote_file_name)
            download_and_remove(sftp, remote_file_name, local_file_name)

    return some_downloaded

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    args = parse_args(sys.argv)
    while download_some(args):
        pass
