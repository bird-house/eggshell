import pytest

from .common import TESTDATA

from os.path import basename, join
import tempfile
import tarfile
import zipfile
from netCDF4 import Dataset

from eggshell import utils

from eggshell.nc import ocg_utils
from eggshell.utils import local_path
from eggshell.config import Paths
import eggshell as eg
paths = Paths(eg)


def test_ocgis_import():
    from ocgis import constants


# def test_has_Lambert_Conformal():
#     has_lambert = ocg_utils.has_Lambert_Conformal(
#         [local_path(TESTDATA['cordex_tasmax_2006_nc']),
#          local_path(TESTDATA['cordex_tasmax_2007_nc'])])
#     assert False == has_lambert


# def test_gdal():
#     from flyingpigeon.subset import clipping


def test_archive_tar():
    result = utils.archive(local_path(TESTDATA['cmip5_tasmax_2006_nc']),
                           format='tar',
                           dir_output=tempfile.mkdtemp())
    tar = tarfile.open(result)
    assert len(tar.getnames()) == 1

# [local_path(TESTDATA['cmip5_tasmax_2007_nc'])],


def test_get_variable():
    variable = ocg_utils.get_variable(local_path(TESTDATA['cmip5_tasmax_2007_nc']))
    assert 'tasmax' == variable
    variable = ocg_utils.get_variable(local_path(TESTDATA['cordex_tasmax_2007_nc']))
    assert 'tasmax' == variable


def test_has_variable():
    assert ocg_utils.has_variable(
        local_path(TESTDATA['cmip5_tasmax_2006_nc']), 'tasmax') is True


def test_calc_grouping():
    assert ocg_utils.calc_grouping('year') == ['year']
    assert ocg_utils.calc_grouping('month') == ['month']
    assert ocg_utils.calc_grouping('sem') == [
        [12, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], 'unique']

    # check invalid value: should raise an exception
    with pytest.raises(Exception):
        ocg_utils.calc_grouping('unknown') == ['year']

# def get_coordinates(resource, variable=None, unrotate=False):
#     """
#     reads out the coordinates of a variable
#     :param resource: netCDF resource file
#     :param variable: variable name
#     :param unrotate: If True the coordinates will be returned for unrotated pole
#     :returns list, list: latitudes , longitudes
#     """
#     if type(resource) != list:
#         resource = [resource]
#
#     if variable is None:
#         variable = get_variable(resource)
#
#     if unrotate is False:
#         try:
#             if len(resource) > 1:
#                 ds = MFDataset(resource)
#             else:
#                 ds = Dataset(resource[0])
#
#             var = ds.variables[variable]
#             dims = list(var.dimensions)
#             if 'time' in dims:
#                 dims.remove('time')
#             # TODO: find position of lat and long in list and replace dims[0] dims[1]
#             lats = ds.variables[dims[0]][:]
#             lons = ds.variables[dims[1]][:]
#             ds.close()
#             LOGGER.info('got coordinates without pole rotation')
#         except Exception:
#             msg = 'failed to extract coordinates'
#             LOGGER.exception(msg)
#     else:
#         lats, lons = unrotate_pole(resource)
#         LOGGER.info('got coordinates with pole rotation')
#     return lats, lons
