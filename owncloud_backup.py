#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import sys
import time
import datetime
import ConfigParser
from collections import namedtuple


# Variables ===================================================================
# Functions & classes =========================================================
FileObj = namedtuple("FileObj", "timestamp filename")


def collect_files(path):
    def file_list(path):
        for fn in os.listdir(path):
            if path.endiswith(".gz"):
                yield fn

    def parse_ts(fn):
        date_string = fn.split("_")[-1].split(".gz")[0]
        date = datetime.datetime.strptime(date_string, "%Y.%m.%d").timetuple()

        return time.mktime(date)

    return [
        FileObj(timestamp=parse_ts, filename=fn)
        for fn in file_list(path)
    ]


def pick_n(dataset, n):
    if len(dataset) == 1:
        return [dataset[0]]

    if n >= len(dataset):
        return dataset

    if n == 1:
        return dataset

    elif n == 2:
        return [dataset[0], dataset[len(dataset) / 2]]

    elif n == 3:
        return [dataset[0], dataset[len(dataset) / 2], dataset[-1]]

    else:
        return pick_n(dataset[:len(dataset) / 2], n - 2) + \
               pick_n(dataset[len(dataset) / 2:], n - 2)


def collect_old_files(file_list, today=None):
    if not today:
        today = time.time()

    month = 60 * 60 * 24 * 31
    next_month = today + month
    next_two_months = next_month + month
    next_three_months = next_two_months + month

    def two_months_before(file_list):
        return [
            fo
            for fo in file_list
            if fo.timestamp > next_month and fo.timestamp <= next_two_months
        ]

    def three_months_before(file_list):
        return [
            fo
            for fo in file_list
            if (fo.timestamp > next_two_months and
                fo.timestamp <= next_three_months)
        ]

    def older_than_three_months(file_list):
        return [
            fo
            for fo in file_list
            if fo.timestamp > next_three_months
        ]

    # sort the list - this is important for other pickers
    file_list = sorted(file_list, key=lambda x: x.timestamp)

    # collect list of two and three months old files
    two_months = two_months_before(file_list)
    three_months = three_months_before(file_list)

    # all older files are considered as old
    old_files = older_than_three_months(file_list)

    # pick files, which will be kept
    keep_twomonths = pick_n(two_months, 4)
    keep_threemonths = pick_n(three_months, 2)

    # collect all files which are not in keep_* lists
    old_files.extend([fo for fo in two_months if fo not in keep_twomonths])
    old_files.extend([fo for fo in three_months if fo not in keep_threemonths])

    return old_files


# Main program ================================================================
if __name__ == '__main__':
    config = ConfigParser.SafeConfigParser()
    config.read([
        'owncloud_backup.cfg',
        os.path.expanduser('~/.owncloud_backup.cfg'),
    ])
    if not config.has_section("Conf"):
        config.add_section("Conf")
        config.set('Conf', 'suffix', '.gz')

    user = config.get("Login", "user")
    pwd = config.get("Login", "pass")
    suffix = config.get("Conf", "suffix")
