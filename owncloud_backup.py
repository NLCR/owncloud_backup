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


# Variables ===================================================================
# Functions & classes =========================================================
def collect_files(path):
    def file_list(path):
        for fn in os.listdir(path):
            if path.endiswith(".gz"):
                yield fn

    def parse_date(fn):
        date_string = fn.split("_")[-1].split(".gz")[0]
        date = datetime.datetime.strptime(date_string, "%Y.%m.%d").timetuple()

        return time.mktime(date)

    return {
        parse_date(fn): fn
        for fn in file_list(path)
    }


def get_user_pass(path):
    config = ConfigParser.ConfigParser()
    config.read(path)

    user = config.get("Login", "user")
    pwd = config.get("Login", "pass")

    return user, pwd


# Main program ================================================================
if __name__ == '__main__':
    print get_user_pass("login.cfg")
