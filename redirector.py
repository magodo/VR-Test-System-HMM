#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Mon 30 Mar 2015 08:53:36 PM CST
# File Name: with_c_code_my_version.py
# Description:
#       Python: file object <=> C: stream pointer(FILE *)
#
#########################################################################

import os
import sys
import ctypes
import tempfile
import io
from contextlib import contextmanager

@contextmanager
def stdout_redirector(stream):
    # Add-ons: Flush C buffer for stdout and flush sys.stdout
    # FIXME

    stdout_fd = sys.stdout.fileno()             # Get fd of standard output, always 1
    saved_stdout_fd = os.dup(stdout_fd)         # Duplicate file table entry for standard output to another fd.

    tmp = tempfile.TemporaryFile(mode = "w+b")  # Create a temparory file object(FILE *)
    os.dup2(tmp.fileno(), stdout_fd)            # Redirect stdout_fd(1) to point to the file table entry of the newed file.
    yield                                       # Yield to caller

    os.dup2(saved_stdout_fd, stdout_fd)         # Redirect back stdout_fd(1) to the file table entry directing to /dev/stdout

    # Fulsh and read the redirected content from the temporary file to the stream.
    tmp.flush()
    tmp.seek(0, io.SEEK_SET)
    stream.write(tmp.read())

    tmp.close()
    os.close(saved_stdout_fd)

@contextmanager
def stderr_redirector(stream):
    # Add-ons: Flush C buffer for stderr and flush sys.stderr
    # FIXME

    stderr_fd = sys.stderr.fileno()             # Get fd of standard error, always 1
    saved_stderr_fd = os.dup(stderr_fd)         # Duplicate file table entry for standard error to another fd.

    tmp = tempfile.TemporaryFile(mode = "w+b")  # Create a temparory file object(FILE *)
    os.dup2(tmp.fileno(), stderr_fd)            # Redirect stderr_fd(2) to point to the file table entry of the newed file.
    yield                                       # Yield to caller

    os.dup2(saved_stderr_fd, stderr_fd)         # Redirect back stderr_fd(2) to the file table entry directing to /dev/stderr

    # Fulsh and read the redirected content from the temporary file to the stream.
    tmp.flush()
    tmp.seek(0, io.SEEK_SET)
    stream.write(tmp.read())

    tmp.close()
    os.close(saved_stderr_fd)

if __name__ == "__main__":

    libc = ctypes.CDLL(None)

    #################
    # Test stdout_redirector
    #################

    # Standard print
    print "Standard output from python"
    libc.puts(b"Standard output from C")
    os.system("echo Standard output from echo")


    # Redirect
    f = io.BytesIO()
    with stdout_redirector(f):
        print "You can't see me! Python."
        libc.puts(b"You can't see me! C.")
        os.system("echo You cant see me! echo.")

    # Read the redirected content from the redirected file.
    print "Reveal ash! > ~ < \n{0}".format(f.getvalue().decode("utf-8"))

