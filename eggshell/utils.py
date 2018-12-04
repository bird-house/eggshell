# -*- coding: utf-8 -*-

"""Utitility functions."""

import os
import tempfile
import tarfile
import zipfile

import logging

LOGGER = logging.getLogger("EGGSHELL")


def archive(resources, format=None, output_dir=None, mode=None):
    """
    Compresses a list of files into an archive.

    :param resources: list of files to be stored in archive
    :param format: archive format. Options: tar (default), zip
    :param output_dir: path to output folder (default: tempory folder)
    :param mode: for format='tar':
                  'w' or 'w:'  open for writing without compression
                  'w:gz'       open for writing with gzip compression
                  'w:bz2'      open for writing with bzip2 compression
                  'w|'         open an uncompressed stream for writing
                  'w|gz'       open a gzip compressed stream for writing
                  'w|bz2'      open a bzip2 compressed stream for writing

                  for foramt='zip':
                  read "r", write "w" or append "a"

    :return str: archive path/filname.ext
    """
    format = format or 'tar'
    output_dir = output_dir or tempfile.gettempdir()
    mode = mode or 'w'

    if format not in ['tar', 'zip']:
        raise Exception('archive format {} not supported (only zip and tar)'.format(format))

    LOGGER.info('compressing files to archive, format={}'.format(format))

    # convert to list if necessary
    if not isinstance(resources, list):
        resources = list([resources])
    resources = [x for x in resources if x is not None]

    _, archive = tempfile.mkstemp(dir=output_dir, suffix='.{}'.format(format))

    try:
        if format == 'tar':
            with tarfile.open(archive, mode) as tar:
                for f in resources:
                    tar.add(f, arcname=os.path.basename(f))
        elif format == 'zip':
            with zipfile.ZipFile(archive, mode=mode) as zf:
                for f in resources:
                    zf.write(f, os.path.basename(f))
    except Exception as e:
        raise Exception('failed to create {} archive: {}'.format(format, e))
    return archive


def extract_archive(resources, output_dir=None):
    """
    extracts archives (tar/zip)

    :param resources: list of archive files (if netCDF files are in list,
                     they are passed and returnd as well in the return).
    :param output_dir: define a directory to store the results (default: tempory folder).

    :return list: [list of extracted files]
    """
    output_dir = output_dir or tempfile.gettempdir()

    if not isinstance(resources, list):
        resources = list([resources])
    files = []

    for archive in resources:
        try:
            LOGGER.debug("archive=%s", archive)
            ext = os.path.basename(archive).split('.')[-1]

            if ext == 'nc':
                files.append(os.path.join(output_dir, archive))
            elif ext == 'tar':
                with tarfile.open(archive, mode='r') as tar:
                    tar.extractall()
                    files.extend([os.path.join(output_dir, f) for f in tar.getnames()])
            elif ext == 'zip':
                with zipfile.open(archive, mode='r') as zf:
                    zf.extractall()
                    files.extend([os.path.join(output_dir, f) for f in zf.filelist])
            else:
                LOGGER.warn('file extention {} unknown'.format(ext))
        except Exception:
            LOGGER.error('failed to extract sub archive {}'.format(archive))
    return files

def get_coordinates(resource, variable=None, unrotate=False):
    """
    reads out the coordinates of a variable

    :param resource: netCDF resource file
    :param variable: variable name
    :param unrotate: If True the coordinates will be returned for unrotated pole

    :returns list, list: latitudes , longitudes
    """
    if type(resource) != list:
        resource = [resource]

    if variable is None:
        variable = get_variable(resource)

    if unrotate is False:
        try:
            if len(resource) > 1:
                ds = MFDataset(resource)
            else:
                ds = Dataset(resource[0])

            var = ds.variables[variable]
            dims = list(var.dimensions)
            if 'time' in dims: dims.remove('time')
            # TODO: find position of lat and long in list and replace dims[0] dims[1]
            lats = ds.variables[dims[0]][:]
            lons = ds.variables[dims[1]][:]
            ds.close()
            LOGGER.info('got coordinates without pole rotation')
        except Exception:
            msg = 'failed to extract coordinates'
            LOGGER.exception(msg)
    else:
        lats, lons = unrotate_pole(resource)
        LOGGER.info('got coordinates with pole rotation')
    return lats, lons
    

def rename_complexinputs(complexinputs):
    """
    TODO: this method is just a dirty workaround to rename input files according to the url name.
    """
    resources = []
    for inpt in complexinputs:
        new_name = inpt.url.split('/')[-1]
        os.rename(inpt.file, new_name)
        resources.append(os.path.abspath(new_name))
    return resources
