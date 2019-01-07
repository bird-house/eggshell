# from eggshell.nc import nc_fetch
# from eggshell import utils

from ocgis import RequestDataset, OcgOperations, env
from ocgis.util.large_array import compute
from os import listdir
from os.path import join

from datetime import datetime as dt
import uuid

env.OVERWRITE = True

# years = range(2015,2017)
#
# ncs = []
# for year in years:
#     url = 'https://www.esrl.noaa.gov/psd/thredds/fileServer/Datasets/ncep.reanalysis.dailyavgs/pressure/slp.%s.nc'
# % (year)
#     ncs.extend([utils.download_file(url)])
# # print ncs

level_range = [700, 700]
#  time_range = [dt.strptime('20100315', '%Y%m%d'), dt.strptime('20111210', '%Y%m%d')]
bbox = [-80, 20, 20, 70]

p = '/home/nils/data/CORDEX/'
ncs = [join(p, nc) for nc in listdir(p) if ".nc" in nc]
ncs.sort()

#ncs = datafetch.reanalyses(start=2000, end=2003)

# TODO: BUG: ocg compute is not running if calc == None
# calc = '%s=%s*1' % (variable, variable)

rd = RequestDataset(ncs)

ops = OcgOperations(rd,
                    # time_range=time_range,
                    calc='%s=%s*1' % ('tas', 'tas'),
                    # level_range=level_range,
                    geom=bbox,
                    output_format='nc',
                    prefix='ocgis_module_optimisation',
                    dir_output='/home/nils/data/',
                    add_auxiliary_files=False)

shnip = dt.now()
geom = ops.execute()
shnap = dt.now()
duration = (shnap - shnip).total_seconds()
print("operation performed with execute in {} sec.".format(duration))
print(geom)

tile_dimension = 5  # default

shnip = dt.now()
geom = compute(ops, tile_dimension=tile_dimension, verbose=True)
shnap = dt.now()
duration = (shnap - shnip).total_seconds()

print("operation performed with compute in {} sec.".format(duration))
print(geom)


# ###################################
# check free memory available somehow
# from eggshell import util_functions as ufs
# free_memory = ufs.FreeMemory(unit='MB')
#
# # ###########################
# # check required memory space
#
# data_kb = ops.get_base_request_size()['total']
# data_mb = data_kb / 1024.
#
# # ###########################
# # check if half of the available memory can take the required data load
#
# if data_mb < fm.user_free/2:
# print "enough memory. data can be processed directly"

########################
# simulation if memory is not enough for the dataload. Than calculate in chunks

fm_sim = data_mb / 2

if data_mb >= fm_sim:
    print("NOT enough memory. data will be processed in chunks")
    # calculate tile dimension:
    tile_dimension = 10
# TODO: needs to be calculated based on dataload and available memory
