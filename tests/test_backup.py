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


def test_pick_n():
    assert owncloud_backup.pick_n(range(10), 4) == [0, 2, 5, 7]
    assert owncloud_backup.pick_n(range(10), 3) == [0, 5, 9]

    assert owncloud_backup.pick_n(range(9), 4) == [0, 2, 4, 6]
    assert owncloud_backup.pick_n(range(9), 3) == [0, 4, 8]

    assert owncloud_backup.pick_n(range(12), 4) == [0, 3, 6, 9]
    assert owncloud_backup.pick_n(range(12), 3) == [0, 6, 11]

    assert owncloud_backup.pick_n(range(15), 3) == [0, 7, 14]