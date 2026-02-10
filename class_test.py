import numpy as np
from typing import Optional, Iterable
from enum import Enum
import json

def addOne(x):
    return x+1

def drop_none(d):
    #print(type(d))
    return {k: v for k, v in d.items() if v is not None}

def range_check(value, min, max):
    if (value >= min if min is not None else True) and (value <= max if max is not None else True):
        return value
    else:
        min_text = f" {min} ≤" if min is not None else ""
        max_text = f" ≤ {max}" if max is not None else ""

        raise TypeError(f"Value {value} is out of range. Expected{min_text} value{max_text}.")


def class_check(value, allowed):
    #allowed = (Time.Object1, Time.Object2)
    if not isinstance(value, allowed):
        allowed_names = ", ".join(cls.__qualname__ for cls in allowed)
        raise TypeError(
            f"Invalid variable type: {type(value).__name__}. "
            f"Expected {allowed_names}"
        )
    return value

def extension_check(extensions, filename):
    if not filename.endswith(tuple(extensions)):
        raise ValueError(
            f"Invalid file extension: {filename!r}. "
            f"Allowed extension are: {extensions}"
        )
    return filename

def enum_check(value, enum):
    if value is None:
        return value
    try:
        if isinstance(value, str):
            value = enum(value)
            return value
        elif not isinstance(value, enum):
            raise TypeError
    except (ValueError, TypeError):
        allowed = [e.value for e in enum]
        raise ValueError(
            f"Invalid value for time_steps: {value!r}. "
            f"Allowed values are: {allowed}"
        ) from None

def type_check(tp, variable):
    if not isinstance(variable, tp):
        raise TypeError(f"Expected type '{tp.__name__}', but got '{type(variable).__name__}'")
    return variable

class Root(object):
    ''' 
    Root of the configuration file.
    Required: 
        string1:
    
    Optional:
        geometry:
        
        other:
    '''
    class_var = 1

    def __init__(
        self,
        string1: str = None,
        geometry: Optional["Root.Geometry"] = None,
        other: Optional["Root.Other"] = None,
        materials: Optional["Root.Materials"] = None,
        time: Optional["Root.Time"] = None
    ):
        self._string1 = type_check(str, string1) if string1 else None
        self.geometry = geometry if geometry else Root.Geometry()
        self.other = other if other else Root.Other()
        self._materials = materials if materials else Root.Materials()
        self._time = time if time else Root.Time()

    """
    def __init__(self, string1 : str, geometry:Geometry = Geometry(), other : Other = Other()):
        self._string1 = type_check(str, string1)
        self._geometry = type_check(self.Geometry, geometry)
        self._other = type_check(self.Other, other)
        # self.camera: str = 'you'
    """

    @property
    def string1(self):
        return self._string1

    @string1.setter
    def string1(self, string1 : str):
        """ Required: string1 """
        self._string1 = string1

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self,  value):
        """ 
        value : obj
        Optional: nested: int
        """
        print("Geometry = " + str(value))
        self._geometry = type_check(self.Geometry ,value)
    
    @property
    def other(self):
        return self._other

    @other.setter
    def other(self, value):
        """ Optional: nested """
        print("Other = " + str(value))
        self._other = type_check(self.Other ,value)

    @property
    def materials(self):
        return self._materials

    @materials.setter
    def materials(self, value):
        """ Optional: nested """
        #print("Other = " + str(value))
        self._other = type_check(self.Materials ,value)

    def as_dict(self):
        return {"string1": self._string1, "geometry": self._geometry.as_dict(), "other": self._other.as_dict(), "materials": self._materials.as_dict()}
    
    class Time(object):
        def __init__(self, value = None):
            self._value = value

        class Object1(object):
            def __init__(self, dt = None):
                self._dt = dt

        class Object2(object):
            def __init__(self, tend = None):
                self._tend = tend
    
    class Other(object):
        class TimeSteps(str, Enum):
            ALL = "all"
            STATIC = "static"
            
        def __init__(self, nested : int = 3, time_steps: TimeSteps = None):
            self._nested = type_check(int, nested)
            self._time_steps = enum_check(time_steps, self.TimeSteps)

        @property
        def nested(self):
            return self._nested

        @nested.setter
        def nested(self, nested : int = 3):
            '''The comment you want to appear when hovering goes here'''
            self._nested = type_check(int, nested)

        @property
        def time_steps(self):
            return self._time_steps

        @time_steps.setter
        def time_steps(self, value):
            '''options are "all","static". Other values are not accepted'''
            self._time_steps = enum_check(value, self.TimeSteps)

        def as_dict(self):
            return drop_none({"nested": self._nested, "time_steps": self._time_steps.value if self._time_steps is not None else None})

    class Geometry(object):
        class Nested(object):
            def __init__(self, default : int = 3):
                self._default = type_check(int, default)
        def __init__(self, nested : int = 3, gamma: float = 0.5):
            self._nested = type_check(int, nested)
            self._gamma = range_check(type_check(float, gamma), min = 0, max = 1) if gamma is not None else None
            

        @property
        def nested(self):
            return self._nested

        @nested.setter
        def nested(self, nested : int = 3):
            '''The comment you want to appear when hovering goes here'''
            self._nested = type_check(int, nested)

        @property
        def gamma(self):
            return self._gamma

        @gamma.setter
        def gamma(self, gamma : float = .5):
            '''The comment you want to appear when hovering goes here'''
            self._gamma = range_check(type_check(float, gamma), min = 0, max = 1)

        def as_dict(self):
            return {"nested": self._nested, "gamma": self._gamma,}
        
    class Materials(object):
        def __init__(self, items : list = None):
            allowed = (self.Neohookean, self.MooneyRivlin)
            self._items = [class_check(i, allowed) for i in (type_check(list, items) if items else [])]

        @property
        def items(self):
            return self._items

        @items.setter
        def items(self, item : object):
            """ Required: string1 """
            allowed = (self.Neohookean, self.MooneyRivlin)
            self._items.append(class_check(item, allowed))

        # CLEAR (make empty)
        def clear(self):
            self._items.clear()

        # REMOVE by index
        def pop(self, index=-1):
            return self._items.pop(index)

        # OPTIONAL: safe remove
        def remove(self, item):
            if item in self._items:
                self._items.remove(item)

        def as_dict(self):
            return [i.as_dict() for i in self._items]
        
        class Neohookean():
            def __init__(
                self,
                type: str = None,
                E: int = None,
                id: Optional[Iterable[int]] = None,
            ):
                self._type = type_check(str, type) if type else None
                self._E = type_check(int, E) if E else None
                self._id = [] if id is None else [type_check(int, i) for i in id]

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value : str):
                '''The comment you want to appear when hovering goes here'''
                self._type = type_check(str, value)

            @property
            def E(self):
                return self._type

            @E.setter
            def E(self, value : int):
                '''The comment you want to appear when hovering goes here'''
                self._E = type_check(int, value)

            @property
            def id(self):
                return self._id
            
            @id.setter
            def id(self, value : int):
                '''The comment you want to appear when hovering goes here'''
                self._id.append(type_check(int, value))

            # CLEAR (make empty)
            def clear(self):
                self._id.clear()

            # REMOVE by index
            def pop(self, index=-1):
                return self._id.pop(index)

            # OPTIONAL: safe remove
            def remove(self, item):
                if item in self._list:
                    self._id.remove(item)

            def as_dict(self):
                return {"type": self._type, "E": self._E, "id": self._id}

        class MooneyRivlin():
            def __init__(
                self,
                type: str = None,
                c1: int = None,
            ):
                self._type = type_check(str, type) if type else None
                self._c1 = type_check(int, c1) if c1 else None

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value : str):
                '''The comment you want to appear when hovering goes here'''
                self._type = type_check(str, value)

            @property
            def c1(self):
                return self._type

            @type.setter
            def c1(self, value : int):
                '''The comment you want to appear when hovering goes here'''
                self._c1 = type_check(int, value)

            def as_dict(self):
                return drop_none({"type": self._type, "c1": self._c1})

root = Root("2")

print(root.as_dict())

# m.addOne()
# m.class_var = "ali" 
# m.String1("ali")
# m.i_var = "hassan"
# print("i_var = " + str(m.i_var))

#print("class_var = " + str(root.class_var))
print("string1 = " + str(root._string1))

#root.geometry.Nested()
root.string1 = "hello"
print(root.string1)
print(root.geometry.nested)

#root.geometry = Root.Geometry(5)

#root.geometry = root.Geometry(root.geometry.Nested(1))

root.Geometry()

root.other.nested = 9

print(root.geometry.nested)

root.geometry.nested = 8

print(root.geometry.nested)
Root()

#geometry = Root.Geometry(6)

Neohookean = root.materials.Neohookean("ali")
Neohookean.id = 1
Neohookean.id = 2

root.materials.items = Neohookean
root.materials.items = root.materials.Neohookean("hasan")

#root.materials = root.Materials([Neohookean])

#root.materials.items = [1]
#root.materials.list[0] = root.materials.NeoHookean("abass")

#root = Root(other=Root.Other(time_steps="hasan"))

root.other.time_steps = "all"

#root.materials.pop(len(root.materials.list)-1)
print (root.materials.items)
print(root.as_dict())
#print(root.__dict__)

""" time_object = root.time.Object3()
root.time.value = root.time.Object3()
root.time.value.time_steps = 2 """
#root.time.value = "2.5"
#root.geometry.mesh_sequence = "path.obj"

root.geometry.gamma = 2.0

json_str = json.dumps(root.as_dict())
print(json_str)