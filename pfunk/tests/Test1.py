#
# Fake test 1
#
# This file is part of Pints Functional Testing.
#  Copyright (c) 2017-2018, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the Pints
#  functional testing software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals

import pfunk


class Test1(pfunk.Test):

    def __init__(self, name):
        super(Test1, self).__init__(name)

    def _run(self, log_name, result_name):

