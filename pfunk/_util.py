#
# (Non-IO) Utility functions.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2019, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
import numpy as np
import time

import pfunk


def format_date(seconds_since_epoch):
    return time.strftime(
        pfunk.DATE_FORMAT, time.gmtime(seconds_since_epoch))


def weave(chains):
    """
    Interweaves the given sequence of identically shaped chains, returning a
    single chain.

    The returned chain has samples in the order::

        chain 0, sample 0
        chain 1, sample 0
        chain 2, sample 0
        ...
        chain 0, sample 1
        chain 1, sample 2
        chain 2, sample 3
        ...
        ...

    """
    # This method is fast, it seems:
    # https://stackoverflow.com/questions/5347065

    # Handle trivial cases
    nc = len(chains)
    if nc == 0:
        return np.array()
    elif nc == 1:
        return np.array(chains[0], copy=True)

    # Check shape of chains
    shape = chains[0].shape
    for i, chain in enumerate(chains):
        if chain.ndim != 2:
            raise ValueError(
                'All chains passed to weave() must be 2-dimensional (error for'
                ' chain ' + str(i) + ').')
        if chain.shape != shape:
            raise ValueError(
                'All chains must have same shape (error for chain ' + str(i)
                + ').')

    # Create single interwoven chain
    nr, nd = shape
    woven = np.zeros(((nr * nc), nd))
    for i, chain in enumerate(chains):
        woven[i::nc] = chain
    return woven

