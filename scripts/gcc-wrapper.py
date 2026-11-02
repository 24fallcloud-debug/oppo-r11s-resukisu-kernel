#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2011-2016, The Linux Foundation. All rights reserved.

import errno
import re
import os
import sys
import subprocess

allowed_warnings = set([
    "core.c:144",
    "inet_connection_sock.c:430",
    "inet_connection_sock.c:467",
    "inet6_connection_sock.c:89",
])

ofile = None

warning_re = re.compile(r'''(.*/|)([^/]+\.[a-z]+:\d+):(\d+:)? warning:''')

def interpret_warning(line):
    line = line.rstrip('\n')
    m = warning_re.match(line)
    if m and m.group(2) not in allowed_warnings:
        print("error, forbidden warning:", m.group(2))
        if ofile:
            try:
                os.remove(ofile)
            except OSError:
                pass
        sys.exit(1)

def run_gcc():
    args = sys.argv[1:]
    try:
        i = args.index('-o')
        global ofile
        ofile = args[i+1]
    except (ValueError, IndexError):
        pass

    try:
        proc = subprocess.Popen(args, stderr=subprocess.PIPE)
        for line in proc.stderr:
            # Python3 需要解码
            decoded_line = line.decode('utf-8', errors='replace')
            print(decoded_line, end='')
            interpret_warning(decoded_line)

        result = proc.wait()
    except OSError as e:
        result = e.errno
        if result == errno.ENOENT:
            print(args[0] + ':', e.strerror)
            print('Is your PATH set correctly?')
        else:
            print(' '.join(args), str(e))

    return result

if __name__ == '__main__':
    status = run_gcc()
    sys.exit(status)
