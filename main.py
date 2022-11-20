#!/usr/bin/env

"""
Python script for syncing two directories (one-way)
with a set interval and logging all operations.

Usage: python3 main.py DIR_1 DIR_2 interval LOG_FILE

Arguments:
        DIR_1 - source folder, files are copied/overwritten to DIR_2

        DIR_2 - replicate/destination folder,
        files are copied/overwritten from DIR_1,
        deleted if non-existent in DIR_1

        frequency - interval at which the script is run, expressed in seconds |
        NOTE: if the script takes less time than the interval it is deducted
        from the time it took to execute, otherwise wait for the interval

        LOG_FILE - file to which operations are logged
"""
import sys
import os
import hashlib
import shutil
import time
import logging
from filecmp import dircmp

from actions import Action

if len(sys.argv) < 5:
    sys.stdout.write("Usage: python3 main.py DIR_1 DIR_2 interval LOG_FILE\n")
    sys.exit()
else:
    OG_DIR = sys.argv[1]
    CP_DIR = sys.argv[2]
    SYNC_PERIOD = float(sys.argv[3])
    LOG_FILE = sys.argv[4]

if not OG_DIR.endswith("/") or not OG_DIR.endswith("\\"):
    OG_DIR = OG_DIR + "/"
if not CP_DIR.endswith("/") or not CP_DIR.endswith("\\"):
    CP_DIR = CP_DIR + "/"

TIME_FORMAT = "%Y-%m-%d %H:%M"
LOG_FORMAT = "%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s"

logging.basicConfig(
    filename=LOG_FILE,
    filemode="a",
    format=LOG_FORMAT,
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def md5(file):
    """ Generates md5 hash for file. """
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def sync(source_dir, replica_dir, files, action):

    """
    Syncs the provided directories and files depending on the action.

    Parameters:
            source_dir (path): source directory,
            files copied to replica_dir

            replica_dir (path): destination folder,
            files copied from source_dir,
            deleted if non-existent in source_dir

            files (list): indicates the files which
            will be updated using action

            action (Enum): operation to be performed on files,
            can be COPY or OVERWRITE or DELETE
    """

    for file in files:
        if os.path.isdir(source_dir + file):
            if action == "DELETE":
                shutil.rmtree(replica_dir + file)
            else:
                shutil.copytree(
                    source_dir + file,
                    replica_dir + file,
                    symlinks=False,
                    ignore=None,
                )
        else:
            if action == "DELETE":
                os.remove(replica_dir + file)
            else:
                shutil.copy2(source_dir + file, replica_dir)

        if action == "DELETE":
            logging.debug(
                time.strftime(TIME_FORMAT)
                + " | " + action
                + ' "' + file + '" '
                + "FROM " + replica_dir
            )
        else:
            logging.debug(
                time.strftime(TIME_FORMAT)
                + " | " + action
                + ' "' + file + '" '
                + "FROM " + source_dir
                + " TO " + replica_dir
            )


def compare(source_dir, replica_dir):

    """
    Compares two directories recursively and syncs them.

    Parameters:
            source_dir (path): source directory,
            files copied to replica_dir

            replica_dir (path): destination folder,
            files copied from source_dir,
            deleted if non-existent in source_dir
    """

    dir_comparison = dircmp(source_dir,
                            replica_dir,
                            ignore=None,
                            hide=None)

    to_copy = dir_comparison.left_only
    to_overwrite = dir_comparison.diff_files + dir_comparison.funny_files
    to_delete = dir_comparison.right_only

    same_files = dir_comparison.same_files

    # Could be improved upon by running md5 check simultaneously and comparing
    for file in same_files:
        if md5(source_dir+file) != md5(replica_dir+file):
            to_overwrite += file

    if (to_copy):
        sync(source_dir,
             replica_dir,
             to_copy,
             Action.COPY.name)

    if (to_overwrite):
        sync(source_dir,
             replica_dir,
             to_overwrite,
             Action.OVERWRITE.name)

    if (to_delete):
        sync(source_dir,
             replica_dir,
             to_delete,
             Action.DELETE.name)

    sub_dirs = dir_comparison.common_dirs

    for sub in sub_dirs:
        compare(source_dir + sub + "/",
                replica_dir + sub + "/")


while 1:

    START_TIME = time.time()
    EXEC_TIME = 0

    try:

        logging.info("############################")
        logging.info("### Starting folder sync ###")
        logging.info("############################")

        compare(OG_DIR, CP_DIR)

        time.sleep(1)
        EXEC_TIME = time.time() - START_TIME
        logging.info("     Time to sync: " +
                     "{:.2f}".format(EXEC_TIME) + "s    ")

    finally:

        logging.info("----------------------------")
        logging.info("---    Folders synced!   ---")
        logging.info("----------------------------")

        sleep_period = SYNC_PERIOD - (EXEC_TIME % SYNC_PERIOD)
        if sleep_period > 0:
            time.sleep(sleep_period)
        else:
            time.sleep(SYNC_PERIOD)
