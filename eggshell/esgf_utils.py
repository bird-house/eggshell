
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
        ds = Dataset(resource)
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
