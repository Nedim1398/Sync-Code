# Sync-Code
Python script for syncing two directories (one-way) with a set interval and logging all operations.

Usage: python3 main.py DIR_1 DIR_2 interval LOG_FILE

Arguments:
        
        DIR_1 - source folder, files are copied/overwritten to DIR_2

        DIR_2 - replicate/destination folder, files are copied/overwritten from DIR_1, deleted if non-existent in DIR_1

        frequency - interval at which the script is run, expressed in seconds
        NOTE: if execution takes less time than the interval it is substracted from the interval, otherwise wait for the interval

        LOG_FILE - file to which operations are logged
