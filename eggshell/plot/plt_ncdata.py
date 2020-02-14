"""
visualization of netCDF data
"""

from tempfile import mkstemp
# from matplotlib import use
# use('Agg')   # use this if no xserver is available
import numpy as np

from matplotlib import pyplot as plt
from matplotlib import colors
from matplotlib.patches import Polygon
import matplotlib.patches as mpatches
import cartopy.feature as cfeature

import cartopy.crs as ccrs
from cartopy.util import add_cyclic_point

from eggshell.nc.calculation import fieldmean
from eggshell.nc.nc_utils import get_variable, get_frequency, get_coordinates
from eggshell.nc.nc_utils import get_time, sort_by_filename
from eggshell.plot.plt_utils import fig2plot

from numpy import meshgrid
from netCDF4 import Dataset
import numpy as np

import logging
LOGGER = logging.getLogger("PYWPS")

class MidpointNormalize(colors.Normalize):
    def __init__(self, vmin=None, vmax=None, vcenter=None, clip=False):
        self.vcenter = vcenter
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.vcenter, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))


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


def spaghetti(resource, variable=None, title=None, file_extension='png', dir_output='.'):
    """
    creates a png file containing the appropriate spaghetti plot as a field mean of the values.

    :param resource: list of files containing the same variable
    :param variable: variable to be visualised. If None (default), variable will be detected
    :param title: string to be used as title

    :retruns str: path to png file
    """
    # from eggshell.nc.calculation import fieldmean

    try:
        fig = plt.figure(figsize=(20, 10), dpi=600, facecolor='w', edgecolor='k')
        LOGGER.debug('Start visualisation spaghetti plot')

        # === prepare invironment
        if type(resource) != list:
            resource = [resource]
        if variable is None:
            variable = get_variable(resource[0])
        if title is None:
            title = "Field mean of %s " % variable

        LOGGER.info('plot values preparation done')
    except Exception as ex:
        msg = "plot values preparation failed {}".format(ex)
        LOGGER.exception(msg)
        raise Exception(msg)
    try:
        for c, nc in enumerate(resource):
            try:
                # dt = get_time(nc)
                # ts = fieldmean(nc)

                if 'historical' in nc:
                    col = 'grey'
                elif 'evaluation' in nc:
                    col = 'black'
                elif 'rcp26' in nc:
                    col = 'blue'
                elif 'rcp85' in nc:
                    col = 'red'
                else:
                    col = 'green'

                dt = get_time(nc) # [datetime.strptime(elem, '%Y-%m-%d') for elem in strDate[0]]
                # ts = fieldmean(nc)

                ds = Dataset(nc)
                var = get_variable(nc)
                tg_val = np.squeeze(ds.variables[var][:])
                d2 = np.nanmean(tg_val, axis=1)
                ts = np.nanmean(d2, axis=1)

                plt.plot(dt, ts, col )
                plt.grid()
                plt.title(title)
                #
                # plt.plot(dt, ts)
                # fig.line( dt,ts )
            except Exception as e:
                msg = "spaghetti plot failed for {} : {}".format(nc, e)
                LOGGER.exception(msg)

        plt.title(title, fontsize=20)
        plt.grid()

        output_png = fig2plot(fig=fig, file_extension=file_extension, dir_output=dir_output)

        plt.close()
        LOGGER.info('timeseries spaghetti plot done for %s with %s lines.' % (variable, c))
    except Exception as ex:
        msg = 'matplotlib spaghetti plot failed: {}'.format(ex)
        LOGGER.exception(msg)
    return output_png


def uncertainty(resource, variable=None, ylim=None, title=None,
                file_extension='png', delta=0, window=None, dir_output='.',
                figsize=(10,10)):
    """
    creates a png file containing the appropriate uncertainty plot.

    :param resource: list of files containing the same variable
    :param variable: variable to be visualised. If None (default), variable will be detected
    :param title: string to be used as title
    :param figsize: figure size defult=(10,10)
    :param window: windowsize of the rolling mean

    :returns str: path/to/file.png
    """
    LOGGER.debug('Start visualisation uncertainty plot')

    import pandas as pd
    import numpy as np
    from datetime import datetime as dt
    from os.path import basename
    #
    # from flyingpigeon.utils import get_time, sort_by_filename
    # from flyingpigeon.calculation import fieldmean
    # from flyingpigeon.metadata import get_frequency

    # === prepare invironment
    if type(resource) == str:
        resource = list([resource])
    if variable is None:
        variable = get_variable(resource[0])
    if title is None:
        title = "Field mean of %s " % variable

    LOGGER.info('variable %s found in resource.' % variable)

    try:
        fig = plt.figure(figsize=figsize, facecolor='w', edgecolor='k')

        dic = sort_by_filename(resource, historical_concatination=True)

        # Create index out of existing timestemps
        for i, key in enumerate(dic.keys()):
            for nc in dic[key]:
                ds = Dataset(nc)
                ts = get_time(nc)
                if i == 0:
                    dates = pd.DatetimeIndex(ts)
                else:
                    dates = dates.union(ts)

        # create empty DataFrame according existing timestemps
        df = pd.DataFrame(columns=list(dic.keys()), index=dates)

        for key in dic.keys():
            try:
                for nc in dic[key]:
                    ds = Dataset(nc)
                    var = get_variable(nc)
                    ts = get_time(nc)
                    tg_val = np.squeeze(ds.variables[var][:])
                    d2 = np.nanmean(tg_val, axis=1)
                    data = np.nanmean(d2, axis=1) + delta
                    df[key].loc[ts] = data
                    # data = fieldmean(dic[key])  # get_values(f)
                    # ts = get_time(dic[key])
                    # ds = pd.Series(data=data, index=ts, name=key)
                    # # ds_yr = ds.resample('12M', ).mean()   # yearly mean loffset='6M'
                    # df[key] = ds
                LOGGER.info('read in pandas series timeseries for: {}'.format(key))
            except Exception:
                LOGGER.exception('failed to calculate timeseries for %s ' % (key))

        frq = get_frequency(resource[0])

        if window is None:
            # if frq == 'day':
            #     window = 1095  # 1
            # elif frq == 'man':
            #     window = 35  # 9
            # elif frq == 'sem':
            #     window = 11  # 9
            # elif frq == 'yr':
            #     window = 3  # 0
            # else:
            #     LOGGER.debug('frequency %s is not included' % frq)
            window = 10

        print('frequency: {}, window: {}'.format(frq, window))

        if len(df.index.values) >= window * 2:
            # TODO: calculate windowsize according to timestapms (day,mon,yr ... with get_frequency)
            df_smooth = df.rolling(window=window, center=True).mean()
            LOGGER.info('rolling mean calculated for all input data')
        else:
            df_smooth = df.copy()
            LOGGER.debug('timeseries too short for moving mean')
            fig.text(0.95, 0.05, '!!! timeseries too short for moving mean over 30years !!!',
                     fontsize=20, color='red',
                     ha='right', va='bottom', alpha=0.5)

        try:
            rmean = np.squeeze(df_smooth.quantile([0.5], axis=1,).values)
            # skipna=False  quantile([0.5], axis=1, numeric_only=False )
            q05 = np.squeeze(df_smooth.quantile([0.10], axis=1,).values)  # numeric_only=False)
            q33 = np.squeeze(df_smooth.quantile([0.33], axis=1,).values)  # numeric_only=False)
            q66 = np.squeeze(df_smooth.quantile([0.66], axis=1,).values)  # numeric_only=False)
            q95 = np.squeeze(df_smooth.quantile([0.90], axis=1,).values)  # numeric_only=False)
            LOGGER.info('quantile calculated for all input data')
        except Exception as e:
            LOGGER.exception('failed to calculate quantiles: {}'.format(e))

        try:
            x = pd.to_datetime(df.index.values)
            x1 = x[x<=dt.strptime('2005-12-31',  "%Y-%m-%d")]
            x2 = x[len(x1)-1:]  # -1 to catch up with the last historical value

            plt.fill_between(x, q05, q95, alpha=0.5, color='grey')
            plt.fill_between(x, q33, q66, alpha=0.5, color='grey')

            plt.plot(x1, rmean[:len(x1)], c='blue', lw=3)
            plt.plot(x2, rmean[len(x1)-1:], c='r', lw=3)
            # plt.xlim(min(df.index.values), max(df.index.values))
            plt.ylim(ylim)
            plt.xticks(fontsize=16, rotation=45)
            plt.yticks(fontsize=16, ) # rotation=90
            plt.title(title, fontsize=20)
            plt.grid()  # .grid_line_alpha=0.3

            output_png = fig2plot(fig=fig, file_extension=file_extension, dir_output=dir_output)
            plt.close()
            LOGGER.debug('timeseries uncertainty plot done for %s' % variable)
        except Exception as e:
            raise Exception('failed to calculate quantiles. {}'.format(e))
    except Exception as e:
        LOGGER.exception('uncertainty plot failed for {}: {}'.format(variable, e))
        _, output_png = mkstemp(dir='.', suffix='.png')
    return output_png


def plot_spatial_analog(ncfile, variable='dissimilarity', cmap='viridis', title='Spatial analog'):
    """Return a matplotlib Figure instance showing a map of the dissimilarity measure.
    """
    import netCDF4 as nc
    from eggshell.nc import nc_utils
    from mpl_toolkits.axes_grid import make_axes_locatable
    import matplotlib.axes as maxes

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


def plot_map(resource, variable,
             title=None, delta=0, cmap=None,
             file_extension='png', dir_output='.'):
    """
    creates a png file containing the appropriate uncertainty plot.

    :param resource: one netCDF file containng spatial values to be plotted
    :param variable: variable to be visualised. If None (default), variable will be detected
    :param title: string to be used as title
    :param delta: set a delta for the values e.g. -273.15 to convert kelvin to temperaure
    :param file_extension: file extinction for the graphic
    :param dir_output: output directory to store the output graphic

    :returns str: path/to/file.png
    """

    try:
        LOGGER.debug('plot_map function read in values for {}'.format(resource))

        # get values of netcdf file
        ds = Dataset(resource)

        if variable is None:
            variable = get_variable(resource)

        lat = ds.variables['rlat']
        lon = ds.variables['rlon']
        lons, lats = meshgrid(lon, lat)

        var = ds.variables[variable]
        var_mean = np.nanmean(var, axis=0) + delta # mean over whole periode 30 Years 1981-2010 and transform to Celsius

        # prepare plot
        LOGGER.info('preparing matplotlib figure')
        fig = plt.figure(figsize=(20, 10), facecolor='w', edgecolor='k')
        ax = plt.axes(projection=ccrs.PlateCarree())

        # extent=(-0,17,10.5,24)
        # ax.set_extent(extent)

        ax.add_feature(cfeature.BORDERS, linewidth=2, linestyle='--')
        # ax.add_feature(cfeature.RIVERS)
        # ax.stock_img()
        # ax.gridlines(draw_labels=False)
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                          linewidth=2, color='gray', alpha=0.5, linestyle='--')
        gl.xlabels_top = False
        gl.ylables_right = False
        # gl.xlines = False
        # gl.xlocator = mticker.FixedLocator([0, 2,4,6,8,10,12,14,16] )
        # gl.xformatter = LONGITUDE_FORMATTER
        # gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': 15, 'color': 'black'}
        gl.ylabel_style = {'size': 15, 'color': 'black'}
        # gl.xlabel_style = {'color': 'red', 'weight': 'bold'}

        # ax.xaxis.set_ticks_position('bottom')
        # ax.yaxis.set_ticks_position('left')
        # ax.colorbar

        plt.title(title, fontsize=20)

        if cmap is None:
            if variable in ['pr','prAdjust','prcptot','rx1day','wetdays','cdd','cwd','sdii','max_n_day_precipitation_amount']:
                cmap = 'Blues'
            if variable in ['tas', 'tasAdjust', 'tg', 'tg_mean']:
                cmap = 'seismic'

        cs = plt.pcolormesh(lons, lats, var_mean,
                            transform=ccrs.PlateCarree(), cmap=cmap,
                            # vmin=20, vmax=30,
                            )
        plt.colorbar(cs)
        LOGGER.info('Matplotlib pcolormesh plot done')

        output_png = fig2plot(fig=fig, file_extension='png',
                              dir_output=dir_output)
        plt.close()
        LOGGER.debug('Plot done for %s' % variable)
    except Exception as err:
        raise Exception('failed to calculate quantiles. %s' % err)

    return output_png


def plot_map_ccsignal(signal, standard_deviation=None,
                   variable=None, cmap=None, title=None,
                   file_extension='png'):  # 'seismic'
    """
    generates a graphic for the output of the ensembleRobustness process for a lat/long file.

    :param signal: netCDF file containing the signal difference over time
    :param standard_deviation:
    :param variable: variable containing the netCDF files
    :param cmap: default='seismic',
    :param title: default='Model agreement of signal'
    :returns str: path/to/file.png
    """
    # from flyingpigeon import utils

    from numpy import mean, ma

    if variable is None:
        variable = get_variable(signal)

    print('found variable in file {}'.format(variable))

    try:
        ds = Dataset(signal)
        var_signal = ds.variables[variable]
        val_signal = np.squeeze(ds.variables[variable])

        lon_att = var_signal.dimensions[-1]
        lat_att = var_signal.dimensions[-2]

        lon = ds.variables[lon_att][:]
        lat = ds.variables[lat_att][:]

        lons, lats = meshgrid(lon, lat)
        ds.close()

        if standard_deviation is not None:
            ds = Dataset(standard_deviation)
            val_std = np.squeeze(ds.variables[variable][:])
            ds.close()

            #  mask = val_signal[:]  #  [val_signal[:]<val_std[:]]

            mask_h = np.empty(list(val_signal[:].shape))    # [[val_signal[:] > val_std[:]]] = 1
            mask_h[(val_signal >= (val_std / 4.))] = 1   #[:]

            mask_l = np.empty(list(val_signal[:].shape))    # [[val_signal[:] > val_std[:]]] = 1
            mask_l[mask_h != 1] = 1


            # cyclic_var, cyclic_lons = add_cyclic_point(var_signal, coord=lons)
            # mask, cyclic_lons = add_cyclic_point(mask, coord=lons)
            #
            # lons = cyclic_lons
            # var_signal = cyclic_var

        LOGGER.info('prepared data for plotting')
    except Exception as e:
        msg = 'failed to get data for plotting: {}'.format(e)
        LOGGER.exception(msg)
        raise Exception(msg)

    try:
        fig = plt.figure(figsize=(20, 10), facecolor='w', edgecolor='k')
        ax = plt.axes(projection=ccrs.PlateCarree())
        # ax = plt.axes(projection=ccrs.Robinson(central_longitude=int(mean(lons))))

        # minval = round(np.nanmin(var_signal))
        if cmap is None:
            if variable in ['pr','prAdjust','prcptot','rx1day','wetdays','cdd','cwd','sdii','max_n_day_precipitation_amount']:
                cmap = 'BrBG'
            if variable in ['tas', 'tasAdjust', 'tg', 'tg_mean']:
                cmap = 'seismic'
        else:
            cmap = 'viridis'
            LOGGER.debug('variable {} not found to set the colormap'.format(variable))

        maxval = round(np.nanmax(val_signal)+.5)
        minval = round(np.nanmin(val_signal))

        norm = MidpointNormalize( vmin=minval, vcenter=0, vmax=maxval)  # )  vcenter=0,,

        cs = plt.pcolormesh(lons, lats, val_signal, transform=ccrs.PlateCarree(), cmap=cmap, norm=norm )    #, vmin=0, vmax=maxval
                #  60,
        plt.colorbar(cs)

        if standard_deviation != None:
            ch = plt.contourf(lons, lats, mask_h, transform=ccrs.PlateCarree(), hatches=[None, '.'], alpha=0, colors='none', cmap=None)    # colors='white'
            cl = plt.contourf(lons, lats, mask_l, 1, transform=ccrs.PlateCarree(), hatches=[None, '/'], alpha=0, colors='none', cmap=None)     # ,

            plt.annotate('// = low model ensemble agreement', (0, 0), (0, -10),
                         xycoords='axes fraction', textcoords='offset points', va='top')
            plt.annotate('..  = high model ensemble agreement', (0, 0), (0, -20),
                         xycoords='axes fraction', textcoords='offset points', va='top')

        # ch = plt.contourf(lons, lats, mask, 1, transform=ccrs.PlateCarree(), colors='none', hatches=[None,'.' ])

        ax.add_feature(cfeature.BORDERS, linewidth=2, linestyle='--')
        ax.add_feature(cfeature.COASTLINE, linewidth=2,) #  coastlines()
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                          linewidth=2, color='gray', alpha=0.5, linestyle='--')
        gl.xlabels_top = False
        gl.ylables_right = False
        gl.xlabel_style = {'size': 15, 'color': 'black'}
        gl.ylabel_style = {'size': 15, 'color': 'black'}

        if title != None:
            plt.title(title, fontsize=20 )


        # # artists, labels = ch.legend_elements()
        # # plt.legend(artists, labels, handleheight=2)
        #
        # ax.gridlines()
        # # ax.set_global()

        graphic = fig2plot(fig=fig, file_extension=file_extension)
        plt.close()

        LOGGER.info('Plot created and figure saved')
    except:
        msg = 'failed to plot graphic'
        LOGGER.exception(msg)

    return graphic





            # extent=(-0,17,10.5,24)
            # ax.set_extent(extent)


            # ax.add_feature(cfeature.RIVERS)
            # ax.stock_img()
            # ax.gridlines(draw_labels=False)

            # gl.xlines = False
            # gl.xlocator = mticker.FixedLocator([0, 2,4,6,8,10,12,14,16] )
            # gl.xformatter = LONGITUDE_FORMATTER
            # gl.yformatter = LATITUDE_FORMATTER

            # gl.xlabel_style = {'color': 'red', 'weight': 'bold'}

            # ax.xaxis.set_ticks_position('bottom')
            # ax.yaxis.set_ticks_position('left')
            # ax.colorbar
