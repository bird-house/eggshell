"""
visualization of netCDF data
"""

from tempfile import mkstemp
# from matplotlib import use
# use('Agg')   # use this if no xserver is available
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.patches as mpatches
import cartopy.crs as ccrs

from eggshell.nc.calculation import fieldmean
from eggshell.nc.nc_utils import get_variable, get_frequency, get_coordinates
from eggshell.nc.nc_utils import get_time, sort_by_filename
from eggshell.plot.plt_utils import fig2plot

import logging
LOGGER = logging.getLogger("PYWPS")


def plot_extend(resource, file_extension='png'):
    """
    plots the extend (domain) of the values stored in a netCDF file:

    :parm resource: path to netCDF file
    :param file_extension: file format of the graphic. if file_extension=None a matplotlib figure will be returned

    :return graphic: graphic in specified format
    """
    lats, lons = get_coordinates(resource, unrotate=True)

    # box_top = 45
    # x, y = [-20, -20, 45, 45, -44], [-45, box_top, box_top, -45, -45]

    xy = np.array([[np.min(lons), np.min(lats)],
                   [np.max(lons), np.min(lats)],
                   [np.max(lons), np.max(lats)],
                   [np.min(lons), np.max(lats)]])

    fig = plt.figure(figsize=(20, 10), dpi=600, facecolor='w', edgecolor='k')
    projection = ccrs.Robinson()

    #  ccrs.Orthographic(central_longitude=np.mean(xy[:, 0]),
    #  central_latitude=np.mean(xy[:, 1]),
    #  globe=None)  # Robinson()

    ax = plt.axes(projection=projection)
    ax.stock_img()
    ax.coastlines()
    ax.add_patch(mpatches.Polygon(xy, closed=True, transform=ccrs.PlateCarree(), color='coral', alpha=0.6))
    # ccrs.Geodetic()
    ax.gridlines()
    plt.show()

    if file_extension is None:
        map_graphic = fig
    else:
        map_graphic = fig2plot(fig=fig, file_extension=file_extension)
    plt.close()

    return map_graphic


def spaghetti(resouces, variable=None, title=None, file_extension='png'):
    """
    creates a png file containing the appropriate spaghetti plot as a field mean of the values.

    :param resouces: list of files containing the same variable
    :param variable: variable to be visualised. If None (default), variable will be detected
    :param title: string to be used as title

    :retruns str: path to png file
    """
    from eggshell.nc.calculation import fieldmean

    try:
        fig = plt.figure(figsize=(20, 10), dpi=600, facecolor='w', edgecolor='k')
        LOGGER.debug('Start visualisation spaghetti plot')

        # === prepare invironment
        if type(resouces) != list:
            resouces = [resouces]
        if variable is None:
            variable = get_variable(resouces[0])
        if title is None:
            title = "Field mean of %s " % variable

        LOGGER.info('plot values preparation done')
    except Exception as ex:
        msg = "plot values preparation failed {}".format(ex)
        LOGGER.exception(msg)
        raise Exception(msg)
    try:
        for c, nc in enumerate(resouces):
            # get timestapms
            try:
                dt = get_time(nc)  # [datetime.strptime(elem, '%Y-%m-%d') for elem in strDate[0]]
                ts = fieldmean(nc)
                plt.plot(dt, ts)
                # fig.line( dt,ts )
            except Exception as e:
                msg = "spaghetti plot failed for {} : {}".format(nc, e)
                LOGGER.exception(msg)

        plt.title(title, fontsize=20)
        plt.grid()

        output_png = fig2plot(fig=fig, file_extension=file_extension)

        plt.close()
        LOGGER.info('timeseries spaghetti plot done for %s with %s lines.' % (variable, c))
    except Exception as ex:
        msg = 'matplotlib spaghetti plot failed: {}'.format(ex)
        LOGGER.exception(msg)
    return output_png


def uncertainty(resouces, variable=None, ylim=None, title=None, file_extension='png', window=None):
    """
    creates a png file containing the appropriate uncertainty plot.

    :param resouces: list of files containing the same variable
    :param variable: variable to be visualised. If None (default), variable will be detected
    :param title: string to be used as title
    :param window: windowsize of the rolling mean

    :returns str: path/to/file.png
    """
    LOGGER.debug('Start visualisation uncertainty plot')

    import pandas as pd
    import numpy as np
    from os.path import basename
    #
    # from flyingpigeon.utils import get_time, sort_by_filename
    # from flyingpigeon.calculation import fieldmean
    # from flyingpigeon.metadata import get_frequency

    # === prepare invironment
    if type(resouces) == str:
        resouces = list([resouces])
    if variable is None:
        variable = get_variable(resouces[0])
    if title is None:
        title = "Field mean of %s " % variable

    try:
        fig = plt.figure(figsize=(20, 10), facecolor='w', edgecolor='k')
        #  variable = get_variable(resouces[0])
        df = pd.DataFrame()

        LOGGER.info('variable %s found in resources.' % variable)
        datasets = sort_by_filename(resouces, historical_concatination=True)

        for key in datasets.keys():
            try:
                data = fieldmean(datasets[key])  # get_values(f)
                ts = get_time(datasets[key])
                ds = pd.Series(data=data, index=ts, name=key)
                # ds_yr = ds.resample('12M', ).mean()   # yearly mean loffset='6M'
                df[key] = ds

            except Exception:
                LOGGER.exception('failed to calculate timeseries for %s ' % (key))

        frq = get_frequency(resouces[0])

        if window is None:
            if frq == 'day':
                window = 10951
            elif frq == 'man':
                window = 359
            elif frq == 'sem':
                window = 119
            elif frq == 'yr':
                window = 30
            else:
                LOGGER.debug('frequency %s is not included' % frq)
                window = 30

        if len(df.index.values) >= window * 2:
            # TODO: calculate windowsize according to timestapms (day,mon,yr ... with get_frequency)
            df_smooth = df.rolling(window=window, center=True).mean()
            LOGGER.info('rolling mean calculated for all input data')
        else:
            df_smooth = df
            LOGGER.debug('timeseries too short for moving mean')
            fig.text(0.95, 0.05, '!!! timeseries too short for moving mean over 30years !!!',
                     fontsize=20, color='red',
                     ha='right', va='bottom', alpha=0.5)

        try:
            rmean = df_smooth.quantile([0.5], axis=1,)
            # df_smooth.median(axis=1)
            # skipna=False  quantile([0.5], axis=1, numeric_only=False )
            q05 = df_smooth.quantile([0.10], axis=1,)  # numeric_only=False)
            q33 = df_smooth.quantile([0.33], axis=1,)  # numeric_only=False)
            q66 = df_smooth.quantile([0.66], axis=1, )  # numeric_only=False)
            q95 = df_smooth.quantile([0.90], axis=1, )  # numeric_only=False)
            LOGGER.info('quantile calculated for all input data')
        except Exception:
            LOGGER.exception('failed to calculate quantiles')

        try:
            plt.fill_between(df_smooth.index.values, np.squeeze(q05.values), np.squeeze(q95.values),
                             alpha=0.5, color='grey')
            plt.fill_between(df_smooth.index.values, np.squeeze(q33.values), np.squeeze(q66.values),
                             alpha=0.5, color='grey')

            plt.plot(df_smooth.index.values, np.squeeze(rmean.values), c='r', lw=3)

            plt.xlim(min(df.index.values), max(df.index.values))
            plt.ylim(ylim)
            plt.title(title, fontsize=20)
            plt.grid()  # .grid_line_alpha=0.3

            output_png = fig2plot(fig=fig, file_extension=file_extension)
            plt.close()
            LOGGER.debug('timeseries uncertainty plot done for %s' % variable)
        except Exception as err:
            raise Exception('failed to calculate quantiles. %s' % err.message)
    except Exception:
        LOGGER.exception('uncertainty plot failed for %s.' % variable)
        _, output_png = mkstemp(dir='.', suffix='.png')
    return output_png


def plot_spatial_analog(ncfile, variable='dissimilarity', cmap='viridis', title='Spatial analog'):
    """Return a matplotlib Figure instance showing a map of the dissimilarity measure.
    """
    import netCDF4 as nc
    from eggshell.nc import nc_utils
    from mpl_toolkits.axes_grid import make_axes_locatable
    import matplotlib.axes as maxes
    from cartopy.util import add_cyclic_point

    try:
        var = nc_utils.get_values(ncfile, variable)
        LOGGER.info('Data loaded')

        lats, lons = nc_utils.get_coordinates(ncfile, variable=variable, unrotate=False)

        if len(lats.shape) == 1:
            cyclic_var, cyclic_lons = add_cyclic_point(var, coord=lons)

            lons = cyclic_lons.data
            var = cyclic_var

        with nc.Dataset(ncfile) as D:
            V = D.variables[variable]
            lon, lat = map(float, V.target_location.split(','))

        LOGGER.info('Lat and lon loaded')

    except Exception as e:
        msg = 'Failed to get data for plotting: {0}\n{1}'.format(ncfile, e)
        LOGGER.exception(msg)
        raise Exception(msg)

    try:
        fig = plt.figure(facecolor='w', edgecolor='k')
        fig.subplots_adjust(top=.95, bottom=.05, left=.03, right=.95)

        ax = plt.axes(
            projection=ccrs.Robinson(central_longitude=int(np.mean(lons))))

        divider = make_axes_locatable(ax)
        cax = divider.new_horizontal("4%", pad=0.15, axes_class=maxes.Axes)
        fig.add_axes(cax)

        ax.plot(lon, lat, marker='o', mfc='#292421', ms=13, transform=ccrs.PlateCarree())
        ax.plot(lon, lat, marker='o', mfc='#ffffff', ms=7, transform=ccrs.PlateCarree())

        cs = ax.contourf(lons, lats, var, 60,
                         transform=ccrs.PlateCarree(),
                         cmap=cmap, interpolation='nearest')

        ax.coastlines(color='k', linewidth=.8)
        ax.set_title(title)

        cb = plt.colorbar(cs, cax=cax, orientation='vertical')
        cb.set_label(u"–            Dissimilarity             +")  # ha='left', va='center')
        cb.set_ticks([])

    except Exception as ex:
        msg = 'failed to plot graphic {}'.format(ex)
        LOGGER.exception(msg)

    LOGGER.info('Plot created and figure saved')
    return fig


# def map_robustness(signal, high_agreement_mask, low_agreement_mask,
#                    variable=None, cmap='seismic', title=None,
#                    file_extension='png'):
#     """
#     generates a graphic for the output of the ensembleRobustness process for a lat/long file.
#
#     :param signal: netCDF file containing the signal difference over time
#     :param highagreement:
#     :param lowagreement:
#     :param variable:
#     :param cmap: default='seismic',
#     :param title: default='Model agreement of signal'
#     :returns str: path/to/file.png
#     """
#     # from flyingpigeon import utils
#     from eggshell.general import utils
#     from numpy import mean, ma
#
#     if variable is None:
#         variable = get_variable(signal)
#
#     try:
#         var_signal = get_values(signal)
#         mask_l = get_values(low_agreement_mask)
#         mask_h = get_values(high_agreement_mask)
#
#         # mask_l = ma.masked_where(low < 0.5, low)
#         # mask_h = ma.masked_where(high < 0.5, high)
#         # mask_l[mask_l == 0] = np.nan
#         # mask_h[mask_h == 0] = np.nan
#
#         LOGGER.info('data loaded')
#
#         lats, lons = get_coordinates(signal, unrotate=True)
#
#         if len(lats.shape) == 1:
#             cyclic_var, cyclic_lons = add_cyclic_point(var_signal, coord=lons)
#             mask_l, cyclic_lons = add_cyclic_point(mask_l, coord=lons)
#             mask_h, cyclic_lons = add_cyclic_point(mask_h, coord=lons)
#
#             lons = cyclic_lons.data
#             var_signal = cyclic_var
#
#         LOGGER.info('lat lon loaded')
#
#         minval = round(np.nanmin(var_signal))
#         maxval = round(np.nanmax(var_signal)+.5)
#
#         LOGGER.info('prepared data for plotting')
#     except:
#         msg = 'failed to get data for plotting'
#         LOGGER.exception(msg)
#         raise Exception(msg)
#
#     try:
#         fig = plt.figure(facecolor='w', edgecolor='k')
#
#         ax = plt.axes(projection=ccrs.Robinson(central_longitude=int(mean(lons))))
#         norm = MidpointNormalize(midpoint=0)
#
#         cs = plt.contourf(lons, lats, var_signal, 60, norm=norm, transform=ccrs.PlateCarree(),
#                           cmap=cmap, interpolation='nearest')
#
#         cl = plt.contourf(lons, lats, mask_l, 1, transform=ccrs.PlateCarree(), colors='none', hatches=[None, '/'])
#         ch = plt.contourf(lons, lats, mask_h, 1, transform=ccrs.PlateCarree(), colors='none', hatches=[None, '.'])
#         # artists, labels = ch.legend_elements()
#         # plt.legend(artists, labels, handleheight=2)
#         # plt.clim(minval,maxval)
#         ax.coastlines()
#         ax.gridlines()
#         # ax.set_global()
#
#         if title is None:
#             plt.title('%s with Agreement' % variable)
#         else:
#             plt.title(title)
#         plt.colorbar(cs)
#
#         plt.annotate('// = low model ensemble agreement', (0, 0), (0, -10),
#                      xycoords='axes fraction', textcoords='offset points', va='top')
#         plt.annotate('..  = high model ensemble agreement', (0, 0), (0, -20),
#                      xycoords='axes fraction', textcoords='offset points', va='top')
#
#         graphic = fig2plot(fig=fig, file_extension=file_extension)
#         plt.close()
#
#         LOGGER.info('Plot created and figure saved')
#     except:
#         msg = 'failed to plot graphic'
#         LOGGER.exception(msg)
#
#     return graphic
