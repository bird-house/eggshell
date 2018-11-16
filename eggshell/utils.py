# -*- coding: utf-8 -*-

"""Utitility functions."""

import os
import tempfile
import tarfile
import zipfile

import logging

LOGGER = logging.getLogger("EGGSHELL")


def archive(resources, format='tar', dir_output='.', mode='w'):
    """
    Compresses a list of files into an archive.

    :param resources: list of files to be stored in archive
    :param format: archive format. Options: tar (default), zip
    :param dir_output: path to output folder (default current directory)
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
    LOGGER.info('compressing files to archive, format={}'.format(format))
    try:
        if isinstance(resources, str):
            resources = list([resources])

        resources_filter = [x for x in resources if x is not None]
        resources = resources_filter
    except Exception as e:
        raise Exception('failed to prepare file list: {}'.format(e))

    if format == 'tar':
        try:
            _, archive = tempfile.mkstemp(dir=dir_output, suffix='.tar')
            with tarfile.open(archive, mode) as tar:
                for f in resources:
                    tar.add(f, arcname=os.path.basename(f))
        except Exception as e:
            raise Exception('failed to create tar archive: {}'.format(e))
    elif format == 'zip':
        try:
            _, archive = tempfile.mkstemp(dir=dir_output, suffix='.zip')
            with zipfile.ZipFile(archive, mode=mode) as zf:
                for f in resources:
                    zf.write(f, os.path.basename(f))
        except Exception as e:
            raise Exception('failed to create zip archive: {}'.format(e))
    else:
        raise Exception('archive format {} not supported (only zip and tar)'.format(format))
    return archive
