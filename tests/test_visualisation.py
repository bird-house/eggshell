

def test_plotlibs():
    from matplotlib import pyplot as plt
    import matplotlib

    from matplotlib import pyplot as plt
    from matplotlib.colors import Normalize
    from cartopy import config as cartopy_config
    from cartopy.util import add_cyclic_point
    import cartopy.crs as ccrs
    from cartopy.io.shapereader import Reader
    from cartopy.feature import ShapelyFeature



# def test_polygons():
#     from flyingpigeon.visualisation import plot_polygons
#     from os.path import exists
#     from os import remove
#
#     png = plot_polygons(['DEU', 'ESP'])
#
#     assert exists(png) is True
#     remove(png)
#
#
# def test_map_spatial_analog():
#     from common import TESTDATA
#     from flyingpigeon.visualisation import map_spatial_analog
#
#     map_spatial_analog(TESTDATA['dissimilarity.nc'][7:])
#     plt.close()
