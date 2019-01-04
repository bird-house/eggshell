# from snappy import ProductIO
# from snappy import ProductUtils
# from snappy import ProgressMonitor
# from snappy import jpy

from matplotlib import pyplot as plt

from os.path import splitext, basename
from os.path import join
from tempfile import mkstemp
import numpy as np

from eggshell.plot import plt_utils

import logging
LOGGER = logging.getLogger("PYWPS")


def plot_products(products, extend=[10, 20, 5, 15], dir_output='.'):
    """
    plot the products extends of the search result

    :param products: output of sentinelapi search
    :parm extend: extend of the background map to be plotted
    :param dir_output: path to folder where to store the returned graphic

    :return png: map of extents
    """
    LOGGER.info('Start plotting extend of found products')

    from matplotlib.patches import Polygon
    import matplotlib.patches as mpatches
    from matplotlib.collections import PatchCollection
    import cartopy.crs as ccrs
    from cartopy import feature as cfeature
    import re

    try:
        fig = plt.figure(dpi=90, facecolor='w', edgecolor='k')
        projection = ccrs.PlateCarree()
        ax = plt.axes(projection=projection)
        ax.set_extent(extend)
        ax.stock_img()
        ax.coastlines()
        ax.add_feature(cfeature.BORDERS)

        pat = re.compile(r'''(-*\d+\.\d+ -*\d+\.\d+);*''')
        LOGGER.info('plot configured')

        for key in products.keys():
            try:
                polygon = str(products[key]['footprint'])
                matches = pat.findall(polygon)
                if matches:
                    xy = np.array([m.split() for m in matches])
                    # [map(float, m.split()) for m in matches]
                    ax.add_patch(mpatches.Polygon(xy, closed=True,
                                                  transform=ccrs.PlateCarree(),
                                                  alpha=0.4))
                    #  color='coral'
                LOGGER.info('Polygon plotted')
            except Exception as ex:
                LOGGER.exception('failded to plot polygon {}'.format(ex))
        # ccrs.Geodetic()
        ax.gridlines(draw_labels=True,)
        img = plt_utils.fig2plot(fig, dir_output=dir_output)
        LOGGER.info('extend plotted')
    except Exception as ex:
        LOGGER.exception('failed to plot EO products {}'.format(ex))
        _, img = mkstemp(dir=dir_output, prefix='dummy_', suffix='.png')
    return img


def plot_RGB(DIR, colorscheem='natural_color'):
    """
    Extracts the files for RGB bands of Sentinel2 directory tree, scales and merge the values.
    Output is a merged tif including 3 bands.

    :param DIR: base directory of Sentinel2 directory tree
    :param colorscheem: usage of bands (default=natural_color will use B4,B3,B2 for red,green,blue)

    :returns: png image
    """

    # from snappy import ProductIO
    # from snappy import ProductUtils
    # from snappy import ProgressMonitor
    # from snappy import jpy
    #
    # from os.path import splitext, basename
    # from os.path import join


    mtd = 'MTD_MSIL1C.xml'
    fname = DIR.split('/')[-1]
    ID = fname.replace('.SAFE','')

    # _, rgb_image = mkstemp(dir='.', prefix=prefix , suffix='.png')
    source = join(DIR, mtd)

    sourceProduct = ProductIO.readProduct(source)

    if colorscheem == 'naturalcolors':
        red = sourceProduct.getBand('B4')
        green = sourceProduct.getBand('B3')
        blue = sourceProduct.getBand('B2')

    elif colorscheem == 'falsecolors-vegetation':
        red = sourceProduct.getBand('B8')
        green = sourceProduct.getBand('B4')
        blue = sourceProduct.getBand('B3')

    elif colorscheem == 'falsecolors-urban':
        red = sourceProduct.getBand('B12')
        green = sourceProduct.getBand('B11')
        blue = resample(source, 'B4', 20)  # sourceProduct.getBand('B4')

    elif colorscheem == 'athmospheric-penetration':
        red = sourceProduct.getBand('B12')
        green = sourceProduct.getBand('B11')
        blue = sourceProduct.getBand('B8a')

    elif colorscheem == 'agriculture':
        red = sourceProduct.getBand('B11')
        green = resample(source, 'B8', 20)
        blue = resample(source, 'B2', 20)

    elif colorscheem == 'healthy-vegetation':
        red = sourceProduct.getBand('B8')
        green = resample(source, 'B11', 10)
        blue = sourceProduct.getBand('B2')

    elif colorscheem == 'land-water':
        red =  resample(source, 'B8', 20)
        green = sourceProduct.getBand('B11')
        blue = resample(source, 'B4', 20 )

    elif colorscheem == 'naturalcolors-athmosphericremoval':
        red = sourceProduct.getBand('B12')
        green = resample(source, 'B8', 20)
        blue = resample(source, 'B3', 20)

    elif colorscheem == 'shortwave-infrared':
        red = sourceProduct.getBand('B12')
        green = resample(source, 'B8', 20)
        blue = resample(source, 'B4',20)

    elif colorscheem == 'vegetation-analyses':
        red = sourceProduct.getBand('B11')
        green = resample(source, 'B8', 20)
        blue = resample(source, 'B4',20)

    else:
        LOGGER.debug('colorscheem %s not found ' % colorscheem)

    Color = jpy.get_type('java.awt.Color')
    ColorPoint = jpy.get_type('org.esa.snap.core.datamodel.ColorPaletteDef$Point')
    ColorPaletteDef = jpy.get_type('org.esa.snap.core.datamodel.ColorPaletteDef')
    ImageInfo = jpy.get_type('org.esa.snap.core.datamodel.ImageInfo')
    ImageLegend = jpy.get_type('org.esa.snap.core.datamodel.ImageLegend')
    ImageManager = jpy.get_type('org.esa.snap.core.image.ImageManager')
    JAI = jpy.get_type('javax.media.jai.JAI')
    RenderedImage = jpy.get_type('java.awt.image.RenderedImage')

    # Disable JAI native MediaLib extensions
    System = jpy.get_type('java.lang.System')
    System.setProperty('com.sun.media.jai.disableMediaLib', 'true')

    #
    legend = ImageLegend(blue.getImageInfo(), blue)
    legend.setHeaderText(blue.getName())

    # red = product.getBand('B4')
    # green = product.getBand('B3')
    # blue = product.getBand('B2')
    # from tempfile import mkstemp
    # from PIL import Image
    #
    # _ , snapfile = mkstemp(dir='.', prefix='RGB_', suffix='.png')

    imagefile = '%s_%s.png' % (colorscheem, ID)

    image_info = ProductUtils.createImageInfo([red, green, blue], True, ProgressMonitor.NULL)
    im = ImageManager.getInstance().createColoredBandImage([red, green, blue], image_info, 0)
    JAI.create("filestore", im, imagefile, 'PNG')

    #
    # basewidth = 600
    # img = Image.open(snapfile)
    # wpercent = (basewidth / float(img.size[0]))
    # hsize = int((float(img.size[1]) * float(wpercent)))
    # img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    # img.save(imagefile)

    return imagefile



def plot_band(source, file_extension='PNG', colorscheem=None):
    """
    plots the first band of a geotif file

    :param source: geotif file containning one band with NDVI values
    :param file_extension: format of the output graphic. default='png'
    :param colorscheem: predifined colorscheem
                        allowed values: "NDVI", "BAI"
                        if None (default), plot will given as grayscale

    :result str: path to graphic file
    """
    # from snappy import ProductIO
    # from snappy import ProductUtils
    # from snappy import ProgressMonitor
    # from snappy import jpy
    #
    # from os.path import splitext, basename
    # from os.path import join


    try:
        LOGGER.debug('Start plotting Band')
        sourceProduct = ProductIO.readProduct(source)
        # bandname = list(sourceProduct.getBandNames())[0]
        # LOGGER.debug('bandname found: %s ' % bandname)
        ndvi = sourceProduct.getBand("band_1")
    except:
        LOGGER.exception("failed to read ndvi values")
    try:
        LOGGER.debug('read in org.esa information')
        # More Java type definitions required for image generation
        Color = jpy.get_type('java.awt.Color')
        ColorPoint = jpy.get_type('org.esa.snap.core.datamodel.ColorPaletteDef$Point')
        ColorPaletteDef = jpy.get_type('org.esa.snap.core.datamodel.ColorPaletteDef')
        ImageInfo = jpy.get_type('org.esa.snap.core.datamodel.ImageInfo')
        ImageLegend = jpy.get_type('org.esa.snap.core.datamodel.ImageLegend')
        ImageManager = jpy.get_type('org.esa.snap.core.image.ImageManager')
        JAI = jpy.get_type('javax.media.jai.JAI')
        RenderedImage = jpy.get_type('java.awt.image.RenderedImage')

        # Disable JAI native MediaLib extensions
        System = jpy.get_type('java.lang.System')
        System.setProperty('com.sun.media.jai.disableMediaLib', 'true')
    except:
        LOGGER.exception('failed to read in org.esa information')

    # points = [ColorPoint(-1.0, Color.WHITE),
    #           # ColorPoint(50.0, Color.RED),
    #           ColorPoint(1.0, Color.GREEN)]
    # cpd = ColorPaletteDef(points)
    # ii = ImageInfo(cpd)
    # ndvi.setImageInfo(ii)

    try:
        LOGGER.debug('write image')
        img_name = 'INDICE_%s.png' % (splitext(basename(source))[0])

        image_format = 'PNG'

        im = ImageManager.getInstance().createColoredBandImage([ndvi], ndvi.getImageInfo(), 0)
        JAI.create("filestore", im, img_name, image_format)
    except:
        LOGGER.exception('failed to write image')
    return img_name
