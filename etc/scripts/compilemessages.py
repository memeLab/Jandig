#!/usr/bin/python

import glob
import os
from subprocess import Popen, PIPE

program = "msgfmt"
program_options = ["--check-format", "-f"]


def main():
    """
    This code was taken and adapted from
    django.core.management.commands.compilemessages
    """
    # Walk entire tree, looking for locale directories
    basedirs = ["locale"]
    for dirpath, dirnames, filenames in os.walk(".", topdown=True):
        for dirname in dirnames:
            if dirname == "locale":
                basedirs.append(os.path.join(dirpath, dirname))
    basedirs = set(map(os.path.abspath, filter(os.path.isdir, basedirs)))

    # Build locale list
    all_locales = []
    for basedir in basedirs:
        locale_dirs = filter(os.path.isdir, glob.glob(f"{basedir}/*"))
        all_locales.extend(map(os.path.basename, locale_dirs))
    locales = set(all_locales)

    for basedir in basedirs:
        dirs = [os.path.join(basedir, locale, "LC_MESSAGES") for locale in locales]
        locations = []
        for ldir in dirs:
            for dirpath, dirnames, filenames in os.walk(ldir):
                locations.extend((dirpath, f) for f in filenames if f.endswith(".po"))
        compile_messages(locations)


def compile_messages(locations):
    """
    Locations is a list of tuples: [(directory, file), ...]
    """
    for _, (dirpath, f) in enumerate(locations):
        print(f"processing file {f} in {dirpath}\n")

        # Program args
        po_path = os.path.join(dirpath, f)
        base_path = os.path.splitext(po_path)[0]
        extra_args = ["-o", base_path + ".mo", base_path + ".po"]
        args = [program] + program_options + extra_args

        # Execute command
        __, errors, status = popen_wrapper(args)
        if status:
            if errors:
                msg = f"Execution of {program} failed: {errors}"
            else:
                msg = f"Execution of {program} failed"
            raise RuntimeError(msg)


def popen_wrapper(args, os_err_exc_type=RuntimeError):
    """
    Friendly wrapper around Popen.
    Return stdout output, stderr output, and OS status code.
    """
    with Popen(args, shell=False, stdout=PIPE, stderr=PIPE, close_fds=True) as p:
        output, errors = p.communicate()
        return output, errors, p.returncode
    raise os_err_exc_type("Error executing")


if __name__ == "__main__":
    main()
