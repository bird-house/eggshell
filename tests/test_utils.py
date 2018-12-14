#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `utils` package."""

import pytest

from eggshell import utils
from eggshell.utils import local_path
from eggshell.config import Paths


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


def test_Paths():
    assert "flyingpigeon/tests/testdata" in paths.testdata
    assert 'flyingpigeon/data' in paths.data
    assert 'flyingpigeon/data/shapefiles' in paths.shapefiles


def test_local_path():
    assert local_path('file:///tmp/test.nc') == '/tmp/test.nc'
    assert local_path('/tmp/test.nc') == '/tmp/test.nc'


@pytest.mark.skip(reason="no way of currently testing this")
def test_download_with_cache():
    filename = utils.download(TESTDATA['cmip5_tasmax_2006_nc'], cache=paths.cache)
    assert basename(filename) == 'tasmax_Amon_MPI-ESM-MR_rcp45_r1i1p1_200601-200612.nc'


def test_archive_zip():
    result = utils.archive(local_path(TESTDATA['cmip5_tasmax_2006_nc']),
                           format='zip',
                           output_dir=tempfile.mkdtemp())
    zipf = zipfile.ZipFile(result)
    assert len(zipf.namelist()) == 1
