# -*- coding: utf-8 -*-

########################################################################
#
# License: BSD
# Created: January 15, 2007
# Author:  Ivan Vilata i Balaguer - ivan at selidor dot net
#
# $Id$
#
########################################################################

"""Functionality related with node paths in a PyTables file.

Variables
=========

`__docformat`__
    The format of documentation strings in this module.

"""

# Imports
# =======
import re
import warnings
import keyword

from .exceptions import NaturalNameWarning

# Public variables
# ================
__docformat__ = 'reStructuredText'
"""The format of documentation strings in this module."""


# Private variables
# =================
_python_id_re = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')
"""Python identifier regular expression."""

_reserved_id_re = re.compile('^_[cfgv]_')
"""PyTables reserved identifier regular expression.

- c: class variables
- f: class public methods
- g: class private methods
- v: instance variables
"""

_hidden_name_re = re.compile('^_[pi]_')
"""Nodes with a name *matching* this expression are considered hidden.

For instance, ``name`` whould be visible while ``_i_name`` would not.
"""

_hidden_path_re = re.compile('/_[pi]_')
"""Nodes with a path *containing* this expression are considered hidden.

For instance, a node with a pathname like ``/a/b/c`` would be visible
while nodes with pathnames like ``/a/c/_i_x`` or ``/a/_p_x/y`` would
not.
"""

_warnInfo = (
        "you will not be able to use natural naming to access this object; "
        "using ``getattr()`` will still work, though")
"""Warning printed when a name will not be reachable through natural naming"""

# Public functions
# ================

def check_attribute_name(name):
    """Check the validity of the `name` of an attribute in AttributeSet.

    If the name is not valid, a ``ValueError`` is raised.  If it is
    valid but it can not be used with natural naming, a
    `NaturalNameWarning` is issued.

    >>> check_attribute_name('a')
    >>> check_attribute_name('a_b')
    >>> check_attribute_name('a:b')
    >>> check_attribute_name('/a/b')
    >>> check_attribute_name('/')
    >>> check_attribute_name('.')
    >>> check_attribute_name('__members__')
    Traceback (most recent call last):
     ...
    ValueError: ``__members__`` is not allowed as an object name
    >>> check_attribute_name(1)
    Traceback (most recent call last):
     ...
    TypeError: object name is not a string: 1
    >>> check_attribute_name('')
    Traceback (most recent call last):
     ...
    ValueError: the empty string is not allowed as an object name
    """
    if not isinstance(name, str):  # Python >= 2.3
        raise TypeError("object name is not a string: %r" % (name,))

    if name == '':
        raise ValueError("the empty string is not allowed as an object name")

    # Check whether `name` is a valid Python identifier.
    if not _python_id_re.match(name):
        warnings.warn("object name is not a valid Python identifier: %r; "
                      "it does not match the pattern ``%s``; %s"
                      % (name, _python_id_re.pattern, _warnInfo),
                      NaturalNameWarning, stacklevel=2)
        return

    # However, Python identifiers and keywords have the same form.
    if keyword.iskeyword(name):
        warnings.warn("object name is a Python keyword: %r; %s"
                      % (name, _warnInfo), NaturalNameWarning, stacklevel=2)
        return

    # Still, names starting with reserved prefixes are not allowed.
    if _reserved_id_re.match(name):
        raise ValueError("object name starts with a reserved prefix: %r; "
                         "it matches the pattern ``%s``"
                         % (name, _reserved_id_re.pattern))

    # ``__members__`` is the only exception to that rule.
    if name == '__members__':
        raise ValueError("``__members__`` is not allowed as an object name")


def check_name_validity(name):
    """Check the validity of the `name` of a Node object, which more limited
    than attribute names.

    If the name is not valid, a ``ValueError`` is raised.  If it is
    valid but it can not be used with natural naming, a
    `NaturalNameWarning` is issued.

    >>> check_name_validity('a')
    >>> check_name_validity('a_b')
    >>> check_name_validity('a:b')
    >>> check_name_validity('/a/b')
    Traceback (most recent call last):
     ...
    ValueError: the ``/`` character is not allowed in object names: '/a/b'
    >>> check_name_validity('.')
    Traceback (most recent call last):
     ...
    ValueError: ``.`` is not allowed as an object name
    >>> check_name_validity('')
    Traceback (most recent call last):
     ...
    ValueError: the empty string is not allowed as an object name

    """
    check_attribute_name(name)

    # Check whether `name` is a valid HDF5 name.
    # http://hdfgroup.org/HDF5/doc/UG/03_Model.html#Structure
    if name == '.':
        raise ValueError("``.`` is not allowed as an object name")
    elif '/' in name:
        raise ValueError("the ``/`` character is not allowed "
                         "in object names: %r" % name)






def join_path(parentpath, name):
    """Join a *canonical* `parentpath` with a *non-empty* `name`.

    .. versionchanged:: 3.0
       The *parentPath* parameter has been renamed into *parentpath*.

    >>> join_path('/', 'foo')
    '/foo'
    >>> join_path('/foo', 'bar')
    '/foo/bar'
    >>> join_path('/foo', '/foo2/bar')
    '/foo/foo2/bar'
    >>> join_path('/foo', '/')
    '/foo'

    """

    if name.startswith('./'):  # Support relative paths (mainly for links)
        name = name[2:]
    if parentpath == '/' and name.startswith('/'):
        pstr = '%s' % name
    elif parentpath == '/' or name.startswith('/'):
        pstr = '%s%s' % (parentpath, name)
    else:
        pstr = '%s/%s' % (parentpath, name)
    if pstr.endswith('/'):
        pstr = pstr[:-1]
    return pstr



def split_path(path):
    """Split a *canonical* `path` into a parent path and a node name.

    The result is returned as a tuple.  The parent path does not
    include a trailing slash.

    >>> split_path('/')
    ('/', '')
    >>> split_path('/foo/bar')
    ('/foo', 'bar')

    """

    lastslash = path.rfind('/')
    ppath = path[:lastslash]
    name = path[lastslash + 1:]

    if ppath == '':
        ppath = '/'

    return (ppath, name)



def isvisiblename(name):
    """Does this `name` make the named node a visible one?"""

    return _hidden_name_re.match(name) is None



def isvisiblepath(path):
    """Does this `path` make the named node a visible one?"""

    return _hidden_path_re.search(path) is None



# Main part
# =========
def _test():
    """Run ``doctest`` on this module."""

    import doctest
    doctest.testmod()


if __name__ == '__main__':
    _test()
