#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `utils` package."""

import pytest

from eggshell import utils


def test_archive():
    assert '.tar' in utils.archive([])
    assert '.zip' in utils.archive([], format='zip')
    with pytest.raises(Exception):
        utils.archive([], format='zip2')


def test_extract_archive():
    files = utils.extract_archive([
        utils.archive([]),
        utils.archive([], format='zip')])
    assert len(files) == 0
