
from typing import Optional, Iterable
from enum import Enum
import json

def drop_none(d):
    return {k: v for k, v in d.items() if v is not None} if type(d) == dict else d

def extension_check(filename, extensions):
    if not filename.endswith(tuple(extensions)):
        raise ValueError(
            f"Invalid file extension: {filename!r}. "
            f"Allowed extension are: {extensions}"
        )
    return filename

def class_check(value, allowed):
    #allowed = (Time.Object1, Time.Object2)
    if not isinstance(value, tuple(allowed)):
        allowed_names = ", ".join(cls.__qualname__ for cls in allowed)
        raise TypeError(
            f"Invalid variable type: {type(value).__name__}. "
            f"Expected {allowed_names}"
        )
    return value
    
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

def range_check(value, min, max):
    if (value >= min if min is not None else True) and (value <= max if max is not None else True):
        return value
    else:
        min_text = f" {min} ≤" if min is not None else ""
        max_text = f" ≤ {max}" if max is not None else ""

        raise TypeError(f"Value {value} is out of range. Expected{min_text} value{max_text}.")

def type_check(variable, tp):
    if not isinstance(variable, tp):
        raise TypeError(f"Expected type '{tp.__name__}', but got '{type(variable).__name__}'")
    return variable

class Root(object):
    '''Root of the configuration file.
    \nRequired: ['string1', 'time']
    \nOptional: ['geometry', 'other', 'materials']'''
    def __init__(
        self,
        string1: str = None,
        time: Optional["Root.Time"] = None,
        geometry: Optional["Root.Geometry"] = None,
        other: Optional["Root.Other"] = None,
        materials: Optional["Root.Materials"] = None
    ):
        self._string1 = type_check(string1, str) if string1 is not None else None
        self._time = type_check(time, self.Time) if time else self.Time()
        self._geometry = type_check(geometry, self.Geometry) if geometry else self.Geometry()
        self._other = type_check(other, self.Other) if other else self.Other()
        self._materials = type_check(materials, self.Materials) if materials else self.Materials()
 
    @property
    def string1(self):
        return self._string1

    @string1.setter
    def string1(self, value):
        ''' 
        There is no definition
        '''
        self._string1 = type_check(value, str) 
 
    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        ''' 
        This is a polymorphic variable, assign an object from its classes to the value
        \nRequired: []
        \nOptional: ['int', 'float', 'object3', 'object4', 'object5']
        '''
        self._time = type_check(value, self.Time) 
 
    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, value):
        ''' 
        Size of the minumum component for collision
        \nRequired: ['gamma', 'linear_displacement_offset']
        \nOptional: ['nested', 'volume_selection', 'normalize_mesh', 'mesh_sequence']
        '''
        self._geometry = type_check(value, self.Geometry) 
 
    @property
    def other(self):
        return self._other

    @other.setter
    def other(self, value):
        ''' 
        There is no definition
        \nRequired: []
        \nOptional: ['nested', 'time_steps']
        '''
        self._other = type_check(value, self.Other) 
 
    @property
    def materials(self):
        return self._materials

    @materials.setter
    def materials(self, value):
        ''' 
        Material Parameters lists including ID pointing to volume selection, Young's modulus ($E$), Poisson's ratio ($\nu$), Density ($\rho$), or Lamé constants ($\lambda$ and $\mu$).
        \nRequired: []
        \nOptional: ['NeoHookean', 'MooneyRivlin']
        '''
        self._materials = type_check(value, self.Materials) 

    def check_required(self):
        
        if self.string1 is None:
            print("Requiered variable Root.string1 does not have value")
        self.time.check_required()
        return

    def as_dict(self):
        return drop_none({"string1": self._string1,"time": self._time.as_dict(),"geometry": self._geometry.as_dict(),"other": self._other.as_dict(),"materials": self._materials.as_dict(),})

    class Time(object):
        '''This is a polymorphic variable, assign an object from its classes to the value
        \nRequired: []
        \nOptional: ['int', 'float', 'object3', 'object4', 'object5']'''
        def __init__(
            self,
            value : object = None
        ):
            self._value = class_check(value, [int, float, self.Object3, self.Object4, self.Object5]) if value is not None else None

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, value):
            ''' 
            This is a polymorphic variable, assign an object from its classes to the value
            '''
            self._value = class_check(value, [int, float, self.Object3, self.Object4, self.Object5]) 

        def check_required(self):

            if self.value is None:
                print("Requiered variable Root.Time.value does not have value")
            else:
                if type(self.value) not in [['int', 'float', 'list', 'str', 'bool']]:
                    self.value.check_required()
            return

        def as_dict(self):
            return drop_none(self._value.as_dict() if isinstance(self._value, tuple([self.Object3, self.Object4, self.Object5])) else self._value)

        class Object3(object):
            '''The time parameters: start time `t0`, end time `tend`, time step `dt`.
            \nRequired: ['tend', 'dt']
            \nOptional: ['t0']'''
            def __init__(
                self,
                tend: float = None,
                dt: float = None,
                t0: float = 0.0
            ):
                self._tend = range_check(type_check(tend, float), 0, None) if tend is not None else None
                self._dt = range_check(type_check(dt, float), 0, None) if dt is not None else None
                self._t0 = range_check(type_check(t0, float), 0, None) if t0 is not None else None

            @property
            def tend(self):
                return self._tend

            @tend.setter
            def tend(self, value):
                ''' 
                Ending time
                '''
                self._tend = range_check(type_check(value, float), 0, None) 

            @property
            def dt(self):
                return self._dt

            @dt.setter
            def dt(self, value):
                ''' 
                Time step size $\Delta t$
                '''
                self._dt = range_check(type_check(value, float), 0, None) 

            @property
            def t0(self):
                return self._t0

            @t0.setter
            def t0(self, value):
                ''' 
                Startning time
                '''
                self._t0 = range_check(type_check(value, float), 0, None) 

            def check_required(self):

                if self.tend is None:
                    print("Requiered variable Root.Time.Object3.tend does not have value")

                if self.dt is None:
                    print("Requiered variable Root.Time.Object3.dt does not have value")
                return

            def as_dict(self):
                return drop_none({"tend": self._tend,"dt": self._dt,"t0": self._t0,})


        class Object4(object):
            '''The time parameters: start time `t0`, time step `dt`, number of time steps.
            \nRequired: ['time_steps', 'dt']
            \nOptional: ['t0']'''
            def __init__(
                self,
                time_steps: int = None,
                dt: float = None,
                t0: float = 0.0
            ):
                self._time_steps = range_check(type_check(time_steps, int), 0, None) if time_steps is not None else None
                self._dt = range_check(type_check(dt, float), 0, None) if dt is not None else None
                self._t0 = range_check(type_check(t0, float), 0, None) if t0 is not None else None

            @property
            def time_steps(self):
                return self._time_steps

            @time_steps.setter
            def time_steps(self, value):
                ''' 
                Number of time steps
                '''
                self._time_steps = range_check(type_check(value, int), 0, None) 

            @property
            def dt(self):
                return self._dt

            @dt.setter
            def dt(self, value):
                ''' 
                Time step size $\Delta t$
                '''
                self._dt = range_check(type_check(value, float), 0, None) 

            @property
            def t0(self):
                return self._t0

            @t0.setter
            def t0(self, value):
                ''' 
                Startning time
                '''
                self._t0 = range_check(type_check(value, float), 0, None) 

            def check_required(self):

                if self.time_steps is None:
                    print("Requiered variable Root.Time.Object4.time_steps does not have value")

                if self.dt is None:
                    print("Requiered variable Root.Time.Object4.dt does not have value")
                return

            def as_dict(self):
                return drop_none({"time_steps": self._time_steps,"dt": self._dt,"t0": self._t0,})


        class Object5(object):
            '''The time parameters: start time `t0`, end time `tend`, number of time steps.
            \nRequired: ['time_steps', 'tend']
            \nOptional: ['t0']'''
            def __init__(
                self,
                time_steps: int = None,
                tend: float = None,
                t0: float = 0.0
            ):
                self._time_steps = range_check(type_check(time_steps, int), 0, None) if time_steps is not None else None
                self._tend = range_check(type_check(tend, float), 0, None) if tend is not None else None
                self._t0 = range_check(type_check(t0, float), 0, None) if t0 is not None else None

            @property
            def time_steps(self):
                return self._time_steps

            @time_steps.setter
            def time_steps(self, value):
                ''' 
                Number of time steps
                '''
                self._time_steps = range_check(type_check(value, int), 0, None) 

            @property
            def tend(self):
                return self._tend

            @tend.setter
            def tend(self, value):
                ''' 
                Ending time
                '''
                self._tend = range_check(type_check(value, float), 0, None) 

            @property
            def t0(self):
                return self._t0

            @t0.setter
            def t0(self, value):
                ''' 
                Startning time
                '''
                self._t0 = range_check(type_check(value, float), 0, None) 

            def check_required(self):

                if self.time_steps is None:
                    print("Requiered variable Root.Time.Object5.time_steps does not have value")

                if self.tend is None:
                    print("Requiered variable Root.Time.Object5.tend does not have value")
                return

            def as_dict(self):
                return drop_none({"time_steps": self._time_steps,"tend": self._tend,"t0": self._t0,})



    class Geometry(object):
        '''Size of the minumum component for collision
        \nRequired: ['gamma', 'linear_displacement_offset']
        \nOptional: ['nested', 'volume_selection', 'normalize_mesh', 'mesh_sequence']'''
        def __init__(
            self,
            gamma: float = 0.5,
            linear_displacement_offset: Optional[Iterable[str]] = None,
            nested: int = 3,
            volume_selection: Optional["Root.Geometry.Volume_selection"] = None,
            normalize_mesh: bool = False,
            mesh_sequence: str = None
        ):
            self._gamma = range_check(type_check(gamma, float), 0, 1) if gamma is not None else None
            self._linear_displacement_offset = [] if linear_displacement_offset is None else [type_check(i, str) for i in linear_displacement_offset]
            self._nested = type_check(nested, int) if nested is not None else None
            self._volume_selection = type_check(volume_selection, self.Volume_selection) if volume_selection else self.Volume_selection()
            self._normalize_mesh = type_check(normalize_mesh, bool) if normalize_mesh is not None else None
            self._mesh_sequence = extension_check(type_check(mesh_sequence, str), ['.obj', '.msh', '.stl', '.ply', '.mesh']) if mesh_sequence is not None else None

        @property
        def gamma(self):
            return self._gamma

        @gamma.setter
        def gamma(self, value):
            ''' 
            Newmark gamma
            '''
            self._gamma = range_check(type_check(value, float), 0, 1) 

        @property
        def linear_displacement_offset(self):
            return self._linear_displacement_offset

        @linear_displacement_offset.setter
        def linear_displacement_offset(self, value):
            ''' 
            There is no definition
            \nRequired: []
            \nOptional: ['value']
            '''
            self._linear_displacement_offset = [type_check(i, str) for i in (type_check(value, list) if value else [])]

        def linear_displacement_offset_add(self, value):
            '''Add to list '''
            self._linear_displacement_offset.append(type_check(value, str))

        def linear_displacement_offset_clear(self):
            '''Clear list (make empty)'''
            self._linear_displacement_offset.clear()

        def linear_displacement_offset_pop(self, index=-1):
            '''Remove by index from list'''
            return self._linear_displacement_offset.pop(index)

        def linear_displacement_offset_remove(self, item):
            '''Safe remove specific item from list'''
            if item in self._list:
                self._linear_displacement_offset.remove(item)


        @property
        def nested(self):
            return self._nested

        @nested.setter
        def nested(self, value):
            ''' 
            There is no definition
            '''
            self._nested = type_check(value, int) 

        @property
        def volume_selection(self):
            return self._volume_selection

        @volume_selection.setter
        def volume_selection(self, value):
            ''' 
            Offsets the volume IDs loaded from the mesh.
            \nRequired: []
            \nOptional: ['id_offset']
            '''
            self._volume_selection = type_check(value, self.Volume_selection) 

        @property
        def normalize_mesh(self):
            return self._normalize_mesh

        @normalize_mesh.setter
        def normalize_mesh(self, value):
            ''' 
            Rescale the mesh to it fits in the biunit cube
            '''
            self._normalize_mesh = type_check(value, bool) 

        @property
        def mesh_sequence(self):
            return self._mesh_sequence

        @mesh_sequence.setter
        def mesh_sequence(self, value):
            ''' 
            Path of the mesh file to load.
            '''
            self._mesh_sequence = extension_check(type_check(value, str), ['.obj', '.msh', '.stl', '.ply', '.mesh']) 

        def check_required(self):

            if self.gamma is None:
                print("Requiered variable Root.Geometry.gamma does not have value")

            if self.linear_displacement_offset:
                print("Requiered variable Root.Geometry.linear_displacement_offset does not have value")
            return

        def as_dict(self):
            return drop_none({"gamma": self._gamma,"linear_displacement_offset": self._linear_displacement_offset,"nested": self._nested,"volume_selection": self._volume_selection.as_dict(),"normalize_mesh": self._normalize_mesh,"mesh_sequence": self._mesh_sequence,})

        class Volume_selection(object):
            '''Offsets the volume IDs loaded from the mesh.
            \nRequired: []
            \nOptional: ['id_offset']'''
            def __init__(
                self,
                id_offset: int = 0
            ):
                self._id_offset = type_check(id_offset, int) if id_offset is not None else None

            @property
            def id_offset(self):
                return self._id_offset

            @id_offset.setter
            def id_offset(self, value):
                ''' 
                Offsets the volume IDs loaded from the mesh.
                '''
                self._id_offset = type_check(value, int) 

            def check_required(self):

                return

            def as_dict(self):
                return drop_none({"id_offset": self._id_offset,})



    class Other(object):
        '''There is no definition
        \nRequired: []
        \nOptional: ['nested', 'time_steps']'''
        class Time_steps(str, Enum):
            ALL = "all",
            STATIC = "static"

        def __init__(
            self,
            nested: int = 3,
            time_steps: Time_steps = None
        ):
            self._nested = type_check(nested, int) if nested is not None else None
            self._time_steps = enum_check(time_steps, self.Time_steps)

        @property
        def nested(self):
            return self._nested

        @nested.setter
        def nested(self, value):
            ''' 
            There is no definition
            '''
            self._nested = type_check(value, int) 

        @property
        def time_steps(self):
            return self._time_steps

        @time_steps.setter
        def time_steps(self, value):
            ''' 
            Number of time steps to test.
            '''
            self._time_steps = enum_check(value, self.Time_steps) 

        def check_required(self):

            return

        def as_dict(self):
            return drop_none({"nested": self._nested,"time_steps": self._time_steps.value if self._time_steps is not None else None,})


    class Materials(object):
        '''Material Parameters lists including ID pointing to volume selection, Young's modulus ($E$), Poisson's ratio ($\nu$), Density ($\rho$), or Lamé constants ($\lambda$ and $\mu$).
        \nRequired: []
        \nOptional: ['NeoHookean', 'MooneyRivlin']'''
        def __init__(
            self,
            items : list = None
        ):
            self._items = [class_check(i, [self.Neohookean, self.Mooneyrivlin]) for i in (type_check(items, list) if items else [])]

        @property
        def items(self):
            return self._items

        @items.setter
        def items(self, items : list):
            ''' Replace the list '''
            self._items = [class_check(i, [self.Neohookean, self.Mooneyrivlin]) for i in (type_check(items, list) if items else [])]

        def add(self, item : object):
            ''' Add to the list '''
            self._items.append(class_check(item, [self.Neohookean, self.Mooneyrivlin]))

        def clear(self):
            '''Clear list (make empty)'''
            self._items.clear()

        def pop(self, index=-1):
            '''Remove by index from list'''
            return self._items.pop(index)

        def remove(self, item):
            '''Safe remove specific item from list'''
            if item in self._items:
                self._items.remove(item) 

        def check_required(self):

            if self.items:
                for item in self.items:
                    if type(item) not in [['int', 'float', 'list', 'str', 'bool']]:
                        item.check_required()
            else:
                print("Requiered variable Root.Materials.items does not have value")
            return

        def as_dict(self):
            return drop_none([i.as_dict() if isinstance(i, tuple([self.Neohookean, self.Mooneyrivlin])) else i for i in self._items])

        class Neohookean(object):
            '''Material Parameters including ID, Young's modulus ($E$), Poisson's ratio ($\nu$), density ($\rho$)
            \nRequired: ['type', 'E']
            \nOptional: ['id', 'elasticity_tensor']'''
            def __init__(
                self,
                type: str = None,
                E: int = None,
                id: Optional[Iterable[int]] = None,
                elasticity_tensor: Optional["Root.Materials.Neohookean.Elasticity_tensor"] = None
            ):
                self._type = type_check(type, str) if type is not None else None
                self._E = type_check(E, int) if E is not None else None
                self._id = [] if id is None else [type_check(i, int) for i in id]
                self._elasticity_tensor = type_check(elasticity_tensor, self.Elasticity_tensor) if elasticity_tensor else self.Elasticity_tensor()

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of material
                '''
                self._type = type_check(value, str) 

            @property
            def E(self):
                return self._E

            @E.setter
            def E(self, value):
                ''' 
                Young's modulus
                '''
                self._E = type_check(value, int) 

            @property
            def id(self):
                return self._id

            @id.setter
            def id(self, value):
                ''' 
                Volume selection IDs
                \nRequired: []
                \nOptional: ['value']
                '''
                self._id = [type_check(i, int) for i in (type_check(value, list) if value else [])]

            def id_add(self, value):
                '''Add to list '''
                self._id.append(type_check(value, int))

            def id_clear(self):
                '''Clear list (make empty)'''
                self._id.clear()

            def id_pop(self, index=-1):
                '''Remove by index from list'''
                return self._id.pop(index)

            def id_remove(self, item):
                '''Safe remove specific item from list'''
                if item in self._list:
                    self._id.remove(item)


            @property
            def elasticity_tensor(self):
                return self._elasticity_tensor

            @elasticity_tensor.setter
            def elasticity_tensor(self, value):
                ''' 
                Symmetric elasticity tensor
                \nRequired: []
                \nOptional: ['value']
                '''
                self._elasticity_tensor = type_check(value, self.Elasticity_tensor) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Materials.Neohookean.type does not have value")

                if self.E is None:
                    print("Requiered variable Root.Materials.Neohookean.E does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type,"E": self._E,"id": self._id,"elasticity_tensor": self._elasticity_tensor.as_dict(),})

            class Elasticity_tensor(object):
                '''Symmetric elasticity tensor
                \nRequired: []
                \nOptional: ['value']'''
                def __init__(
                    self,
                    items : list = None
                ):
                    self._items = [class_check(i, [self.Value]) for i in (type_check(items, list) if items else [])]

                @property
                def items(self):
                    return self._items

                @items.setter
                def items(self, items : list):
                    ''' Replace the list '''
                    self._items = [class_check(i, [self.Value]) for i in (type_check(items, list) if items else [])]

                def add(self, item : object):
                    ''' Add to the list '''
                    self._items.append(class_check(item, [self.Value]))

                def clear(self):
                    '''Clear list (make empty)'''
                    self._items.clear()

                def pop(self, index=-1):
                    '''Remove by index from list'''
                    return self._items.pop(index)

                def remove(self, item):
                    '''Safe remove specific item from list'''
                    if item in self._items:
                        self._items.remove(item) 

                def check_required(self):

                    if self.items:
                        for item in self.items:
                            if type(item) not in [['int', 'float', 'list', 'str', 'bool']]:
                                item.check_required()
                    else:
                        print("Requiered variable Root.Materials.Neohookean.Elasticity_tensor.items does not have value")
                    return

                def as_dict(self):
                    return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

                class Value(object):
                    '''Entries of elasticity tensor
                    \nRequired: ['input']
                    \nOptional: []'''
                    def __init__(
                        self,
                        input: int = 1
                    ):
                        self._input = type_check(input, int) if input is not None else None

                    @property
                    def input(self):
                        return self._input

                    @input.setter
                    def input(self, value):
                        ''' 
                        There is no definition
                        '''
                        self._input = type_check(value, int) 

                    def check_required(self):

                        if self.input is None:
                            print("Requiered variable Root.Materials.Neohookean.Elasticity_tensor.Value.input does not have value")
                        return

                    def as_dict(self):
                        return drop_none({"input": self._input,})




        class Mooneyrivlin(object):
            '''Material Parameters including ID, for Mooney-Rivlin
            \nRequired: ['type', 'c1']
            \nOptional: ['id', 'elasticity_tensor']'''
            def __init__(
                self,
                type: str = None,
                c1: int = None,
                id: Optional[Iterable[int]] = None,
                elasticity_tensor: Optional["Root.Materials.Mooneyrivlin.Elasticity_tensor"] = None
            ):
                self._type = type_check(type, str) if type is not None else None
                self._c1 = type_check(c1, int) if c1 is not None else None
                self._id = [] if id is None else [type_check(i, int) for i in id]
                self._elasticity_tensor = type_check(elasticity_tensor, self.Elasticity_tensor) if elasticity_tensor else self.Elasticity_tensor()

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of material
                '''
                self._type = type_check(value, str) 

            @property
            def c1(self):
                return self._c1

            @c1.setter
            def c1(self, value):
                ''' 
                First Parameter for Mooney-Rivlin
                '''
                self._c1 = type_check(value, int) 

            @property
            def id(self):
                return self._id

            @id.setter
            def id(self, value):
                ''' 
                Volume selection IDs
                \nRequired: []
                \nOptional: ['value']
                '''
                self._id = [type_check(i, int) for i in (type_check(value, list) if value else [])]

            def id_add(self, value):
                '''Add to list '''
                self._id.append(type_check(value, int))

            def id_clear(self):
                '''Clear list (make empty)'''
                self._id.clear()

            def id_pop(self, index=-1):
                '''Remove by index from list'''
                return self._id.pop(index)

            def id_remove(self, item):
                '''Safe remove specific item from list'''
                if item in self._list:
                    self._id.remove(item)


            @property
            def elasticity_tensor(self):
                return self._elasticity_tensor

            @elasticity_tensor.setter
            def elasticity_tensor(self, value):
                ''' 
                Symmetric elasticity tensor
                \nRequired: []
                \nOptional: ['value']
                '''
                self._elasticity_tensor = type_check(value, self.Elasticity_tensor) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Materials.Mooneyrivlin.type does not have value")

                if self.c1 is None:
                    print("Requiered variable Root.Materials.Mooneyrivlin.c1 does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type,"c1": self._c1,"id": self._id,"elasticity_tensor": self._elasticity_tensor.as_dict(),})

            class Elasticity_tensor(object):
                '''Symmetric elasticity tensor
                \nRequired: []
                \nOptional: ['value']'''
                def __init__(
                    self,
                    items : list = None
                ):
                    self._items = [class_check(i, [self.Value]) for i in (type_check(items, list) if items else [])]

                @property
                def items(self):
                    return self._items

                @items.setter
                def items(self, items : list):
                    ''' Replace the list '''
                    self._items = [class_check(i, [self.Value]) for i in (type_check(items, list) if items else [])]

                def add(self, item : object):
                    ''' Add to the list '''
                    self._items.append(class_check(item, [self.Value]))

                def clear(self):
                    '''Clear list (make empty)'''
                    self._items.clear()

                def pop(self, index=-1):
                    '''Remove by index from list'''
                    return self._items.pop(index)

                def remove(self, item):
                    '''Safe remove specific item from list'''
                    if item in self._items:
                        self._items.remove(item) 

                def check_required(self):

                    if self.items:
                        for item in self.items:
                            if type(item) not in [['int', 'float', 'list', 'str', 'bool']]:
                                item.check_required()
                    else:
                        print("Requiered variable Root.Materials.Mooneyrivlin.Elasticity_tensor.items does not have value")
                    return

                def as_dict(self):
                    return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

                class Value(object):
                    '''Entries of elasticity tensor
                    \nRequired: ['input']
                    \nOptional: []'''
                    def __init__(
                        self,
                        input: int = 1
                    ):
                        self._input = type_check(input, int) if input is not None else None

                    @property
                    def input(self):
                        return self._input

                    @input.setter
                    def input(self, value):
                        ''' 
                        There is no definition
                        '''
                        self._input = type_check(value, int) 

                    def check_required(self):

                        if self.input is None:
                            print("Requiered variable Root.Materials.Mooneyrivlin.Elasticity_tensor.Value.input does not have value")
                        return

                    def as_dict(self):
                        return drop_none({"input": self._input,})





