# Copyright (c) 2017, Fundacion Dr. Manuel Sadosky
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import absolute_import

from barf.core.smt.smtsymbol import BitVec

from barf.core.smt.smtsymbol import Constant


def zero_extend(s, size):
    """This function extends a given value to a specified size by zero-padding. It checks the input value is of relevant type and if the size difference is non-negative. If the size is already equal to the value's size, it returns the value as is. Otherwise, it creates a new Class with the specified size and the zero-extend operation and returns it.
    Input-Output Arguments
    :param s: Constant or BitVec. The value to be extended.
    :param size: Integer. The desired size to extend the value to.
    :return: BitVec. The value after zero-extension.
    """


def sign_extend(s, size):
    assert type(s) in (Constant, BitVec) and size - s.size >= 0

    if size == s.size:
        return s

    return BitVec(size, "(_ sign_extend {})".format(size - s.size), s)


def extract(s, offset, size):
    assert type(s) in (Constant, BitVec)

    if offset == 0 and size == s.size:
        return s

    return BitVec(size, "(_ extract {} {})".format(offset + size - 1, offset), s)


def ite(size, cond, true, false):
    from barf.core.smt.smtsymbol import Bool
    assert type(cond) is Bool

    return BitVec(size, "ite", cond, true, false)


def concat(size, *args):
    if len(args) == 1:
        return args[0]

    return BitVec(size * len(args), "concat", *args)