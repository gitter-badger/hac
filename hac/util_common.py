# -*- coding: utf-8 -*-
"""Common utilities.
"""
import sys
from os import mkdir, remove
from os.path import exists, isdir
from shutil import rmtree


# -- Printing to CLI ----------------------------------------------------------
def warn(msg):
    sys.stderr.write("WARNING: " + msg + "\n")

def error(msg):
    sys.stderr.write("ERROR: " + msg + "\n")


# -- Lists and dictionaries ---------------------------------------------------
def dict_override(a, b):
    """Overriding dictionary values.

    Values in second dictionary override the values in the first one (except
    when relevant value in second dictionary is None).

    >>> dict_override({'a': 1,'b': 2}, {'a': 3,'b': None}) == {'a': 3,'b': 2}
    True

    >>> dict_override({'a': 3,'b': None}, {'a': 1,'b': 2}) == {'a': 1,'b': 2}
    True
    """
    res = {}
    for key in (set(a.keys()) | set(b.keys())):
        if (key in b) and (b[key] != None):
            res[key] = b[key]
        else:
            res[key] = a[key]
    return res


def list_reduce(a):
    """Reduces provided list in two steps:
        1) removes all elements from list that appear prior to any 'no' element,
        2) removes duplicates and sorts elements.

    >>> list_reduce(['cpp', 'no', 'php', 'py', 'php', 'py'])
    ['php', 'py']

    >>> list_reduce(['cpp', 'no', 'php', 'py', 'php', 'no', 'py', 'cpp'])
    ['cpp', 'py']
    """
    b = list(reversed(a))
    if "no" in b:
        ind = b.index("no")
        del b[ind:]
    return sorted(set(b))


def mainargs_index(a):
    """Removes optional arguments that precede mandatory arguments.

    >>> mainargs_index(['-lcpp', '--no', '-t', 'php', 'py'])
    3

    >>> mainargs_index(['--cpp', '--no'])
    2

    >>> mainargs_index([])
    0
    """
    indices = [ i for i, v in enumerate(a) if not v.startswith("-") ]
    return indices[0] if indices else len(a)


def choice_generate(a, separator='.'):
    """Returns input list with additional entries that represent choices
    without priority specifiers.

    >>> choice_generate(['no', 'cpp.0', 'cpp.1'])
    ['cpp', 'cpp.0', 'cpp.1', 'no']

    >>> choice_generate(['no', 'cpp.0', 'cpp.1', 'py.15'])
    ['cpp', 'cpp.0', 'cpp.1', 'no', 'py', 'py.15']
    """
    separator = '.'
    b = set(a)
    for e in a:
        if separator in e:
            b.add(e.split(separator)[0])
    return sorted(b)


def choice_normal(a, b, separator='.'):
    """Normalizes list a so that among multiple choices that differ only in
    priority modifier, just the highest priority one is present in the output
    list. All the members in the output list are in the canonic form
    <TYPE>.<PRIORITY>.

    If in there is entry without the priority modifier in the input list, it
    corresponds to the request for highest priority choice available (one with
    lowest priority modifier).

    >>> choice_normal(['cpp.0', 'cpp.1', 'py'], ['cpp.0', 'cpp.1', 'py.15'])
    ['cpp.0', 'py.15']

    >>> choice_normal(['cpp', 'py.1', 'py'], ['cpp.1', 'py.0', 'py.1'])
    ['cpp.1', 'py.0']

    DEFINITIONS:
        - regular entries: 'cpp', 'cpp.0', 'py', 'py.15'
        - canonic entries: 'cpp.0', 'py.15'
        - bare entries: 'cpp', 'py'
    """
    separator = '.'
    assert all([separator in ec for ec in b])
    c2c = {ec: ec for ec in b}  # Map canonic to canonic.

    r2c = c2c.copy()            # Map regular to canonic.
    for ec in sorted(set(b)):
        eb = ec.split(separator)[0]
        if eb not in r2c:
            r2c[eb] = ec

    r2b = {}                    # Map regular to bare.
    for er in r2c:
        assert separator in r2c[er]
        r2b[er] = r2c[er].split(separator)[0]

    b_track = set()
    ret = []
    for er in sorted(set(a)):
        eb = r2b[er]
        ec = r2c[er]
        if eb not in b_track:
            b_track.add(eb)
            ret.append(ec)

    return ret


# -- Filesystem ---------------------------------------------------------------
def safe_mkdir(path, force=False):
    """Carefully handles directory creation. Notifies about special
    occurrences.

    Argument force used to decide if priorly existing file named "path" should
    be replaced with directory named "path".
    """
    if not exists(path):
        mkdir(path)
    else:
        if isdir(path):
            warn('Directory "' + path + '" already exists!')
        else:
            # Distinguish between two cases (depending on argument force), if:
            #
            #   - path exists and
            #   - it's not a directory
            #
            if force:
                warn('Deleting file "' + path + '" and creating directory!')
                remove(path)
                mkdir(path)
            else:
                warn('"' + path + '" is not a directory!')


def safe_fwrite(path, contents="", force=False):
    """Carefully handles file writing. Notifies about special occurrences.

    Argument force used to decide if priorly existing file named "path" should
    be overwritten with provided contents.
    """
    # Path exists and is directory.
    if isdir(path):
        if force:
            warn('Deleting directory "' + path + '" and creating file!')
            rmtree(path)
        else:
            warn('Directory named "' + path + '" already exists!')

    # Path exists but is not directory.
    elif exists(path):
        if force:
            warn('Deleting file "' + path + '" and creating file!')
            remove(path)
        else:
            warn('File named "' + path + '" already exists!')

    # Writing to file.
    if not exists(path):
        with open(path, 'w') as f:
            f.write(contents)


# -- Metaclassing (portable, works on Python2/Python3) ------------------------
def with_metaclass(mcls):
    def decorator(cls):
        body = vars(cls).copy()
        # Clean out class body.
        body.pop('__dict__', None)
        body.pop('__weakref__', None)
        return mcls(cls.__name__, cls.__bases__, body)
    return decorator

