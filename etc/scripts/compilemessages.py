#!/usr/bin/python

import glob
import os
from subprocess import Popen, PIPE

program = 'msgfmt'
program_options = ['--check-format', '-f']


def main():
    """
    This code was taken and adapted from
    django.core.management.commands.compilemessages
    """
    # Walk entire tree, looking for locale directories
    basedirs = ['locale']
    for dirpath, dirnames, filenames in os.walk('.', topdown=True):
        for dirname in dirnames:
            if dirname == 'locale':
                basedirs.append(os.path.join(dirpath, dirname))
    basedirs = set(map(os.path.abspath, filter(os.path.isdir, basedirs)))

    # Build locale list
    all_locales = []
    for basedir in basedirs:
        locale_dirs = filter(os.path.isdir, glob.glob('%s/*' % basedir))
        all_locales.extend(map(os.path.basename, locale_dirs))
    locales = set(all_locales)

    for basedir in basedirs:
        dirs = [os.path.join(basedir, l, 'LC_MESSAGES') for l in locales]
        locations = []
        for ldir in dirs:
            for dirpath, dirnames, filenames in os.walk(ldir):
                locations.extend((dirpath, f) for f in filenames if f.endswith('.po'))
        compile_messages(locations)


def compile_messages(locations):
    """
    Locations is a list of tuples: [(directory, file), ...]
    """
    for i, (dirpath, f) in enumerate(locations):
        print('processing file %s in %s\n' % (f, dirpath))

        # Program args
        po_path = os.path.join(dirpath, f)
        base_path = os.path.splitext(po_path)[0]
        extra_args = ['-o', base_path + '.mo', base_path + '.po']
        args = [program] + program_options + extra_args

        # Execute command
        output, errors, status = popen_wrapper(args)
        if status:
            if errors:
                msg = "Execution of %s failed: %s" % (program, errors)
            else:
                msg = "Execution of %s failed" % program
            raise RuntimeError(msg)


def popen_wrapper(args, os_err_exc_type=RuntimeError):
    """
    Friendly wrapper around Popen.
    Return stdout output, stderr output, and OS status code.
    """
    try:
        p = Popen(args, shell=False, stdout=PIPE, stderr=PIPE, close_fds=True)
    except OSError as err:
        raise os_err_exc_type('Error executing %s' % args[0]) from err
    output, errors = p.communicate()
    return output, errors, p.returncode


if __name__ == '__main__':
    main()