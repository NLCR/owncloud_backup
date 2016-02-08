#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import ConfigParser


# Variables ===================================================================
# Functions & classes =========================================================
def collect_files(path):
    def file_list():
        for fn in os.listdir(path):
            if path.endiswith(".gz"):
                yield fn

    def parse_date(fn):
        pass

    

def get_user_pass(path):
    config = ConfigParser.ConfigParser()
    config.read(path)

    user = config.get("Login", "user")
    pwd = config.get("Login", "pass")

    return user, pwd


# Main program ================================================================
if __name__ == '__main__':
    print get_user_pass("login.cfg")
