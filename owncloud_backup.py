#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
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


def divide_files(file_list, today=None):
    if not today:
        today = time.time()

    month = 60 * 60 * 24 * 31
    next_month = today + month

    def two_months_before(file_list):
        return [
            fo
            for fo in file_list
            if fo.timestamp > next_month and fo.timestamp <= next_month + month
        ]

    def three_months_or_older(file_list):
        return [
            fo
            for fo in file_list
            if fo.timestamp > next_month + month
        ]

    file_list = sorted(file_list, key=lambda x: x.timestamp)
    two_months = two_months_before(file_list)
    three_months = three_months_or_older(file_list)




def get_user_pass(path):
    config = ConfigParser.ConfigParser()
    config.read(path)

    user = config.get("Login", "user")
    pwd = config.get("Login", "pass")

    return user, pwd


# Main program ================================================================
if __name__ == '__main__':
    print get_user_pass("login.cfg")
