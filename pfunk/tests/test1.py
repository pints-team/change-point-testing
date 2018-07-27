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

import numpy as np

import pfunk


class Test1(pfunk.FunctionalTest):

    def __init__(self):
        super(Test1, self).__init__('test1')

    def _run(self, result, log_path):

        result['y'] = 1 + np.random.uniform(-0.25, 0.25)
        result['status'] = 'done'

