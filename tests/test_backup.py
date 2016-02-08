#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os.path

import pytest

import owncloud_backup


# Variables ===================================================================
# Fixtures ====================================================================
@pytest.fixture
def data_path():
    return os.path.join(os.path.dirname(__file__), "data")

# with pytest.raises(Exception):
#     raise Exception()


# Functions ===================================================================
def data_context(fn):
    return os.path.join(data_path(), fn)


# Tests =======================================================================
def test_collect_files(data_path):
    owncloud_backup.collect_files(data_path)
