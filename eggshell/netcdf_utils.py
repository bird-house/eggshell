from netCDF4 import Dataset, MFDataset, num2date
from ocgis import RequestDataset
import datetime as dt
import time
import logging
LOGGER = logging.getLogger("PYWPS")


def get_calendar(resource, variable=None):
    """
    returns the calendar and units in wich the timestamps are stored

    :param resource: netCDF file or files of one Dataset

    :return str: calendar, unit
    """

    if type(resource) != list:
        resource = [resource]

    try:
        if len(resource) > 1:
            ds = MFDataset(resource)
        else:
            ds = Dataset(resource[0])
        time = ds.variables['time']
    except:
        msg = 'failed to get time'
        LOGGER.exception(msg)
        raise Exception(msg)

    if hasattr(time, 'units') is True:
        unit = time.units
    else:
        unit = None

    if hasattr(time, 'calendar') is True:
        calendar = time.calendar
    else:
        calendar = None
    return str(calendar), str(unit)


def get_coordinates(resource, variable=None, unrotate=False):
    """
    reads out the coordinates of a variable

    :param resource: netCDF resource file
    :param variable: variable name
    :param unrotate: If True the coordinates will be returned for unrotated pole

    :returns list, list: latitudes , longitudes
    """
    if type(resource) != list:
        resource = [resource]

    if variable is None:
        variable = get_variable(resource)

    if unrotate is False:
        try:
            if len(resource) > 1:
                ds = MFDataset(resource)
            else:
                ds = Dataset(resource[0])

            var = ds.variables[variable]
            dims = list(var.dimensions)
            if 'time' in dims: dims.remove('time')
            # TODO: find position of lat and long in list and replace dims[0] dims[1]
            lats = ds.variables[dims[0]][:]
            lons = ds.variables[dims[1]][:]
            ds.close()
            LOGGER.info('got coordinates without pole rotation')
        except Exception:
            msg = 'failed to extract coordinates'
            LOGGER.exception(msg)
    else:
        lats, lons = unrotate_pole(resource)
        LOGGER.info('got coordinates with pole rotation')
    return lats, lons


def get_domain(resource):
    """
    returns the domain of a netCDF file

    :param resource: netCDF file (metadata quality checked!)

    :return str: domain
    """
    try:
        ds = Dataset(resource)
        if 'CMIP' in ds.project_id or 'EUCLEIA' in ds.project_id:
            domain = None
            LOGGER.debug('resource belongs to a global experiment project')
        elif 'CORDEX' in ds.project_id:
            domain = ds.CORDEX_domain
            LOGGER.info('resource belongs to CORDEX')
        else:
            LOGGER.debug('No known project_id found in meta data')
        ds.close()
    except Exception as e:
        LOGGER.debug('Could not specify domain for %s: %s' % (resource, e))
    return domain


def get_frequency(resource):
    """
    returns the frequency as set in the metadata (see also metadata.get_frequency)

    :param resource: NetCDF file

    :return str: frequency
    """
    ds = Dataset(resource)

    try:
        frequency = ds.frequency
        LOGGER.info('frequency written in the meta data:  %s', frequency)
    except Exception as e:
        msg = "Could not specify frequency for %s" % (resource)
        LOGGER.exception(msg)
        raise Exception(msg)
    else:
        ds.close()
    return frequency


def get_index_lat(resource, variable=None):
    """
    returns the dimension index of the latiude values

    :param resource:  list of path(s) to netCDF file(s) of one Dataset
    :param variable: variable name

    :return int: index
    """

    if variable is None:
        variable = get_variable(resource)
    if type(resource) != list:
        resource = [resource]
    if len(resource) == 1:
        ds = Dataset(resource[0])
    else:
        ds = MFDataset(resource)

    var = ds.variables[variable]
    dims = list(var.dimensions)

    if 'rlat' in dims:
        index = dims.index('rlat')
    if 'lat' in dims:
        index = dims.index('lat')
    if 'latitude' in dims:
        index = dims.index('latitude')
    if 'y' in dims:
        index = dims.index('y')
    return index


def get_timerange(resource):
    """
    returns from/to timestamp of given netcdf file(s).

    :param resource: list of path(s) to netCDF file(s)

    :returns netcdf.datetime.datetime: start, end

    """
    start = end = None

    if type(resource) != list:
        resource = [resource]
    LOGGER.debug('length of recources: %s files' % len(resource))

    try:
        if len(resource) > 1:
            ds = MFDataset(resource)
            LOGGER.debug('MFDataset loaded for %s of files in resource:' % len(resource))
        else:
            ds = Dataset(resource[0])
            LOGGER.debug('Dataset loaded for %s file in resource:' % len(resource))
        time = ds.variables['time']

        if (hasattr(time, 'units') and hasattr(time, 'calendar')) is True:
            s = num2date(time[0], time.units, time.calendar)
            e = num2date(time[-1], time.units, time.calendar)
        elif hasattr(time, 'units'):
            s = num2date(time[0], time.units)
            e = num2date(time[-1], time.units)
        else:
            s = num2date(time[0])
            e = num2date(time[-1])

        # TODO: include frequency
        start = '%s%s%s' % (s.year, str(s.month).zfill(2), str(s.day).zfill(2))
        end = '%s%s%s' % (e.year, str(e.month).zfill(2), str(e.day).zfill(2))
        ds.close()
    except Exception:
        msg = 'failed to get time range'
        LOGGER.exception(msg)
        ds.close()
        raise Exception(msg)
    return start, end


def get_time(resource):
    """
    returns all timestamps of given netcdf file as datetime list.

    :param resource: NetCDF file(s)

    :return : list of timesteps
    """
    # :param format: if a format is provided (e.g format='%Y%d%m'), values will be converted to string

    if type(resource) != list:
        resource = [resource]

    try:
        if len(resource) > 1:
            ds = MFDataset(resource)
        else:
            ds = Dataset(resource[0])
        time = ds.variables['time']
    except:
        msg = 'failed to get time'
        LOGGER.exception(msg)
        raise Exception(msg)

    try:
        if (hasattr(time, 'units') and hasattr(time, 'calendar')) is True:
            timestamps = num2date(time[:], time.units, time.calendar)
        elif hasattr(time, 'units'):
            timestamps = num2date(time[:], time.units)
        else:
            timestamps = num2date(time[:])
        ds.close()
        try:
            ts = [dt.strptime(str(i), '%Y-%m-%d %H:%M:%S') for i in timestamps]

            # if date_format is not None:
            #     ts = [t.strftime(format=date_format) for t in timestamps]
            # else:
            #    ts = [dt.strptime(str(i), '%Y-%m-%d %H:%M:%S') for i in timestamps]

            # TODO give out dateformat by frequency
            # ERROR: ValueError: unconverted data remains: 12:00:00
            # from flyingpigeon.metadata import get_frequency

            # frq = get_frequency(resource)
            # if frq is 'day':
            #     ts = [dt.strptime(str(i), '%Y-%m-%d') for i in timestamps]
            # elif frq is 'mon':
            #     ts = [dt.strptime(str(i), '%Y-%m') for i in timestamps]
            # elif frq is 'sem':
            #     ts = [dt.strptime(str(i), '%Y-%m') for i in timestamps]
            # elif frq is 'yr':
            #     ts = [dt.strptime(str(i), '%Y') for i in timestamps]
            # else:
            #     ts = [dt.strptime(str(i), '%Y-%m-%d %H:%M:%S') for i in timestamps]
        except:
            msg = 'failed to convert times to string'
            LOGGER.exception(msg)
    except:
        msg = 'failed to convert time'
        LOGGER.exception(msg)
    return ts


def get_variable(resource):
    """
    detects processable variable name in netCDF file

    :param resource: NetCDF file(s)

    :returns str: variable name
    """
    rds = RequestDataset(resource)
    return rds.variable


def get_values(resource, variable=None):
    """
    returns the values for a list of files of files belonging to one dataset

    :param resource: list of files
    :param variable: variable to be picked from the files (if not set, variable will be detected)

    :returs numpy.array: values
    """
    from numpy import squeeze
    if variable is None:
        variable = get_variable(resource)

    if isinstance(resource, basestring):
        ds = Dataset(resource)
    elif len(resource) == 1:
        ds = Dataset(resource)
    else:
        ds = MFDataset(resource)
    vals = squeeze(ds.variables[variable][:])
    return vals



def unrotate_pole(resource, write_to_file=False):
    """
    Calculates the unrotatated coordinates for a rotated pole grid

    :param resource: netCDF file or list of files of one datatset
    :param write_to_file: calculated values will be written to file if True (default=False)

    :return list: lats, lons
    """
    from numpy import reshape, repeat
    from iris.analysis import cartography as ct

    if len(resource) == 1:
        ds = Dataset(resource[0])
    else:
        ds = MFDataset(resource)

    # ds = MFDataset(resource)

    if 'lat' in ds.variables.keys():
        LOGGER.info('file include unrotated coordinate values')
        lats = ds.variables['lat'][:]
        lons = ds.variables['lon'][:]
    else:
        try:
            if 'rotated_latitude_longitude' in ds.variables:
                rp = ds.variables['rotated_latitude_longitude']
            elif 'rotated_pole' in ds.variables:
                rp = ds.variables['rotated_pole']
            else:
                LOGGER.debug('rotated pole variable not found')
            pole_lat = rp.grid_north_pole_latitude
            pole_lon = rp.grid_north_pole_longitude
        except:
            LOGGER.exception('failed to find rotated_pole coordinates')
        try:
            if 'rlat' in ds.variables:
                rlats = ds.variables['rlat']
                rlons = ds.variables['rlon']

            if 'x' in ds.variables:
                rlats = ds.variables['y']
                rlons = ds.variables['x']
        except:
            LOGGER.exception('failed to read in rotated coordiates')

        try:
            rlons_i = reshape(rlons, (1, len(rlons)))
            rlats_i = reshape(rlats, (len(rlats), 1))
            grid_rlats = repeat(rlats_i, (len(rlons)), axis=1)
            grid_rlons = repeat(rlons_i, (len(rlats)), axis=0)
        except:
            LOGGER.execption('failed to repeat coordinates')

        lons, lats = ct.unrotate_pole(grid_rlons, grid_rlats, pole_lon, pole_lat)

    if write_to_file is True:
        lat = ds.createVariable('lat', 'f8', ('rlat', 'rlon'))
        lon = ds.createVariable('lon', 'f8', ('rlat', 'rlon'))

        lon.standard_name = "longitude"
        lon.long_name = "longitude coordinate"
        lon.units = 'degrees_east'
        lat.standard_name = "latitude"
        lat.long_name = "latitude coordinate"
        lat.units = 'degrees_north'

        lat[:] = lats
        lon[:] = lons

    ds.close()

    return lats, lons


# TODO: doc
def sort_by_time(resource):
    """
    Sort a list of files by their time variable.

    :param resource: File path.
    :return: Sorted file list.
    """
    from ocgis.util.helpers import get_sorted_uris_by_time_dimension

    if type(resource) == list and len(resource) > 1:
        sorted_list = get_sorted_uris_by_time_dimension(resource)
    elif type(resource) == str:
        sorted_list = [resource]
    else:
        sorted_list = resource
    return sorted_list


def sort_by_filename(resource, historical_concatination=False):
    """
    Sort a list of files with CORDEX-conformant file names.

    :param resource: netCDF file
    :param historical_concatination: if True (default=False), appropriate historial
                                    runs will be sorted to the rcp datasets
    :return  dictionary: {'drs_filename': [list of netCDF files]}
    """
    from os import path
    if type(resource) == str:
        resource = [resource]

    ndic = {}
    tmp_dic = {}

    try:
        if len(resource) > 1:
            LOGGER.debug('sort_by_filename module start sorting %s files' % len(resource))
            # LOGGER.debug('resource is list with %s files' % len(resource))
            try:  # if len(resource) > 1:
                # collect the different experiment names
                for nc in resource:
                    # LOGGER.info('file: %s' % nc)
                    p, f = path.split(path.abspath(nc))
                    n = f.split('_')
                    bn = '_'.join(n[0:-1])  # skipping the date information in the filename
                    ndic[bn] = []  # dictionary containing all datasets names
                LOGGER.info('found %s datasets', len(ndic.keys()))
            except Exception:
                LOGGER.exception('failed to find names of datasets!')
            LOGGER.info('check for historical/RCP datasets')
            try:
                if historical_concatination is True:
                    # select only necessary names
                    if any("_rcp" in s for s in ndic.keys()):
                        for key in ndic.keys():
                            if 'historical' in key:
                                ndic.pop(key)
                        LOGGER.info('historical data set names removed from dictionary')
                    else:
                        LOGGER.info('no RCP dataset names found in dictionary')
            except Exception:
                LOGGER.exception('failed to pop historical data set names!')
            LOGGER.info('start sorting the files')
            try:
                for key in ndic:
                    try:
                        if historical_concatination is False:
                            for n in resource:
                                if '%s_' % key in n:
                                    ndic[key].append(path.abspath(n))  # path.join(p, n))

                        elif historical_concatination is True:
                            key_hist = key.replace('rcp26', 'historical'). \
                                replace('rcp45', 'historical'). \
                                replace('rcp65', 'historical'). \
                                replace('rcp85', 'historical')
                            for n in resource:
                                if '%s_' % key in n or '%s_' % key_hist in n:
                                    ndic[key].append(path.abspath(n))  # path.join(p, n))
                        else:
                            LOGGER.error('append file paths to dictionary for key %s failed' % key)
                        ndic[key].sort()
                    except Exception:
                        LOGGER.exception('failed for %s ' % key)
            except Exception:
                LOGGER.exception('failed to populate the dictionary with appropriate files')
            for key in ndic.keys():
                try:
                    ndic[key].sort()
                    start, end = get_timerange(ndic[key])
                    newkey = key + '_' + start + '-' + end
                    tmp_dic[newkey] = ndic[key]
                except Exception:
                    msg = 'failed to sort the list of resources and add dates to keyname: %s' % key
                    LOGGER.exception(msg)
                    tmp_dic[key] = ndic[key]
                    # raise Exception(msg)
        elif len(resource) == 1:
            p, f = path.split(path.abspath(resource[0]))
            tmp_dic[f.replace('.nc', '')] = path.abspath(resource[0])
            LOGGER.debug('only one file! Nothing to sort, resource is passed into dictionary')
        else:
            LOGGER.debug('sort_by_filename module failed: resource is not 1 or >1')
        LOGGER.info('sort_by_filename module done: %s datasets found' % len(ndic))
    except Exception:
        msg = 'failed to sort files by filename'
        LOGGER.exception(msg)
        raise Exception(msg)
    return tmp_dic



def search_landsea_mask_by_esgf(resource):
    """
    Search a landsea mask (variable sftlf) in ESGF which matches the
    NetCDF attributes in the NetCDF files ``resource``.

    Raises an Exception if no mask is found.

    Returns the OpenDAP URL of the first found mask file.
    """
    # fill search constraints from nc attributes
    ds = Dataset(resource)
    attributes = ds.ncattrs()
    constraints = dict(variable="sftlf")
    for attr, facet in ATTRIBUTE_TO_FACETS_MAP.iteritems():
        if attr in attributes:
            constraints[facet] = ds.getncattr(attr)

    # run file search
    conn = SearchConnection(config.esgfsearch_url(), distrib=config.esgfsearch_distrib())
    ctx = conn.new_context(search_type=TYPE_FILE, **constraints)
    if ctx.hit_count == 0:
        raise Exception("Could not find a mask in ESGF for dataset {0}".format(
            os.path.basename(resource)))
        # LOGGER.exception("Could not find a mask in ESGF.")
        # return
    if ctx.hit_count > 1:
        LOGGER.warn("Found more then one mask file.")
    results = ctx.search(batch_size=1)
    return results[0].opendap_url
