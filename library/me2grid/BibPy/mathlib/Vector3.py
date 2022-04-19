# /usr/bin/env python3
# -*- coding: utf-8 (ü) -*-
"""!
@file  Vector3.py

@brief Provides a three dimensional class 'Vector3' just based on 'math' library

@section VECTOR3_CREDITS Credits

The implementation is inspired by the class Vector(tuple) from the autor 'tobal'\n

- @html https://github.com/tofol/Python-Programs
- @html https://codereview.stackexchange.com/questions/49454/class-vector-with-python-3
"""

import math

try:   # Necessary, for direct module execution
    from mathext import norm
except:
    from me2grid.BibPy.mathlib.mathext import norm
    
class Spherical():
    """! @brief Vector within spherical coordinates in radians (see math.radians(degreeAngle) and math.degree(radiansAngle))
        @param r is the magnitude, norm or length of the vector
        @param phi is the hour angle defined by the vector projection on the x,y plain with repect to the x-Axis. Positive values in case the projection is directed towards the positive y-Axis
        @param theta is the declination angle defined as the angle between the vector and ist projection on the x,y plain. Positive values in case the vector is directed towards the positve z-Axis
        You can receive the cartesian coordinates by using the python list() function. \n
        This class is aimed to carry spherical coordinates, only! For vector calculation purpose use Vector3(Spherica(r, phi, theta)) (see \ref Vector3 )
    """
    def __init__(self, r, phi, theta, degrees: bool = False):
        if degrees:
            phi = math.radians(phi)
            theta = math.radians(theta)
        self.r = r
        self.phi = phi
        self.theta = theta
        
    def __str__(self):
        return f"{type(self).__name__}(r={self.r}, phi={self.phi}, theta={self.theta})"
        
    def __repr__(self):
        mod = self.__module__ + '.'
        if mod == '__main__.':
            mod = ""
        return f"{mod}{str(self)}"
    
    def __iter__(self):
        """! @brief Delivers a list of cartesian coordinates [x, y, z] """
        return [self.x, self.y, self.z].__iter__()

    @property
    def x(self):
        """! @brief x component of the spherical defined vector """
        return math.cos(self.phi) * self.__xyProjectionNorm__()
    
    @property
    def y(self):
        """! @brief y component of the spherical defined vector """
        return math.sin(self.phi) * self.__xyProjectionNorm__()
    
    @property
    def z(self):
        """! @brief z component of the spherical defined vector """
        return math.sin(self.theta) * self.r
    
    def asDegrees(self) -> str:
        """! @brief Returns an readable string using degrees """
        return(f"{type(self).__name__}(r={self.r}, phi={math.degrees(self.phi)}, theta={math.degrees(self.theta)}, degrees=True)")
           
    def asReprDegrees(self) -> str:
        """! @brief Returns an reqresentation string using degrees """
        mod = self.__module__ + '.'
        if mod == '__main__.':
            mod = ""
        return f"{mod}{toDegrees(self)}"
    
    def __xyProjectionNorm__(self):
        """! @brief Magnitude, norm or length of the vector projection on the x-y-plane """
        return math.cos(self.theta) * self.r
        
class BaseVector3():
    """! @brief Base class for deriving 3 dimensional vector classes the properties x, y and z """
    __sphericalRepresentation: Spherical = None

    @property
    def isSpherical(self) -> bool:
        """! @brief True, in case the vector has a spherical internal representation """
        if not self.__sphericalRepresentation:
            return False
        else:
            return True

    @isSpherical.setter
    def isSpherical(self, set: bool):
        """! @brief If set to 'True', converts the internal representation to spherical coordinates otherwise converts to cartesian """
        if self.isSpherical and not set:
            s = self.spherical
            self.__sphericalRepresentation = None
            xyz = list[s]
            self[0] = xyz[0]
            self[1] = xyz[1]
            self[2] = xyz[2]
        elif not self.isSpherical and set:
            self.__sphericalRepresentation = self.toSpherical()
    
    @property
    def __spherical__(self) -> bool:
        if self.isSpherical:
            return __sphericalRepresentation
        else:
            raise ValueError("'Vector3' has cartesian representation and cannot return the refernce of spherical representation!")

    @property
    def x(self):
        """! @brief x component of the vector """
        if not self.isSpherical:
            return self[0]
        else:
            return self.toSpherical.x

    @x.setter
    def x(self, var):
        """! @brief Sets the x-coordinate if the internal representation is cartesian """
        if not self.spherical:
            self[0] = var
        else:
            raise ValueError("'Vector3' has spherical representation. Therefore cartesian coordinates must not be written to: Change to cartesian representation using 'vector3.isSherical=False' .")

    @property
    def y(self):
        """! @brief y component of the vector """
        if not self.isSpherical:
            return self[1]
        else:
            return self.__spherical__.y

    @y.setter
    def y(self, var):
        """! @brief Sets the y-coordinate if the internal representation is cartesian """
        if not self.spherical:
            self[1] = var
        else:
            raise ValueError("'Vector3' has spherical representation. Therefore cartesian coordinates must not be written to: Change to cartesian representation using 'vector3.isSherical=False' .")

    @property
    def z(self):
        """! @brief z component of the vector """
        if not self.isSpherical:
            return self[2]
        else:
            return self.__spherical__.z
    
    @z.setter
    def z(self, var):
        """! @brief Sets the z-coordinate if the internal representation is cartesian """
        if not self.spherical:
            self[2] = var
        else:
            raise ValueError("'Vector3' has spherical representation. Therefore cartesian coordinates must not be written to: Change to cartesian representation using 'vector3.isSherical=False' .")

    @property
    def r(self):
        """! @brief Magnitude, norm or length value of the vector in spherical coordinates """
        return self.norm

    @r.setter
    def r(self, var):
        """! @brief Sets the r-coordinate if the internal representation is spherical """
        if self.isSpherical:
            self.r = var
        else:
            raise ValueError("'Vector3' has cartesian representation. Therefore sherical coordinates must not be written to: Change to sherical representation using 'vector3.isSherical=True' .")

    @property
    def phi(self):
        """! @brief Hour angle in radians (see math.degree(radiansAngle) and math.radians(degreeAngle))
            The hour angle is given by the vector projection on the x,y plain with repect to the x-Axis. Positive values in case the projection is directed towards the positive y-Axis
        """
        return math.atan2(self.y, self.x)
    
    @phi.setter
    def phi(self, var):
        """! @brief Sets the r-coordinate if the internal representation is spherical """
        if self.isSpherical:
            self.phi = var
        else:
            raise ValueError("'Vector3' has cartesian representation. Therefore sherical coordinates must not be written to: Change to sherical representation using 'vector3.isSherical=True' .")

    @property
    def theta(self):
        """! @brief Declination Angle
            The declination angle is given as the angle between the vector and ist projection on the x,y plain. Positive values in case the vector is directed towards the positve z-Axis \n
        """
        return math.atan2(self.z, math.sqrt(self.x**2 + self.y**2))
    
    @theta.setter
    def theta(self, var):
        """! @brief Sets the r-coordinate if the internal representation is spherical """
        if self.isSpherical:
            self.theta = var
        else:
            raise ValueError("'Vector3' has cartesian representation. Therefore sherical coordinates must not be written to: Change to sherical representation using 'vector3.isSherical=True' .")

    @property
    def norm(self):
        """! @brief Magnitude, norm or length of the vector """
        return norm(self) # which is the global function
           
    def neg(self):
        """! @brief Magnitude, norm or length of the vector """
        return self.__class__([-val for val in self])
           
    def toSpherical(self) -> Spherical:
        """! @brief Returns a Spherical object within spherical coordinates (r, phi, theta) """
        return Spherical(self.r, self.phi, self.theta)
    
    def __xyNorm__(self):
        """! @brief Magnitude, norm or length of the vector projection on the x-y-plane """
        return math.sqrt(self[0]**2 + self[1]**2)
    
class Vector3(BaseVector3, list):
    """! @brief A cartesian three dimensional vector based on 'list' and accessable through the properties x, y and z
        See the documentation of \ref BaseVector3 !
    """
    def __init__(self, value):
        if isinstance(value, Spherical):
            super().__init__(list(value))
        else:
            super().__init__(value)
            if len(self) != 3:
                raise IndexError(f"The dimension of the initialization value of {type(self).__name__} must be 3!")

    def __str__(self):
        if not self.isSpherical:
            return f"{type(self).__name__}({super().__repr__()})"
        else:
            return f"{type(self).__name__}({self.__spherical__.__str__()})"
                    
    def __repr__(self):
        mod = self.__module__ + '.'
        if mod == '__main__.':
            mod = ""
        if not self.isSpherical:
            return f"{mod}{str(self)}"
        else:
            return f"{mod}{type(self).__name__}({mod}{self.__spherical__.__repr__()})"
            
    @classmethod
    def fromSpherical(cls, sphericalVector: Spherical):
        """! @brief Returns a cartesian Vector3 class from a given Spherical class
            You can also use the Vector3 constructor directly by passing the Spherical class to it.
        """
        return Vector3(list(sphericalVector))
           
if __name__ == '__main__':
    
    from math import radians, degrees, sqrt
    
    def testConv(v: Vector3):
        print("\nTesting Vector3 to and from spherical coordinates")
        print(v)
        print(v.toSpherical().asDegrees())
        print(Vector3(v.toSpherical()))
        print("\n")
        
    def testInvConv(s: Spherical):
        print("\nTesting Spherical to and from cartesian coordinates")
        print(s.asDegrees())
        print(Vector3(s))
        print(Vector3(s).toSpherical().asDegrees())
        print("\n")
    
    print("Test Vector3")
    v=Vector3([1,2,3])
    print("- Properties (Values calculated directly from the internal members)")
    print("  - Vector string of v")
    print(v)
    print("  - Vector x coordinate ")
    print(v.x)
    print("  - Vector norm, magnitude or length ")
    print(v.norm)
    print("  - Spherical coordinate 'phi' (hour angle) ")
    print(v.phi)
    print("- Methods (Delivering of new created vector objects")
    print("  - negative vector ")
    print(v.neg())
    print("- class Spherical: r=2, phi=30°, theta=15° ")
    s = Spherical(2, math.radians(30), math.radians(15))
    print(s)
    print("  - all coordinates ")
    print(list(s))
    print("  - x coordinate ")
    print(s.x)
    testConv(v)
    testInvConv(s)
    print("- Testing with python functions ")
    print("  - eval(repr(Vector3([1, 2, 3]))")
    print(eval(repr(Vector3([1, 2, 3]))))
    print("\n### Error finding ###")
    testInvConv(Spherical(1, 45, 0, True))
    