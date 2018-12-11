"""
In theory, libarchive can do this for us but in practice the python wrappers do not implement encryption.
We can look into forking the library and adding support.

https://github.com/libarchive/libarchive/commit/f31a5a02722adc67186a86b300ec88eb5c687dfb
https://github.com/dsoprea/PyEasyArchive and add support,
"""
from os import devnull
from shutil import rmtree
from subprocess import (
    call,
    Popen
)
from tempfile import mkdtemp
from time import sleep

# Pause for 2 seconds so 7z has a chance to start (dunno what load is like)
PAUSE = 0.5


def _filthy_subprocess_solution(command, _file):
    get_in_the_sea = open(devnull, 'wb')
    binary = command.split(' ')[0]
    if call('which {}'.format(binary).split(' '), stdout=get_in_the_sea, stderr=get_in_the_sea) != 0:
        raise Exception('{} cmd line application is missing'.format(binary))
    encrypted = False
    tempdir = None
    try:
        tempdir = mkdtemp()
        proc = Popen(
            command.format(target=tempdir, archive=_file.name).split(' '),
            stdout=get_in_the_sea,
            stderr=get_in_the_sea
        )
        sleep(PAUSE)
        poll = proc.poll()
        if poll is None or poll == 0:
            # still extracting or successfully extracted
            proc.kill()
        else:
            encrypted = True
    except:
        pass
    finally:
        if tempdir:
            rmtree(tempdir)
    return encrypted


def filthy_7zip_solution(_file):
    return _filthy_subprocess_solution(command="7z e -p'' -o{target} {archive}", _file=_file)


def filthy_rar_solution(_file):
    return _filthy_subprocess_solution(command="unrar e -p- {archive} {target}", _file=_file)
