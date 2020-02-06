from eggshell.nc.nc_utils import get_values, get_coordinates, get_index_lat
# from eggshell.nc.ocg_utils import call
from os import path
import numpy as np
import logging
LOGGER = logging.getLogger("PYWPS")


def fieldmean(resource):
    """
    calculating of a weighted field mean

    :param resource: str or list of str containing the netCDF files paths

    :return list: timeseries of the averaged values per timestep
    """
    from numpy import radians, average, cos, sqrt, array

    data = get_values(resource)  # np.squeeze(ds.variables[variable][:])
    # dim = data.shape
    LOGGER.debug(data.shape)

    if len(data.shape) == 3:
        # TODO if data.shape == 2 , 4 ...
        lats, lons = get_coordinates(resource, unrotate=False)
        lats = array(lats)
        if len(lats.shape) == 2:
            lats = lats[:, 0]
        else:
            LOGGER.debug('Latitudes not reduced to 1D')
        # TODO: calculat weighed average with 2D lats (rotated pole coordinates)
        # lats, lons = get_coordinates(resource, unrotate=False)
        # if len(lats.shape) == 2:
        #     lats, lons = get_coordinates(resource)

        lat_index = get_index_lat(resource)
        LOGGER.debug('lats dimension %s ' % len(lats.shape))
        LOGGER.debug('lats index %s' % lat_index)

        lat_w = sqrt(cos(lats * radians(1)))
        meanLon = average(data, axis=lat_index, weights=lat_w)
        meanTimeserie = average(meanLon, axis=1)
        LOGGER.debug('fieldmean calculated')
    else:
        LOGGER.error('not 3D shaped data. Average can not be calculated')
    return meanTimeserie


def ens_stats(resources, time_range=[None,None], dir_output=None, output_format='nc'):

    from ocgis import OcgOperations, RequestDataset, env
    from os.path import basename
    from datetime import datetime as dt
    env.OVERWRITE = True

    var = 'tg_mean'
    out_means = []
    for resource in resources:

        rd = RequestDataset(resource, var)
        prefix = basename(resource).replace('.nc', '')
        LOGGER.debug('processing mean of {}'.format(prefix))
        calc = [{'func': 'median', 'name': 'median'}]  #  {'func': 'median', 'name': 'monthly_median'}
        ops = OcgOperations(dataset=rd, calc=calc, calc_grouping=['all'],
                            output_format=output_format, prefix='median_'+prefix, time_range=time_range)
        out_means.append(ops.execute())
    # nc_out = call(resource=resources, calc=[{'func': 'mean', 'name': 'ens_mean'}],
    #               calc_grouping='all', # time_region=time_region,
    #               dir_output=dir_output, output_format='nc')

    #####
    # prepare fieles by copying ...


    ####
    # read in numpy array


    ####
    # calc median, std 


    ####
    # write values to files

    LOGGER.info('processing the overall ensemble statistical mean ')

    # prefix = 'ensmean_tg-mean_{}-{}'.format(dt.strftime(time_range[0], '%Y-%m-%d'),
    #                                         dt.strftime(time_range[1], '%Y-%m-%d'))
    # rd = RequestDataset(out_means, var)
    # calc = [{'func': 'mean', 'name': 'mean'}]  #  {'func': 'median', 'name': 'monthly_median'}
    # ops = OcgOperations(dataset=rd, calc=calc, calc_grouping=['all'],
    #                     output_format=output_format, prefix='mean_'+prefix, time_range=time_range)
    # ensmean = ops.execute()

    return ensmean  # median


# call(resource=[], variable=None, dimension_map=None, agg_selection=True,
#          calc=None, calc_grouping=None, conform_units_to=None, crs=None,
#          memory_limit=None, prefix=None,
#          regrid_destination=None, regrid_options='bil', level_range=None,  # cdover='python',
#          geom=None, output_format_options=None, search_radius_mult=2.,
#          select_nearest=False, select_ugid=None, spatial_wrapping=None,
#          t_calendar=None, time_region=None,
#          time_range=None, dir_output=None, output_format='nc'):


# CDO is disabled ...
# def remove_mean_trend(fana, varname):
#     """
#     Removing the smooth trend from 3D netcdf file
#     """
#     from cdo import Cdo
#     from netCDF4 import Dataset
#     import uuid
#     from scipy.interpolate import UnivariateSpline
#     from os import system
#
#     if type(fana) == list:
#         fana = fana[0]
#
#     backup_ana = 'orig_mod_' + path.basename(fana)
#
#     cdo = Cdo()
#
#     # create backup of input file
#     # Again, an issue with cdo versioning.
#     # TODO: Fix CDO versioning workaround...
#
#     try:
#         cdo_cp = getattr(cdo, 'copy')
#         cdo_cp(input=fana, output=backup_ana)
#     except Exception:
#         if(path.isfile(backup_ana) is False):
#             com = 'copy'
#             comcdo = 'cdo -O %s %s %s' % (com, fana, backup_ana)
#             system(comcdo)
#         else:
#             backup_ana = 'None'
#
#     # create fmana - mean field
#     fmana = '%s.nc' % uuid.uuid1()
#
#     cdo_op = getattr(cdo, 'fldmean')
#     cdo_op(input=fana, output=fmana)
#
#     mean_arc_dataset = Dataset(fmana)
#     mean_arcvar = mean_arc_dataset.variables[varname][:]
#     data = mean_arcvar[:, 0, 0]
#     mean_arc_dataset.close()
#     x = np.linspace(0, len(data) - 1, len(data))
#     y = data
#
#     # Very slow method.
#     # TODO: sub by fast one
#     # (there is one in R, but doesn't want to add R to analogs...)
#     spl = UnivariateSpline(x, y)
#
#     smf = (len(y)) * np.var(y)
#     spl.set_smoothing_factor(smf)
#     trend = np.zeros(len(y), dtype=np.float)
#     trend[:] = spl(x)
#
# #    orig_arc_dataset = Dataset(fana,'r+')
#     orig_arc_dataset = Dataset(fana, 'a')
#     orig_arcvar = orig_arc_dataset.variables.pop(varname)
#     orig_data = orig_arcvar[:]
#
#     det = np.zeros(np.shape(orig_data), dtype=np.float)
#     det = (orig_data.T - trend).T
#
#     orig_arcvar[:] = det
#
#     # at = {k: orig_arcvar.getncattr(k) for k in orig_arcvar.ncattrs()}
#     maxat = np.max(det)
#     minat = np.min(det)
#     act = np.zeros((2), dtype=np.float32)
#     valid = np.zeros((2), dtype=np.float32)
#     act[0] = minat
#     act[1] = maxat
#     valid[0] = minat - abs(0.2 * minat)
#     valid[1] = maxat + abs(0.2 * maxat)
#     act_attr = {}
#     val_attr = {}
#
#     act_attr['actual_range'] = act
#     val_attr['valid_range'] = valid
#     orig_arcvar.setncatts(act_attr)
#     orig_arcvar.setncatts(val_attr)
#     orig_arc_dataset.close()
#
#     return backup_ana
