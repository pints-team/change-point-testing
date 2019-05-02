#
# Pints functional testing module.
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2018, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#

import time


def format_date(seconds_since_epoch):
    return time.strftime("%a, %d %b %Y %H:%M", time.gmtime(seconds_since_epoch))
