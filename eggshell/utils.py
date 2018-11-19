# -*- coding: utf-8 -*-

"""Utitility functions."""

import six
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
    :param output_dir: path to output folder (default tempory folder)
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
