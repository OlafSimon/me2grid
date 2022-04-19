# /usr/bin/env python3
# -*- coding: utf-8 (ü) -*-
"""!
@file  Vector3.py

@author Olaf Simon
@date   14.4.2022

@brief Provides functions extending the python 'math' library
"""

import math

def normSquare(data: []):
    res = 0
    for i in data:
        res = res + i**2
    return res

def norm(data: []):
    return math.sqrt(normSquare(data))

def tan2(r, phi):
    """! @brief Delivers a touple (y, x) of cartesian coordinates from given magnitude r and angle phi
        The order is chosen that way for compatibility to the invers function of phi = math.atan2(y, x) using r=1!
    """     
    return (r*math.sin(phi), r*math.cos(phi))        


if __name__ == '__main__':
    
    print("- BibPi math functions ")
    print("  - Norm, magnitude or length of an iterable class e.g. 'list'. Test deliveres 5")
    print(norm([3, 4]))
    print("  - Function tan2 delivering a tuple of (y, x). It is the inverse function of math.atan2(y, x). Test uses (y=4, x=3)")
    v = (4, 3)
    r = norm(v)
    phi = math.atan2(v[0], v[1])
    print(tan2(r, phi))
