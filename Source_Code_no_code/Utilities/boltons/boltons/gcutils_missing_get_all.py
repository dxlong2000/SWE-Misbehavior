# -*- coding: utf-8 -*-

# Copyright (c) 2013, Mahmoud Hashemi
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * The names of the contributors may not be used to endorse or
#      promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""The Python Garbage Collector (`GC`_) doesn't usually get too much
attention, probably because:

  - Python's `reference counting`_ effectively handles the vast majority of
    unused objects
  - People are slowly learning to avoid implementing `object.__del__()`_
  - The collection itself strikes a good balance between simplicity and
    power (`tunable generation sizes`_)
  - The collector itself is fast and rarely the cause of long pauses
    associated with GC in other runtimes

Even so, for many applications, the time will come when the developer
will need to track down:

  - Circular references
  - Misbehaving objects (locks, ``__del__()``)
  - Memory leaks
  - Or just ways to shave off a couple percent of execution time

Thanks to the :mod:`gc` module, the GC is a well-instrumented entry
point for exactly these tasks, and ``gcutils`` aims to facilitate it
further.

.. _GC: https://docs.python.org/2/glossary.html#term-garbage-collection
.. _reference counting: https://docs.python.org/2/glossary.html#term-reference-count
.. _object.__del__(): https://docs.python.org/2/glossary.html#term-reference-count
.. _tunable generation sizes: https://docs.python.org/2/library/gc.html#gc.set_threshold
"""
# TODO: type survey

from __future__ import print_function

import gc
import sys

__all__ = ['get_all', 'GCToggler', 'toggle_gc', 'toggle_gc_postcollect']


def get_all(type_obj, include_subtypes=True):
    """This function returns a list containing all instances of a given type. It works for the vast majority of types, but there are some exceptions. It is optimized for getting instances of user-created types quite fast. Setting *include_subtypes* to ``False`` will further increase performance in cases where instances of subtypes aren't required.
    Input-Output Arguments
    :param type_obj: Type. The type of object to get all instances of.
    :param include_subtypes: Bool. Whether to include instances of subtypes. Defaults to True.
    :return: List. A list containing all instances of the given type.
    """


_IS_PYPY = '__pypy__' in sys.builtin_module_names
if _IS_PYPY:
    # pypy's gc is just different, y'all
    del get_all


class GCToggler(object):
    """The ``GCToggler`` is a context-manager that allows one to safely
    take more control of your garbage collection schedule. Anecdotal
    experience says certain object-creation-heavy tasks see speedups
    of around 10% by simply doing one explicit collection at the very
    end, especially if most of the objects will stay resident.

    Two GCTogglers are already present in the ``gcutils`` module:

    - :data:`toggle_gc` simply turns off GC at context entrance, and
      re-enables at exit
    - :data:`toggle_gc_postcollect` does the same, but triggers an
      explicit collection after re-enabling.

    >>> with toggle_gc:
    ...     x = [object() for i in range(1000)]

    Between those two instances, the ``GCToggler`` type probably won't
    be used much directly, but is documented for inheritance purposes.
    """
    def __init__(self, postcollect=False):
        self.postcollect = postcollect

    def __enter__(self):
        gc.disable()

    def __exit__(self, exc_type, exc_val, exc_tb):
        gc.enable()
        if self.postcollect:
            gc.collect()


toggle_gc = GCToggler()
"""A context manager for disabling GC for a code block. See
:class:`GCToggler` for more details."""


toggle_gc_postcollect = GCToggler(postcollect=True)
"""A context manager for disabling GC for a code block, and collecting
before re-enabling. See :class:`GCToggler` for more details."""