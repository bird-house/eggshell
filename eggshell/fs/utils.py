import six
import urlparse
import os
import requests
import shutil
from datetime import datetime as dt
import time
import logging
import eggshell.config
from pywps import configuration
LOGGER = logging.getLogger("PYWPS")


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
    from tempfile import mkstemp
    from os.path import basename

    LOGGER.info('compressing files to archive')
    try:
        if isinstance(resources, str):
            resources = list([resources])

        resources_filter = [x for x in resources if x is not None]
        resources = resources_filter
    except Exception as e:
        msg = 'failed to prepare file list: %s' % e
        LOGGER.exception(msg)
        raise Exception(msg)

    if format == 'tar':
        import tarfile
        try:
            o1, archive = mkstemp(dir=dir_output, suffix='.tar')
            tar = tarfile.open(archive, mode)

            for f in resources:
                try:
                    tar.add(f, arcname=basename(f))
                except Exception as e:
                    msg = 'archiving failed for %s: %s' % (f, e)
                    LOGGER.exception(msg)
                    raise Exception(msg)
            tar.close()
        except Exception as e:
            msg = 'failed to compress into archive %s', e
            LOGGER.exception(msg)
            raise Exception(msg)
    elif format == 'zip':
        import zipfile

        LOGGER.info('creating zip archive')
        try:
            o1, archive = mkstemp(dir=dir_output, suffix='.zip')
            zf = zipfile.ZipFile(archive, mode=mode)
            for f in resources:
                zf.write(f, basename(f))
            zf.close()
        except Exception as e:
            msg = 'failed to create zip archive: %s' % e
            LOGGER.exception(msg)
            raise Exception(msg)
            # LOGGER.info(print_info('zipfile_write.zip'))
    else:
        raise Exception('no common archive format like: zip / tar')
    return archive


def archiveextract(resource, path='.'):
    """
    extracts archives (tar/zip)

    :param resource: list/str of archive files (if netCDF files are in list,
                     they are passed and returnd as well in the return)
    :param path: define a directory to store the results (default='.')

    :return list: [list of extracted files]
    """
    from tarfile import open
    import zipfile
    from os.path import basename, join

    try:
        if isinstance(resource, six.string_types):
            resource = [resource]
        files = []

        for archive in resource:
            try:
                LOGGER.debug("archive=%s", archive)
                # if mime_type == 'application/x-netcdf':
                if basename(archive).split('.')[-1] == 'nc':
                    files.append(join(path, archive))
                # elif mime_type == 'application/x-tar':
                elif basename(archive).split('.')[-1] == 'tar':
                    tar = open(archive, mode='r')
                    tar.extractall()
                    files.extend([join(path, nc) for nc in tar.getnames()])
                    tar.close()
                # elif mime_type == 'application/zip':
                elif basename(archive).split('.')[1] == 'zip':
                    zf = zipfile.open(archive, mode='r')
                    zf.extractall()
                    files.extend([join(path, nc) for nc in zf.filelist])
                    zf.close()
                else:
                    LOGGER.warn('file extention unknown')
            except Exception as e:
                LOGGER.exception('failed to extract sub archive')
    except Exception as e:
        LOGGER.exception('failed to extract archive resource')
    return files

def check_creationtime(path, url):
    """
    Compares the creation time of an archive file with the file creation time of the local disc space.

    :param path: Path to the local file
    :param url: URL to the archive file

    :returns boolean: True/False (True if archive file is newer)
    """

    try:
        req = requests.head(url)
        LOGGER.debug('headers: %s', req.headers.keys())
        if 'Last-Modified' not in req.headers:
            return False
        LOGGER.info("Last Modified: %s", req.headers['Last-Modified'])

        # CONVERTING HEADER TIME TO UTC TIMESTAMP
        # ASSUMING 'Sun, 28 Jun 2015 06:30:17 GMT' FORMAT
        meta_modifiedtime = time.mktime(
            dt.strptime(req.headers['Last-Modified'], "%a, %d %b %Y %X GMT").timetuple())

        # file = 'C:\Path\ToFile\somefile.xml'
        if os.path.getmtime(path) < meta_modifiedtime:
            LOGGER.info("local file is older than archive file.")
            newer = True
        else:
            LOGGER.info("local file is up-to-date. Nothing to fetch.")
            newer = False
    except Exception:
        msg = 'failed to check archive and cache creation time assuming newer = False'
        LOGGER.exception(msg)
        newer = False
    return newer

def download(url, cache=None):
    """
    Downloads URL using the Python requests module to the current directory.

    :param URL: Link to the file.
    :param cache: If not None, then files will be downloaded to the given cache directory.

    :returns: Filename
    :rtype: str
    """
    try:
        if cache is not None:
            parsed_url = urlparse.urlparse(url)
            filename = os.path.join(cache, parsed_url.netloc, parsed_url.path.strip('/'))
            if os.path.exists(filename):
                LOGGER.info('file already in cache: %s', os.path.basename(filename))
                if check_creationtime(filename, url):
                    LOGGER.info('file in cache older than archive file, downloading: %s ', os.path.basename(filename))
                    os.remove(filename)
                    filename = download_file(url, out=filename)
            else:
                if not os.path.exists(os.path.dirname(filename)):
                    os.makedirs(os.path.dirname(filename))
                LOGGER.info('downloading: %s', url)
                filename = download_file(url, out=filename)
                # make softlink to current dir
                # os.symlink(filename, os.path.basename(filename))
# filename = os.path.basename(filename)
        else:
            filename = download_file(url)
        return filename

    except Exception:
        LOGGER.exception('failed to download data')




def download_file(url, out=None, verify=False):
    """Download URL to local file system.

    :param url: Link to file.
    :param out: Path to local copy.
    :param verify: Whether or not to check the TLS certificate (bool) or string indicating path to CA bundle. See requests.request for more info.

    :return: Local filename.
    :rtype: str

    """
    if out:
        local_filename = out
    else:
        local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True, verify=verify)
    with open(local_filename, 'wb') as fp:
        shutil.copyfileobj(r.raw, fp)
    return local_filename


def make_dirs(directory):
    """
    Create a directory if it does not already exist.

    :param direcory: Directory path
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

# TODO: Complete doc. Add example.
def local_path(url):
    """Return an URL."""
    url_parts = urlparse.urlparse(url)
    return url_parts.path


def actual_output_path(fn):
    """Return the path to an output file, adjusting for whether or not the server is active or not.

    Example
    -------
    On a local server it would yield something like::

       http://localhost:8090/wpsoutputs/flyingpigeon/af06fb/af06fb.nc

    While in test mode it would yield::

       file:///tmp/af06fb/af06fb.nc

    """
    outputurl = configuration.get_config_value('server', 'outputurl')
    outputpath = configuration.get_config_value('server', 'outputpath')

    return os.path.join(outputurl, os.path.relpath(fn, outputpath))


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


def searchfile(pattern, base_dir):
    """
    Search recursively for files with an given pattern within a base directory.

    :param pattern: file name pattern including wildcards (e.g. tas_*_day_*.nc)
    :param base_dir: base direcory of the direcory tree

    return:  list of fitting files
    """

    from os import path, walk
    import fnmatch

    nc_list = []
    for root, dir, files in walk(base_dir):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                nc_list.extend([path.join(root, name)])

    return nc_list

# TODO: Optimize and link to ocgis module.
class FreeMemory(object):
    """
    Non-cross platform way to get free memory on Linux. Note that this code
    uses the key word as, which is conditionally Python 2.5 compatible!
    If for some reason you still have Python 2.5 on your system, add in the head
    of your code, before all imports:
    from __future__ import with_statement
    """

    def __init__(self, unit='kB'):
        with open('/proc/meminfo', 'r') as mem:
            lines = mem.readlines()
        self._tot = int(lines[0].split()[1])
        self._free = int(lines[1].split()[1])
        self._buff = int(lines[2].split()[1])
        self._cached = int(lines[3].split()[1])
        self._shared = int(lines[20].split()[1])
        self._swapt = int(lines[14].split()[1])
        self._swapf = int(lines[15].split()[1])
        self._swapu = self._swapt - self._swapf
        self.unit = unit
        self._convert = self._faktor()

    def _faktor(self):
        """determine the conversion factor"""
        if self.unit == 'kB':
            return 1
        if self.unit == 'k':
            return 1024.0
        if self.unit == 'MB':
            return 1 / 1024.0
        if self.unit == 'GB':
            return 1 / 1024.0 / 1024.0
        if self.unit == '%':
            return 1.0 / self._tot
        else:
            raise Exception("Unit not understood")

    @property
    def total(self):
        return self._convert * self._tot

    @property
    def used(self):
        return self._convert * (self._tot - self._free)

    @property
    def used_real(self):
        """memory used which != cache or buffers"""
        return self._convert * (self._tot - self._free - self._buff - self._cached)

    @property
    def shared(self):
        return self._convert * (self._tot - self._free)

    @property
    def buffers(self):
        return self._convert * (self._buff)

    @property
    def cached(self):
        return self._convert * self._cached

    @property
    def user_free(self):
        """This is the free memory available for the user"""
        return self._convert * (self._free + self._buff + self._cached)

    @property
    def swap(self):
        return self._convert * self._swapt

    @property
    def swap_free(self):
        return self._convert * self._swapf

    @property
    def swap_used(self):
        return self._convert * self._swapu

def prepare_static_folder(paths):
    """
    Link static folder to output folder.
    """
    destination = os.path.join(paths.output_path, 'static')
    if not os.path.exists(destination):
        os.symlink(paths.static_path, destination)