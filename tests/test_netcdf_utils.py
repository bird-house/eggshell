def test_libs():
    from netCDF4 import Dataset, MFDataset
    from netCDF4 import num2date

def test_iris():
    from iris.analysis import cartography as ct
    import iris.cube
    import iris.analysis
    from iris.analysis._area_weighted import AreaWeightedRegridder
    from iris.analysis._interpolation import get_xy_dim_coords, snapshot_grid
    from iris.analysis.cartography import wrap_lons as wrap_circular_points
    import cf_units
