#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import ConfigParser


# Variables ===================================================================
# Functions & classes =========================================================
def get_user_pass(path):
    config = ConfigParser.ConfigParser()
    config.read(path)

    user = config.get("Login", "user")
    pwd = config.get("Login", "pass")

    return user, pwd


# Main program ================================================================
if __name__ == '__main__':
    print get_user_pass("login.cfg")
