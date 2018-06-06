from netcdf_utils import sort_by_time, get_timerange, get_variable
import netCDF4 as nc
import logging
from pyesgf.search.connection import SearchConnection
from pyesgf.search import TYPE_FILE
LOGGER = logging.getLogger("PYWPS")

ATTRIBUTE_TO_FACETS_MAP = dict(
    project_id='project',
    experiment='experiment',
    CORDEX_domain='domain',
    institute_id='institute',
    driving_model_id='driving_model',
)

def aggregations(resource):
    """
    Aggregate netcdf files by experiment.



    Example
    -------

    CORDEX: EUR-11_ICHEC-EC-EARTH_historical_r3i1p1_DMI-HIRHAM5_v1_day
    CMIP5:
    We collect for each experiment all files on the time axis:
    200101-200512, 200601-201012, ...

    Time axis is sorted by time.

    :param resource: list of netcdf files

    :return: dictionary with key=experiment
    """

    aggregations = {}
    for nc in resource:
        key = drs_filename(nc, skip_timestamp=True, skip_format=True)

        # collect files of each aggregation (time axis)
        if key in aggregations:
            aggregations[key]['files'].append(nc)
        else:
            aggregations[key] = dict(files=[nc])

    # collect aggregation metadata
    for key in aggregations.keys():
        # sort files by time
        aggregations[key]['files'] = sort_by_time(aggregations[key]['files'])
        # start timestamp of first file
        start, _ = get_timerange(aggregations[key]['files'][0])
        # end timestamp of last file
        _, end = get_timerange(aggregations[key]['files'][-1])
        aggregations[key]['from_timestamp'] = start
        aggregations[key]['to_timestamp'] = end
        aggregations[key]['start_year'] = int(start[0:4])
        aggregations[key]['end_year'] = int(end[0:4])
        aggregations[key]['variable'] = get_variable(aggregations[key]['files'][0])
        aggregations[key]['filename'] = "%s_%s-%s.nc" % (key, start, end)
    return aggregations


def drs_filename(resource, skip_timestamp=False, skip_format=False,
                 variable=None, rename_file=False, add_file_path=False):
    """
    Generate filename according to the data reference syntax (DRS)
    based on the metadata in the resource.

    :param add_file_path: if add_file_path=True, path to file will be added (default=False)
    :param resource: netcdf file
    :param skip_timestamp: if True then from/to timestamp != added to the filename
                           (default: False)
    :param variable: appropriate variable for filename, if not set (default), variable will
                      be determined. For files with more than one data variable,
                      the variable parameter has to be defined (default: )
                      example: variable='tas'
    :param rename_file: rename the file. (default: False)

    :returns str: DRS filename

    References
    ----------
    http://cmip-pcmdi.llnl.gov/cmip5/docs/cmip5_data_reference_syntax.pdf
    https://pypi.python.org/pypi/drslib
    """
    from os import path, rename

    try:
        ds = nc.Dataset(resource)
        if variable is None:
            variable = get_variable(resource)
        # CORDEX example: EUR-11_ICHEC-EC-EARTH_historical_r3i1p1_DMI-HIRHAM5_v1_day
        cordex_pattern = "{variable}_{domain}_{driving_model}_{experiment}_{ensemble}_{model}_{version}_{frequency}"
        # CMIP5 example: tas_MPI-ESM-LR_historical_r1i1p1
        cmip5_pattern = "{variable}_{model}_{experiment}_{ensemble}"
        filename = resource
        if ds.project_id == 'CORDEX' or ds.project_id == 'EOBS':
            filename = cordex_pattern.format(
                variable=variable,
                domain=ds.CORDEX_domain,
                driving_model=ds.driving_model_id,
                experiment=ds.experiment_id,
                ensemble=ds.driving_model_ensemble_member,
                model=ds.model_id,
                version=ds.rcm_version_id,
                frequency=ds.frequency)
        elif ds.project_id == 'CMIP5':
            # TODO: attributes missing in netcdf file for name generation?
            filename = cmip5_pattern.format(
                variable=variable,
                model=ds.model_id,
                experiment=ds.experiment,
                ensemble=ds.parent_experiment_rip
            )
        else:
            raise Exception('unknown project %s' % ds.project_id)
        ds.close()
    except Exception:
        LOGGER.exception('Could not read metadata %s', resource)
    try:
        # add from/to timestamp if not skipped
        if skip_timestamp is False:
            LOGGER.debug("add timestamp")
            from_timestamp, to_timestamp = get_timerange(resource)
            LOGGER.debug("from_timestamp %s", from_timestamp)
            filename = "%s_%s-%s" % (filename, int(from_timestamp), int(to_timestamp))

        # add format extension
        if skip_format is False:
            filename = filename + '.nc'

        pf = path.dirname(resource)
        # add file path
        if add_file_path is True:
            filename = path.join(pf, filename)

        # rename the file
        if rename_file is True:
            if path.exists(path.join(resource)):
                rename(resource, path.join(pf, filename))
    except Exception:
        LOGGER.exception('Could not generate DRS filename for %s', resource)

    return filename


def search_landsea_mask_by_esgf(resource):
    """
    Search the ESGF for a land-sea mask (variable sftlf) associated with
    the given netCDF `resource`.

    The attributes of the resource are extracted and used to find the mask
    for the same domain, model, project and experiment. An exception is raised
    if no mask is found.

    :param str resource: Path to netCDF file.

    :returns: OpenDAP URL of the first mask file found.
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