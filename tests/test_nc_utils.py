import pytest

from .common import TESTDATA

from eggshell.utils import local_path
from eggshell.nc import nc_utils


def test_get_frequency():
    freq = nc_utils.get_frequency(local_path(TESTDATA['cmip5_tasmax_2007_nc']))
    assert 'mon' == freq


def test_get_values():
    values = nc_utils.get_values(local_path(TESTDATA['cmip5_tasmax_2007_nc']))
    assert 12 == len(values)

    values = nc_utils.get_values(local_path(TESTDATA['cordex_tasmax_2007_nc']))
    assert 12 == len(values)

    values = nc_utils.get_values([local_path(TESTDATA['cordex_tasmax_2006_nc']),
                                 local_path(TESTDATA['cordex_tasmax_2007_nc'])])
    assert 23 == len(values)


def test_get_time():
    timestamps = nc_utils.get_time(local_path(TESTDATA['cmip5_tasmax_2007_nc']))
    assert 12 == len(timestamps)

    timestamps = nc_utils.get_time(local_path(TESTDATA['cordex_tasmax_2007_nc']))
    assert 12 == len(timestamps)

    values = nc_utils.get_values([local_path(TESTDATA['cordex_tasmax_2006_nc']),
                                 local_path(TESTDATA['cordex_tasmax_2007_nc'])])
    assert 23 == len(values)


@pytest.mark.skip(reason="no way of currently testing this")
def test_unrotate_pole():
    ncs = [local_path(TESTDATA['cordex_tasmax_2006_nc']),
           local_path(TESTDATA['cordex_tasmax_2007_nc'])]
    lats, lons = nc_utils.unrotate_pole(ncs)
    assert lats.shape == (103, 106)


def test_get_index_lat():
    ncs = [local_path(TESTDATA['cordex_tasmax_2006_nc']),
           local_path(TESTDATA['cordex_tasmax_2007_nc'])]
    index = nc_utils.get_index_lat(ncs)
    assert 1 == index
    index = nc_utils.get_index_lat(ncs[0])
    assert 1 == index
    index = nc_utils.get_index_lat(local_path(TESTDATA['cmip5_tasmax_2007_nc']))
    assert 1 == index


def test_get_coordinates():
    ncs = [local_path(TESTDATA['cordex_tasmax_2006_nc']),
           local_path(TESTDATA['cordex_tasmax_2007_nc'])]

    lats, lons = nc_utils.get_coordinates(ncs, unrotate=False)

    assert 1 == len(lats.shape)

    lats, lons = nc_utils.get_coordinates(ncs)
    assert 103 == len(lats)
    assert 106 == len(lons)


def test_sort_by_time():
    result = nc_utils.sort_by_time([local_path(TESTDATA['cmip5_tasmax_2007_nc']),
                                   local_path(TESTDATA['cmip5_tasmax_2006_nc'])])
    assert '200601' in result[0]
    assert '200701' in result[1]

# def test_get_timestamps():
#     start,end = nc_utils.get_timestamps(local_path(TESTDATA['cmip5_tasmax_2006_nc']))
#     assert "20060116" == start
#     assert "20061216" == end


def test_get_timerange():
    start, end = nc_utils.get_timerange(local_path(TESTDATA['cmip5_tasmax_2006_nc']))
    assert "20060116" == start
    assert "20061216" == end

    start, end = nc_utils.get_timerange(local_path(TESTDATA['cordex_tasmax_2007_nc']))
    assert "20070116" == start
    assert "20071216" == end

    start, end = nc_utils.get_timerange([local_path(TESTDATA['cordex_tasmax_2006_nc']),
                                        local_path(TESTDATA['cordex_tasmax_2007_nc'])])
    assert "20060215" == start
    assert "20071216" == end


def test_drs_filename():
    # cordex
    filename = nc_utils.drs_filename(local_path(TESTDATA['cordex_tasmax_2006_nc']), skip_timestamp=False)
    assert filename == "tasmax_EUR-44_MPI-M-MPI-ESM-LR_rcp45_r1i1p1_MPI-CSC-REMO2009_v1_mon_20060215-20061216.nc"

    # cordex ... skip timestamp
    filename = nc_utils.drs_filename(local_path(TESTDATA['cordex_tasmax_2006_nc']), skip_timestamp=True)
    assert filename == "tasmax_EUR-44_MPI-M-MPI-ESM-LR_rcp45_r1i1p1_MPI-CSC-REMO2009_v1_mon.nc"

    # cmip5
    filename = nc_utils.drs_filename(local_path(TESTDATA['cmip5_tasmax_2006_nc']), skip_timestamp=False)
    assert filename == "tasmax_MPI-ESM-MR_RCP4.5_r1i1p1_20060116-20061216.nc"


def test_aggregations():
    nc_files = []
    nc_files.append(local_path(TESTDATA['cmip5_tasmax_2007_nc']))
    nc_files.append(local_path(TESTDATA['cmip5_tasmax_2006_nc']))

    aggs = nc_utils.aggregations(nc_files)

    assert len(aggs) == 1
    assert "tasmax_MPI-ESM-MR_RCP4.5_r1i1p1" in aggs
    agg = aggs["tasmax_MPI-ESM-MR_RCP4.5_r1i1p1"]

    # check aggregation files
    agg_files = agg['files']
    assert len(agg_files) == 2
    assert "tasmax_Amon_MPI-ESM-MR_rcp45_r1i1p1_200601-200612.nc" in agg_files[0]
    assert "tasmax_Amon_MPI-ESM-MR_rcp45_r1i1p1_200701-200712.nc" in agg_files[1]

    # check timestamps
    assert agg['from_timestamp'] == '20060116'
    assert agg['to_timestamp'] == '20071216'

    # check variable
    assert agg['variable'] == "tasmax"

    # check filename
    assert agg['filename'] == 'tasmax_MPI-ESM-MR_RCP4.5_r1i1p1_20060116-20071216.nc'
