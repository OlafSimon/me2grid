# /usr/bin/env python3
# -*- coding: utf-8 (ü) -*-
"""!
    @file  Vector3np.py
"""

import numpy

try: # Necessary, to run this file directly
    from Vector3 import BaseVector3, Vector3
except:
    from me2grid.BibPy.math.Vector3 import Vector3

class Vector3np(numpy.array):
    """! @brief A cartesian three dimensional vector based on 'numpy.array'
        The vector is accessable through the properties x, y and z. Specific mathematic functions apropriate for
        three dimensional vectors only are implemented (e.g. sperical coordinates)\n
        See the documentation of \ref BaseVector3 !
    """
    def __str__(self):
        return super().__repr__()
        
    def __repr__(self):
        return f"<{Vector3.__bases__[0].__name__} '{self.__module__}.{type(self).__name__}' {str(self)}>"
        
