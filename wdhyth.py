#!/usr/bin/env python
from __future__ import print_function
from msoffcrypto import OfficeFile
from os import fdopen
from PyPDF2 import PdfFileReader
from shutil import copyfileobj
from sys import (
    argv,
    exit,
    stderr,
    stdin
)
from tempfile import TemporaryFile
from filthy_solutions import (
    filthy_7zip_solution,
    filthy_rar_solution
)
from zipfile import (
    BadZipfile,
    ZipFile
)


def error(msg, exit_with_code=None):
    print(msg, file=stderr)
    if exit_with_code is not None:
        exit(exit_with_code)


def _is_pdf_encrypted(_file):
    return PdfFileReader(_file).isEncrypted


def _is_zip_encrypted(_file):
    # https://stackoverflow.com/questions/12038446/how-to-check-if-a-zip-file-is-encrypted-using-pythons-standard-library-zipfile
    with ZipFile(file=_file) as zf:
        for zinfo in zf.infolist():
            is_encrypted = zinfo.flag_bits & 0x1
            if is_encrypted:
                return True
    return False


def _is_7zip_encrypted(_file):
    return filthy_7zip_solution(_file=_file)


def _is_rar_encrypted(_file):
    return filthy_rar_solution(_file=_file)


def _is_ole_encrypted(_file):
    return OfficeFile(_file).is_encrypted()


def _is_ooxml_encrypted(_file):
    try:
        # It should be a zip file, if it doesn't open then it must be encrypted
        _is_zip_encrypted(_file=_file)
    except BadZipfile:
        return True
    return False


FILE_INSPECTORS = {
    'zip': _is_zip_encrypted,
    '7z': _is_7zip_encrypted,
    'rar': _is_rar_encrypted,
    'pdf': _is_pdf_encrypted,
    'doc': _is_ole_encrypted,
    'xls': _is_ole_encrypted,
    'ppt': _is_ole_encrypted,
    'docx': _is_ooxml_encrypted,
    'clsx': _is_ooxml_encrypted,
    'pptx': _is_ooxml_encrypted,
}


def help(exit_with_status=None):
    print(
        '''
./wdyhth.py FILE_TYPE [FILE_PATH]
        
If no FILE_PATH is provided, read from STDIN.
supported FILE_TYPE: {}
        '''.format(', '.join(FILE_INSPECTORS.keys()))
    )
    if exit_with_status is not None:
        exit(exit_with_status)


def get_file_type_from_args():
    if len(argv) not in [2, 3]:
        error('Please provide the filetype of the streamed file as the first argument')
        help(exit_with_status=1)

    file_type = argv[1].lower()
    if file_type not in FILE_INSPECTORS:
        error(
            'The provided filetype "{}" is not one of the supported file types: {}'.format(
                file_type,
                FILE_INSPECTORS.keys()
            ),
            exit_with_code=1
        )
    return file_type


def main():
    file_type = get_file_type_from_args()
    file_inspector = FILE_INSPECTORS[file_type]

    if len(argv) == 3:
        with open(argv[2], mode='rb') as input_file:
            is_encrypted = file_inspector(input_file)
    else:
        with TemporaryFile(mode='r+b') as temp_file:
            with fdopen(stdin.fileno(), 'rb') as input_file:
                copyfileobj(input_file, temp_file)

            is_encrypted = file_inspector(_file=temp_file)

    print('The streamed file is{} encrypted'.format('' if is_encrypted else ' not'))
    exit(1 if is_encrypted else 0)


if __name__ == "__main__":
    main()
