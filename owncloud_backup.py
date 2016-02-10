#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import sys
import time
import argparse
import datetime
import ConfigParser
from collections import namedtuple

import owncloud


# Variables ===================================================================
# Functions & classes =========================================================
FileObj = namedtuple("FileObj", "timestamp filename")


def collect_files(path, suffix):
    def file_list(path):
        for fn in os.listdir(path):
            if path.endiswith(suffix):
                yield fn

    def parse_ts(fn):
        date_string = fn.split("_")[-1].split(suffix)[0]
        date = datetime.datetime.strptime(date_string, "%Y.%m.%d").timetuple()

        return time.mktime(date)

    return [
        FileObj(timestamp=parse_ts, filename=fn)
        for fn in file_list(path)
    ]


def pick_n(dataset, n):
    """
    Pick `n` items from `dataset`. The function tries to divide the items into
    same-sized groups and then picks first item from each of the group.

    Args:
        dataset (list): Array of items.
        n (int): How many items to pick from `dataset`.

    Returns:
        list: Picked items.
    """
    if len(dataset) == 1:
        return [dataset[0]]

    if n == 1 or n >= len(dataset):
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


def exists(client, path):
    path = os.path.abspath(path)

    dirname = os.path.dirname(path)
    filename = os.path.basename(path)

    listing = client.list(dirname)

    return filename in {
        os.path.basename(os.path.abspath(x.path))
        for x in listing
    }


def upload_file(remote_path, path, add_date_string=True):
    if add_date_string:
        filename = os.path.basename(os.path.abspath(path))
        remote_path = os.path.join(
            remote_path,
            time.strftime("%Y.%m.%d_") + filename,
        )

    return client.put_file(remote_path, path)


def get_config(args):
    config = ConfigParser.SafeConfigParser()
    config.read([
        "owncloud_backup.cfg",
        os.path.expanduser("~/.owncloud_backup.cfg"),
    ])

    # set configuration options
    if not config.has_section("Config"):
        config.add_section("Config")
    if not config.has_option("Config", "suffix"):
        config.set("Config", "suffix", ".gz")
    if not config.has_option("Config", "remote_path"):
        config.set("Config", "remote_path", "backups")

    # set login options
    if not config.has_section("Login"):
        config.add_section("Login")
    if not config.has_option("Login", "url"):
        config.set("Login", "url", args.url)

    return config


# Main program ================================================================
if __name__ == "__main__":
    default_url = "https://owncloud.cesnet.cz"

    parser = argparse.ArgumentParser(
        description="""This program may be used to perform database backups
            into ownCloud."""
    )
    parser.add_argument(
        "-u",
        "--username",
        help="Username of the ownCloud user."
    )
    parser.add_argument(
        "-p",
        "--password",
        help="Password of the ownCloud user."
    )
    parser.add_argument(
        "--url",
        default=default_url,
        help="URL of the ownCloud service. Default `%s`." % default_url
    )
    parser.add_argument(
        "-n",
        "--no-timestamp",
        dest="no_ts",
        action="store_true",
        help="""By default, the script adds `%%Y.%%m.%%d_` prefix to each \
            uploaded file."""
    )
    parser.add_argument(
        "FILENAME",
        nargs=1,
        help="Upload FILENAME into the ownCloud."
    )

    args = parser.parse_args()
    config = get_config(args)

    client = owncloud.Client(config.get("Login", "url"))
    client.login(config.get("Login", "user"), config.get("Login", "pass"))

    # check whether the user was really logged in
    try:
        client.list("/")
    except owncloud.ResponseError as e:
        if e.status_code == 401:
            print >>sys.stderr, "Invalid username/password."
            sys.exit(1)

        print >>sys.stderr, e.message
        sys.exit(1)

    # try to create `remote_path` directory
    remote_path = config.get("Config", "remote_path")
    if not exists(client, remote_path):
        if not client.mkdir(remote_path):
            print >>sys.stderr, (
                "Can't create `%s`. Please create the directory and repeat."
                % remote_path
            )
            sys.exit(1)

    filename = args.FILENAME[0]
    if not os.path.exists(filename):
        print >>sys.stderr, "`%s` doesn't exists!" % filename
        sys.exit(1)

    if not upload_file(remote_path, filename, not args.no_ts):
        print >>sys.stderr, "Couln't upload `%s`, sorry." % filename
        sys.exit(1)

    all_files = collect_files(remote_path, config.get("Config", "suffix"))
    old_files = collect_old_files(all_files)

    for file in old_files:
        client.delete(file.path)
