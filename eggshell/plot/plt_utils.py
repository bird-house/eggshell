# encoding: utf8
from tempfile import mkstemp
import logging
# from matplotlib import use
# use('Agg')   # use this if no xserver is available
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection

# from cartopy import config as cartopy_config
# import cartopy.feature as cfeature
# from cartopy.util import add_cyclic_point
# import re

from matplotlib.colors import Normalize
import cartopy.crs as ccrs

LOGGER = logging.getLogger("PYWPS")


def fig2plot(fig, file_extension='png', output_dir='.', bbox_inches='tight', dpi=300, facecolor='w', edgecolor='k', figsize=(20, 10)):
    '''saving a matplotlib figure to a graphic

    :param fig: matplotlib figure object
    :param output_dir: directory of output plot
    :param file_extension: file file_extension (default='png')

    :return str: path to graphic
    '''

    _, graphic = mkstemp(dir=output_dir, suffix='.%s' % file_extension)
    fig.savefig(graphic, bbox_inches=bbox_inches, dpi=dpi, facecolor=facecolor, edgecolor=edgecolor, figsize=figsize)

    return graphic


class MidpointNormalize(Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))


def plot_polygons(regions, file_extension='png'):
    """
    extract the polygon coordinate and plot it on a worldmap

    :param regions: list of ISO abreviations for polygons

    :return png: map_graphic.png
    """

    from cartopy.io.shapereader import Reader
    from cartopy.feature import ShapelyFeature
    from numpy import mean, append

    import eggshell.config
    # from flyingpigeon import config
    DIR_SHP = config.shapefiles_path()

    if type(regions) == str:
        regions = list([regions])

    fname = join(DIR_SHP, "countries.shp")
    geos = Reader(fname).geometries()
    records = Reader(fname).records()
    central_latitude = []
    central_longitude = []

    for r in records:
        geo = geos.next()
        if r.attributes['ISO_A3'] in regions:
            x, y = geo.centroid.coords.xy
            central_longitude.append(x[0])
            central_latitude.append(y[0])

    fig = plt.figure(figsize=(20, 10))
    projection = ccrs.Orthographic(central_longitude=mean(central_longitude),
                                   central_latitude=mean(central_latitude),
                                   globe=None)  # Robinson()
    ax = plt.axes(projection=projection)

    geos = Reader(fname).geometries()
    records = Reader(fname).records()

    for r in records:
        geo = geos.next()
        if r.attributes['ISO_A3'] in regions:
            shape_feature = ShapelyFeature(geo, ccrs.PlateCarree(),
                                           edgecolor='black', color='coral')
            ax.add_feature(shape_feature)
    ax.coastlines()
    ax.gridlines()
    ax.stock_img()
    # ax.set_global()
    map_graphic = fig2plot(fig=fig, file_extension=file_extension)
    plt.close()

    return map_graphic


def concat_images(images, orientation='v'):
    """
    concatenation of images.

    :param images: list of images
    :param orientation: vertical ('v' default) or horizontal ('h') concatenation

    :return string: path to image
    """
    from PIL import Image
    import sys

    LOGGER.debug('Images to be concatinated: %s' % images)

    if len(images) > 1:
        try:
            images_existing = [img for img in images if os.path.exists(img)]
            open_images = map(Image.open, images_existing)
            w = max(i.size[0] for i in open_images)
            h = max(i.size[1] for i in open_images)
            nr = len(open_images)
            if orientation == 'v':
                result = Image.new("RGB", (w, h * nr))
                # p = nr # h / len(images)
                for i in range(len(open_images)):
                    oi = open_images[i]
                    cw = oi.size[0]
                    ch = oi.size[1]
                    cp = h * i
                    box = [0, cp, cw, ch+cp]
                    result.paste(oi, box=box)

            if orientation == 'h':
                result = Image.new("RGB", (w * nr, h))
                # p = nr # h / len(images)
                for i in range(len(open_images)):
                    oi = open_images[i]

                    cw = oi.size[0]
                    ch = oi.size[1]
                    cp = w * i
                    box = [cp, 0, cw+cp, ch]
                    result.paste(oi, box=box)

            ip, image = mkstemp(dir='.', suffix='.png')
            result.save(image)
        except:
            LOGGER.exception('failed to concat images')
            _, image = mkstemp(dir='.', suffix='.png')
            result = Image.new("RGB", (50, 50))
            result.save(image)
    elif len(images) == 1:
        image = images[0]
    else:
        LOGGER.exception('No concatable number of images: %s, Dummy will be produced' % len(images))
        _, image = mkstemp(dir='.', suffix='.png')
        result = Image.new("RGB", (50, 50))
        result.save(image)
    return image


def pdfmerge(pdfs):
    """
    merge a list of pdfs

    :param pdfs: list of pdf files

    :retun str: merged pdf
    """
    from PyPDF2 import PdfFileMerger

    # pdfs = ['file1.pdf', 'file2.pdf', 'file3.pdf', 'file4.pdf']
    try:
        merger = PdfFileMerger()
        for pdf in pdfs:
            merger.append(pdf)
        _, mergedpdf = mkstemp(dir='.', suffix='.pdf')
        merger.write(mergedpdf)
    except:
        LOGGER.excetion('failed to merge pdfs')
        _, mergedpdf = mkstemp(dir='.', suffix='.pdf')

    return mergedpdf
