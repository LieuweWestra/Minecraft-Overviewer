#    This file is part of the Minecraft Overviewer.
#
#    Minecraft Overviewer is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or (at
#    your option) any later version.
#
#    Minecraft Overviewer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#    Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with the Overviewer.  If not, see <http://www.gnu.org/licenses/>.

"""
Misc utility routines used by multiple files that don't belong anywhere else
"""

import os.path
import sys
import platform
from subprocess import Popen, PIPE
from itertools import cycle, islice, product

# does not require git, very likely to work everywhere
def findGitHash():
    # normally, we're in ./overviewer/util.py
    # we want ./
    this_dir = os.path.dirname(os.path.dirname(__file__))
    
    if os.path.exists(os.path.join(this_dir,".git")):
        with open(os.path.join(this_dir,".git","HEAD")) as f:
            data = f.read().strip()
        if data.startswith("ref: "):
            if not os.path.exists(os.path.join(this_dir, ".git", data[5:])):
                return data
            with open(os.path.join(this_dir, ".git", data[5:])) as g:
                return g.read().strip()
        else:
            return data
    else:
        try:
            import overviewer_version
            return overviewer_version.HASH
        except Exception:
            return "unknown"

def findGitVersion():
    try:
        p = Popen('git describe --tags', stdout=PIPE, stderr=PIPE, shell=True)
        p.stderr.close()
        line = p.stdout.readlines()[0].decode()
        if line.startswith('release-'):
            line = line.split('-', 1)[1]
        if line.startswith('v'):
            line = line[1:]
        # turn 0.1.0-50-somehash into 0.1.50
        # and 0.1.0 into 0.1.0
        line = line.strip().replace('-', '.').split('.')
        if len(line) == 5:
            del line[4]
            del line[2]
        else:
            assert len(line) == 3
            line[2] = '0'
        line = '.'.join(line)
        return line
    except Exception as e:
        print(e)
        try:
            import overviewer_version
            return overviewer_version.VERSION
        except Exception:
            return "unknown"

def is_bare_console():
    """Returns true if Overviewer is running in a bare console in
    Windows, that is, if overviewer wasn't started in a cmd.exe
    session.
    """
    if platform.system() == 'Windows':
        try:
            import ctypes
            GetConsoleProcessList = ctypes.windll.kernel32.GetConsoleProcessList
            num = GetConsoleProcessList(ctypes.byref(ctypes.c_int(0)), ctypes.c_int(1))
            if (num == 1):
                return True
                
        except Exception:
            pass
    return False

def nice_exit(ret=0):
    """Drop-in replacement for sys.exit that will automatically detect
    bare consoles and wait for user input before closing.
    """
    if ret and is_bare_console():
        print()
        print("Press [Enter] to close this window.")
        raw_input()
    sys.exit(ret)

# http://docs.python.org/library/itertools.html
def roundrobin(iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = cycle(iter(it).__next__ for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))

def dict_subset(d, keys):
    "Return a new dictionary that is built from copying select keys from d"
    n = dict()
    for key in keys:
        if key in d:
            n[key] = d[key]
    return n
