
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
    \nRequired: ['geometry', 'materials']
    \nOptional: ['units', 'preset_problem', 'common', 'root_path', 'space', 'time', 'contact', 'solver', 'boundary_conditions', 'initial_conditions', 'constraints', 'output', 'input', 'tests']'''
    def __init__(
        self,
        geometry: Optional["Root.Geometry"] = None,
        materials: Optional["Root.Materials"] = None,
        units: Optional["Root.Units"] = None,
        preset_problem: Optional["Root.Preset_problem"] = None,
        common: str = '',
        root_path: str = '',
        space: Optional["Root.Space"] = None,
        time: Optional["Root.Time"] = None,
        contact: Optional["Root.Contact"] = None,
        solver: Optional["Root.Solver"] = None,
        boundary_conditions: Optional["Root.Boundary_conditions"] = None,
        initial_conditions: Optional["Root.Initial_conditions"] = None,
        constraints: Optional["Root.Constraints"] = None,
        output: Optional["Root.Output"] = None,
        input: Optional["Root.Input"] = None,
        tests: Optional["Root.Tests"] = None
    ):
        self._geometry = type_check(geometry, self.Geometry) if geometry else self.Geometry()
        self._materials = type_check(materials, self.Materials) if materials else self.Materials()
        self._units = type_check(units, self.Units) if units else self.Units()
        self._preset_problem = type_check(preset_problem, self.Preset_problem) if preset_problem else self.Preset_problem()
        self._common = extension_check(type_check(common, str), ['.json']) if common is not None else None
        self._root_path = type_check(root_path, str) if root_path is not None else None
        self._space = type_check(space, self.Space) if space else self.Space()
        self._time = type_check(time, self.Time) if time else self.Time()
        self._contact = type_check(contact, self.Contact) if contact else self.Contact()
        self._solver = type_check(solver, self.Solver) if solver else self.Solver()
        self._boundary_conditions = type_check(boundary_conditions, self.Boundary_conditions) if boundary_conditions else self.Boundary_conditions()
        self._initial_conditions = type_check(initial_conditions, self.Initial_conditions) if initial_conditions else self.Initial_conditions()
        self._constraints = type_check(constraints, self.Constraints) if constraints else self.Constraints()
        self._output = type_check(output, self.Output) if output else self.Output()
        self._input = type_check(input, self.Input) if input else self.Input()
        self._tests = type_check(tests, self.Tests) if tests else self.Tests()
 
    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, value):
        ''' 
        List of geometry objects.
        \nRequired: []
        \nOptional: ['value', 'mesh_array', 'plane', 'ground', 'mesh_sequence']
        '''
        self._geometry = range_check(type_check(value, self.Geometry), 1, None) 
 
    @property
    def materials(self):
        return self._materials

    @materials.setter
    def materials(self, value):
        ''' 
        Material Parameters lists including ID pointing to volume selection, Young's modulus ($E$), Poisson's ratio ($\\nu$), Density ($\\rho$), or Lamé constants ($\\lambda$ and $\\mu$).
        \nRequired: []
        \nOptional: ['value']
        '''
        self._materials = type_check(value, self.Materials) 
 
    @property
    def units(self):
        return self._units

    @units.setter
    def units(self, value):
        ''' 
        Basic units used in the code.
        \nRequired: []
        \nOptional: ['length', 'mass', 'time', 'characteristic_length']
        '''
        self._units = type_check(value, self.Units) 
 
    @property
    def preset_problem(self):
        return self._preset_problem

    @preset_problem.setter
    def preset_problem(self, value):
        ''' 
        This is a polymorphic variable, assign an object from its classes to the value
        \nRequired: []
        \nOptional: ['object1', 'object2', 'object3', 'object4', 'object5', 'object6', 'object7', 'object8', 'object9', 'object10', 'object11', 'object12', 'object13', 'object14', 'object15', 'object16', 'object17', 'object18', 'object19', 'object20', 'object21', 'object22', 'object23', 'object24', 'object25', 'object26', 'object27', 'object28', 'object29', 'object30', 'object31', 'object32', 'object33', 'object34', 'object35', 'object36', 'object37', 'object38', 'object39', 'object40', 'object41', 'object42', 'object43']
        '''
        self._preset_problem = type_check(value, self.Preset_problem) 
 
    @property
    def common(self):
        return self._common

    @common.setter
    def common(self, value):
        ''' 
        Path to common settings will patch the current file.
        '''
        self._common = extension_check(type_check(value, str), ['.json']) 
 
    @property
    def root_path(self):
        return self._root_path

    @root_path.setter
    def root_path(self, value):
        ''' 
        Path for all relative paths, set automatically to the folder containing this JSON.
        '''
        self._root_path = type_check(value, str) 
 
    @property
    def space(self):
        return self._space

    @space.setter
    def space(self, value):
        ''' 
        Options related to the FE space.
        \nRequired: []
        \nOptional: ['discr_order', 'discr_orderq', 'pressure_discr_order', 'basis_type', 'poly_basis_type', 'use_p_ref', 'remesh', 'advanced']
        '''
        self._space = type_check(value, self.Space) 
 
    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        ''' 
        This is a polymorphic variable, assign an object from its classes to the value
        \nRequired: []
        \nOptional: ['object1', 'object2', 'object3']
        '''
        self._time = type_check(value, self.Time) 
 
    @property
    def contact(self):
        return self._contact

    @contact.setter
    def contact(self, value):
        ''' 
        Contact handling parameters.
        \nRequired: []
        \nOptional: ['enabled', 'dhat', 'dhat_percentage', 'epsv', 'friction_coefficient', 'use_convergent_formulation', 'use_area_weighting', 'use_improved_max_operator', 'use_physical_barrier', 'collision_mesh', 'use_gcp_formulation', 'alpha_n', 'alpha_t', 'min_distance_ratio', 'use_adaptive_dhat', 'periodic', 'adhesion']
        '''
        self._contact = type_check(value, self.Contact) 
 
    @property
    def solver(self):
        return self._solver

    @solver.setter
    def solver(self, value):
        ''' 
        The settings for the solver including linear solver, nonlinear solver, and some advanced options.
        \nRequired: []
        \nOptional: ['max_threads', 'linear', 'adjoint_linear', 'nonlinear', 'augmented_lagrangian', 'contact', 'rayleigh_damping', 'advanced']
        '''
        self._solver = type_check(value, self.Solver) 
 
    @property
    def boundary_conditions(self):
        return self._boundary_conditions

    @boundary_conditions.setter
    def boundary_conditions(self, value):
        ''' 
        The settings for boundary conditions.
        \nRequired: []
        \nOptional: ['rhs', 'dirichlet_boundary', 'neumann_boundary', 'normal_aligned_neumann_boundary', 'pressure_boundary', 'pressure_cavity', 'obstacle_displacements', 'periodic_boundary']
        '''
        self._boundary_conditions = type_check(value, self.Boundary_conditions) 
 
    @property
    def initial_conditions(self):
        return self._initial_conditions

    @initial_conditions.setter
    def initial_conditions(self, value):
        ''' 
        Initial conditions for the time-dependent problem, imposed on the main variable, its derivative or second derivative
        \nRequired: []
        \nOptional: ['solution', 'velocity', 'acceleration']
        '''
        self._initial_conditions = type_check(value, self.Initial_conditions) 
 
    @property
    def constraints(self):
        return self._constraints

    @constraints.setter
    def constraints(self, value):
        ''' 
        soft and hard constraints
        \nRequired: []
        \nOptional: ['soft', 'hard']
        '''
        self._constraints = type_check(value, self.Constraints) 
 
    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value):
        ''' 
        output settings
        \nRequired: []
        \nOptional: ['directory', 'log', 'json', 'restart_json', 'paraview', 'data', 'advanced', 'reference', 'stats']
        '''
        self._output = type_check(value, self.Output) 
 
    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, value):
        ''' 
        input data
        \nRequired: []
        \nOptional: ['data']
        '''
        self._input = type_check(value, self.Input) 
 
    @property
    def tests(self):
        return self._tests

    @tests.setter
    def tests(self, value):
        ''' 
        Used to test to compare different norms of solutions.
        \nRequired: []
        \nOptional: ['err_h1', 'err_h1_semi', 'err_l2', 'err_linf', 'err_linf_grad', 'err_lp', 'margin', 'time_steps']
        '''
        self._tests = type_check(value, self.Tests) 

    def check_required(self):
        self.geometry.check_required()
        self.materials.check_required()
        return

    def as_dict(self):
        return drop_none({"geometry": self._geometry.as_dict(),"materials": self._materials.as_dict(),"units": self._units.as_dict(),"preset_problem": self._preset_problem.as_dict(),"common": self._common,"root_path": self._root_path,"space": self._space.as_dict(),"time": self._time.as_dict(),"contact": self._contact.as_dict(),"solver": self._solver.as_dict(),"boundary_conditions": self._boundary_conditions.as_dict(),"initial_conditions": self._initial_conditions.as_dict(),"constraints": self._constraints.as_dict(),"output": self._output.as_dict(),"input": self._input.as_dict(),"tests": self._tests.as_dict(),})

    class Geometry(object):
        '''List of geometry objects.
        \nRequired: []
        \nOptional: ['value', 'mesh_array', 'plane', 'ground', 'mesh_sequence']'''
        def __init__(
            self,
            items : list = None
        ):
            self._items = [class_check(i, [self.Value, self.Mesh_array, self.Plane, self.Ground, self.Mesh_sequence]) for i in (type_check(items, list) if items else [])]

        @property
        def items(self):
            return self._items

        @items.setter
        def items(self, items : list):
            ''' Replace the list '''
            self._items = [class_check(i, [self.Value, self.Mesh_array, self.Plane, self.Ground, self.Mesh_sequence]) for i in (type_check(items, list) if items else [])]

        def add(self, item : object):
            ''' Add to the list '''
            self._items.append(class_check(item, [self.Value, self.Mesh_array, self.Plane, self.Ground, self.Mesh_sequence]))

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
                print("Requiered variable Root.Geometry.items does not have value")
            return

        def as_dict(self):
            return drop_none([i.as_dict() if isinstance(i, tuple([self.Value, self.Mesh_array, self.Plane, self.Ground, self.Mesh_sequence])) else i for i in self._items])

        class Value(object):
            '''Each geometry object stores a mesh, a set of transformations applied to it after loading, and a set of selections, which can be used to specify boundary conditions, materials, optimization parameters and other quantities that can be associated with a part of an object.
            \nRequired: ['mesh']
            \nOptional: ['type', 'extract', 'unit', 'transformation', 'volume_selection', 'surface_selection', 'curve_selection', 'point_selection', 'n_refs', 'advanced', 'enabled', 'is_obstacle']'''
            class Type(str, Enum):
                MESH = 'mesh'
                PLANE = 'plane'
                GROUND = 'ground'
                MESH_SEQUENCE = 'mesh_sequence'
                MESH_ARRAY = 'mesh_array'

            class Extract(str, Enum):
                VOLUME = 'volume'
                EDGES = 'edges'
                POINTS = 'points'
                SURFACE = 'surface'

            def __init__(
                self,
                mesh: str = None,
                type: "Type" = 'mesh',
                extract: "Extract" = 'volume',
                unit: str = '',
                transformation: Optional["Root.Geometry.Value.Transformation"] = None,
                volume_selection: Optional["Root.Geometry.Value.Volume_selection"] = None,
                surface_selection: Optional["Root.Geometry.Value.Surface_selection"] = None,
                curve_selection: Optional["Root.Geometry.Value.Curve_selection"] = None,
                point_selection: Optional["Root.Geometry.Value.Point_selection"] = None,
                n_refs: int = 0,
                advanced: Optional["Root.Geometry.Value.Advanced"] = None,
                enabled: bool = True,
                is_obstacle: bool = False
            ):
                self._mesh = extension_check(type_check(mesh, str), ['.obj', '.msh', '.stl', '.ply', '.mesh']) if mesh is not None else None
                self._type = enum_check(type, self.Type)
                self._extract = enum_check(extract, self.Extract)
                self._unit = type_check(unit, str) if unit is not None else None
                self._transformation = type_check(transformation, self.Transformation) if transformation else self.Transformation()
                self._volume_selection = type_check(volume_selection, self.Volume_selection) if volume_selection else self.Volume_selection()
                self._surface_selection = type_check(surface_selection, self.Surface_selection) if surface_selection else self.Surface_selection()
                self._curve_selection = type_check(curve_selection, self.Curve_selection) if curve_selection else self.Curve_selection()
                self._point_selection = type_check(point_selection, self.Point_selection) if point_selection else self.Point_selection()
                self._n_refs = type_check(n_refs, int) if n_refs is not None else None
                self._advanced = type_check(advanced, self.Advanced) if advanced else self.Advanced()
                self._enabled = type_check(enabled, bool) if enabled is not None else None
                self._is_obstacle = type_check(is_obstacle, bool) if is_obstacle is not None else None

            @property
            def mesh(self):
                return self._mesh

            @mesh.setter
            def mesh(self, value):
                ''' 
                Path of the mesh file to load.
                '''
                self._mesh = extension_check(type_check(value, str), ['.obj', '.msh', '.stl', '.ply', '.mesh']) 

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of geometry, currently only one supported. In future we will add stuff like planes, spheres, etc.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def extract(self):
                return self._extract

            @extract.setter
            def extract(self, value):
                ''' 
                Used to extract stuff from the mesh. Eg extract surface extracts the surface from a tet mesh.
                '''
                self._extract = enum_check(value, self.Extract) 

            @property
            def unit(self):
                return self._unit

            @unit.setter
            def unit(self, value):
                ''' 
                Units of the geometric model.
                '''
                self._unit = type_check(value, str) 

            @property
            def transformation(self):
                return self._transformation

            @transformation.setter
            def transformation(self, value):
                ''' 
                Geometric transformations applied to the geometry after loading it.
                \nRequired: []
                \nOptional: ['translation', 'rotation', 'rotation_mode', 'scale', 'dimensions']
                '''
                self._transformation = type_check(value, self.Transformation) 

            @property
            def volume_selection(self):
                return self._volume_selection

            @volume_selection.setter
            def volume_selection(self, value):
                ''' 
                This is a polymorphic variable, assign an object from its classes to the value
                \nRequired: []
                \nOptional: ['object1', 'list']
                '''
                self._volume_selection = type_check(value, self.Volume_selection) 

            @property
            def surface_selection(self):
                return self._surface_selection

            @surface_selection.setter
            def surface_selection(self, value):
                ''' 
                List of selection (ID assignment) operations to apply to the geometry; operations can be box, sphere, etc.
                \nRequired: []
                \nOptional: ['value']
                '''
                self._surface_selection = type_check(value, self.Surface_selection) 

            @property
            def curve_selection(self):
                return self._curve_selection

            @curve_selection.setter
            def curve_selection(self, value):
                ''' 
                Selection of curves
                \nRequired: []
                \nOptional: []
                '''
                self._curve_selection = type_check(value, self.Curve_selection) 

            @property
            def point_selection(self):
                return self._point_selection

            @point_selection.setter
            def point_selection(self, value):
                ''' 
                List of selection (ID assignment) operations to apply to the geometry; operations can be box, sphere, etc.
                \nRequired: []
                \nOptional: ['value']
                '''
                self._point_selection = type_check(value, self.Point_selection) 

            @property
            def n_refs(self):
                return self._n_refs

            @n_refs.setter
            def n_refs(self, value):
                ''' 
                number of uniform refinements
                '''
                self._n_refs = type_check(value, int) 

            @property
            def advanced(self):
                return self._advanced

            @advanced.setter
            def advanced(self, value):
                ''' 
                Advanced options for geometry
                \nRequired: []
                \nOptional: ['normalize_mesh', 'force_linear_geometry', 'refinement_location', 'min_component']
                '''
                self._advanced = type_check(value, self.Advanced) 

            @property
            def enabled(self):
                return self._enabled

            @enabled.setter
            def enabled(self, value):
                ''' 
                Skips the geometry if false
                '''
                self._enabled = type_check(value, bool) 

            @property
            def is_obstacle(self):
                return self._is_obstacle

            @is_obstacle.setter
            def is_obstacle(self, value):
                ''' 
                The geometry elements are not included in deforming geometry, only in collision computations
                '''
                self._is_obstacle = type_check(value, bool) 

            def check_required(self):

                if self.mesh is None:
                    print("Requiered variable Root.Geometry.Value.mesh does not have value")
                return

            def as_dict(self):
                return drop_none({"mesh": self._mesh,"type": self._type.value if self._type is not None else None,"extract": self._extract.value if self._extract is not None else None,"unit": self._unit,"transformation": self._transformation.as_dict(),"volume_selection": self._volume_selection.as_dict(),"surface_selection": self._surface_selection.as_dict(),"curve_selection": self._curve_selection.as_dict(),"point_selection": self._point_selection.as_dict(),"n_refs": self._n_refs,"advanced": self._advanced.as_dict(),"enabled": self._enabled,"is_obstacle": self._is_obstacle,})

            class Transformation(object):
                '''Geometric transformations applied to the geometry after loading it.
                \nRequired: []
                \nOptional: ['translation', 'rotation', 'rotation_mode', 'scale', 'dimensions']'''
                def __init__(
                    self,
                    translation: Optional[Iterable[float]] = None,
                    rotation: Optional[Iterable[float]] = None,
                    rotation_mode: str = 'xyz',
                    scale: Optional[Iterable[float]] = None,
                    float: float = 1.0
                ):
                    self._translation = [] if translation is None else [type_check(i, float) for i in translation]
                    self._rotation = [] if rotation is None else [type_check(i, float) for i in rotation]
                    self._rotation_mode = type_check(rotation_mode, str) if rotation_mode is not None else None
                    self._scale = [] if scale is None else [type_check(i, float) for i in scale]
                    self._float = type_check(float, float) if float is not None else None

                @property
                def translation(self):
                    return self._translation

                @translation.setter
                def translation(self, value):
                    ''' 
                    Translate (two entries for 2D problems or three entries for 3D problems).
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._translation = [type_check(i, float) for i in (type_check(value, list) if value else [])]

                def translation_add(self, value):
                    '''Add to list '''
                    self._translation.append(type_check(value, float))

                def translation_clear(self):
                    '''Clear list (make empty)'''
                    self._translation.clear()

                def translation_pop(self, index=-1):
                    '''Remove by index from list'''
                    return self._translation.pop(index)

                def translation_remove(self, item):
                    '''Safe remove specific item from list'''
                    if item in self._list:
                        self._translation.remove(item)


                @property
                def rotation(self):
                    return self._rotation

                @rotation.setter
                def rotation(self, value):
                    ''' 
                    Rotate, in 2D, one number, the rotation angle, in 3D, three or four Euler angles, axis+angle, or a unit quaternion. Depends on rotation mode.
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._rotation = [type_check(i, float) for i in (type_check(value, list) if value else [])]

                def rotation_add(self, value):
                    '''Add to list '''
                    self._rotation.append(type_check(value, float))

                def rotation_clear(self):
                    '''Clear list (make empty)'''
                    self._rotation.clear()

                def rotation_pop(self, index=-1):
                    '''Remove by index from list'''
                    return self._rotation.pop(index)

                def rotation_remove(self, item):
                    '''Safe remove specific item from list'''
                    if item in self._list:
                        self._rotation.remove(item)


                @property
                def rotation_mode(self):
                    return self._rotation_mode

                @rotation_mode.setter
                def rotation_mode(self, value):
                    ''' 
                    Type of rotation, supported are any permutation of [xyz]+, axis_angle, quaternion, or rotation_vector.
                    '''
                    self._rotation_mode = type_check(value, str) 

                @property
                def scale(self):
                    return self._scale

                @scale.setter
                def scale(self, value):
                    ''' 
                    Scale by specified factors along axes (two entries for 2D problems or three entries for 3D problems).
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._scale = [type_check(i, float) for i in (type_check(value, list) if value else [])]

                def scale_add(self, value):
                    '''Add to list '''
                    self._scale.append(type_check(value, float))

                def scale_clear(self):
                    '''Clear list (make empty)'''
                    self._scale.clear()

                def scale_pop(self, index=-1):
                    '''Remove by index from list'''
                    return self._scale.pop(index)

                def scale_remove(self, item):
                    '''Safe remove specific item from list'''
                    if item in self._list:
                        self._scale.remove(item)


                @property
                def float(self):
                    return self._float

                @float.setter
                def float(self, value):
                    ''' 
                    Scale the object so that bounding box dimensions match specified dimensions, 2 entries for 2D problems, 3 entries for 3D problems.
                    '''
                    self._float = type_check(value, float) 

                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({"translation": self._translation,"rotation": self._rotation,"rotation_mode": self._rotation_mode,"scale": self._scale,"float": self._float,})


            class Volume_selection(object):
                '''This is a polymorphic variable, assign an object from its classes to the value
                \nRequired: []
                \nOptional: ['object1', 'list']'''
                def __init__(
                    self,
                    value : object = None
                ):
                    self._value = class_check(value, [self.Object1, list]) if value is not None else None

                @property
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    ''' 
                    This is a polymorphic variable, assign an object from its classes to the value
                    '''
                    self._value = class_check(value, [self.Object1, list]) 

                def check_required(self):

                    if self.value is None:
                        print("Requiered variable Root.Geometry.Value.Volume_selection.value does not have value")
                    else:
                        if type(self.value) not in [['int', 'float', 'list', 'str', 'bool']]:
                            self.value.check_required()
                    return

                def as_dict(self):
                    return drop_none(self._value.as_dict() if isinstance(self._value, tuple([self.Object1])) else self._value)

                class Object1(object):
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



            class Surface_selection(object):
                '''List of selection (ID assignment) operations to apply to the geometry; operations can be box, sphere, etc.
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
                        print("Requiered variable Root.Geometry.Value.Surface_selection.items does not have value")
                    return

                def as_dict(self):
                    return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

                class Value(object):
                    '''Assigns ids to sides touching the bbox of the model using a threshold. Assigns 1+offset to left, 2+offset to bottom, 3+offset to right, 4+offset to top, 5+offset to front, 6+offset to back, 7+offset to everything else.
                    \nRequired: ['threshold']
                    \nOptional: ['id_offset']'''
                    def __init__(
                        self,
                        threshold: None = None,
                        id_offset: int = 0
                    ):
                        self._threshold = type_check(threshold, None) if threshold is not None else None
                        self._id_offset = type_check(id_offset, int) if id_offset is not None else None

                    @property
                    def threshold(self):
                        return self._threshold

                    @threshold.setter
                    def threshold(self, value):
                        ''' 
                        There is no definition
                        '''
                        self._threshold = type_check(value, None) 

                    @property
                    def id_offset(self):
                        return self._id_offset

                    @id_offset.setter
                    def id_offset(self, value):
                        ''' 
                        ID offset of box side selection.
                        '''
                        self._id_offset = type_check(value, int) 

                    def check_required(self):

                        if self.threshold is None:
                            print("Requiered variable Root.Geometry.Value.Surface_selection.Value.threshold does not have value")
                        return

                    def as_dict(self):
                        return drop_none({"threshold": self._threshold,"id_offset": self._id_offset,})



            class Curve_selection(object):
                '''Selection of curves
                \nRequired: []
                \nOptional: []'''
                def __init__(
                    self,

                ):
                    pass


                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({})


            class Point_selection(object):
                '''List of selection (ID assignment) operations to apply to the geometry; operations can be box, sphere, etc.
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
                        print("Requiered variable Root.Geometry.Value.Point_selection.items does not have value")
                    return

                def as_dict(self):
                    return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

                class Value(object):
                    '''Assigns ids to sides touching the bbox of the model using a threshold. Assigns 1+offset to left, 2+offset to bottom, 3+offset to right, 4+offset to top, 5+offset to front, 6+offset to back, 7+offset to everything else.
                    \nRequired: ['threshold']
                    \nOptional: ['id_offset']'''
                    def __init__(
                        self,
                        threshold: None = None,
                        id_offset: int = 0
                    ):
                        self._threshold = type_check(threshold, None) if threshold is not None else None
                        self._id_offset = type_check(id_offset, int) if id_offset is not None else None

                    @property
                    def threshold(self):
                        return self._threshold

                    @threshold.setter
                    def threshold(self, value):
                        ''' 
                        There is no definition
                        '''
                        self._threshold = type_check(value, None) 

                    @property
                    def id_offset(self):
                        return self._id_offset

                    @id_offset.setter
                    def id_offset(self, value):
                        ''' 
                        ID offset of box side selection.
                        '''
                        self._id_offset = type_check(value, int) 

                    def check_required(self):

                        if self.threshold is None:
                            print("Requiered variable Root.Geometry.Value.Point_selection.Value.threshold does not have value")
                        return

                    def as_dict(self):
                        return drop_none({"threshold": self._threshold,"id_offset": self._id_offset,})



            class Advanced(object):
                '''Advanced options for geometry
                \nRequired: []
                \nOptional: ['normalize_mesh', 'force_linear_geometry', 'refinement_location', 'min_component']'''
                def __init__(
                    self,
                    normalize_mesh: bool = False,
                    force_linear_geometry: bool = False,
                    refinement_location: float = 0.5,
                    min_component: int = -1
                ):
                    self._normalize_mesh = type_check(normalize_mesh, bool) if normalize_mesh is not None else None
                    self._force_linear_geometry = type_check(force_linear_geometry, bool) if force_linear_geometry is not None else None
                    self._refinement_location = type_check(refinement_location, float) if refinement_location is not None else None
                    self._min_component = type_check(min_component, int) if min_component is not None else None

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
                def force_linear_geometry(self):
                    return self._force_linear_geometry

                @force_linear_geometry.setter
                def force_linear_geometry(self, value):
                    ''' 
                    Discard high-order nodes for curved geometries
                    '''
                    self._force_linear_geometry = type_check(value, bool) 

                @property
                def refinement_location(self):
                    return self._refinement_location

                @refinement_location.setter
                def refinement_location(self, value):
                    ''' 
                    parametric location of the refinement
                    '''
                    self._refinement_location = type_check(value, float) 

                @property
                def min_component(self):
                    return self._min_component

                @min_component.setter
                def min_component(self, value):
                    ''' 
                    Size of the minimum component for collision
                    '''
                    self._min_component = type_check(value, int) 

                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({"normalize_mesh": self._normalize_mesh,"force_linear_geometry": self._force_linear_geometry,"refinement_location": self._refinement_location,"min_component": self._min_component,})



        class Mesh_array(object):
            '''Each geometry object stores a mesh, a set of transformations applied to it after loading, and a set of selections, which can be used to specify boundary conditions, materials, optimization parameters and other quantities that can be associated with a part of an object.
            \nRequired: ['mesh', 'array']
            \nOptional: ['type', 'extract', 'unit', 'transformation', 'volume_selection', 'surface_selection', 'curve_selection', 'point_selection', 'n_refs', 'advanced', 'enabled', 'is_obstacle']'''
            class Type(str, Enum):
                MESH = 'mesh'
                PLANE = 'plane'
                GROUND = 'ground'
                MESH_SEQUENCE = 'mesh_sequence'
                MESH_ARRAY = 'mesh_array'

            class Extract(str, Enum):
                VOLUME = 'volume'
                EDGES = 'edges'
                POINTS = 'points'
                SURFACE = 'surface'

            def __init__(
                self,
                mesh: str = None,
                array: Optional["Root.Geometry.Mesh_array.Array"] = None,
                type: "Type" = 'mesh',
                extract: "Extract" = 'volume',
                unit: str = '',
                transformation: Optional["Root.Geometry.Mesh_array.Transformation"] = None,
                volume_selection: Optional["Root.Geometry.Mesh_array.Volume_selection"] = None,
                surface_selection: Optional["Root.Geometry.Mesh_array.Surface_selection"] = None,
                curve_selection: Optional["Root.Geometry.Mesh_array.Curve_selection"] = None,
                point_selection: Optional["Root.Geometry.Mesh_array.Point_selection"] = None,
                n_refs: int = 0,
                advanced: Optional["Root.Geometry.Mesh_array.Advanced"] = None,
                enabled: bool = True,
                is_obstacle: bool = False
            ):
                self._mesh = extension_check(type_check(mesh, str), ['.obj', '.msh', '.stl', '.ply', '.mesh']) if mesh is not None else None
                self._array = type_check(array, self.Array) if array else self.Array()
                self._type = enum_check(type, self.Type)
                self._extract = enum_check(extract, self.Extract)
                self._unit = type_check(unit, str) if unit is not None else None
                self._transformation = type_check(transformation, self.Transformation) if transformation else self.Transformation()
                self._volume_selection = type_check(volume_selection, self.Volume_selection) if volume_selection else self.Volume_selection()
                self._surface_selection = type_check(surface_selection, self.Surface_selection) if surface_selection else self.Surface_selection()
                self._curve_selection = type_check(curve_selection, self.Curve_selection) if curve_selection else self.Curve_selection()
                self._point_selection = type_check(point_selection, self.Point_selection) if point_selection else self.Point_selection()
                self._n_refs = type_check(n_refs, int) if n_refs is not None else None
                self._advanced = type_check(advanced, self.Advanced) if advanced else self.Advanced()
                self._enabled = type_check(enabled, bool) if enabled is not None else None
                self._is_obstacle = type_check(is_obstacle, bool) if is_obstacle is not None else None

            @property
            def mesh(self):
                return self._mesh

            @mesh.setter
            def mesh(self, value):
                ''' 
                Path of the mesh file to load.
                '''
                self._mesh = extension_check(type_check(value, str), ['.obj', '.msh', '.stl', '.ply', '.mesh']) 

            @property
            def array(self):
                return self._array

            @array.setter
            def array(self, value):
                ''' 
                Array of meshes
                \nRequired: ['offset', 'size']
                \nOptional: ['relative']
                '''
                self._array = type_check(value, self.Array) 

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of geometry, currently only one supported. In future we will add stuff like planes, spheres, etc.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def extract(self):
                return self._extract

            @extract.setter
            def extract(self, value):
                ''' 
                Used to extract stuff from the mesh. Eg extract surface extracts the surface from a tet mesh.
                '''
                self._extract = enum_check(value, self.Extract) 

            @property
            def unit(self):
                return self._unit

            @unit.setter
            def unit(self, value):
                ''' 
                Units of the geometric model.
                '''
                self._unit = type_check(value, str) 

            @property
            def transformation(self):
                return self._transformation

            @transformation.setter
            def transformation(self, value):
                ''' 
                Geometric transformations applied to the geometry after loading it.
                \nRequired: []
                \nOptional: ['translation', 'rotation', 'rotation_mode', 'scale', 'dimensions']
                '''
                self._transformation = type_check(value, self.Transformation) 

            @property
            def volume_selection(self):
                return self._volume_selection

            @volume_selection.setter
            def volume_selection(self, value):
                ''' 
                This is a polymorphic variable, assign an object from its classes to the value
                \nRequired: []
                \nOptional: ['object1', 'list']
                '''
                self._volume_selection = type_check(value, self.Volume_selection) 

            @property
            def surface_selection(self):
                return self._surface_selection

            @surface_selection.setter
            def surface_selection(self, value):
                ''' 
                List of selection (ID assignment) operations to apply to the geometry; operations can be box, sphere, etc.
                \nRequired: []
                \nOptional: ['value']
                '''
                self._surface_selection = type_check(value, self.Surface_selection) 

            @property
            def curve_selection(self):
                return self._curve_selection

            @curve_selection.setter
            def curve_selection(self, value):
                ''' 
                Selection of curves
                \nRequired: []
                \nOptional: []
                '''
                self._curve_selection = type_check(value, self.Curve_selection) 

            @property
            def point_selection(self):
                return self._point_selection

            @point_selection.setter
            def point_selection(self, value):
                ''' 
                List of selection (ID assignment) operations to apply to the geometry; operations can be box, sphere, etc.
                \nRequired: []
                \nOptional: ['value']
                '''
                self._point_selection = type_check(value, self.Point_selection) 

            @property
            def n_refs(self):
                return self._n_refs

            @n_refs.setter
            def n_refs(self, value):
                ''' 
                number of uniform refinements
                '''
                self._n_refs = type_check(value, int) 

            @property
            def advanced(self):
                return self._advanced

            @advanced.setter
            def advanced(self, value):
                ''' 
                Advanced options for geometry
                \nRequired: []
                \nOptional: ['normalize_mesh', 'force_linear_geometry', 'refinement_location', 'min_component']
                '''
                self._advanced = type_check(value, self.Advanced) 

            @property
            def enabled(self):
                return self._enabled

            @enabled.setter
            def enabled(self, value):
                ''' 
                Skips the geometry if false
                '''
                self._enabled = type_check(value, bool) 

            @property
            def is_obstacle(self):
                return self._is_obstacle

            @is_obstacle.setter
            def is_obstacle(self, value):
                ''' 
                The geometry elements are not included in deforming geometry, only in collision computations
                '''
                self._is_obstacle = type_check(value, bool) 

            def check_required(self):

                if self.mesh is None:
                    print("Requiered variable Root.Geometry.Mesh_array.mesh does not have value")
                self.array.check_required()
                return

            def as_dict(self):
                return drop_none({"mesh": self._mesh,"array": self._array.as_dict(),"type": self._type.value if self._type is not None else None,"extract": self._extract.value if self._extract is not None else None,"unit": self._unit,"transformation": self._transformation.as_dict(),"volume_selection": self._volume_selection.as_dict(),"surface_selection": self._surface_selection.as_dict(),"curve_selection": self._curve_selection.as_dict(),"point_selection": self._point_selection.as_dict(),"n_refs": self._n_refs,"advanced": self._advanced.as_dict(),"enabled": self._enabled,"is_obstacle": self._is_obstacle,})

            class Array(object):
                '''Array of meshes
                \nRequired: ['offset', 'size']
                \nOptional: ['relative']'''
                def __init__(
                    self,
                    offset: float = None,
                    size: Optional[Iterable[int]] = None,
                    relative: bool = False
                ):
                    self._offset = type_check(offset, float) if offset is not None else None
                    self._size = [] if size is None else [type_check(i, int) for i in size]
                    self._relative = type_check(relative, bool) if relative is not None else None

                @property
                def offset(self):
                    return self._offset

                @offset.setter
                def offset(self, value):
                    ''' 
                    Offset of the mesh in the array.
                    '''
                    self._offset = type_check(value, float) 

                @property
                def size(self):
                    return self._size

                @size.setter
                def size(self, value):
                    ''' 
                    Size of the array (two entries for 2D problems or three entries for 3D problems).
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._size = [type_check(i, int) for i in (type_check(value, list) if value else [])]

                def size_add(self, value):
                    '''Add to list '''
                    self._size.append(type_check(value, int))

                def size_clear(self):
                    '''Clear list (make empty)'''
                    self._size.clear()

                def size_pop(self, index=-1):
                    '''Remove by index from list'''
                    return self._size.pop(index)

                def size_remove(self, item):
                    '''Safe remove specific item from list'''
                    if item in self._list:
                        self._size.remove(item)


                @property
                def relative(self):
                    return self._relative

                @relative.setter
                def relative(self, value):
                    ''' 
                    Is the offset value relative to the mesh's dimensions.
                    '''
                    self._relative = type_check(value, bool) 

                def check_required(self):

                    if self.offset is None:
                        print("Requiered variable Root.Geometry.Mesh_array.Array.offset does not have value")

                    if self.size:
                        print("Requiered variable Root.Geometry.Mesh_array.Array.size does not have value")
                    return

                def as_dict(self):
                    return drop_none({"offset": self._offset,"size": self._size,"relative": self._relative,})


            class Transformation(object):
                '''Geometric transformations applied to the geometry after loading it.
                \nRequired: []
                \nOptional: ['translation', 'rotation', 'rotation_mode', 'scale', 'dimensions']'''
                def __init__(
                    self,
                    translation: Optional[Iterable[float]] = None,
                    rotation: Optional[Iterable[float]] = None,
                    rotation_mode: str = 'xyz',
                    scale: Optional[Iterable[float]] = None,
                    float: float = 1.0
                ):
                    self._translation = [] if translation is None else [type_check(i, float) for i in translation]
                    self._rotation = [] if rotation is None else [type_check(i, float) for i in rotation]
                    self._rotation_mode = type_check(rotation_mode, str) if rotation_mode is not None else None
                    self._scale = [] if scale is None else [type_check(i, float) for i in scale]
                    self._float = type_check(float, float) if float is not None else None

                @property
                def translation(self):
                    return self._translation

                @translation.setter
                def translation(self, value):
                    ''' 
                    Translate (two entries for 2D problems or three entries for 3D problems).
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._translation = [type_check(i, float) for i in (type_check(value, list) if value else [])]

                def translation_add(self, value):
                    '''Add to list '''
                    self._translation.append(type_check(value, float))

                def translation_clear(self):
                    '''Clear list (make empty)'''
                    self._translation.clear()

                def translation_pop(self, index=-1):
                    '''Remove by index from list'''
                    return self._translation.pop(index)

                def translation_remove(self, item):
                    '''Safe remove specific item from list'''
                    if item in self._list:
                        self._translation.remove(item)


                @property
                def rotation(self):
                    return self._rotation

                @rotation.setter
                def rotation(self, value):
                    ''' 
                    Rotate, in 2D, one number, the rotation angle, in 3D, three or four Euler angles, axis+angle, or a unit quaternion. Depends on rotation mode.
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._rotation = [type_check(i, float) for i in (type_check(value, list) if value else [])]

                def rotation_add(self, value):
                    '''Add to list '''
                    self._rotation.append(type_check(value, float))

                def rotation_clear(self):
                    '''Clear list (make empty)'''
                    self._rotation.clear()

                def rotation_pop(self, index=-1):
                    '''Remove by index from list'''
                    return self._rotation.pop(index)

                def rotation_remove(self, item):
                    '''Safe remove specific item from list'''
                    if item in self._list:
                        self._rotation.remove(item)


                @property
                def rotation_mode(self):
                    return self._rotation_mode

                @rotation_mode.setter
                def rotation_mode(self, value):
                    ''' 
                    Type of rotation, supported are any permutation of [xyz]+, axis_angle, quaternion, or rotation_vector.
                    '''
                    self._rotation_mode = type_check(value, str) 

                @property
                def scale(self):
                    return self._scale

                @scale.setter
                def scale(self, value):
                    ''' 
                    Scale by specified factors along axes (two entries for 2D problems or three entries for 3D problems).
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._scale = [type_check(i, float) for i in (type_check(value, list) if value else [])]

                def scale_add(self, value):
                    '''Add to list '''
                    self._scale.append(type_check(value, float))

                def scale_clear(self):
                    '''Clear list (make empty)'''
                    self._scale.clear()

                def scale_pop(self, index=-1):
                    '''Remove by index from list'''
                    return self._scale.pop(index)

                def scale_remove(self, item):
                    '''Safe remove specific item from list'''
                    if item in self._list:
                        self._scale.remove(item)


                @property
                def float(self):
                    return self._float

                @float.setter
                def float(self, value):
                    ''' 
                    Scale the object so that bounding box dimensions match specified dimensions, 2 entries for 2D problems, 3 entries for 3D problems.
                    '''
                    self._float = type_check(value, float) 

                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({"translation": self._translation,"rotation": self._rotation,"rotation_mode": self._rotation_mode,"scale": self._scale,"float": self._float,})


            class Volume_selection(object):
                '''This is a polymorphic variable, assign an object from its classes to the value
                \nRequired: []
                \nOptional: ['object1', 'list']'''
                def __init__(
                    self,
                    value : object = None
                ):
                    self._value = class_check(value, [self.Object1, list]) if value is not None else None

                @property
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    ''' 
                    This is a polymorphic variable, assign an object from its classes to the value
                    '''
                    self._value = class_check(value, [self.Object1, list]) 

                def check_required(self):

                    if self.value is None:
                        print("Requiered variable Root.Geometry.Mesh_array.Volume_selection.value does not have value")
                    else:
                        if type(self.value) not in [['int', 'float', 'list', 'str', 'bool']]:
                            self.value.check_required()
                    return

                def as_dict(self):
                    return drop_none(self._value.as_dict() if isinstance(self._value, tuple([self.Object1])) else self._value)

                class Object1(object):
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



            class Surface_selection(object):
                '''List of selection (ID assignment) operations to apply to the geometry; operations can be box, sphere, etc.
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
                        print("Requiered variable Root.Geometry.Mesh_array.Surface_selection.items does not have value")
                    return

                def as_dict(self):
                    return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

                class Value(object):
                    '''Assigns ids to sides touching the bbox of the model using a threshold. Assigns 1+offset to left, 2+offset to bottom, 3+offset to right, 4+offset to top, 5+offset to front, 6+offset to back, 7+offset to everything else.
                    \nRequired: ['threshold']
                    \nOptional: ['id_offset']'''
                    def __init__(
                        self,
                        threshold: None = None,
                        id_offset: int = 0
                    ):
                        self._threshold = type_check(threshold, None) if threshold is not None else None
                        self._id_offset = type_check(id_offset, int) if id_offset is not None else None

                    @property
                    def threshold(self):
                        return self._threshold

                    @threshold.setter
                    def threshold(self, value):
                        ''' 
                        There is no definition
                        '''
                        self._threshold = type_check(value, None) 

                    @property
                    def id_offset(self):
                        return self._id_offset

                    @id_offset.setter
                    def id_offset(self, value):
                        ''' 
                        ID offset of box side selection.
                        '''
                        self._id_offset = type_check(value, int) 

                    def check_required(self):

                        if self.threshold is None:
                            print("Requiered variable Root.Geometry.Mesh_array.Surface_selection.Value.threshold does not have value")
                        return

                    def as_dict(self):
                        return drop_none({"threshold": self._threshold,"id_offset": self._id_offset,})



            class Curve_selection(object):
                '''Selection of curves
                \nRequired: []
                \nOptional: []'''
                def __init__(
                    self,

                ):
                    pass


                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({})


            class Point_selection(object):
                '''List of selection (ID assignment) operations to apply to the geometry; operations can be box, sphere, etc.
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
                        print("Requiered variable Root.Geometry.Mesh_array.Point_selection.items does not have value")
                    return

                def as_dict(self):
                    return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

                class Value(object):
                    '''Assigns ids to sides touching the bbox of the model using a threshold. Assigns 1+offset to left, 2+offset to bottom, 3+offset to right, 4+offset to top, 5+offset to front, 6+offset to back, 7+offset to everything else.
                    \nRequired: ['threshold']
                    \nOptional: ['id_offset']'''
                    def __init__(
                        self,
                        threshold: None = None,
                        id_offset: int = 0
                    ):
                        self._threshold = type_check(threshold, None) if threshold is not None else None
                        self._id_offset = type_check(id_offset, int) if id_offset is not None else None

                    @property
                    def threshold(self):
                        return self._threshold

                    @threshold.setter
                    def threshold(self, value):
                        ''' 
                        There is no definition
                        '''
                        self._threshold = type_check(value, None) 

                    @property
                    def id_offset(self):
                        return self._id_offset

                    @id_offset.setter
                    def id_offset(self, value):
                        ''' 
                        ID offset of box side selection.
                        '''
                        self._id_offset = type_check(value, int) 

                    def check_required(self):

                        if self.threshold is None:
                            print("Requiered variable Root.Geometry.Mesh_array.Point_selection.Value.threshold does not have value")
                        return

                    def as_dict(self):
                        return drop_none({"threshold": self._threshold,"id_offset": self._id_offset,})



            class Advanced(object):
                '''Advanced options for geometry
                \nRequired: []
                \nOptional: ['normalize_mesh', 'force_linear_geometry', 'refinement_location', 'min_component']'''
                def __init__(
                    self,
                    normalize_mesh: bool = False,
                    force_linear_geometry: bool = False,
                    refinement_location: float = 0.5,
                    min_component: int = -1
                ):
                    self._normalize_mesh = type_check(normalize_mesh, bool) if normalize_mesh is not None else None
                    self._force_linear_geometry = type_check(force_linear_geometry, bool) if force_linear_geometry is not None else None
                    self._refinement_location = type_check(refinement_location, float) if refinement_location is not None else None
                    self._min_component = type_check(min_component, int) if min_component is not None else None

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
                def force_linear_geometry(self):
                    return self._force_linear_geometry

                @force_linear_geometry.setter
                def force_linear_geometry(self, value):
                    ''' 
                    Discard high-order nodes for curved geometries
                    '''
                    self._force_linear_geometry = type_check(value, bool) 

                @property
                def refinement_location(self):
                    return self._refinement_location

                @refinement_location.setter
                def refinement_location(self, value):
                    ''' 
                    parametric location of the refinement
                    '''
                    self._refinement_location = type_check(value, float) 

                @property
                def min_component(self):
                    return self._min_component

                @min_component.setter
                def min_component(self, value):
                    ''' 
                    Size of the minimum component for collision
                    '''
                    self._min_component = type_check(value, int) 

                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({"normalize_mesh": self._normalize_mesh,"force_linear_geometry": self._force_linear_geometry,"refinement_location": self._refinement_location,"min_component": self._min_component,})



        class Plane(object):
            '''Plane geometry object defined by its origin and normal.
            \nRequired: ['point', 'normal']
            \nOptional: ['type', 'enabled', 'is_obstacle']'''
            class Type(str, Enum):
                MESH = 'mesh'
                PLANE = 'plane'
                GROUND = 'ground'
                MESH_SEQUENCE = 'mesh_sequence'
                MESH_ARRAY = 'mesh_array'

            def __init__(
                self,
                point: Optional[Iterable[float]] = None,
                normal: Optional[Iterable[float]] = None,
                type: "Type" = 'mesh',
                enabled: bool = True,
                is_obstacle: bool = False
            ):
                self._point = [] if point is None else [type_check(i, float) for i in point]
                self._normal = [] if normal is None else [type_check(i, float) for i in normal]
                self._type = enum_check(type, self.Type)
                self._enabled = type_check(enabled, bool) if enabled is not None else None
                self._is_obstacle = type_check(is_obstacle, bool) if is_obstacle is not None else None

            @property
            def point(self):
                return self._point

            @point.setter
            def point(self, value):
                ''' 
                Point on plane (two entries for 2D problems or three entries for 3D problems).
                \nRequired: []
                \nOptional: ['value']
                '''
                self._point = [type_check(i, float) for i in (type_check(value, list) if value else [])]

            def point_add(self, value):
                '''Add to list '''
                self._point.append(type_check(value, float))

            def point_clear(self):
                '''Clear list (make empty)'''
                self._point.clear()

            def point_pop(self, index=-1):
                '''Remove by index from list'''
                return self._point.pop(index)

            def point_remove(self, item):
                '''Safe remove specific item from list'''
                if item in self._list:
                    self._point.remove(item)


            @property
            def normal(self):
                return self._normal

            @normal.setter
            def normal(self, value):
                ''' 
                Normal of plane (two entries for 2D problems or three entries for 3D problems).
                \nRequired: []
                \nOptional: ['value']
                '''
                self._normal = [type_check(i, float) for i in (type_check(value, list) if value else [])]

            def normal_add(self, value):
                '''Add to list '''
                self._normal.append(type_check(value, float))

            def normal_clear(self):
                '''Clear list (make empty)'''
                self._normal.clear()

            def normal_pop(self, index=-1):
                '''Remove by index from list'''
                return self._normal.pop(index)

            def normal_remove(self, item):
                '''Safe remove specific item from list'''
                if item in self._list:
                    self._normal.remove(item)


            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of geometry, currently only one supported. In future we will add stuff like planes, spheres, etc.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def enabled(self):
                return self._enabled

            @enabled.setter
            def enabled(self, value):
                ''' 
                Skips the geometry if false
                '''
                self._enabled = type_check(value, bool) 

            @property
            def is_obstacle(self):
                return self._is_obstacle

            @is_obstacle.setter
            def is_obstacle(self, value):
                ''' 
                The geometry elements are not included in deforming geometry, only in collision computations
                '''
                self._is_obstacle = type_check(value, bool) 

            def check_required(self):

                if self.point:
                    print("Requiered variable Root.Geometry.Plane.point does not have value")

                if self.normal:
                    print("Requiered variable Root.Geometry.Plane.normal does not have value")
                return

            def as_dict(self):
                return drop_none({"point": self._point,"normal": self._normal,"type": self._type.value if self._type is not None else None,"enabled": self._enabled,"is_obstacle": self._is_obstacle,})


        class Ground(object):
            '''Plane orthogonal to gravity defined by its height.
            \nRequired: ['height']
            \nOptional: ['type', 'enabled', 'is_obstacle']'''
            class Type(str, Enum):
                MESH = 'mesh'
                PLANE = 'plane'
                GROUND = 'ground'
                MESH_SEQUENCE = 'mesh_sequence'
                MESH_ARRAY = 'mesh_array'

            def __init__(
                self,
                height: float = None,
                type: "Type" = 'mesh',
                enabled: bool = True,
                is_obstacle: bool = False
            ):
                self._height = type_check(height, float) if height is not None else None
                self._type = enum_check(type, self.Type)
                self._enabled = type_check(enabled, bool) if enabled is not None else None
                self._is_obstacle = type_check(is_obstacle, bool) if is_obstacle is not None else None

            @property
            def height(self):
                return self._height

            @height.setter
            def height(self, value):
                ''' 
                Height of ground plane.
                '''
                self._height = type_check(value, float) 

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of geometry, currently only one supported. In future we will add stuff like planes, spheres, etc.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def enabled(self):
                return self._enabled

            @enabled.setter
            def enabled(self, value):
                ''' 
                Skips the geometry if false
                '''
                self._enabled = type_check(value, bool) 

            @property
            def is_obstacle(self):
                return self._is_obstacle

            @is_obstacle.setter
            def is_obstacle(self, value):
                ''' 
                The geometry elements are not included in deforming geometry, only in collision computations
                '''
                self._is_obstacle = type_check(value, bool) 

            def check_required(self):

                if self.height is None:
                    print("Requiered variable Root.Geometry.Ground.height does not have value")
                return

            def as_dict(self):
                return drop_none({"height": self._height,"type": self._type.value if self._type is not None else None,"enabled": self._enabled,"is_obstacle": self._is_obstacle,})


        class Mesh_sequence(object):
            '''Mesh sequence.
            \nRequired: ['mesh_sequence', 'fps']
            \nOptional: ['type', 'extract', 'unit', 'transformation', 'n_refs', 'advanced', 'enabled', 'is_obstacle']'''
            class Type(str, Enum):
                MESH = 'mesh'
                PLANE = 'plane'
                GROUND = 'ground'
                MESH_SEQUENCE = 'mesh_sequence'
                MESH_ARRAY = 'mesh_array'

            class Extract(str, Enum):
                VOLUME = 'volume'
                EDGES = 'edges'
                POINTS = 'points'
                SURFACE = 'surface'

            def __init__(
                self,
                mesh_sequence: Optional["Root.Geometry.Mesh_sequence.Mesh_sequence"] = None,
                fps: int = None,
                type: "Type" = 'mesh',
                extract: "Extract" = 'volume',
                unit: str = '',
                transformation: Optional["Root.Geometry.Mesh_sequence.Transformation"] = None,
                n_refs: int = 0,
                advanced: Optional["Root.Geometry.Mesh_sequence.Advanced"] = None,
                enabled: bool = True,
                is_obstacle: bool = False
            ):
                self._mesh_sequence = type_check(mesh_sequence, self.Mesh_sequence) if mesh_sequence else self.Mesh_sequence()
                self._fps = type_check(fps, int) if fps is not None else None
                self._type = enum_check(type, self.Type)
                self._extract = enum_check(extract, self.Extract)
                self._unit = type_check(unit, str) if unit is not None else None
                self._transformation = type_check(transformation, self.Transformation) if transformation else self.Transformation()
                self._n_refs = type_check(n_refs, int) if n_refs is not None else None
                self._advanced = type_check(advanced, self.Advanced) if advanced else self.Advanced()
                self._enabled = type_check(enabled, bool) if enabled is not None else None
                self._is_obstacle = type_check(is_obstacle, bool) if is_obstacle is not None else None

            @property
            def mesh_sequence(self):
                return self._mesh_sequence

            @mesh_sequence.setter
            def mesh_sequence(self, value):
                ''' 
                This is a polymorphic variable, assign an object from its classes to the value
                \nRequired: []
                \nOptional: ['string', 'list', 'file']
                '''
                self._mesh_sequence = type_check(value, self.Mesh_sequence) 

            @property
            def fps(self):
                return self._fps

            @fps.setter
            def fps(self, value):
                ''' 
                Frames of the mesh sequence per second.
                '''
                self._fps = type_check(value, int) 

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of geometry, currently only one supported. In future we will add stuff like planes, spheres, etc.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def extract(self):
                return self._extract

            @extract.setter
            def extract(self, value):
                ''' 
                Used to extract stuff from the mesh. Eg extract surface extracts the surface from a tet mesh.
                '''
                self._extract = enum_check(value, self.Extract) 

            @property
            def unit(self):
                return self._unit

            @unit.setter
            def unit(self, value):
                ''' 
                Units of the geometric model.
                '''
                self._unit = type_check(value, str) 

            @property
            def transformation(self):
                return self._transformation

            @transformation.setter
            def transformation(self, value):
                ''' 
                Geometric transformations applied to the geometry after loading it.
                \nRequired: []
                \nOptional: ['translation', 'rotation', 'rotation_mode', 'scale', 'dimensions']
                '''
                self._transformation = type_check(value, self.Transformation) 

            @property
            def n_refs(self):
                return self._n_refs

            @n_refs.setter
            def n_refs(self, value):
                ''' 
                number of uniform refinements
                '''
                self._n_refs = type_check(value, int) 

            @property
            def advanced(self):
                return self._advanced

            @advanced.setter
            def advanced(self, value):
                ''' 
                Advanced options for geometry
                \nRequired: []
                \nOptional: ['normalize_mesh', 'force_linear_geometry', 'refinement_location', 'min_component']
                '''
                self._advanced = type_check(value, self.Advanced) 

            @property
            def enabled(self):
                return self._enabled

            @enabled.setter
            def enabled(self, value):
                ''' 
                Skips the geometry if false
                '''
                self._enabled = type_check(value, bool) 

            @property
            def is_obstacle(self):
                return self._is_obstacle

            @is_obstacle.setter
            def is_obstacle(self, value):
                ''' 
                The geometry elements are not included in deforming geometry, only in collision computations
                '''
                self._is_obstacle = type_check(value, bool) 

            def check_required(self):
                self.mesh_sequence.check_required()

                if self.fps is None:
                    print("Requiered variable Root.Geometry.Mesh_sequence.fps does not have value")
                return

            def as_dict(self):
                return drop_none({"mesh_sequence": self._mesh_sequence.as_dict(),"fps": self._fps,"type": self._type.value if self._type is not None else None,"extract": self._extract.value if self._extract is not None else None,"unit": self._unit,"transformation": self._transformation.as_dict(),"n_refs": self._n_refs,"advanced": self._advanced.as_dict(),"enabled": self._enabled,"is_obstacle": self._is_obstacle,})

            class Mesh_sequence(object):
                '''This is a polymorphic variable, assign an object from its classes to the value
                \nRequired: []
                \nOptional: ['string', 'list', 'file']'''
                def __init__(
                    self,
                    value : object = None
                ):
                    self._value = class_check(value, [string, list, file]) if value is not None else None

                @property
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    ''' 
                    This is a polymorphic variable, assign an object from its classes to the value
                    '''
                    self._value = class_check(value, [string, list, file]) 

                def check_required(self):

                    if self.value is None:
                        print("Requiered variable Root.Geometry.Mesh_sequence.Mesh_sequence.value does not have value")
                    else:
                        if type(self.value) not in [['int', 'float', 'list', 'str', 'bool']]:
                            self.value.check_required()
                    return

                def as_dict(self):
                    return drop_none(self._value.as_dict() if isinstance(self._value, tuple([])) else self._value)


            class Transformation(object):
                '''Geometric transformations applied to the geometry after loading it.
                \nRequired: []
                \nOptional: ['translation', 'rotation', 'rotation_mode', 'scale', 'dimensions']'''
                def __init__(
                    self,
                    translation: Optional[Iterable[float]] = None,
                    rotation: Optional[Iterable[float]] = None,
                    rotation_mode: str = 'xyz',
                    scale: Optional[Iterable[float]] = None,
                    float: float = 1.0
                ):
                    self._translation = [] if translation is None else [type_check(i, float) for i in translation]
                    self._rotation = [] if rotation is None else [type_check(i, float) for i in rotation]
                    self._rotation_mode = type_check(rotation_mode, str) if rotation_mode is not None else None
                    self._scale = [] if scale is None else [type_check(i, float) for i in scale]
                    self._float = type_check(float, float) if float is not None else None

                @property
                def translation(self):
                    return self._translation

                @translation.setter
                def translation(self, value):
                    ''' 
                    Translate (two entries for 2D problems or three entries for 3D problems).
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._translation = [type_check(i, float) for i in (type_check(value, list) if value else [])]

                def translation_add(self, value):
                    '''Add to list '''
                    self._translation.append(type_check(value, float))

                def translation_clear(self):
                    '''Clear list (make empty)'''
                    self._translation.clear()

                def translation_pop(self, index=-1):
                    '''Remove by index from list'''
                    return self._translation.pop(index)

                def translation_remove(self, item):
                    '''Safe remove specific item from list'''
                    if item in self._list:
                        self._translation.remove(item)


                @property
                def rotation(self):
                    return self._rotation

                @rotation.setter
                def rotation(self, value):
                    ''' 
                    Rotate, in 2D, one number, the rotation angle, in 3D, three or four Euler angles, axis+angle, or a unit quaternion. Depends on rotation mode.
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._rotation = [type_check(i, float) for i in (type_check(value, list) if value else [])]

                def rotation_add(self, value):
                    '''Add to list '''
                    self._rotation.append(type_check(value, float))

                def rotation_clear(self):
                    '''Clear list (make empty)'''
                    self._rotation.clear()

                def rotation_pop(self, index=-1):
                    '''Remove by index from list'''
                    return self._rotation.pop(index)

                def rotation_remove(self, item):
                    '''Safe remove specific item from list'''
                    if item in self._list:
                        self._rotation.remove(item)


                @property
                def rotation_mode(self):
                    return self._rotation_mode

                @rotation_mode.setter
                def rotation_mode(self, value):
                    ''' 
                    Type of rotation, supported are any permutation of [xyz]+, axis_angle, quaternion, or rotation_vector.
                    '''
                    self._rotation_mode = type_check(value, str) 

                @property
                def scale(self):
                    return self._scale

                @scale.setter
                def scale(self, value):
                    ''' 
                    Scale by specified factors along axes (two entries for 2D problems or three entries for 3D problems).
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._scale = [type_check(i, float) for i in (type_check(value, list) if value else [])]

                def scale_add(self, value):
                    '''Add to list '''
                    self._scale.append(type_check(value, float))

                def scale_clear(self):
                    '''Clear list (make empty)'''
                    self._scale.clear()

                def scale_pop(self, index=-1):
                    '''Remove by index from list'''
                    return self._scale.pop(index)

                def scale_remove(self, item):
                    '''Safe remove specific item from list'''
                    if item in self._list:
                        self._scale.remove(item)


                @property
                def float(self):
                    return self._float

                @float.setter
                def float(self, value):
                    ''' 
                    Scale the object so that bounding box dimensions match specified dimensions, 2 entries for 2D problems, 3 entries for 3D problems.
                    '''
                    self._float = type_check(value, float) 

                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({"translation": self._translation,"rotation": self._rotation,"rotation_mode": self._rotation_mode,"scale": self._scale,"float": self._float,})


            class Advanced(object):
                '''Advanced options for geometry
                \nRequired: []
                \nOptional: ['normalize_mesh', 'force_linear_geometry', 'refinement_location', 'min_component']'''
                def __init__(
                    self,
                    normalize_mesh: bool = False,
                    force_linear_geometry: bool = False,
                    refinement_location: float = 0.5,
                    min_component: int = -1
                ):
                    self._normalize_mesh = type_check(normalize_mesh, bool) if normalize_mesh is not None else None
                    self._force_linear_geometry = type_check(force_linear_geometry, bool) if force_linear_geometry is not None else None
                    self._refinement_location = type_check(refinement_location, float) if refinement_location is not None else None
                    self._min_component = type_check(min_component, int) if min_component is not None else None

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
                def force_linear_geometry(self):
                    return self._force_linear_geometry

                @force_linear_geometry.setter
                def force_linear_geometry(self, value):
                    ''' 
                    Discard high-order nodes for curved geometries
                    '''
                    self._force_linear_geometry = type_check(value, bool) 

                @property
                def refinement_location(self):
                    return self._refinement_location

                @refinement_location.setter
                def refinement_location(self, value):
                    ''' 
                    parametric location of the refinement
                    '''
                    self._refinement_location = type_check(value, float) 

                @property
                def min_component(self):
                    return self._min_component

                @min_component.setter
                def min_component(self, value):
                    ''' 
                    Size of the minimum component for collision
                    '''
                    self._min_component = type_check(value, int) 

                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({"normalize_mesh": self._normalize_mesh,"force_linear_geometry": self._force_linear_geometry,"refinement_location": self._refinement_location,"min_component": self._min_component,})




    class Materials(object):
        '''Material Parameters lists including ID pointing to volume selection, Young's modulus ($E$), Poisson's ratio ($\\nu$), Density ($\\rho$), or Lamé constants ($\\lambda$ and $\\mu$).
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
                print("Requiered variable Root.Materials.items does not have value")
            return

        def as_dict(self):
            return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

        class Value(object):
            '''There is no definition
            \nRequired: []
            \nOptional: ['models']'''
            def __init__(
                self,
                models: Optional["Root.Materials.Value.Models"] = None
            ):
                self._models = type_check(models, self.Models) if models else self.Models()

            @property
            def models(self):
                return self._models

            @models.setter
            def models(self, value):
                ''' 
                List of models
                \nRequired: []
                \nOptional: ['value']
                '''
                self._models = type_check(value, self.Models) 

            def check_required(self):

                return

            def as_dict(self):
                return drop_none({"models": self._models.as_dict(),})

            class Models(object):
                '''List of models
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
                        print("Requiered variable Root.Materials.Value.Models.items does not have value")
                    return

                def as_dict(self):
                    return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

                class Value(object):
                    '''There is no definition
                    \nRequired: []
                    \nOptional: []'''
                    def __init__(
                        self,

                    ):
                        pass


                    def check_required(self):

                        return

                    def as_dict(self):
                        return drop_none({})





    class Units(object):
        '''Basic units used in the code.
        \nRequired: []
        \nOptional: ['length', 'mass', 'time', 'characteristic_length']'''
        def __init__(
            self,
            length: str = 'm',
            mass: str = 'kg',
            time: str = 's',
            characteristic_length: float = 1.0
        ):
            self._length = type_check(length, str) if length is not None else None
            self._mass = type_check(mass, str) if mass is not None else None
            self._time = type_check(time, str) if time is not None else None
            self._characteristic_length = type_check(characteristic_length, float) if characteristic_length is not None else None

        @property
        def length(self):
            return self._length

        @length.setter
        def length(self, value):
            ''' 
            Length unit.
            '''
            self._length = type_check(value, str) 

        @property
        def mass(self):
            return self._mass

        @mass.setter
        def mass(self, value):
            ''' 
            Mass unit.
            '''
            self._mass = type_check(value, str) 

        @property
        def time(self):
            return self._time

        @time.setter
        def time(self, value):
            ''' 
            Time unit.
            '''
            self._time = type_check(value, str) 

        @property
        def characteristic_length(self):
            return self._characteristic_length

        @characteristic_length.setter
        def characteristic_length(self, value):
            ''' 
            Characteristic length, used for tolerances.
            '''
            self._characteristic_length = type_check(value, float) 

        def check_required(self):

            return

        def as_dict(self):
            return drop_none({"length": self._length,"mass": self._mass,"time": self._time,"characteristic_length": self._characteristic_length,})


    class Preset_problem(object):
        '''This is a polymorphic variable, assign an object from its classes to the value
        \nRequired: []
        \nOptional: ['object1', 'object2', 'object3', 'object4', 'object5', 'object6', 'object7', 'object8', 'object9', 'object10', 'object11', 'object12', 'object13', 'object14', 'object15', 'object16', 'object17', 'object18', 'object19', 'object20', 'object21', 'object22', 'object23', 'object24', 'object25', 'object26', 'object27', 'object28', 'object29', 'object30', 'object31', 'object32', 'object33', 'object34', 'object35', 'object36', 'object37', 'object38', 'object39', 'object40', 'object41', 'object42', 'object43']'''
        def __init__(
            self,
            value : object = None
        ):
            self._value = class_check(value, [self.Object1, self.Object2, self.Object3, self.Object4, self.Object5, self.Object6, self.Object7, self.Object8, self.Object9, self.Object10, self.Object11, self.Object12, self.Object13, self.Object14, self.Object15, self.Object16, self.Object17, self.Object18, self.Object19, self.Object20, self.Object21, self.Object22, self.Object23, self.Object24, self.Object25, self.Object26, self.Object27, self.Object28, self.Object29, self.Object30, self.Object31, self.Object32, self.Object33, self.Object34, self.Object35, self.Object36, self.Object37, self.Object38, self.Object39, self.Object40, self.Object41, self.Object42, self.Object43]) if value is not None else None

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, value):
            ''' 
            This is a polymorphic variable, assign an object from its classes to the value
            '''
            self._value = class_check(value, [self.Object1, self.Object2, self.Object3, self.Object4, self.Object5, self.Object6, self.Object7, self.Object8, self.Object9, self.Object10, self.Object11, self.Object12, self.Object13, self.Object14, self.Object15, self.Object16, self.Object17, self.Object18, self.Object19, self.Object20, self.Object21, self.Object22, self.Object23, self.Object24, self.Object25, self.Object26, self.Object27, self.Object28, self.Object29, self.Object30, self.Object31, self.Object32, self.Object33, self.Object34, self.Object35, self.Object36, self.Object37, self.Object38, self.Object39, self.Object40, self.Object41, self.Object42, self.Object43]) 

        def check_required(self):

            if self.value is None:
                print("Requiered variable Root.Preset_problem.value does not have value")
            else:
                if type(self.value) not in [['int', 'float', 'list', 'str', 'bool']]:
                    self.value.check_required()
            return

        def as_dict(self):
            return drop_none(self._value.as_dict() if isinstance(self._value, tuple([self.Object1, self.Object2, self.Object3, self.Object4, self.Object5, self.Object6, self.Object7, self.Object8, self.Object9, self.Object10, self.Object11, self.Object12, self.Object13, self.Object14, self.Object15, self.Object16, self.Object17, self.Object18, self.Object19, self.Object20, self.Object21, self.Object22, self.Object23, self.Object24, self.Object25, self.Object26, self.Object27, self.Object28, self.Object29, self.Object30, self.Object31, self.Object32, self.Object33, self.Object34, self.Object35, self.Object36, self.Object37, self.Object38, self.Object39, self.Object40, self.Object41, self.Object42, self.Object43])) else self._value)

        class Object1(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object1.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object2(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object2.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object3(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object3.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object4(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object4.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object5(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object5.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object6(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object6.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object7(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: ['func']'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None,
                func: int = 0
            ):
                self._type = enum_check(type, self.Type)
                self._func = type_check(func, int) if func is not None else None

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def func(self):
                return self._func

            @func.setter
            def func(self, value):
                ''' 
                TODO
                '''
                self._func = type_check(value, int) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object7.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,"func": self._func,})


        class Object8(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object8.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object9(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object9.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object10(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object10.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object11(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: ['axis_coordiante', 'n_turns', 'fixed_boundary', 'turning_boundary', 'bbox_center']'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None,
                axis_coordiante: int = 2,
                n_turns: float = 0.5,
                fixed_boundary: int = 5,
                turning_boundary: int = 6,
                bbox_center: Optional[Iterable[float]] = None
            ):
                self._type = enum_check(type, self.Type)
                self._axis_coordiante = type_check(axis_coordiante, int) if axis_coordiante is not None else None
                self._n_turns = type_check(n_turns, float) if n_turns is not None else None
                self._fixed_boundary = type_check(fixed_boundary, int) if fixed_boundary is not None else None
                self._turning_boundary = type_check(turning_boundary, int) if turning_boundary is not None else None
                self._bbox_center = [] if bbox_center is None else [type_check(i, float) for i in bbox_center]

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def axis_coordiante(self):
                return self._axis_coordiante

            @axis_coordiante.setter
            def axis_coordiante(self, value):
                ''' 
                TODO
                '''
                self._axis_coordiante = type_check(value, int) 

            @property
            def n_turns(self):
                return self._n_turns

            @n_turns.setter
            def n_turns(self, value):
                ''' 
                TODO
                '''
                self._n_turns = type_check(value, float) 

            @property
            def fixed_boundary(self):
                return self._fixed_boundary

            @fixed_boundary.setter
            def fixed_boundary(self, value):
                ''' 
                TODO
                '''
                self._fixed_boundary = type_check(value, int) 

            @property
            def turning_boundary(self):
                return self._turning_boundary

            @turning_boundary.setter
            def turning_boundary(self, value):
                ''' 
                TODO
                '''
                self._turning_boundary = type_check(value, int) 

            @property
            def bbox_center(self):
                return self._bbox_center

            @bbox_center.setter
            def bbox_center(self, value):
                ''' 
                TODO
                \nRequired: []
                \nOptional: ['value']
                '''
                self._bbox_center = [type_check(i, float) for i in (type_check(value, list) if value else [])]

            def bbox_center_add(self, value):
                '''Add to list '''
                self._bbox_center.append(type_check(value, float))

            def bbox_center_clear(self):
                '''Clear list (make empty)'''
                self._bbox_center.clear()

            def bbox_center_pop(self, index=-1):
                '''Remove by index from list'''
                return self._bbox_center.pop(index)

            def bbox_center_remove(self, item):
                '''Safe remove specific item from list'''
                if item in self._list:
                    self._bbox_center.remove(item)


            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object11.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,"axis_coordiante": self._axis_coordiante,"n_turns": self._n_turns,"fixed_boundary": self._fixed_boundary,"turning_boundary": self._turning_boundary,"bbox_center": self._bbox_center,})


        class Object12(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: ['axis_coordiante0', 'axis_coordiante1', 'angular_v0', 'angular_v1', 'turning_boundary0', 'turning_boundary1', 'bbox_center']'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None,
                axis_coordiante0: int = 2,
                axis_coordiante1: int = 2,
                angular_v0: float = 0.5,
                angular_v1: float = -0.5,
                turning_boundary0: int = 5,
                turning_boundary1: int = 6,
                bbox_center: Optional[Iterable[float]] = None
            ):
                self._type = enum_check(type, self.Type)
                self._axis_coordiante0 = type_check(axis_coordiante0, int) if axis_coordiante0 is not None else None
                self._axis_coordiante1 = type_check(axis_coordiante1, int) if axis_coordiante1 is not None else None
                self._angular_v0 = type_check(angular_v0, float) if angular_v0 is not None else None
                self._angular_v1 = type_check(angular_v1, float) if angular_v1 is not None else None
                self._turning_boundary0 = type_check(turning_boundary0, int) if turning_boundary0 is not None else None
                self._turning_boundary1 = type_check(turning_boundary1, int) if turning_boundary1 is not None else None
                self._bbox_center = [] if bbox_center is None else [type_check(i, float) for i in bbox_center]

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def axis_coordiante0(self):
                return self._axis_coordiante0

            @axis_coordiante0.setter
            def axis_coordiante0(self, value):
                ''' 
                TODO
                '''
                self._axis_coordiante0 = type_check(value, int) 

            @property
            def axis_coordiante1(self):
                return self._axis_coordiante1

            @axis_coordiante1.setter
            def axis_coordiante1(self, value):
                ''' 
                TODO
                '''
                self._axis_coordiante1 = type_check(value, int) 

            @property
            def angular_v0(self):
                return self._angular_v0

            @angular_v0.setter
            def angular_v0(self, value):
                ''' 
                TODO
                '''
                self._angular_v0 = type_check(value, float) 

            @property
            def angular_v1(self):
                return self._angular_v1

            @angular_v1.setter
            def angular_v1(self, value):
                ''' 
                TODO
                '''
                self._angular_v1 = type_check(value, float) 

            @property
            def turning_boundary0(self):
                return self._turning_boundary0

            @turning_boundary0.setter
            def turning_boundary0(self, value):
                ''' 
                TODO
                '''
                self._turning_boundary0 = type_check(value, int) 

            @property
            def turning_boundary1(self):
                return self._turning_boundary1

            @turning_boundary1.setter
            def turning_boundary1(self, value):
                ''' 
                TODO
                '''
                self._turning_boundary1 = type_check(value, int) 

            @property
            def bbox_center(self):
                return self._bbox_center

            @bbox_center.setter
            def bbox_center(self, value):
                ''' 
                TODO
                \nRequired: []
                \nOptional: ['value']
                '''
                self._bbox_center = [type_check(i, float) for i in (type_check(value, list) if value else [])]

            def bbox_center_add(self, value):
                '''Add to list '''
                self._bbox_center.append(type_check(value, float))

            def bbox_center_clear(self):
                '''Clear list (make empty)'''
                self._bbox_center.clear()

            def bbox_center_pop(self, index=-1):
                '''Remove by index from list'''
                return self._bbox_center.pop(index)

            def bbox_center_remove(self, item):
                '''Safe remove specific item from list'''
                if item in self._list:
                    self._bbox_center.remove(item)


            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object12.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,"axis_coordiante0": self._axis_coordiante0,"axis_coordiante1": self._axis_coordiante1,"angular_v0": self._angular_v0,"angular_v1": self._angular_v1,"turning_boundary0": self._turning_boundary0,"turning_boundary1": self._turning_boundary1,"bbox_center": self._bbox_center,})


        class Object13(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object13.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object14(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object14.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object15(object):
            '''TODO, add displacement, E, nu, formulation, mesh_size
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object15.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object16(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object16.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object17(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object17.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object18(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object18.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object19(object):
            '''TODO, add optionals
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object19.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object20(object):
            '''TODO, add optionals
            \nRequired: ['type']
            \nOptional: ['formulation', 'n_kernels', 'kernel_distance', 'kernel_weights']'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None,
                formulation: str = '',
                n_kernels: int = 0,
                kernel_distance: float = 0.0,
                kernel_weights: str = ''
            ):
                self._type = enum_check(type, self.Type)
                self._formulation = type_check(formulation, str) if formulation is not None else None
                self._n_kernels = type_check(n_kernels, int) if n_kernels is not None else None
                self._kernel_distance = type_check(kernel_distance, float) if kernel_distance is not None else None
                self._kernel_weights = type_check(kernel_weights, str) if kernel_weights is not None else None

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def formulation(self):
                return self._formulation

            @formulation.setter
            def formulation(self, value):
                ''' 
                TODO
                '''
                self._formulation = type_check(value, str) 

            @property
            def n_kernels(self):
                return self._n_kernels

            @n_kernels.setter
            def n_kernels(self, value):
                ''' 
                TODO
                '''
                self._n_kernels = type_check(value, int) 

            @property
            def kernel_distance(self):
                return self._kernel_distance

            @kernel_distance.setter
            def kernel_distance(self, value):
                ''' 
                TODO
                '''
                self._kernel_distance = type_check(value, float) 

            @property
            def kernel_weights(self):
                return self._kernel_weights

            @kernel_weights.setter
            def kernel_weights(self, value):
                ''' 
                TODO
                '''
                self._kernel_weights = type_check(value, str) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object20.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,"formulation": self._formulation,"n_kernels": self._n_kernels,"kernel_distance": self._kernel_distance,"kernel_weights": self._kernel_weights,})


        class Object21(object):
            '''TODO, add optionals
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object21.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object22(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object22.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object23(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object23.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object24(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: ['force']'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None,
                force: Optional[Iterable[float]] = None
            ):
                self._type = enum_check(type, self.Type)
                self._force = [] if force is None else [type_check(i, float) for i in force]

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def force(self):
                return self._force

            @force.setter
            def force(self, value):
                ''' 
                TODO
                \nRequired: []
                \nOptional: ['value']
                '''
                self._force = [type_check(i, float) for i in (type_check(value, list) if value else [])]

            def force_add(self, value):
                '''Add to list '''
                self._force.append(type_check(value, float))

            def force_clear(self):
                '''Clear list (make empty)'''
                self._force.clear()

            def force_pop(self, index=-1):
                '''Remove by index from list'''
                return self._force.pop(index)

            def force_remove(self, item):
                '''Safe remove specific item from list'''
                if item in self._list:
                    self._force.remove(item)


            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object24.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,"force": self._force,})


        class Object25(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object25.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object26(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object26.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object27(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object27.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object28(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object28.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object29(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object29.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object30(object):
            '''TODO, add inflow, outflow, inflow_amout, outflow_amout, direction, obstacle
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object30.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object31(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: ['U']'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None,
                U: float = 0.0
            ):
                self._type = enum_check(type, self.Type)
                self._U = type_check(U, float) if U is not None else None

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def U(self):
                return self._U

            @U.setter
            def U(self, value):
                ''' 
                TODO
                '''
                self._U = type_check(value, float) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object31.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,"U": self._U,})


        class Object32(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: ['U', 'time_dependent']'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None,
                U: float = 0.0,
                time_dependent: bool = False
            ):
                self._type = enum_check(type, self.Type)
                self._U = type_check(U, float) if U is not None else None
                self._time_dependent = type_check(time_dependent, bool) if time_dependent is not None else None

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def U(self):
                return self._U

            @U.setter
            def U(self, value):
                ''' 
                TODO
                '''
                self._U = type_check(value, float) 

            @property
            def time_dependent(self):
                return self._time_dependent

            @time_dependent.setter
            def time_dependent(self, value):
                ''' 
                TODO
                '''
                self._time_dependent = type_check(value, bool) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object32.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,"U": self._U,"time_dependent": self._time_dependent,})


        class Object33(object):
            '''TODO, add inflow_id, direction, no_slip
            \nRequired: ['type']
            \nOptional: ['U']'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None,
                U: float = 0.0
            ):
                self._type = enum_check(type, self.Type)
                self._U = type_check(U, float) if U is not None else None

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def U(self):
                return self._U

            @U.setter
            def U(self, value):
                ''' 
                TODO
                '''
                self._U = type_check(value, float) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object33.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,"U": self._U,})


        class Object34(object):
            '''TODO, add radius
            \nRequired: ['type']
            \nOptional: ['time_dependent', 'viscosity']'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None,
                time_dependent: bool = False,
                viscosity: float = 0.0
            ):
                self._type = enum_check(type, self.Type)
                self._time_dependent = type_check(time_dependent, bool) if time_dependent is not None else None
                self._viscosity = type_check(viscosity, float) if viscosity is not None else None

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def time_dependent(self):
                return self._time_dependent

            @time_dependent.setter
            def time_dependent(self, value):
                ''' 
                TODO
                '''
                self._time_dependent = type_check(value, bool) 

            @property
            def viscosity(self):
                return self._viscosity

            @viscosity.setter
            def viscosity(self, value):
                ''' 
                TODO
                '''
                self._viscosity = type_check(value, float) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object34.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,"time_dependent": self._time_dependent,"viscosity": self._viscosity,})


        class Object35(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: ['viscosity']'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None,
                viscosity: float = 0.0
            ):
                self._type = enum_check(type, self.Type)
                self._viscosity = type_check(viscosity, float) if viscosity is not None else None

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def viscosity(self):
                return self._viscosity

            @viscosity.setter
            def viscosity(self, value):
                ''' 
                TODO
                '''
                self._viscosity = type_check(value, float) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object35.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,"viscosity": self._viscosity,})


        class Object36(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: ['func']'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None,
                func: int = 0
            ):
                self._type = enum_check(type, self.Type)
                self._func = type_check(func, int) if func is not None else None

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def func(self):
                return self._func

            @func.setter
            def func(self, value):
                ''' 
                TODO
                '''
                self._func = type_check(value, int) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object36.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,"func": self._func,})


        class Object37(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object37.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object38(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: ['func', 'viscosity']'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None,
                func: int = 0,
                viscosity: float = 0.0
            ):
                self._type = enum_check(type, self.Type)
                self._func = type_check(func, int) if func is not None else None
                self._viscosity = type_check(viscosity, float) if viscosity is not None else None

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def func(self):
                return self._func

            @func.setter
            def func(self, value):
                ''' 
                TODO
                '''
                self._func = type_check(value, int) 

            @property
            def viscosity(self):
                return self._viscosity

            @viscosity.setter
            def viscosity(self, value):
                ''' 
                TODO
                '''
                self._viscosity = type_check(value, float) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object38.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,"func": self._func,"viscosity": self._viscosity,})


        class Object39(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: ['viscosity']'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None,
                viscosity: float = 0.0
            ):
                self._type = enum_check(type, self.Type)
                self._viscosity = type_check(viscosity, float) if viscosity is not None else None

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def viscosity(self):
                return self._viscosity

            @viscosity.setter
            def viscosity(self, value):
                ''' 
                TODO
                '''
                self._viscosity = type_check(value, float) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object39.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,"viscosity": self._viscosity,})


        class Object40(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: ['time_dependent']'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None,
                time_dependent: bool = False
            ):
                self._type = enum_check(type, self.Type)
                self._time_dependent = type_check(time_dependent, bool) if time_dependent is not None else None

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def time_dependent(self):
                return self._time_dependent

            @time_dependent.setter
            def time_dependent(self, value):
                ''' 
                TODO
                '''
                self._time_dependent = type_check(value, bool) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object40.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,"time_dependent": self._time_dependent,})


        class Object41(object):
            '''TODO
            \nRequired: ['type']
            \nOptional: ['U', 'time_dependent']'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None,
                U: float = 0.0,
                time_dependent: bool = False
            ):
                self._type = enum_check(type, self.Type)
                self._U = type_check(U, float) if U is not None else None
                self._time_dependent = type_check(time_dependent, bool) if time_dependent is not None else None

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            @property
            def U(self):
                return self._U

            @U.setter
            def U(self, value):
                ''' 
                TODO
                '''
                self._U = type_check(value, float) 

            @property
            def time_dependent(self):
                return self._time_dependent

            @time_dependent.setter
            def time_dependent(self, value):
                ''' 
                TODO
                '''
                self._time_dependent = type_check(value, bool) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object41.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,"U": self._U,"time_dependent": self._time_dependent,})


        class Object42(object):
            '''TODO, type, omega, is_scalar
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object42.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})


        class Object43(object):
            '''TODO, type, omega, is_scalar
            \nRequired: ['type']
            \nOptional: []'''
            class Type(str, Enum):
                LINEAR = 'Linear'
                QUADRATIC = 'Quadratic'
                CUBIC = 'Cubic'
                SINE = 'Sine'
                FRANKE = 'Franke'
                FRANKEOLD = 'FrankeOld'
                GENERICSCALAREXACT = 'GenericScalarExact'
                ZERO_BC = 'Zero_BC'
                ELASTIC = 'Elastic'
                WALK = 'Walk'
                TORSIONELASTIC = 'TorsionElastic'
                DOUBLETORSIONELASTIC = 'DoubleTorsionElastic'
                ELASTICZEROBC = 'ElasticZeroBC'
                ELASTICEXACT = 'ElasticExact'
                ELASTICCANTILEVEREXACT = 'ElasticCantileverExact'
                COMPRESSIONELASTICEXACT = 'CompressionElasticExact'
                QUADRATICELASTICEXACT = 'QuadraticElasticExact'
                LINEARELASTICEXACT = 'LinearElasticExact'
                POINTBASEDTENSOR = 'PointBasedTensor'
                KERNEL = 'Kernel'
                NODE = 'Node'
                TIMEDEPENDENTSCALAR = 'TimeDependentScalar'
                MINSURF = 'MinSurf'
                GRAVITY = 'Gravity'
                CONSTANTVELOCITY = 'ConstantVelocity'
                TWOSPHERES = 'TwoSpheres'
                DRIVENCAVITY = 'DrivenCavity'
                DRIVENCAVITYC0 = 'DrivenCavityC0'
                DRIVENCAVITYSMOOTH = 'DrivenCavitySmooth'
                FLOW = 'Flow'
                FLOWWITHOBSTACLE = 'FlowWithObstacle'
                CORNERFLOW = 'CornerFlow'
                UNITFLOWWITHOBSTACLE = 'UnitFlowWithObstacle'
                STOKESLAW = 'StokesLaw'
                TAYLORGREENVORTEX = 'TaylorGreenVortex'
                SIMPLESTOKEPROBLEMEXACT = 'SimpleStokeProblemExact'
                SINESTOKEPROBLEMEXACT = 'SineStokeProblemExact'
                TRANSIENTSTOKEPROBLEMEXACT = 'TransientStokeProblemExact'
                KOVNASZY = 'Kovnaszy'
                AIRFOIL = 'Airfoil'
                LSHAPE = 'Lshape'
                TESTPROBLEM = 'TestProblem'
                BILAPLACIANPROBLEMWITHSOLUTION = 'BilaplacianProblemWithSolution'

            def __init__(
                self,
                type: "Type" = None
            ):
                self._type = enum_check(type, self.Type)

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of preset problem to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                if self.type is None:
                    print("Requiered variable Root.Preset_problem.Object43.type does not have value")
                return

            def as_dict(self):
                return drop_none({"type": self._type.value if self._type is not None else None,})



    class Space(object):
        '''Options related to the FE space.
        \nRequired: []
        \nOptional: ['discr_order', 'discr_orderq', 'pressure_discr_order', 'basis_type', 'poly_basis_type', 'use_p_ref', 'remesh', 'advanced']'''
        class Basis_type(str, Enum):
            LAGRANGE = 'Lagrange'
            SPLINE = 'Spline'
            SERENDIPITY = 'Serendipity'
            BERNSTEIN = 'Bernstein'

        class Poly_basis_type(str, Enum):
            MFSHARMONIC = 'MFSHarmonic'
            MEANVALUE = 'MeanValue'
            WACHSPRESS = 'Wachspress'

        def __init__(
            self,
            discr_order: Optional["Root.Space.Discr_order"] = None,
            discr_orderq: int = 1,
            pressure_discr_order: int = 1,
            basis_type: "Basis_type" = 'Lagrange',
            poly_basis_type: "Poly_basis_type" = 'MFSHarmonic',
            use_p_ref: bool = False,
            remesh: Optional["Root.Space.Remesh"] = None,
            advanced: Optional["Root.Space.Advanced"] = None
        ):
            self._discr_order = type_check(discr_order, self.Discr_order) if discr_order else self.Discr_order()
            self._discr_orderq = type_check(discr_orderq, int) if discr_orderq is not None else None
            self._pressure_discr_order = type_check(pressure_discr_order, int) if pressure_discr_order is not None else None
            self._basis_type = enum_check(basis_type, self.Basis_type)
            self._poly_basis_type = enum_check(poly_basis_type, self.Poly_basis_type)
            self._use_p_ref = type_check(use_p_ref, bool) if use_p_ref is not None else None
            self._remesh = type_check(remesh, self.Remesh) if remesh else self.Remesh()
            self._advanced = type_check(advanced, self.Advanced) if advanced else self.Advanced()

        @property
        def discr_order(self):
            return self._discr_order

        @discr_order.setter
        def discr_order(self, value):
            ''' 
            This is a polymorphic variable, assign an object from its classes to the value
            \nRequired: []
            \nOptional: ['int', 'file', 'list', 'object4']
            '''
            self._discr_order = type_check(value, self.Discr_order) 

        @property
        def discr_orderq(self):
            return self._discr_orderq

        @discr_orderq.setter
        def discr_orderq(self, value):
            ''' 
            Lagrange element order at height dimension for the space for the main unknown, for prism.
            '''
            self._discr_orderq = type_check(value, int) 

        @property
        def pressure_discr_order(self):
            return self._pressure_discr_order

        @pressure_discr_order.setter
        def pressure_discr_order(self, value):
            ''' 
             Lagrange element order for the space for the pressure unknown, for all elements.
            '''
            self._pressure_discr_order = type_check(value, int) 

        @property
        def basis_type(self):
            return self._basis_type

        @basis_type.setter
        def basis_type(self, value):
            ''' 
            Type of basis to use for non polygonal element, one of Lagrange, Spline, or Serendipity. Spline or Serendipity work only for quad/hex meshes
            '''
            self._basis_type = enum_check(value, self.Basis_type) 

        @property
        def poly_basis_type(self):
            return self._poly_basis_type

        @poly_basis_type.setter
        def poly_basis_type(self, value):
            ''' 
            Type of basis to use for a polygonal element, one of MFSHarmonic, MeanValue, or Wachspress see 'PolySpline..' paper for details.
            '''
            self._poly_basis_type = enum_check(value, self.Poly_basis_type) 

        @property
        def use_p_ref(self):
            return self._use_p_ref

        @use_p_ref.setter
        def use_p_ref(self, value):
            ''' 
            Perform a priori p-refinement based on element shape, as described in 'Decoupling..' paper.
            '''
            self._use_p_ref = type_check(value, bool) 

        @property
        def remesh(self):
            return self._remesh

        @remesh.setter
        def remesh(self, value):
            ''' 
            Settings for adaptive remeshing
            \nRequired: []
            \nOptional: ['enabled', 'split', 'collapse', 'swap', 'smooth', 'local_relaxation', 'type']
            '''
            self._remesh = type_check(value, self.Remesh) 

        @property
        def advanced(self):
            return self._advanced

        @advanced.setter
        def advanced(self, value):
            ''' 
            Advanced settings for the FE space.
            \nRequired: []
            \nOptional: ['discr_order_max', 'isoparametric', 'bc_method', 'n_boundary_samples', 'quadrature_order', 'mass_quadrature_order', 'use_corner_quadrature', 'integral_constraints', 'n_harmonic_samples', 'force_no_ref_for_harmonic', 'B', 'h1_formula', 'count_flipped_els', 'count_flipped_els_continuous', 'use_particle_advection']
            '''
            self._advanced = type_check(value, self.Advanced) 

        def check_required(self):

            return

        def as_dict(self):
            return drop_none({"discr_order": self._discr_order.as_dict(),"discr_orderq": self._discr_orderq,"pressure_discr_order": self._pressure_discr_order,"basis_type": self._basis_type.value if self._basis_type is not None else None,"poly_basis_type": self._poly_basis_type.value if self._poly_basis_type is not None else None,"use_p_ref": self._use_p_ref,"remesh": self._remesh.as_dict(),"advanced": self._advanced.as_dict(),})

        class Discr_order(object):
            '''This is a polymorphic variable, assign an object from its classes to the value
            \nRequired: []
            \nOptional: ['int', 'file', 'list', 'object4']'''
            def __init__(
                self,
                value : object = None
            ):
                self._value = class_check(value, [int, file, list, self.Object4]) if value is not None else None

            @property
            def value(self):
                return self._value

            @value.setter
            def value(self, value):
                ''' 
                This is a polymorphic variable, assign an object from its classes to the value
                '''
                self._value = class_check(value, [int, file, list, self.Object4]) 

            def check_required(self):

                if self.value is None:
                    print("Requiered variable Root.Space.Discr_order.value does not have value")
                else:
                    if type(self.value) not in [['int', 'float', 'list', 'str', 'bool']]:
                        self.value.check_required()
                return

            def as_dict(self):
                return drop_none(self._value.as_dict() if isinstance(self._value, tuple([self.Object4])) else self._value)

            class Object4(object):
                '''Lagrange element order for the a space tagged with volume ID for the main unknown.
                \nRequired: ['id', 'order']
                \nOptional: []'''
                def __init__(
                    self,
                    id: Optional["Root.Space.Discr_order.Object4.Id"] = None,
                    order: int = None
                ):
                    self._id = type_check(id, self.Id) if id else self.Id()
                    self._order = type_check(order, int) if order is not None else None

                @property
                def id(self):
                    return self._id

                @id.setter
                def id(self, value):
                    ''' 
                    This is a polymorphic variable, assign an object from its classes to the value
                    \nRequired: []
                    \nOptional: ['int', 'list']
                    '''
                    self._id = type_check(value, self.Id) 

                @property
                def order(self):
                    return self._order

                @order.setter
                def order(self, value):
                    ''' 
                    Lagrange element order for the space for the main unknown, for all elements.
                    '''
                    self._order = type_check(value, int) 

                def check_required(self):
                    self.id.check_required()

                    if self.order is None:
                        print("Requiered variable Root.Space.Discr_order.Object4.order does not have value")
                    return

                def as_dict(self):
                    return drop_none({"id": self._id.as_dict(),"order": self._order,})

                class Id(object):
                    '''This is a polymorphic variable, assign an object from its classes to the value
                    \nRequired: []
                    \nOptional: ['int', 'list']'''
                    def __init__(
                        self,
                        value : object = None
                    ):
                        self._value = class_check(value, [int, list]) if value is not None else None

                    @property
                    def value(self):
                        return self._value

                    @value.setter
                    def value(self, value):
                        ''' 
                        This is a polymorphic variable, assign an object from its classes to the value
                        '''
                        self._value = class_check(value, [int, list]) 

                    def check_required(self):

                        if self.value is None:
                            print("Requiered variable Root.Space.Discr_order.Object4.Id.value does not have value")
                        else:
                            if type(self.value) not in [['int', 'float', 'list', 'str', 'bool']]:
                                self.value.check_required()
                        return

                    def as_dict(self):
                        return drop_none(self._value.as_dict() if isinstance(self._value, tuple([])) else self._value)




        class Remesh(object):
            '''Settings for adaptive remeshing
            \nRequired: []
            \nOptional: ['enabled', 'split', 'collapse', 'swap', 'smooth', 'local_relaxation', 'type']'''
            class Type(str, Enum):
                PHYSICS = 'physics'
                SIZING_FIELD = 'sizing_field'

            def __init__(
                self,
                enabled: bool = False,
                split: Optional["Root.Space.Remesh.Split"] = None,
                collapse: Optional["Root.Space.Remesh.Collapse"] = None,
                swap: Optional["Root.Space.Remesh.Swap"] = None,
                smooth: Optional["Root.Space.Remesh.Smooth"] = None,
                local_relaxation: Optional["Root.Space.Remesh.Local_relaxation"] = None,
                type: "Type" = 'physics'
            ):
                self._enabled = type_check(enabled, bool) if enabled is not None else None
                self._split = type_check(split, self.Split) if split else self.Split()
                self._collapse = type_check(collapse, self.Collapse) if collapse else self.Collapse()
                self._swap = type_check(swap, self.Swap) if swap else self.Swap()
                self._smooth = type_check(smooth, self.Smooth) if smooth else self.Smooth()
                self._local_relaxation = type_check(local_relaxation, self.Local_relaxation) if local_relaxation else self.Local_relaxation()
                self._type = enum_check(type, self.Type)

            @property
            def enabled(self):
                return self._enabled

            @enabled.setter
            def enabled(self, value):
                ''' 
                Whether to do adaptive remeshing
                '''
                self._enabled = type_check(value, bool) 

            @property
            def split(self):
                return self._split

            @split.setter
            def split(self, value):
                ''' 
                Settings for adaptive remeshing edge splitting operations
                \nRequired: []
                \nOptional: ['enabled', 'acceptance_tolerance', 'culling_threshold', 'max_depth', 'min_edge_length']
                '''
                self._split = type_check(value, self.Split) 

            @property
            def collapse(self):
                return self._collapse

            @collapse.setter
            def collapse(self, value):
                ''' 
                Settings for adaptive remeshing edge collapse operations
                \nRequired: []
                \nOptional: ['enabled', 'acceptance_tolerance', 'culling_threshold', 'max_depth', 'rel_max_edge_length', 'abs_max_edge_length']
                '''
                self._collapse = type_check(value, self.Collapse) 

            @property
            def swap(self):
                return self._swap

            @swap.setter
            def swap(self, value):
                ''' 
                Settings for adaptive remeshing edge/face swap operations
                \nRequired: []
                \nOptional: ['enabled', 'acceptance_tolerance', 'max_depth']
                '''
                self._swap = type_check(value, self.Swap) 

            @property
            def smooth(self):
                return self._smooth

            @smooth.setter
            def smooth(self, value):
                ''' 
                Settings for adaptive remeshing vertex smoothing operations
                \nRequired: []
                \nOptional: ['enabled', 'acceptance_tolerance', 'max_iters']
                '''
                self._smooth = type_check(value, self.Smooth) 

            @property
            def local_relaxation(self):
                return self._local_relaxation

            @local_relaxation.setter
            def local_relaxation(self, value):
                ''' 
                Settings for adaptive remeshing local relaxation
                \nRequired: []
                \nOptional: ['local_mesh_n_ring', 'local_mesh_rel_area', 'max_nl_iterations']
                '''
                self._local_relaxation = type_check(value, self.Local_relaxation) 

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                ''' 
                Type of adaptive remeshing to use.
                '''
                self._type = enum_check(value, self.Type) 

            def check_required(self):

                return

            def as_dict(self):
                return drop_none({"enabled": self._enabled,"split": self._split.as_dict(),"collapse": self._collapse.as_dict(),"swap": self._swap.as_dict(),"smooth": self._smooth.as_dict(),"local_relaxation": self._local_relaxation.as_dict(),"type": self._type.value if self._type is not None else None,})

            class Split(object):
                '''Settings for adaptive remeshing edge splitting operations
                \nRequired: []
                \nOptional: ['enabled', 'acceptance_tolerance', 'culling_threshold', 'max_depth', 'min_edge_length']'''
                def __init__(
                    self,
                    enabled: bool = True,
                    acceptance_tolerance: float = 0.001,
                    culling_threshold: float = 0.95,
                    max_depth: int = 3,
                    min_edge_length: float = 1e-06
                ):
                    self._enabled = type_check(enabled, bool) if enabled is not None else None
                    self._acceptance_tolerance = range_check(type_check(acceptance_tolerance, float), 0, None) if acceptance_tolerance is not None else None
                    self._culling_threshold = range_check(type_check(culling_threshold, float), 0, 1) if culling_threshold is not None else None
                    self._max_depth = range_check(type_check(max_depth, int), 1, None) if max_depth is not None else None
                    self._min_edge_length = range_check(type_check(min_edge_length, float), 0, None) if min_edge_length is not None else None

                @property
                def enabled(self):
                    return self._enabled

                @enabled.setter
                def enabled(self, value):
                    ''' 
                    Whether to do edge splitting in adaptive remeshing
                    '''
                    self._enabled = type_check(value, bool) 

                @property
                def acceptance_tolerance(self):
                    return self._acceptance_tolerance

                @acceptance_tolerance.setter
                def acceptance_tolerance(self, value):
                    ''' 
                    Accept split operation if energy decreased by at least x
                    '''
                    self._acceptance_tolerance = range_check(type_check(value, float), 0, None) 

                @property
                def culling_threshold(self):
                    return self._culling_threshold

                @culling_threshold.setter
                def culling_threshold(self, value):
                    ''' 
                    Split operation culling threshold on energy
                    '''
                    self._culling_threshold = range_check(type_check(value, float), 0, 1) 

                @property
                def max_depth(self):
                    return self._max_depth

                @max_depth.setter
                def max_depth(self, value):
                    ''' 
                    Maximum depth split per time-step
                    '''
                    self._max_depth = range_check(type_check(value, int), 1, None) 

                @property
                def min_edge_length(self):
                    return self._min_edge_length

                @min_edge_length.setter
                def min_edge_length(self, value):
                    ''' 
                    Minimum edge length to split
                    '''
                    self._min_edge_length = range_check(type_check(value, float), 0, None) 

                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({"enabled": self._enabled,"acceptance_tolerance": self._acceptance_tolerance,"culling_threshold": self._culling_threshold,"max_depth": self._max_depth,"min_edge_length": self._min_edge_length,})


            class Collapse(object):
                '''Settings for adaptive remeshing edge collapse operations
                \nRequired: []
                \nOptional: ['enabled', 'acceptance_tolerance', 'culling_threshold', 'max_depth', 'rel_max_edge_length', 'abs_max_edge_length']'''
                def __init__(
                    self,
                    enabled: bool = True,
                    acceptance_tolerance: float = -1e-08,
                    culling_threshold: float = 0.01,
                    max_depth: int = 3,
                    rel_max_edge_length: float = 1.0,
                    abs_max_edge_length: float = 1e+100
                ):
                    self._enabled = type_check(enabled, bool) if enabled is not None else None
                    self._acceptance_tolerance = range_check(type_check(acceptance_tolerance, float), None, 0) if acceptance_tolerance is not None else None
                    self._culling_threshold = range_check(type_check(culling_threshold, float), 0, 1) if culling_threshold is not None else None
                    self._max_depth = range_check(type_check(max_depth, int), 1, None) if max_depth is not None else None
                    self._rel_max_edge_length = range_check(type_check(rel_max_edge_length, float), 0, None) if rel_max_edge_length is not None else None
                    self._abs_max_edge_length = range_check(type_check(abs_max_edge_length, float), 0, None) if abs_max_edge_length is not None else None

                @property
                def enabled(self):
                    return self._enabled

                @enabled.setter
                def enabled(self, value):
                    ''' 
                    Whether to do edge collapse in adaptive remeshing
                    '''
                    self._enabled = type_check(value, bool) 

                @property
                def acceptance_tolerance(self):
                    return self._acceptance_tolerance

                @acceptance_tolerance.setter
                def acceptance_tolerance(self, value):
                    ''' 
                    Accept collapse operation if energy decreased by at least x
                    '''
                    self._acceptance_tolerance = range_check(type_check(value, float), None, 0) 

                @property
                def culling_threshold(self):
                    return self._culling_threshold

                @culling_threshold.setter
                def culling_threshold(self, value):
                    ''' 
                    Collapse operation culling threshold on energy
                    '''
                    self._culling_threshold = range_check(type_check(value, float), 0, 1) 

                @property
                def max_depth(self):
                    return self._max_depth

                @max_depth.setter
                def max_depth(self, value):
                    ''' 
                    Maximum depth collapse per time-step
                    '''
                    self._max_depth = range_check(type_check(value, int), 1, None) 

                @property
                def rel_max_edge_length(self):
                    return self._rel_max_edge_length

                @rel_max_edge_length.setter
                def rel_max_edge_length(self, value):
                    ''' 
                    Length of maximum edge length to collapse relative to initial minimum edge length
                    '''
                    self._rel_max_edge_length = range_check(type_check(value, float), 0, None) 

                @property
                def abs_max_edge_length(self):
                    return self._abs_max_edge_length

                @abs_max_edge_length.setter
                def abs_max_edge_length(self, value):
                    ''' 
                    Length of maximum edge length to collapse in absolute units of distance
                    '''
                    self._abs_max_edge_length = range_check(type_check(value, float), 0, None) 

                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({"enabled": self._enabled,"acceptance_tolerance": self._acceptance_tolerance,"culling_threshold": self._culling_threshold,"max_depth": self._max_depth,"rel_max_edge_length": self._rel_max_edge_length,"abs_max_edge_length": self._abs_max_edge_length,})


            class Swap(object):
                '''Settings for adaptive remeshing edge/face swap operations
                \nRequired: []
                \nOptional: ['enabled', 'acceptance_tolerance', 'max_depth']'''
                def __init__(
                    self,
                    enabled: bool = False,
                    acceptance_tolerance: float = -1e-08,
                    max_depth: int = 3
                ):
                    self._enabled = type_check(enabled, bool) if enabled is not None else None
                    self._acceptance_tolerance = range_check(type_check(acceptance_tolerance, float), None, 0) if acceptance_tolerance is not None else None
                    self._max_depth = range_check(type_check(max_depth, int), 1, None) if max_depth is not None else None

                @property
                def enabled(self):
                    return self._enabled

                @enabled.setter
                def enabled(self, value):
                    ''' 
                    Whether to do edge/face swap in adaptive remeshing
                    '''
                    self._enabled = type_check(value, bool) 

                @property
                def acceptance_tolerance(self):
                    return self._acceptance_tolerance

                @acceptance_tolerance.setter
                def acceptance_tolerance(self, value):
                    ''' 
                    Accept swap operation if energy decreased by at least x
                    '''
                    self._acceptance_tolerance = range_check(type_check(value, float), None, 0) 

                @property
                def max_depth(self):
                    return self._max_depth

                @max_depth.setter
                def max_depth(self, value):
                    ''' 
                    Maximum depth swap per time-step
                    '''
                    self._max_depth = range_check(type_check(value, int), 1, None) 

                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({"enabled": self._enabled,"acceptance_tolerance": self._acceptance_tolerance,"max_depth": self._max_depth,})


            class Smooth(object):
                '''Settings for adaptive remeshing vertex smoothing operations
                \nRequired: []
                \nOptional: ['enabled', 'acceptance_tolerance', 'max_iters']'''
                def __init__(
                    self,
                    enabled: bool = False,
                    acceptance_tolerance: float = -1e-08,
                    max_iters: int = 1
                ):
                    self._enabled = type_check(enabled, bool) if enabled is not None else None
                    self._acceptance_tolerance = range_check(type_check(acceptance_tolerance, float), None, 0) if acceptance_tolerance is not None else None
                    self._max_iters = range_check(type_check(max_iters, int), 1, None) if max_iters is not None else None

                @property
                def enabled(self):
                    return self._enabled

                @enabled.setter
                def enabled(self, value):
                    ''' 
                    Whether to do vertex smoothing in adaptive remeshing
                    '''
                    self._enabled = type_check(value, bool) 

                @property
                def acceptance_tolerance(self):
                    return self._acceptance_tolerance

                @acceptance_tolerance.setter
                def acceptance_tolerance(self, value):
                    ''' 
                    Accept smooth operation if energy decreased by at least x
                    '''
                    self._acceptance_tolerance = range_check(type_check(value, float), None, 0) 

                @property
                def max_iters(self):
                    return self._max_iters

                @max_iters.setter
                def max_iters(self, value):
                    ''' 
                    Maximum number of smoothing iterations per time-step
                    '''
                    self._max_iters = range_check(type_check(value, int), 1, None) 

                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({"enabled": self._enabled,"acceptance_tolerance": self._acceptance_tolerance,"max_iters": self._max_iters,})


            class Local_relaxation(object):
                '''Settings for adaptive remeshing local relaxation
                \nRequired: []
                \nOptional: ['local_mesh_n_ring', 'local_mesh_rel_area', 'max_nl_iterations']'''
                def __init__(
                    self,
                    local_mesh_n_ring: int = 2,
                    local_mesh_rel_area: float = 0.01,
                    max_nl_iterations: int = 1
                ):
                    self._local_mesh_n_ring = type_check(local_mesh_n_ring, int) if local_mesh_n_ring is not None else None
                    self._local_mesh_rel_area = type_check(local_mesh_rel_area, float) if local_mesh_rel_area is not None else None
                    self._max_nl_iterations = type_check(max_nl_iterations, int) if max_nl_iterations is not None else None

                @property
                def local_mesh_n_ring(self):
                    return self._local_mesh_n_ring

                @local_mesh_n_ring.setter
                def local_mesh_n_ring(self, value):
                    ''' 
                    Size of n-ring for local relaxation
                    '''
                    self._local_mesh_n_ring = type_check(value, int) 

                @property
                def local_mesh_rel_area(self):
                    return self._local_mesh_rel_area

                @local_mesh_rel_area.setter
                def local_mesh_rel_area(self, value):
                    ''' 
                    Minimum area for local relaxation
                    '''
                    self._local_mesh_rel_area = type_check(value, float) 

                @property
                def max_nl_iterations(self):
                    return self._max_nl_iterations

                @max_nl_iterations.setter
                def max_nl_iterations(self, value):
                    ''' 
                    Maximum number of nonlinear solver iterations before acceptance check
                    '''
                    self._max_nl_iterations = type_check(value, int) 

                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({"local_mesh_n_ring": self._local_mesh_n_ring,"local_mesh_rel_area": self._local_mesh_rel_area,"max_nl_iterations": self._max_nl_iterations,})



        class Advanced(object):
            '''Advanced settings for the FE space.
            \nRequired: []
            \nOptional: ['discr_order_max', 'isoparametric', 'bc_method', 'n_boundary_samples', 'quadrature_order', 'mass_quadrature_order', 'use_corner_quadrature', 'integral_constraints', 'n_harmonic_samples', 'force_no_ref_for_harmonic', 'B', 'h1_formula', 'count_flipped_els', 'count_flipped_els_continuous', 'use_particle_advection']'''
            class Bc_method(str, Enum):
                LSQ = 'lsq'
                SAMPLE = 'sample'

            def __init__(
                self,
                discr_order_max: int = 4,
                isoparametric: bool = False,
                bc_method: "Bc_method" = 'sample',
                n_boundary_samples: int = -1,
                quadrature_order: int = -1,
                mass_quadrature_order: int = -1,
                use_corner_quadrature: bool = False,
                integral_constraints: int = 2,
                n_harmonic_samples: int = 10,
                force_no_ref_for_harmonic: bool = False,
                B: int = 3,
                h1_formula: bool = False,
                count_flipped_els: bool = True,
                count_flipped_els_continuous: bool = False,
                use_particle_advection: bool = False
            ):
                self._discr_order_max = type_check(discr_order_max, int) if discr_order_max is not None else None
                self._isoparametric = type_check(isoparametric, bool) if isoparametric is not None else None
                self._bc_method = enum_check(bc_method, self.Bc_method)
                self._n_boundary_samples = type_check(n_boundary_samples, int) if n_boundary_samples is not None else None
                self._quadrature_order = type_check(quadrature_order, int) if quadrature_order is not None else None
                self._mass_quadrature_order = type_check(mass_quadrature_order, int) if mass_quadrature_order is not None else None
                self._use_corner_quadrature = type_check(use_corner_quadrature, bool) if use_corner_quadrature is not None else None
                self._integral_constraints = type_check(integral_constraints, int) if integral_constraints is not None else None
                self._n_harmonic_samples = type_check(n_harmonic_samples, int) if n_harmonic_samples is not None else None
                self._force_no_ref_for_harmonic = type_check(force_no_ref_for_harmonic, bool) if force_no_ref_for_harmonic is not None else None
                self._B = type_check(B, int) if B is not None else None
                self._h1_formula = type_check(h1_formula, bool) if h1_formula is not None else None
                self._count_flipped_els = type_check(count_flipped_els, bool) if count_flipped_els is not None else None
                self._count_flipped_els_continuous = type_check(count_flipped_els_continuous, bool) if count_flipped_els_continuous is not None else None
                self._use_particle_advection = type_check(use_particle_advection, bool) if use_particle_advection is not None else None

            @property
            def discr_order_max(self):
                return self._discr_order_max

            @discr_order_max.setter
            def discr_order_max(self, value):
                ''' 
                Maximal discretization order in adaptive p-refinement and hp-refinement
                '''
                self._discr_order_max = type_check(value, int) 

            @property
            def isoparametric(self):
                return self._isoparametric

            @isoparametric.setter
            def isoparametric(self, value):
                ''' 
                Forces geometric map basis to be the same degree as the main variable basis, irrespective of the degree associated with the geom. map degrees associated with the elements of the geometry.
                '''
                self._isoparametric = type_check(value, bool) 

            @property
            def bc_method(self):
                return self._bc_method

            @bc_method.setter
            def bc_method(self, value):
                ''' 
                Method for imposing analytic Dirichet boundary conditions. If 'lsq' (least-squares fit), then the bc function is sampled at quadrature points, and the FEspace nodal values on the boundary are determined by minimizing L2 norm of the difference. If 'sample', then the analytic bc function is sampled at the boundary nodes.
                '''
                self._bc_method = enum_check(value, self.Bc_method) 

            @property
            def n_boundary_samples(self):
                return self._n_boundary_samples

            @n_boundary_samples.setter
            def n_boundary_samples(self, value):
                ''' 
                Per-element number of boundary samples for analytic Dirichlet and Neumann boundary conditions.
                '''
                self._n_boundary_samples = type_check(value, int) 

            @property
            def quadrature_order(self):
                return self._quadrature_order

            @quadrature_order.setter
            def quadrature_order(self, value):
                ''' 
                Minimal quadrature order to use in matrix and rhs assembly; the actual order is determined as min(2*(p-1)+1,quadrature_order).
                '''
                self._quadrature_order = type_check(value, int) 

            @property
            def mass_quadrature_order(self):
                return self._mass_quadrature_order

            @mass_quadrature_order.setter
            def mass_quadrature_order(self, value):
                ''' 
                Minimal quadrature order to use in mass matrix assembler; the actual order is determined as min(2*p+1,quadrature_order)
                '''
                self._mass_quadrature_order = type_check(value, int) 

            @property
            def use_corner_quadrature(self):
                return self._use_corner_quadrature

            @use_corner_quadrature.setter
            def use_corner_quadrature(self, value):
                ''' 
                Use quadrature rules that always include all the vertices of the element.
                '''
                self._use_corner_quadrature = type_check(value, bool) 

            @property
            def integral_constraints(self):
                return self._integral_constraints

            @integral_constraints.setter
            def integral_constraints(self, value):
                ''' 
                Number of constraints for non-conforming polygonal basis;  0, 1, or 2; see 'PolySpline..' paper for details.
                '''
                self._integral_constraints = type_check(value, int) 

            @property
            def n_harmonic_samples(self):
                return self._n_harmonic_samples

            @n_harmonic_samples.setter
            def n_harmonic_samples(self, value):
                ''' 
                If MFSHarmonics is used for a polygonal element, number of collocation samples used in the basis construction;see 'PolySpline..' paper for details.
                '''
                self._n_harmonic_samples = type_check(value, int) 

            @property
            def force_no_ref_for_harmonic(self):
                return self._force_no_ref_for_harmonic

            @force_no_ref_for_harmonic.setter
            def force_no_ref_for_harmonic(self, value):
                ''' 
                If true, do not do uniform global refinement if the mesh contains polygonal elements.
                '''
                self._force_no_ref_for_harmonic = type_check(value, bool) 

            @property
            def B(self):
                return self._B

            @B.setter
            def B(self, value):
                ''' 
                The target deviation of the error on elements from perfect element error, for a priori geometry-dependent p-refinement, see 'Decoupling .. ' paper.
                '''
                self._B = type_check(value, int) 

            @property
            def h1_formula(self):
                return self._h1_formula

            @h1_formula.setter
            def h1_formula(self, value):
                ''' 
                There is no definition
                '''
                self._h1_formula = type_check(value, bool) 

            @property
            def count_flipped_els(self):
                return self._count_flipped_els

            @count_flipped_els.setter
            def count_flipped_els(self, value):
                ''' 
                Count the number of elements with Jacobian of the geometric map not positive at quadrature points.
                '''
                self._count_flipped_els = type_check(value, bool) 

            @property
            def count_flipped_els_continuous(self):
                return self._count_flipped_els_continuous

            @count_flipped_els_continuous.setter
            def count_flipped_els_continuous(self, value):
                ''' 
                Count the number of elements with Jacobian of the geometric map not positive at any point.
                '''
                self._count_flipped_els_continuous = type_check(value, bool) 

            @property
            def use_particle_advection(self):
                return self._use_particle_advection

            @use_particle_advection.setter
            def use_particle_advection(self, value):
                ''' 
                Use particle advection in splitting method for solving NS equation.
                '''
                self._use_particle_advection = type_check(value, bool) 

            def check_required(self):

                return

            def as_dict(self):
                return drop_none({"discr_order_max": self._discr_order_max,"isoparametric": self._isoparametric,"bc_method": self._bc_method.value if self._bc_method is not None else None,"n_boundary_samples": self._n_boundary_samples,"quadrature_order": self._quadrature_order,"mass_quadrature_order": self._mass_quadrature_order,"use_corner_quadrature": self._use_corner_quadrature,"integral_constraints": self._integral_constraints,"n_harmonic_samples": self._n_harmonic_samples,"force_no_ref_for_harmonic": self._force_no_ref_for_harmonic,"B": self._B,"h1_formula": self._h1_formula,"count_flipped_els": self._count_flipped_els,"count_flipped_els_continuous": self._count_flipped_els_continuous,"use_particle_advection": self._use_particle_advection,})



    class Time(object):
        '''This is a polymorphic variable, assign an object from its classes to the value
        \nRequired: []
        \nOptional: ['object1', 'object2', 'object3']'''
        def __init__(
            self,
            value : object = None
        ):
            self._value = class_check(value, [self.Object1, self.Object2, self.Object3]) if value is not None else None

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, value):
            ''' 
            This is a polymorphic variable, assign an object from its classes to the value
            '''
            self._value = class_check(value, [self.Object1, self.Object2, self.Object3]) 

        def check_required(self):

            if self.value is None:
                print("Requiered variable Root.Time.value does not have value")
            else:
                if type(self.value) not in [['int', 'float', 'list', 'str', 'bool']]:
                    self.value.check_required()
            return

        def as_dict(self):
            return drop_none(self._value.as_dict() if isinstance(self._value, tuple([self.Object1, self.Object2, self.Object3])) else self._value)

        class Object1(object):
            '''The time parameters: start time `t0`, end time `tend`, time step `dt`.
            \nRequired: ['tend', 'dt']
            \nOptional: ['t0', 'integrator', 'quasistatic']'''
            def __init__(
                self,
                tend: float = None,
                dt: float = None,
                t0: float = 0.0,
                object3: Optional["Root.Time.Object1.Object3"] = None,
                quasistatic: bool = False
            ):
                self._tend = range_check(type_check(tend, float), 0, None) if tend is not None else None
                self._dt = range_check(type_check(dt, float), 0, None) if dt is not None else None
                self._t0 = range_check(type_check(t0, float), 0, None) if t0 is not None else None
                self._object3 = type_check(object3, self.Object3) if object3 else self.Object3()
                self._quasistatic = type_check(quasistatic, bool) if quasistatic is not None else None

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
                Time step size $\\Delta t$
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

            @property
            def object3(self):
                return self._object3

            @object3.setter
            def object3(self, value):
                ''' 
                This is a polymorphic variable, assign an object from its classes to the value
                \nRequired: []
                \nOptional: ['object1', 'object2']
                '''
                self._object3 = type_check(value, self.Object3) 

            @property
            def quasistatic(self):
                return self._quasistatic

            @quasistatic.setter
            def quasistatic(self, value):
                ''' 
                Ignore inertia in time dependent. Used for doing incremental load.
                '''
                self._quasistatic = type_check(value, bool) 

            def check_required(self):

                if self.tend is None:
                    print("Requiered variable Root.Time.Object1.tend does not have value")

                if self.dt is None:
                    print("Requiered variable Root.Time.Object1.dt does not have value")
                return

            def as_dict(self):
                return drop_none({"tend": self._tend,"dt": self._dt,"t0": self._t0,"object3": self._object3.as_dict(),"quasistatic": self._quasistatic,})

            class Object3(object):
                '''This is a polymorphic variable, assign an object from its classes to the value
                \nRequired: []
                \nOptional: ['object1', 'object2']'''
                def __init__(
                    self,
                    value : object = None
                ):
                    self._value = class_check(value, [self.Object1, self.Object2]) if value is not None else None

                @property
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    ''' 
                    This is a polymorphic variable, assign an object from its classes to the value
                    '''
                    self._value = class_check(value, [self.Object1, self.Object2]) 

                def check_required(self):

                    if self.value is None:
                        print("Requiered variable Root.Time.Object1.Object3.value does not have value")
                    else:
                        if type(self.value) not in [['int', 'float', 'list', 'str', 'bool']]:
                            self.value.check_required()
                    return

                def as_dict(self):
                    return drop_none(self._value.as_dict() if isinstance(self._value, tuple([self.Object1, self.Object2])) else self._value)

                class Object1(object):
                    '''Backwards differentiation formula time integration
                    \nRequired: ['type']
                    \nOptional: ['steps']'''
                    class Type(str, Enum):
                        IMPLICITEULER = 'ImplicitEuler'
                        BDF = 'BDF'
                        IMPLICITNEWMARK = 'ImplicitNewmark'

                    def __init__(
                        self,
                        type: "Type" = None,
                        steps: int = 1
                    ):
                        self._type = enum_check(type, self.Type)
                        self._steps = range_check(type_check(steps, int), 1, 6) if steps is not None else None

                    @property
                    def type(self):
                        return self._type

                    @type.setter
                    def type(self, value):
                        ''' 
                        Type of time integrator to use
                        '''
                        self._type = enum_check(value, self.Type) 

                    @property
                    def steps(self):
                        return self._steps

                    @steps.setter
                    def steps(self, value):
                        ''' 
                        BDF order
                        '''
                        self._steps = range_check(type_check(value, int), 1, 6) 

                    def check_required(self):

                        if self.type is None:
                            print("Requiered variable Root.Time.Object1.Object3.Object1.type does not have value")
                        return

                    def as_dict(self):
                        return drop_none({"type": self._type.value if self._type is not None else None,"steps": self._steps,})


                class Object2(object):
                    '''Implicit Newmark time integration
                    \nRequired: ['type']
                    \nOptional: ['gamma', 'beta']'''
                    def __init__(
                        self,
                        type: None = None,
                        gamma: float = 0.5,
                        beta: float = 0.25
                    ):
                        self._type = type_check(type, None) if type is not None else None
                        self._gamma = range_check(type_check(gamma, float), 0, 1) if gamma is not None else None
                        self._beta = range_check(type_check(beta, float), 0, 0.5) if beta is not None else None

                    @property
                    def type(self):
                        return self._type

                    @type.setter
                    def type(self, value):
                        ''' 
                        There is no definition
                        '''
                        self._type = type_check(value, None) 

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
                    def beta(self):
                        return self._beta

                    @beta.setter
                    def beta(self, value):
                        ''' 
                        Newmark beta
                        '''
                        self._beta = range_check(type_check(value, float), 0, 0.5) 

                    def check_required(self):

                        if self.type is None:
                            print("Requiered variable Root.Time.Object1.Object3.Object2.type does not have value")
                        return

                    def as_dict(self):
                        return drop_none({"type": self._type,"gamma": self._gamma,"beta": self._beta,})




        class Object2(object):
            '''The time parameters: start time `t0`, time step `dt`, number of time steps.
            \nRequired: ['time_steps', 'dt']
            \nOptional: ['t0', 'integrator', 'quasistatic']'''
            def __init__(
                self,
                time_steps: int = None,
                dt: float = None,
                t0: float = 0.0,
                object3: Optional["Root.Time.Object2.Object3"] = None,
                quasistatic: bool = False
            ):
                self._time_steps = range_check(type_check(time_steps, int), 0, None) if time_steps is not None else None
                self._dt = range_check(type_check(dt, float), 0, None) if dt is not None else None
                self._t0 = range_check(type_check(t0, float), 0, None) if t0 is not None else None
                self._object3 = type_check(object3, self.Object3) if object3 else self.Object3()
                self._quasistatic = type_check(quasistatic, bool) if quasistatic is not None else None

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
                Time step size $\\Delta t$
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

            @property
            def object3(self):
                return self._object3

            @object3.setter
            def object3(self, value):
                ''' 
                This is a polymorphic variable, assign an object from its classes to the value
                \nRequired: []
                \nOptional: ['object1', 'object2']
                '''
                self._object3 = type_check(value, self.Object3) 

            @property
            def quasistatic(self):
                return self._quasistatic

            @quasistatic.setter
            def quasistatic(self, value):
                ''' 
                Ignore inertia in time dependent. Used for doing incremental load.
                '''
                self._quasistatic = type_check(value, bool) 

            def check_required(self):

                if self.time_steps is None:
                    print("Requiered variable Root.Time.Object2.time_steps does not have value")

                if self.dt is None:
                    print("Requiered variable Root.Time.Object2.dt does not have value")
                return

            def as_dict(self):
                return drop_none({"time_steps": self._time_steps,"dt": self._dt,"t0": self._t0,"object3": self._object3.as_dict(),"quasistatic": self._quasistatic,})

            class Object3(object):
                '''This is a polymorphic variable, assign an object from its classes to the value
                \nRequired: []
                \nOptional: ['object1', 'object2']'''
                def __init__(
                    self,
                    value : object = None
                ):
                    self._value = class_check(value, [self.Object1, self.Object2]) if value is not None else None

                @property
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    ''' 
                    This is a polymorphic variable, assign an object from its classes to the value
                    '''
                    self._value = class_check(value, [self.Object1, self.Object2]) 

                def check_required(self):

                    if self.value is None:
                        print("Requiered variable Root.Time.Object2.Object3.value does not have value")
                    else:
                        if type(self.value) not in [['int', 'float', 'list', 'str', 'bool']]:
                            self.value.check_required()
                    return

                def as_dict(self):
                    return drop_none(self._value.as_dict() if isinstance(self._value, tuple([self.Object1, self.Object2])) else self._value)

                class Object1(object):
                    '''Backwards differentiation formula time integration
                    \nRequired: ['type']
                    \nOptional: ['steps']'''
                    class Type(str, Enum):
                        IMPLICITEULER = 'ImplicitEuler'
                        BDF = 'BDF'
                        IMPLICITNEWMARK = 'ImplicitNewmark'

                    def __init__(
                        self,
                        type: "Type" = None,
                        steps: int = 1
                    ):
                        self._type = enum_check(type, self.Type)
                        self._steps = range_check(type_check(steps, int), 1, 6) if steps is not None else None

                    @property
                    def type(self):
                        return self._type

                    @type.setter
                    def type(self, value):
                        ''' 
                        Type of time integrator to use
                        '''
                        self._type = enum_check(value, self.Type) 

                    @property
                    def steps(self):
                        return self._steps

                    @steps.setter
                    def steps(self, value):
                        ''' 
                        BDF order
                        '''
                        self._steps = range_check(type_check(value, int), 1, 6) 

                    def check_required(self):

                        if self.type is None:
                            print("Requiered variable Root.Time.Object2.Object3.Object1.type does not have value")
                        return

                    def as_dict(self):
                        return drop_none({"type": self._type.value if self._type is not None else None,"steps": self._steps,})


                class Object2(object):
                    '''Implicit Newmark time integration
                    \nRequired: ['type']
                    \nOptional: ['gamma', 'beta']'''
                    def __init__(
                        self,
                        type: None = None,
                        gamma: float = 0.5,
                        beta: float = 0.25
                    ):
                        self._type = type_check(type, None) if type is not None else None
                        self._gamma = range_check(type_check(gamma, float), 0, 1) if gamma is not None else None
                        self._beta = range_check(type_check(beta, float), 0, 0.5) if beta is not None else None

                    @property
                    def type(self):
                        return self._type

                    @type.setter
                    def type(self, value):
                        ''' 
                        There is no definition
                        '''
                        self._type = type_check(value, None) 

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
                    def beta(self):
                        return self._beta

                    @beta.setter
                    def beta(self, value):
                        ''' 
                        Newmark beta
                        '''
                        self._beta = range_check(type_check(value, float), 0, 0.5) 

                    def check_required(self):

                        if self.type is None:
                            print("Requiered variable Root.Time.Object2.Object3.Object2.type does not have value")
                        return

                    def as_dict(self):
                        return drop_none({"type": self._type,"gamma": self._gamma,"beta": self._beta,})




        class Object3(object):
            '''This is a polymorphic variable, assign an object from its classes to the value
            \nRequired: []
            \nOptional: ['object1', 'object2']'''
            def __init__(
                self,
                value : object = None
            ):
                self._value = class_check(value, [self.Object1, self.Object2]) if value is not None else None

            @property
            def value(self):
                return self._value

            @value.setter
            def value(self, value):
                ''' 
                This is a polymorphic variable, assign an object from its classes to the value
                '''
                self._value = class_check(value, [self.Object1, self.Object2]) 

            def check_required(self):

                if self.value is None:
                    print("Requiered variable Root.Time.Object3.value does not have value")
                else:
                    if type(self.value) not in [['int', 'float', 'list', 'str', 'bool']]:
                        self.value.check_required()
                return

            def as_dict(self):
                return drop_none(self._value.as_dict() if isinstance(self._value, tuple([self.Object1, self.Object2])) else self._value)

            class Object1(object):
                '''Backwards differentiation formula time integration
                \nRequired: ['type']
                \nOptional: ['steps']'''
                class Type(str, Enum):
                    IMPLICITEULER = 'ImplicitEuler'
                    BDF = 'BDF'
                    IMPLICITNEWMARK = 'ImplicitNewmark'

                def __init__(
                    self,
                    type: "Type" = None,
                    steps: int = 1
                ):
                    self._type = enum_check(type, self.Type)
                    self._steps = range_check(type_check(steps, int), 1, 6) if steps is not None else None

                @property
                def type(self):
                    return self._type

                @type.setter
                def type(self, value):
                    ''' 
                    Type of time integrator to use
                    '''
                    self._type = enum_check(value, self.Type) 

                @property
                def steps(self):
                    return self._steps

                @steps.setter
                def steps(self, value):
                    ''' 
                    BDF order
                    '''
                    self._steps = range_check(type_check(value, int), 1, 6) 

                def check_required(self):

                    if self.type is None:
                        print("Requiered variable Root.Time.Object3.Object1.type does not have value")
                    return

                def as_dict(self):
                    return drop_none({"type": self._type.value if self._type is not None else None,"steps": self._steps,})


            class Object2(object):
                '''Implicit Newmark time integration
                \nRequired: ['type']
                \nOptional: ['gamma', 'beta']'''
                def __init__(
                    self,
                    type: None = None,
                    gamma: float = 0.5,
                    beta: float = 0.25
                ):
                    self._type = type_check(type, None) if type is not None else None
                    self._gamma = range_check(type_check(gamma, float), 0, 1) if gamma is not None else None
                    self._beta = range_check(type_check(beta, float), 0, 0.5) if beta is not None else None

                @property
                def type(self):
                    return self._type

                @type.setter
                def type(self, value):
                    ''' 
                    There is no definition
                    '''
                    self._type = type_check(value, None) 

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
                def beta(self):
                    return self._beta

                @beta.setter
                def beta(self, value):
                    ''' 
                    Newmark beta
                    '''
                    self._beta = range_check(type_check(value, float), 0, 0.5) 

                def check_required(self):

                    if self.type is None:
                        print("Requiered variable Root.Time.Object3.Object2.type does not have value")
                    return

                def as_dict(self):
                    return drop_none({"type": self._type,"gamma": self._gamma,"beta": self._beta,})




    class Contact(object):
        '''Contact handling parameters.
        \nRequired: []
        \nOptional: ['enabled', 'dhat', 'dhat_percentage', 'epsv', 'friction_coefficient', 'use_convergent_formulation', 'use_area_weighting', 'use_improved_max_operator', 'use_physical_barrier', 'collision_mesh', 'use_gcp_formulation', 'alpha_n', 'alpha_t', 'min_distance_ratio', 'use_adaptive_dhat', 'periodic', 'adhesion']'''
        def __init__(
            self,
            enabled: bool = False,
            dhat: float = 0.001,
            dhat_percentage: float = 0.8,
            epsv: float = 0.001,
            friction_coefficient: float = 0.0,
            use_convergent_formulation: bool = False,
            use_area_weighting: bool = True,
            use_improved_max_operator: bool = True,
            use_physical_barrier: bool = True,
            collision_mesh: Optional["Root.Contact.Collision_mesh"] = None,
            use_gcp_formulation: bool = False,
            alpha_n: float = 0.5,
            alpha_t: float = 0.5,
            min_distance_ratio: float = 0.5,
            use_adaptive_dhat: bool = False,
            periodic: bool = False,
            adhesion: Optional["Root.Contact.Adhesion"] = None
        ):
            self._enabled = type_check(enabled, bool) if enabled is not None else None
            self._dhat = range_check(type_check(dhat, float), 0, None) if dhat is not None else None
            self._dhat_percentage = type_check(dhat_percentage, float) if dhat_percentage is not None else None
            self._epsv = range_check(type_check(epsv, float), 0, None) if epsv is not None else None
            self._friction_coefficient = type_check(friction_coefficient, float) if friction_coefficient is not None else None
            self._use_convergent_formulation = type_check(use_convergent_formulation, bool) if use_convergent_formulation is not None else None
            self._use_area_weighting = type_check(use_area_weighting, bool) if use_area_weighting is not None else None
            self._use_improved_max_operator = type_check(use_improved_max_operator, bool) if use_improved_max_operator is not None else None
            self._use_physical_barrier = type_check(use_physical_barrier, bool) if use_physical_barrier is not None else None
            self._collision_mesh = type_check(collision_mesh, self.Collision_mesh) if collision_mesh else self.Collision_mesh()
            self._use_gcp_formulation = type_check(use_gcp_formulation, bool) if use_gcp_formulation is not None else None
            self._alpha_n = range_check(type_check(alpha_n, float), -1, 1) if alpha_n is not None else None
            self._alpha_t = range_check(type_check(alpha_t, float), -1, 1) if alpha_t is not None else None
            self._min_distance_ratio = range_check(type_check(min_distance_ratio, float), 0, None) if min_distance_ratio is not None else None
            self._use_adaptive_dhat = type_check(use_adaptive_dhat, bool) if use_adaptive_dhat is not None else None
            self._periodic = type_check(periodic, bool) if periodic is not None else None
            self._adhesion = type_check(adhesion, self.Adhesion) if adhesion else self.Adhesion()

        @property
        def enabled(self):
            return self._enabled

        @enabled.setter
        def enabled(self, value):
            ''' 
            True if contact handling is enabled.
            '''
            self._enabled = type_check(value, bool) 

        @property
        def dhat(self):
            return self._dhat

        @dhat.setter
        def dhat(self, value):
            ''' 
            Contact barrier activation distance.
            '''
            self._dhat = range_check(type_check(value, float), 0, None) 

        @property
        def dhat_percentage(self):
            return self._dhat_percentage

        @dhat_percentage.setter
        def dhat_percentage(self, value):
            ''' 
            $\\hat{d}$ as percentage of the diagonal of the bounding box
            '''
            self._dhat_percentage = type_check(value, float) 

        @property
        def epsv(self):
            return self._epsv

        @epsv.setter
        def epsv(self, value):
            ''' 
            Friction smoothing parameter.
            '''
            self._epsv = range_check(type_check(value, float), 0, None) 

        @property
        def friction_coefficient(self):
            return self._friction_coefficient

        @friction_coefficient.setter
        def friction_coefficient(self, value):
            ''' 
            Coefficient of friction (global)
            '''
            self._friction_coefficient = type_check(value, float) 

        @property
        def use_convergent_formulation(self):
            return self._use_convergent_formulation

        @use_convergent_formulation.setter
        def use_convergent_formulation(self, value):
            ''' 
            Whether to use the convergent (area weighted) formulation of IPC.
            '''
            self._use_convergent_formulation = type_check(value, bool) 

        @property
        def use_area_weighting(self):
            return self._use_area_weighting

        @use_area_weighting.setter
        def use_area_weighting(self, value):
            ''' 
            If using the convergent formulation, whether or not to use area weighting. Currently not implemented.
            '''
            self._use_area_weighting = type_check(value, bool) 

        @property
        def use_improved_max_operator(self):
            return self._use_improved_max_operator

        @use_improved_max_operator.setter
        def use_improved_max_operator(self, value):
            ''' 
            If using the convergent formulation, whether or not to use improved max operator. Currently not implemented.
            '''
            self._use_improved_max_operator = type_check(value, bool) 

        @property
        def use_physical_barrier(self):
            return self._use_physical_barrier

        @use_physical_barrier.setter
        def use_physical_barrier(self, value):
            ''' 
            If using the convergent formulation, whether or not to use physical barrier stiffness. Currently not implemented.
            '''
            self._use_physical_barrier = type_check(value, bool) 

        @property
        def collision_mesh(self):
            return self._collision_mesh

        @collision_mesh.setter
        def collision_mesh(self, value):
            ''' 
            This is a polymorphic variable, assign an object from its classes to the value
            \nRequired: []
            \nOptional: ['object1', 'object2', 'object3']
            '''
            self._collision_mesh = type_check(value, self.Collision_mesh) 

        @property
        def use_gcp_formulation(self):
            return self._use_gcp_formulation

        @use_gcp_formulation.setter
        def use_gcp_formulation(self, value):
            ''' 
            True if the smooth contact formulation is used.
            '''
            self._use_gcp_formulation = type_check(value, bool) 

        @property
        def alpha_n(self):
            return self._alpha_n

        @alpha_n.setter
        def alpha_n(self, value):
            ''' 
            Control the smoothness of normal angle contraints of contact pairs.
            '''
            self._alpha_n = range_check(type_check(value, float), -1, 1) 

        @property
        def alpha_t(self):
            return self._alpha_t

        @alpha_t.setter
        def alpha_t(self, value):
            ''' 
            Control the smoothness of tangent angle contraints of contact pairs.
            '''
            self._alpha_t = range_check(type_check(value, float), -1, 1) 

        @property
        def min_distance_ratio(self):
            return self._min_distance_ratio

        @min_distance_ratio.setter
        def min_distance_ratio(self, value):
            ''' 
            Ratio of the minimum distance to contact to define local epsilon.
            '''
            self._min_distance_ratio = range_check(type_check(value, float), 0, None) 

        @property
        def use_adaptive_dhat(self):
            return self._use_adaptive_dhat

        @use_adaptive_dhat.setter
        def use_adaptive_dhat(self, value):
            ''' 
            True if adaptive epsilon is used.
            '''
            self._use_adaptive_dhat = type_check(value, bool) 

        @property
        def periodic(self):
            return self._periodic

        @periodic.setter
        def periodic(self, value):
            ''' 
            Set to true to check collision between adjacent periodic cells.
            '''
            self._periodic = type_check(value, bool) 

        @property
        def adhesion(self):
            return self._adhesion

        @adhesion.setter
        def adhesion(self, value):
            ''' 
            Adhesion settings.
            \nRequired: []
            \nOptional: ['adhesion_enabled', 'dhat_p', 'dhat_a', 'adhesion_strength', 'tangential_adhesion_coefficient', 'epsa']
            '''
            self._adhesion = type_check(value, self.Adhesion) 

        def check_required(self):

            return

        def as_dict(self):
            return drop_none({"enabled": self._enabled,"dhat": self._dhat,"dhat_percentage": self._dhat_percentage,"epsv": self._epsv,"friction_coefficient": self._friction_coefficient,"use_convergent_formulation": self._use_convergent_formulation,"use_area_weighting": self._use_area_weighting,"use_improved_max_operator": self._use_improved_max_operator,"use_physical_barrier": self._use_physical_barrier,"collision_mesh": self._collision_mesh.as_dict(),"use_gcp_formulation": self._use_gcp_formulation,"alpha_n": self._alpha_n,"alpha_t": self._alpha_t,"min_distance_ratio": self._min_distance_ratio,"use_adaptive_dhat": self._use_adaptive_dhat,"periodic": self._periodic,"adhesion": self._adhesion.as_dict(),})

        class Collision_mesh(object):
            '''This is a polymorphic variable, assign an object from its classes to the value
            \nRequired: []
            \nOptional: ['object1', 'object2', 'object3']'''
            def __init__(
                self,
                value : object = None
            ):
                self._value = class_check(value, [self.Object1, self.Object2, self.Object3]) if value is not None else None

            @property
            def value(self):
                return self._value

            @value.setter
            def value(self, value):
                ''' 
                This is a polymorphic variable, assign an object from its classes to the value
                '''
                self._value = class_check(value, [self.Object1, self.Object2, self.Object3]) 

            def check_required(self):

                if self.value is None:
                    print("Requiered variable Root.Contact.Collision_mesh.value does not have value")
                else:
                    if type(self.value) not in [['int', 'float', 'list', 'str', 'bool']]:
                        self.value.check_required()
                return

            def as_dict(self):
                return drop_none(self._value.as_dict() if isinstance(self._value, tuple([self.Object1, self.Object2, self.Object3])) else self._value)

            class Object1(object):
                '''Load a preconstructed collision mesh.
                \nRequired: ['mesh', 'linear_map']
                \nOptional: ['enabled']'''
                def __init__(
                    self,
                    mesh: str = None,
                    linear_map: str = None,
                    enabled: bool = True
                ):
                    self._mesh = type_check(mesh, str) if mesh is not None else None
                    self._linear_map = type_check(linear_map, str) if linear_map is not None else None
                    self._enabled = type_check(enabled, bool) if enabled is not None else None

                @property
                def mesh(self):
                    return self._mesh

                @mesh.setter
                def mesh(self, value):
                    ''' 
                    Path to preconstructed collision mesh.
                    '''
                    self._mesh = type_check(value, str) 

                @property
                def linear_map(self):
                    return self._linear_map

                @linear_map.setter
                def linear_map(self, value):
                    ''' 
                    HDF file storing the linear mapping of displacements.
                    '''
                    self._linear_map = type_check(value, str) 

                @property
                def enabled(self):
                    return self._enabled

                @enabled.setter
                def enabled(self, value):
                    ''' 
                    There is no definition
                    '''
                    self._enabled = type_check(value, bool) 

                def check_required(self):

                    if self.mesh is None:
                        print("Requiered variable Root.Contact.Collision_mesh.Object1.mesh does not have value")

                    if self.linear_map is None:
                        print("Requiered variable Root.Contact.Collision_mesh.Object1.linear_map does not have value")
                    return

                def as_dict(self):
                    return drop_none({"mesh": self._mesh,"linear_map": self._linear_map,"enabled": self._enabled,})


            class Object2(object):
                '''Construct a collision mesh with a maximum edge length.
                \nRequired: ['max_edge_length']
                \nOptional: ['tessellation_type', 'enabled']'''
                class Tessellation_type(str, Enum):
                    REGULAR = 'regular'
                    IRREGULAR = 'irregular'

                def __init__(
                    self,
                    max_edge_length: float = None,
                    tessellation_type: "Tessellation_type" = 'regular',
                    enabled: bool = True
                ):
                    self._max_edge_length = type_check(max_edge_length, float) if max_edge_length is not None else None
                    self._tessellation_type = enum_check(tessellation_type, self.Tessellation_type)
                    self._enabled = type_check(enabled, bool) if enabled is not None else None

                @property
                def max_edge_length(self):
                    return self._max_edge_length

                @max_edge_length.setter
                def max_edge_length(self, value):
                    ''' 
                    Maximum edge length to use for building the collision mesh.
                    '''
                    self._max_edge_length = type_check(value, float) 

                @property
                def tessellation_type(self):
                    return self._tessellation_type

                @tessellation_type.setter
                def tessellation_type(self, value):
                    ''' 
                    Type of tessellation to use for building the collision mesh.
                    '''
                    self._tessellation_type = enum_check(value, self.Tessellation_type) 

                @property
                def enabled(self):
                    return self._enabled

                @enabled.setter
                def enabled(self, value):
                    ''' 
                    There is no definition
                    '''
                    self._enabled = type_check(value, bool) 

                def check_required(self):

                    if self.max_edge_length is None:
                        print("Requiered variable Root.Contact.Collision_mesh.Object2.max_edge_length does not have value")
                    return

                def as_dict(self):
                    return drop_none({"max_edge_length": self._max_edge_length,"tessellation_type": self._tessellation_type.value if self._tessellation_type is not None else None,"enabled": self._enabled,})


            class Object3(object):
                '''Construct a collision mesh.
                \nRequired: []
                \nOptional: ['enabled']'''
                def __init__(
                    self,
                    enabled: bool = True
                ):
                    self._enabled = type_check(enabled, bool) if enabled is not None else None

                @property
                def enabled(self):
                    return self._enabled

                @enabled.setter
                def enabled(self, value):
                    ''' 
                    There is no definition
                    '''
                    self._enabled = type_check(value, bool) 

                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({"enabled": self._enabled,})



        class Adhesion(object):
            '''Adhesion settings.
            \nRequired: []
            \nOptional: ['adhesion_enabled', 'dhat_p', 'dhat_a', 'adhesion_strength', 'tangential_adhesion_coefficient', 'epsa']'''
            def __init__(
                self,
                adhesion_enabled: bool = False,
                dhat_p: float = 0.001,
                dhat_a: float = 0.01,
                adhesion_strength: float = 0.001,
                tangential_adhesion_coefficient: float = 0.0,
                epsa: float = 0.001
            ):
                self._adhesion_enabled = type_check(adhesion_enabled, bool) if adhesion_enabled is not None else None
                self._dhat_p = type_check(dhat_p, float) if dhat_p is not None else None
                self._dhat_a = type_check(dhat_a, float) if dhat_a is not None else None
                self._adhesion_strength = type_check(adhesion_strength, float) if adhesion_strength is not None else None
                self._tangential_adhesion_coefficient = type_check(tangential_adhesion_coefficient, float) if tangential_adhesion_coefficient is not None else None
                self._epsa = range_check(type_check(epsa, float), 0, None) if epsa is not None else None

            @property
            def adhesion_enabled(self):
                return self._adhesion_enabled

            @adhesion_enabled.setter
            def adhesion_enabled(self, value):
                ''' 
                Set to true to enable normal adhesion forces.
                '''
                self._adhesion_enabled = type_check(value, bool) 

            @property
            def dhat_p(self):
                return self._dhat_p

            @dhat_p.setter
            def dhat_p(self, value):
                ''' 
                Distance at which normal adhesion force reaches its maximum.
                '''
                self._dhat_p = type_check(value, float) 

            @property
            def dhat_a(self):
                return self._dhat_a

            @dhat_a.setter
            def dhat_a(self, value):
                ''' 
                Distance at which normal adhesion force is activated.
                '''
                self._dhat_a = type_check(value, float) 

            @property
            def adhesion_strength(self):
                return self._adhesion_strength

            @adhesion_strength.setter
            def adhesion_strength(self, value):
                ''' 
                Parameter that sets the strength of the normal adhesion force.
                '''
                self._adhesion_strength = type_check(value, float) 

            @property
            def tangential_adhesion_coefficient(self):
                return self._tangential_adhesion_coefficient

            @tangential_adhesion_coefficient.setter
            def tangential_adhesion_coefficient(self, value):
                ''' 
                Coefficient of tangential adhesion (global)
                '''
                self._tangential_adhesion_coefficient = type_check(value, float) 

            @property
            def epsa(self):
                return self._epsa

            @epsa.setter
            def epsa(self, value):
                ''' 
                Tangential adhesion smoothing parameter.
                '''
                self._epsa = range_check(type_check(value, float), 0, None) 

            def check_required(self):

                return

            def as_dict(self):
                return drop_none({"adhesion_enabled": self._adhesion_enabled,"dhat_p": self._dhat_p,"dhat_a": self._dhat_a,"adhesion_strength": self._adhesion_strength,"tangential_adhesion_coefficient": self._tangential_adhesion_coefficient,"epsa": self._epsa,})



    class Solver(object):
        '''The settings for the solver including linear solver, nonlinear solver, and some advanced options.
        \nRequired: []
        \nOptional: ['max_threads', 'linear', 'adjoint_linear', 'nonlinear', 'augmented_lagrangian', 'contact', 'rayleigh_damping', 'advanced']'''
        def __init__(
            self,
            max_threads: int = 0,
            linear: None = None,
            adjoint_linear: None = None,
            nonlinear: None = None,
            augmented_lagrangian: Optional["Root.Solver.Augmented_lagrangian"] = None,
            contact: Optional["Root.Solver.Contact"] = None,
            rayleigh_damping: Optional["Root.Solver.Rayleigh_damping"] = None,
            advanced: Optional["Root.Solver.Advanced"] = None
        ):
            self._max_threads = range_check(type_check(max_threads, int), 0, None) if max_threads is not None else None
            self._linear = type_check(linear, None) if linear is not None else None
            self._adjoint_linear = type_check(adjoint_linear, None) if adjoint_linear is not None else None
            self._nonlinear = type_check(nonlinear, None) if nonlinear is not None else None
            self._augmented_lagrangian = type_check(augmented_lagrangian, self.Augmented_lagrangian) if augmented_lagrangian else self.Augmented_lagrangian()
            self._contact = type_check(contact, self.Contact) if contact else self.Contact()
            self._rayleigh_damping = type_check(rayleigh_damping, self.Rayleigh_damping) if rayleigh_damping else self.Rayleigh_damping()
            self._advanced = type_check(advanced, self.Advanced) if advanced else self.Advanced()

        @property
        def max_threads(self):
            return self._max_threads

        @max_threads.setter
        def max_threads(self, value):
            ''' 
            Maximum number of threads used; 0 is unlimited.
            '''
            self._max_threads = range_check(type_check(value, int), 0, None) 

        @property
        def linear(self):
            return self._linear

        @linear.setter
        def linear(self, value):
            ''' 
            There is no definition
            '''
            self._linear = type_check(value, None) 

        @property
        def adjoint_linear(self):
            return self._adjoint_linear

        @adjoint_linear.setter
        def adjoint_linear(self, value):
            ''' 
            There is no definition
            '''
            self._adjoint_linear = type_check(value, None) 

        @property
        def nonlinear(self):
            return self._nonlinear

        @nonlinear.setter
        def nonlinear(self, value):
            ''' 
            There is no definition
            '''
            self._nonlinear = type_check(value, None) 

        @property
        def augmented_lagrangian(self):
            return self._augmented_lagrangian

        @augmented_lagrangian.setter
        def augmented_lagrangian(self, value):
            ''' 
            Parameters for the AL for imposing Dirichlet BCs. If the bc are not imposable, we add $w\\|u - bc\\|^2$ to the energy ($u$ is the solution at the Dirichlet nodes and $bc$ are the Dirichlet values). After convergence, we try to impose bc again. The algorithm computes E + a/2*AL^2 - lambda AL, where E is the current energy (elastic, inertia, contact, etc.) and AL is the augmented Lagrangian energy. a starts at `initial_weight` and, in case DBC cannot be imposed, we update a as `a *= scaling` until `max_weight`. See IPC additional material
            \nRequired: []
            \nOptional: ['initial_weight', 'scaling', 'max_weight', 'eta', 'nonlinear', 'error']
            '''
            self._augmented_lagrangian = type_check(value, self.Augmented_lagrangian) 

        @property
        def contact(self):
            return self._contact

        @contact.setter
        def contact(self, value):
            ''' 
            Settings for contact handling in the solver.
            \nRequired: []
            \nOptional: ['CCD', 'friction_iterations', 'tangential_adhesion_iterations', 'friction_convergence_tol', 'barrier_stiffness', 'initial_barrier_stiffness']
            '''
            self._contact = type_check(value, self.Contact) 

        @property
        def rayleigh_damping(self):
            return self._rayleigh_damping

        @rayleigh_damping.setter
        def rayleigh_damping(self, value):
            ''' 
            Apply Rayleigh damping.
            \nRequired: []
            \nOptional: ['value']
            '''
            self._rayleigh_damping = type_check(value, self.Rayleigh_damping) 

        @property
        def advanced(self):
            return self._advanced

        @advanced.setter
        def advanced(self, value):
            ''' 
            Advanced settings for the solver
            \nRequired: []
            \nOptional: ['cache_size', 'lump_mass_matrix', 'lagged_regularization_weight', 'lagged_regularization_iterations', 'check_inversion', 'jacobian_threshold', 'characteristic_length', 'characteristic_force_density']
            '''
            self._advanced = type_check(value, self.Advanced) 

        def check_required(self):

            return

        def as_dict(self):
            return drop_none({"max_threads": self._max_threads,"linear": self._linear,"adjoint_linear": self._adjoint_linear,"nonlinear": self._nonlinear,"augmented_lagrangian": self._augmented_lagrangian.as_dict(),"contact": self._contact.as_dict(),"rayleigh_damping": self._rayleigh_damping.as_dict(),"advanced": self._advanced.as_dict(),})

        class Augmented_lagrangian(object):
            '''Parameters for the AL for imposing Dirichlet BCs. If the bc are not imposable, we add $w\\|u - bc\\|^2$ to the energy ($u$ is the solution at the Dirichlet nodes and $bc$ are the Dirichlet values). After convergence, we try to impose bc again. The algorithm computes E + a/2*AL^2 - lambda AL, where E is the current energy (elastic, inertia, contact, etc.) and AL is the augmented Lagrangian energy. a starts at `initial_weight` and, in case DBC cannot be imposed, we update a as `a *= scaling` until `max_weight`. See IPC additional material
            \nRequired: []
            \nOptional: ['initial_weight', 'scaling', 'max_weight', 'eta', 'nonlinear', 'error']'''
            def __init__(
                self,
                initial_weight: float = 1000000.0,
                scaling: float = 2.0,
                max_weight: float = 100000000.0,
                eta: float = 0.99,
                nonlinear: Optional["Root.Solver.Augmented_lagrangian.Nonlinear"] = None,
                error: float = 0.01
            ):
                self._initial_weight = range_check(type_check(initial_weight, float), 0, None) if initial_weight is not None else None
                self._scaling = type_check(scaling, float) if scaling is not None else None
                self._max_weight = type_check(max_weight, float) if max_weight is not None else None
                self._eta = range_check(type_check(eta, float), 0, 1) if eta is not None else None
                self._nonlinear = type_check(nonlinear, self.Nonlinear) if nonlinear else self.Nonlinear()
                self._error = range_check(type_check(error, float), 0, None) if error is not None else None

            @property
            def initial_weight(self):
                return self._initial_weight

            @initial_weight.setter
            def initial_weight(self, value):
                ''' 
                Initial weight for AL
                '''
                self._initial_weight = range_check(type_check(value, float), 0, None) 

            @property
            def scaling(self):
                return self._scaling

            @scaling.setter
            def scaling(self, value):
                ''' 
                Multiplication factor
                '''
                self._scaling = type_check(value, float) 

            @property
            def max_weight(self):
                return self._max_weight

            @max_weight.setter
            def max_weight(self, value):
                ''' 
                Maximum weight
                '''
                self._max_weight = type_check(value, float) 

            @property
            def eta(self):
                return self._eta

            @eta.setter
            def eta(self, value):
                ''' 
                Tolerance for increasing the weight or updating the lagrangian
                '''
                self._eta = range_check(type_check(value, float), 0, 1) 

            @property
            def nonlinear(self):
                return self._nonlinear

            @nonlinear.setter
            def nonlinear(self, value):
                ''' 
                Settings for nonlinear solver in augmented lagrangian.
                \nRequired: []
                \nOptional: []
                '''
                self._nonlinear = type_check(value, self.Nonlinear) 

            @property
            def error(self):
                return self._error

            @error.setter
            def error(self, value):
                ''' 
                Don't stop AL unless the error is smaller than this number.
                '''
                self._error = range_check(type_check(value, float), 0, None) 

            def check_required(self):

                return

            def as_dict(self):
                return drop_none({"initial_weight": self._initial_weight,"scaling": self._scaling,"max_weight": self._max_weight,"eta": self._eta,"nonlinear": self._nonlinear.as_dict(),"error": self._error,})

            class Nonlinear(object):
                '''Settings for nonlinear solver in augmented lagrangian.
                \nRequired: []
                \nOptional: []'''
                def __init__(
                    self,

                ):
                    pass


                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({})



        class Contact(object):
            '''Settings for contact handling in the solver.
            \nRequired: []
            \nOptional: ['CCD', 'friction_iterations', 'tangential_adhesion_iterations', 'friction_convergence_tol', 'barrier_stiffness', 'initial_barrier_stiffness']'''
            def __init__(
                self,
                CCD: Optional["Root.Solver.Contact.Ccd"] = None,
                friction_iterations: int = 1,
                tangential_adhesion_iterations: int = 1,
                friction_convergence_tol: float = 0.01,
                barrier_stiffness: Optional["Root.Solver.Contact.Barrier_stiffness"] = None,
                initial_barrier_stiffness: float = 1.0
            ):
                self._CCD = type_check(CCD, self.Ccd) if CCD else self.Ccd()
                self._friction_iterations = type_check(friction_iterations, int) if friction_iterations is not None else None
                self._tangential_adhesion_iterations = type_check(tangential_adhesion_iterations, int) if tangential_adhesion_iterations is not None else None
                self._friction_convergence_tol = type_check(friction_convergence_tol, float) if friction_convergence_tol is not None else None
                self._barrier_stiffness = type_check(barrier_stiffness, self.Barrier_stiffness) if barrier_stiffness else self.Barrier_stiffness()
                self._initial_barrier_stiffness = type_check(initial_barrier_stiffness, float) if initial_barrier_stiffness is not None else None

            @property
            def CCD(self):
                return self._CCD

            @CCD.setter
            def CCD(self, value):
                ''' 
                CCD options
                \nRequired: []
                \nOptional: ['broad_phase', 'tolerance', 'max_iterations']
                '''
                self._CCD = type_check(value, self.Ccd) 

            @property
            def friction_iterations(self):
                return self._friction_iterations

            @friction_iterations.setter
            def friction_iterations(self, value):
                ''' 
                Maximum number of update iterations for lagged friction formulation (see IPC paper).
                '''
                self._friction_iterations = type_check(value, int) 

            @property
            def tangential_adhesion_iterations(self):
                return self._tangential_adhesion_iterations

            @tangential_adhesion_iterations.setter
            def tangential_adhesion_iterations(self, value):
                ''' 
                Maximum number of update iterations for lagged tangential adhesion formulation (see IPC paper).
                '''
                self._tangential_adhesion_iterations = type_check(value, int) 

            @property
            def friction_convergence_tol(self):
                return self._friction_convergence_tol

            @friction_convergence_tol.setter
            def friction_convergence_tol(self, value):
                ''' 
                Tolerence for friction convergence
                '''
                self._friction_convergence_tol = type_check(value, float) 

            @property
            def barrier_stiffness(self):
                return self._barrier_stiffness

            @barrier_stiffness.setter
            def barrier_stiffness(self, value):
                ''' 
                This is a polymorphic variable, assign an object from its classes to the value
                \nRequired: []
                \nOptional: ['string', 'float']
                '''
                self._barrier_stiffness = type_check(value, self.Barrier_stiffness) 

            @property
            def initial_barrier_stiffness(self):
                return self._initial_barrier_stiffness

            @initial_barrier_stiffness.setter
            def initial_barrier_stiffness(self, value):
                ''' 
                Initial barrier stiffness if adaptive barrier is used.
                '''
                self._initial_barrier_stiffness = type_check(value, float) 

            def check_required(self):

                return

            def as_dict(self):
                return drop_none({"CCD": self._CCD.as_dict(),"friction_iterations": self._friction_iterations,"tangential_adhesion_iterations": self._tangential_adhesion_iterations,"friction_convergence_tol": self._friction_convergence_tol,"barrier_stiffness": self._barrier_stiffness.as_dict(),"initial_barrier_stiffness": self._initial_barrier_stiffness,})

            class Ccd(object):
                '''CCD options
                \nRequired: []
                \nOptional: ['broad_phase', 'tolerance', 'max_iterations']'''
                class Broad_phase(str, Enum):
                    HASH_GRID = 'hash_grid'
                    HG = 'HG'
                    BRUTE_FORCE = 'brute_force'
                    BF = 'BF'
                    SPATIAL_HASH = 'spatial_hash'
                    SH = 'SH'
                    BVH = 'bvh'
                    BVH_2 = 'BVH'
                    SWEEP_AND_PRUNE = 'sweep_and_prune'
                    SAP = 'SAP'
                    SWEEP_AND_TINIEST_QUEUE = 'sweep_and_tiniest_queue'
                    STQ = 'STQ'

                def __init__(
                    self,
                    broad_phase: "Broad_phase" = 'hash_grid',
                    tolerance: float = 1e-06,
                    max_iterations: int = 1000000
                ):
                    self._broad_phase = enum_check(broad_phase, self.Broad_phase)
                    self._tolerance = type_check(tolerance, float) if tolerance is not None else None
                    self._max_iterations = type_check(max_iterations, int) if max_iterations is not None else None

                @property
                def broad_phase(self):
                    return self._broad_phase

                @broad_phase.setter
                def broad_phase(self, value):
                    ''' 
                    Broad phase collision-detection algorithm to use
                    '''
                    self._broad_phase = enum_check(value, self.Broad_phase) 

                @property
                def tolerance(self):
                    return self._tolerance

                @tolerance.setter
                def tolerance(self, value):
                    ''' 
                    CCD tolerance
                    '''
                    self._tolerance = type_check(value, float) 

                @property
                def max_iterations(self):
                    return self._max_iterations

                @max_iterations.setter
                def max_iterations(self, value):
                    ''' 
                    Maximum number of iterations for continuous collision detection
                    '''
                    self._max_iterations = type_check(value, int) 

                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({"broad_phase": self._broad_phase.value if self._broad_phase is not None else None,"tolerance": self._tolerance,"max_iterations": self._max_iterations,})


            class Barrier_stiffness(object):
                '''This is a polymorphic variable, assign an object from its classes to the value
                \nRequired: []
                \nOptional: ['string', 'float']'''
                def __init__(
                    self,
                    value : object = None
                ):
                    self._value = class_check(value, [string, float]) if value is not None else None

                @property
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    ''' 
                    This is a polymorphic variable, assign an object from its classes to the value
                    '''
                    self._value = class_check(value, [string, float]) 

                def check_required(self):

                    if self.value is None:
                        print("Requiered variable Root.Solver.Contact.Barrier_stiffness.value does not have value")
                    else:
                        if type(self.value) not in [['int', 'float', 'list', 'str', 'bool']]:
                            self.value.check_required()
                    return

                def as_dict(self):
                    return drop_none(self._value.as_dict() if isinstance(self._value, tuple([])) else self._value)



        class Rayleigh_damping(object):
            '''Apply Rayleigh damping.
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
                    print("Requiered variable Root.Solver.Rayleigh_damping.items does not have value")
                return

            def as_dict(self):
                return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

            class Value(object):
                '''Apply Rayleigh damping to the given Form with a stiffness.
                \nRequired: ['form', 'stiffness']
                \nOptional: ['lagging_iterations', 'stiffness_ratio']'''
                class Form(str, Enum):
                    ELASTICITY = 'elasticity'
                    CONTACT = 'contact'
                    FRICTION = 'friction'

                def __init__(
                    self,
                    form: "Form" = None,
                    stiffness: float = None,
                    lagging_iterations: int = 1,
                    stiffness_ratio: float = None
                ):
                    self._form = enum_check(form, self.Form)
                    self._stiffness = range_check(type_check(stiffness, float), 0, None) if stiffness is not None else None
                    self._lagging_iterations = type_check(lagging_iterations, int) if lagging_iterations is not None else None
                    self._stiffness_ratio = range_check(type_check(stiffness_ratio, float), 0, None) if stiffness_ratio is not None else None

                @property
                def form(self):
                    return self._form

                @form.setter
                def form(self, value):
                    ''' 
                    Form to damp.
                    '''
                    self._form = enum_check(value, self.Form) 

                @property
                def stiffness(self):
                    return self._stiffness

                @stiffness.setter
                def stiffness(self, value):
                    ''' 
                    Ratio of to damp.
                    '''
                    self._stiffness = range_check(type_check(value, float), 0, None) 

                @property
                def lagging_iterations(self):
                    return self._lagging_iterations

                @lagging_iterations.setter
                def lagging_iterations(self, value):
                    ''' 
                    Maximum number of update iterations for lagging.
                    '''
                    self._lagging_iterations = type_check(value, int) 

                @property
                def stiffness_ratio(self):
                    return self._stiffness_ratio

                @stiffness_ratio.setter
                def stiffness_ratio(self, value):
                    ''' 
                    Ratio of to damp (stiffness = 0.75 * stiffness_ratio * Δt³).
                    '''
                    self._stiffness_ratio = range_check(type_check(value, float), 0, None) 

                def check_required(self):

                    if self.form is None:
                        print("Requiered variable Root.Solver.Rayleigh_damping.Value.form does not have value")

                    if self.stiffness is None:
                        print("Requiered variable Root.Solver.Rayleigh_damping.Value.stiffness does not have value")
                    return

                def as_dict(self):
                    return drop_none({"form": self._form.value if self._form is not None else None,"stiffness": self._stiffness,"lagging_iterations": self._lagging_iterations,"stiffness_ratio": self._stiffness_ratio,})



        class Advanced(object):
            '''Advanced settings for the solver
            \nRequired: []
            \nOptional: ['cache_size', 'lump_mass_matrix', 'lagged_regularization_weight', 'lagged_regularization_iterations', 'check_inversion', 'jacobian_threshold', 'characteristic_length', 'characteristic_force_density']'''
            class Check_inversion(str, Enum):
                DISCRETE = 'Discrete'
                CONSERVATIVE = 'Conservative'

            def __init__(
                self,
                cache_size: int = 900000,
                lump_mass_matrix: bool = False,
                lagged_regularization_weight: float = 0.0,
                lagged_regularization_iterations: int = 1,
                check_inversion: "Check_inversion" = 'Discrete',
                jacobian_threshold: float = 0.0,
                characteristic_length: float = -1.0,
                characteristic_force_density: float = 10000.0
            ):
                self._cache_size = type_check(cache_size, int) if cache_size is not None else None
                self._lump_mass_matrix = type_check(lump_mass_matrix, bool) if lump_mass_matrix is not None else None
                self._lagged_regularization_weight = type_check(lagged_regularization_weight, float) if lagged_regularization_weight is not None else None
                self._lagged_regularization_iterations = type_check(lagged_regularization_iterations, int) if lagged_regularization_iterations is not None else None
                self._check_inversion = enum_check(check_inversion, self.Check_inversion)
                self._jacobian_threshold = type_check(jacobian_threshold, float) if jacobian_threshold is not None else None
                self._characteristic_length = type_check(characteristic_length, float) if characteristic_length is not None else None
                self._characteristic_force_density = type_check(characteristic_force_density, float) if characteristic_force_density is not None else None

            @property
            def cache_size(self):
                return self._cache_size

            @cache_size.setter
            def cache_size(self, value):
                ''' 
                Maximum number of elements when the assembly values are cached.
                '''
                self._cache_size = type_check(value, int) 

            @property
            def lump_mass_matrix(self):
                return self._lump_mass_matrix

            @lump_mass_matrix.setter
            def lump_mass_matrix(self, value):
                ''' 
                If true, use diagonal mass matrix with entries on the diagonal equal to the sum of entries in each row of the full mass matrix.}
                '''
                self._lump_mass_matrix = type_check(value, bool) 

            @property
            def lagged_regularization_weight(self):
                return self._lagged_regularization_weight

            @lagged_regularization_weight.setter
            def lagged_regularization_weight(self, value):
                ''' 
                Weight used to regularize singular static problems.
                '''
                self._lagged_regularization_weight = type_check(value, float) 

            @property
            def lagged_regularization_iterations(self):
                return self._lagged_regularization_iterations

            @lagged_regularization_iterations.setter
            def lagged_regularization_iterations(self, value):
                ''' 
                Number of regularize singular static problems.
                '''
                self._lagged_regularization_iterations = type_check(value, int) 

            @property
            def check_inversion(self):
                return self._check_inversion

            @check_inversion.setter
            def check_inversion(self, value):
                ''' 
                The method for checking if any element is flipped.
                '''
                self._check_inversion = enum_check(value, self.Check_inversion) 

            @property
            def jacobian_threshold(self):
                return self._jacobian_threshold

            @jacobian_threshold.setter
            def jacobian_threshold(self, value):
                ''' 
                .
                '''
                self._jacobian_threshold = type_check(value, float) 

            @property
            def characteristic_length(self):
                return self._characteristic_length

            @characteristic_length.setter
            def characteristic_length(self, value):
                ''' 
                Characteristic length, used for tolerances. Defaults to bounding box diagonal if not specified.
                '''
                self._characteristic_length = type_check(value, float) 

            @property
            def characteristic_force_density(self):
                return self._characteristic_force_density

            @characteristic_force_density.setter
            def characteristic_force_density(self, value):
                ''' 
                Characteristic force density, used for tolerances.
                '''
                self._characteristic_force_density = type_check(value, float) 

            def check_required(self):

                return

            def as_dict(self):
                return drop_none({"cache_size": self._cache_size,"lump_mass_matrix": self._lump_mass_matrix,"lagged_regularization_weight": self._lagged_regularization_weight,"lagged_regularization_iterations": self._lagged_regularization_iterations,"check_inversion": self._check_inversion.value if self._check_inversion is not None else None,"jacobian_threshold": self._jacobian_threshold,"characteristic_length": self._characteristic_length,"characteristic_force_density": self._characteristic_force_density,})



    class Boundary_conditions(object):
        '''The settings for boundary conditions.
        \nRequired: []
        \nOptional: ['rhs', 'dirichlet_boundary', 'neumann_boundary', 'normal_aligned_neumann_boundary', 'pressure_boundary', 'pressure_cavity', 'obstacle_displacements', 'periodic_boundary']'''
        def __init__(
            self,
            rhs: Optional["Root.Boundary_conditions.Rhs"] = None,
            dirichlet_boundary: Optional["Root.Boundary_conditions.Dirichlet_boundary"] = None,
            neumann_boundary: Optional["Root.Boundary_conditions.Neumann_boundary"] = None,
            normal_aligned_neumann_boundary: Optional["Root.Boundary_conditions.Normal_aligned_neumann_boundary"] = None,
            pressure_boundary: Optional["Root.Boundary_conditions.Pressure_boundary"] = None,
            pressure_cavity: Optional["Root.Boundary_conditions.Pressure_cavity"] = None,
            obstacle_displacements: Optional["Root.Boundary_conditions.Obstacle_displacements"] = None,
            periodic_boundary: Optional["Root.Boundary_conditions.Periodic_boundary"] = None
        ):
            self._rhs = type_check(rhs, self.Rhs) if rhs else self.Rhs()
            self._dirichlet_boundary = type_check(dirichlet_boundary, self.Dirichlet_boundary) if dirichlet_boundary else self.Dirichlet_boundary()
            self._neumann_boundary = type_check(neumann_boundary, self.Neumann_boundary) if neumann_boundary else self.Neumann_boundary()
            self._normal_aligned_neumann_boundary = type_check(normal_aligned_neumann_boundary, self.Normal_aligned_neumann_boundary) if normal_aligned_neumann_boundary else self.Normal_aligned_neumann_boundary()
            self._pressure_boundary = type_check(pressure_boundary, self.Pressure_boundary) if pressure_boundary else self.Pressure_boundary()
            self._pressure_cavity = type_check(pressure_cavity, self.Pressure_cavity) if pressure_cavity else self.Pressure_cavity()
            self._obstacle_displacements = type_check(obstacle_displacements, self.Obstacle_displacements) if obstacle_displacements else self.Obstacle_displacements()
            self._periodic_boundary = type_check(periodic_boundary, self.Periodic_boundary) if periodic_boundary else self.Periodic_boundary()

        @property
        def rhs(self):
            return self._rhs

        @rhs.setter
        def rhs(self, value):
            ''' 
            Right-hand side of the system being solved for vector-valued PDEs.
            \nRequired: []
            \nOptional: ['value']
            '''
            self._rhs = type_check(value, self.Rhs) 

        @property
        def dirichlet_boundary(self):
            return self._dirichlet_boundary

        @dirichlet_boundary.setter
        def dirichlet_boundary(self, value):
            ''' 
            This is a polymorphic variable, assign an object from its classes to the value
            \nRequired: []
            \nOptional: ['object1', 'object2', 'string']
            '''
            self._dirichlet_boundary = type_check(value, self.Dirichlet_boundary) 

        @property
        def neumann_boundary(self):
            return self._neumann_boundary

        @neumann_boundary.setter
        def neumann_boundary(self, value):
            ''' 
            This is a polymorphic variable, assign an object from its classes to the value
            \nRequired: []
            \nOptional: ['object1', 'object2']
            '''
            self._neumann_boundary = type_check(value, self.Neumann_boundary) 

        @property
        def normal_aligned_neumann_boundary(self):
            return self._normal_aligned_neumann_boundary

        @normal_aligned_neumann_boundary.setter
        def normal_aligned_neumann_boundary(self, value):
            ''' 
            Neumann boundary condition for normal times value for vector-valued PDEs.
            \nRequired: []
            \nOptional: ['value']
            '''
            self._normal_aligned_neumann_boundary = type_check(value, self.Normal_aligned_neumann_boundary) 

        @property
        def pressure_boundary(self):
            return self._pressure_boundary

        @pressure_boundary.setter
        def pressure_boundary(self, value):
            ''' 
            Neumann boundary condition for normal times value for vector-valued PDEs.
            \nRequired: []
            \nOptional: ['value']
            '''
            self._pressure_boundary = type_check(value, self.Pressure_boundary) 

        @property
        def pressure_cavity(self):
            return self._pressure_cavity

        @pressure_cavity.setter
        def pressure_cavity(self, value):
            ''' 
            Neumann boundary condition for normal times value for vector-valued PDEs.
            \nRequired: []
            \nOptional: ['value']
            '''
            self._pressure_cavity = type_check(value, self.Pressure_cavity) 

        @property
        def obstacle_displacements(self):
            return self._obstacle_displacements

        @obstacle_displacements.setter
        def obstacle_displacements(self, value):
            ''' 
            This is a polymorphic variable, assign an object from its classes to the value
            \nRequired: []
            \nOptional: ['object1', 'object2']
            '''
            self._obstacle_displacements = type_check(value, self.Obstacle_displacements) 

        @property
        def periodic_boundary(self):
            return self._periodic_boundary

        @periodic_boundary.setter
        def periodic_boundary(self, value):
            ''' 
            Options for periodic boundary conditions.
            \nRequired: []
            \nOptional: ['enabled', 'tolerance', 'correspondence', 'linear_displacement_offset', 'fixed_macro_strain', 'force_zero_mean']
            '''
            self._periodic_boundary = type_check(value, self.Periodic_boundary) 

        def check_required(self):

            return

        def as_dict(self):
            return drop_none({"rhs": self._rhs.as_dict(),"dirichlet_boundary": self._dirichlet_boundary.as_dict(),"neumann_boundary": self._neumann_boundary.as_dict(),"normal_aligned_neumann_boundary": self._normal_aligned_neumann_boundary.as_dict(),"pressure_boundary": self._pressure_boundary.as_dict(),"pressure_cavity": self._pressure_cavity.as_dict(),"obstacle_displacements": self._obstacle_displacements.as_dict(),"periodic_boundary": self._periodic_boundary.as_dict(),})

        class Rhs(object):
            '''Right-hand side of the system being solved for vector-valued PDEs.
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
                    print("Requiered variable Root.Boundary_conditions.Rhs.items does not have value")
                return

            def as_dict(self):
                return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

            class Value(object):
                '''Right-hand side of the system being solved, value.
                \nRequired: []
                \nOptional: []'''
                def __init__(
                    self,

                ):
                    pass


                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({})



        class Dirichlet_boundary(object):
            '''This is a polymorphic variable, assign an object from its classes to the value
            \nRequired: []
            \nOptional: ['object1', 'object2', 'string']'''
            def __init__(
                self,
                value : object = None
            ):
                self._value = class_check(value, [self.Object1, self.Object2, string]) if value is not None else None

            @property
            def value(self):
                return self._value

            @value.setter
            def value(self, value):
                ''' 
                This is a polymorphic variable, assign an object from its classes to the value
                '''
                self._value = class_check(value, [self.Object1, self.Object2, string]) 

            def check_required(self):

                if self.value is None:
                    print("Requiered variable Root.Boundary_conditions.Dirichlet_boundary.value does not have value")
                else:
                    if type(self.value) not in [['int', 'float', 'list', 'str', 'bool']]:
                        self.value.check_required()
                return

            def as_dict(self):
                return drop_none(self._value.as_dict() if isinstance(self._value, tuple([self.Object1, self.Object2])) else self._value)

            class Object1(object):
                '''Dirichlet boundary conditions.
                \nRequired: []
                \nOptional: []'''
                def __init__(
                    self,

                ):
                    pass


                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({})


            class Object2(object):
                '''Dirichlet boundary condition.
                \nRequired: ['id', 'value']
                \nOptional: ['time_reference', 'interpolation', 'dimension']'''
                def __init__(
                    self,
                    id: None = None,
                    value: Optional["Root.Boundary_conditions.Dirichlet_boundary.Object2.Value"] = None,
                    time_reference: Optional[Iterable[float]] = None,
                    interpolation: None = None,
                    dimension: Optional[Iterable[bool]] = None
                ):
                    self._id = type_check(id, None) if id is not None else None
                    self._value = type_check(value, self.Value) if value else self.Value()
                    self._time_reference = [] if time_reference is None else [type_check(i, float) for i in time_reference]
                    self._interpolation = type_check(interpolation, None) if interpolation is not None else None
                    self._dimension = [] if dimension is None else [type_check(i, bool) for i in dimension]

                @property
                def id(self):
                    return self._id

                @id.setter
                def id(self, value):
                    ''' 
                    There is no definition
                    '''
                    self._id = type_check(value, None) 

                @property
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    ''' 
                    Dirichlet boundary condition specified per timestep.
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._value = type_check(value, self.Value) 

                @property
                def time_reference(self):
                    return self._time_reference

                @time_reference.setter
                def time_reference(self, value):
                    ''' 
                    List of times when the Dirichlet boundary condition is specified
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._time_reference = [type_check(i, float) for i in (type_check(value, list) if value else [])]

                def time_reference_add(self, value):
                    '''Add to list '''
                    self._time_reference.append(type_check(value, float))

                def time_reference_clear(self):
                    '''Clear list (make empty)'''
                    self._time_reference.clear()

                def time_reference_pop(self, index=-1):
                    '''Remove by index from list'''
                    return self._time_reference.pop(index)

                def time_reference_remove(self, item):
                    '''Safe remove specific item from list'''
                    if item in self._list:
                        self._time_reference.remove(item)


                @property
                def interpolation(self):
                    return self._interpolation

                @interpolation.setter
                def interpolation(self, value):
                    ''' 
                    There is no definition
                    '''
                    self._interpolation = type_check(value, None) 

                @property
                def dimension(self):
                    return self._dimension

                @dimension.setter
                def dimension(self, value):
                    ''' 
                    List of 2 (2D) or 3 (3D) boolean values indicating if the Dirichlet boundary condition  is applied for a particular dimension.
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._dimension = [type_check(i, bool) for i in (type_check(value, list) if value else [])]

                def dimension_add(self, value):
                    '''Add to list '''
                    self._dimension.append(type_check(value, bool))

                def dimension_clear(self):
                    '''Clear list (make empty)'''
                    self._dimension.clear()

                def dimension_pop(self, index=-1):
                    '''Remove by index from list'''
                    return self._dimension.pop(index)

                def dimension_remove(self, item):
                    '''Safe remove specific item from list'''
                    if item in self._list:
                        self._dimension.remove(item)


                def check_required(self):

                    if self.id is None:
                        print("Requiered variable Root.Boundary_conditions.Dirichlet_boundary.Object2.id does not have value")
                    self.value.check_required()
                    return

                def as_dict(self):
                    return drop_none({"id": self._id,"value": self._value.as_dict(),"time_reference": self._time_reference,"interpolation": self._interpolation,"dimension": self._dimension,})

                class Value(object):
                    '''Dirichlet boundary condition specified per timestep.
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
                            print("Requiered variable Root.Boundary_conditions.Dirichlet_boundary.Object2.Value.items does not have value")
                        return

                    def as_dict(self):
                        return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

                    class Value(object):
                        '''Dirichlet boundary condition specified per timestep.
                        \nRequired: []
                        \nOptional: []'''
                        def __init__(
                            self,

                        ):
                            pass


                        def check_required(self):

                            return

                        def as_dict(self):
                            return drop_none({})





        class Neumann_boundary(object):
            '''This is a polymorphic variable, assign an object from its classes to the value
            \nRequired: []
            \nOptional: ['object1', 'object2']'''
            def __init__(
                self,
                value : object = None
            ):
                self._value = class_check(value, [self.Object1, self.Object2]) if value is not None else None

            @property
            def value(self):
                return self._value

            @value.setter
            def value(self, value):
                ''' 
                This is a polymorphic variable, assign an object from its classes to the value
                '''
                self._value = class_check(value, [self.Object1, self.Object2]) 

            def check_required(self):

                if self.value is None:
                    print("Requiered variable Root.Boundary_conditions.Neumann_boundary.value does not have value")
                else:
                    if type(self.value) not in [['int', 'float', 'list', 'str', 'bool']]:
                        self.value.check_required()
                return

            def as_dict(self):
                return drop_none(self._value.as_dict() if isinstance(self._value, tuple([self.Object1, self.Object2])) else self._value)

            class Object1(object):
                '''Neumann boundary conditions.
                \nRequired: []
                \nOptional: []'''
                def __init__(
                    self,

                ):
                    pass


                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({})


            class Object2(object):
                '''Neumann boundary condition
                \nRequired: ['id', 'value']
                \nOptional: ['interpolation']'''
                def __init__(
                    self,
                    id: None = None,
                    value: None = None,
                    interpolation: None = None
                ):
                    self._id = type_check(id, None) if id is not None else None
                    self._value = type_check(value, None) if value is not None else None
                    self._interpolation = type_check(interpolation, None) if interpolation is not None else None

                @property
                def id(self):
                    return self._id

                @id.setter
                def id(self, value):
                    ''' 
                    There is no definition
                    '''
                    self._id = type_check(value, None) 

                @property
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    ''' 
                    There is no definition
                    '''
                    self._value = type_check(value, None) 

                @property
                def interpolation(self):
                    return self._interpolation

                @interpolation.setter
                def interpolation(self, value):
                    ''' 
                    There is no definition
                    '''
                    self._interpolation = type_check(value, None) 

                def check_required(self):

                    if self.id is None:
                        print("Requiered variable Root.Boundary_conditions.Neumann_boundary.Object2.id does not have value")

                    if self.value is None:
                        print("Requiered variable Root.Boundary_conditions.Neumann_boundary.Object2.value does not have value")
                    return

                def as_dict(self):
                    return drop_none({"id": self._id,"value": self._value,"interpolation": self._interpolation,})



        class Normal_aligned_neumann_boundary(object):
            '''Neumann boundary condition for normal times value for vector-valued PDEs.
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
                    print("Requiered variable Root.Boundary_conditions.Normal_aligned_neumann_boundary.items does not have value")
                return

            def as_dict(self):
                return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

            class Value(object):
                '''pressure BC entry
                \nRequired: ['id', 'value']
                \nOptional: ['interpolation']'''
                def __init__(
                    self,
                    id: int = None,
                    value: Optional["Root.Boundary_conditions.Normal_aligned_neumann_boundary.Value.Value"] = None,
                    interpolation: Optional["Root.Boundary_conditions.Normal_aligned_neumann_boundary.Value.Interpolation"] = None
                ):
                    self._id = range_check(type_check(id, int), 0, 2147483646) if id is not None else None
                    self._value = type_check(value, self.Value) if value else self.Value()
                    self._interpolation = type_check(interpolation, self.Interpolation) if interpolation else self.Interpolation()

                @property
                def id(self):
                    return self._id

                @id.setter
                def id(self, value):
                    ''' 
                    ID for the pressure Neumann boundary condition
                    '''
                    self._id = range_check(type_check(value, int), 0, 2147483646) 

                @property
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    ''' 
                    Values of pressure boundary condition as a function of $x,y,z,t$
                    \nRequired: []
                    \nOptional: []
                    '''
                    self._value = type_check(value, self.Value) 

                @property
                def interpolation(self):
                    return self._interpolation

                @interpolation.setter
                def interpolation(self, value):
                    ''' 
                    interpolation of boundary condition
                    \nRequired: []
                    \nOptional: []
                    '''
                    self._interpolation = type_check(value, self.Interpolation) 

                def check_required(self):

                    if self.id is None:
                        print("Requiered variable Root.Boundary_conditions.Normal_aligned_neumann_boundary.Value.id does not have value")
                    self.value.check_required()
                    return

                def as_dict(self):
                    return drop_none({"id": self._id,"value": self._value.as_dict(),"interpolation": self._interpolation.as_dict(),})

                class Value(object):
                    '''Values of pressure boundary condition as a function of $x,y,z,t$
                    \nRequired: []
                    \nOptional: []'''
                    def __init__(
                        self,

                    ):
                        pass


                    def check_required(self):

                        return

                    def as_dict(self):
                        return drop_none({})


                class Interpolation(object):
                    '''interpolation of boundary condition
                    \nRequired: []
                    \nOptional: []'''
                    def __init__(
                        self,

                    ):
                        pass


                    def check_required(self):

                        return

                    def as_dict(self):
                        return drop_none({})




        class Pressure_boundary(object):
            '''Neumann boundary condition for normal times value for vector-valued PDEs.
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
                    print("Requiered variable Root.Boundary_conditions.Pressure_boundary.items does not have value")
                return

            def as_dict(self):
                return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

            class Value(object):
                '''pressure BC entry
                \nRequired: ['id', 'value']
                \nOptional: ['time_reference']'''
                def __init__(
                    self,
                    id: int = None,
                    value: Optional["Root.Boundary_conditions.Pressure_boundary.Value.Value"] = None,
                    time_reference: Optional[Iterable[float]] = None
                ):
                    self._id = range_check(type_check(id, int), 0, 2147483646) if id is not None else None
                    self._value = type_check(value, self.Value) if value else self.Value()
                    self._time_reference = [] if time_reference is None else [type_check(i, float) for i in time_reference]

                @property
                def id(self):
                    return self._id

                @id.setter
                def id(self, value):
                    ''' 
                    ID for the pressure Neumann boundary condition
                    '''
                    self._id = range_check(type_check(value, int), 0, 2147483646) 

                @property
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    ''' 
                    Values of pressure boundary condition specified per timestep
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._value = type_check(value, self.Value) 

                @property
                def time_reference(self):
                    return self._time_reference

                @time_reference.setter
                def time_reference(self, value):
                    ''' 
                    List of times when the pressure boundary condition is specified
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._time_reference = [type_check(i, float) for i in (type_check(value, list) if value else [])]

                def time_reference_add(self, value):
                    '''Add to list '''
                    self._time_reference.append(type_check(value, float))

                def time_reference_clear(self):
                    '''Clear list (make empty)'''
                    self._time_reference.clear()

                def time_reference_pop(self, index=-1):
                    '''Remove by index from list'''
                    return self._time_reference.pop(index)

                def time_reference_remove(self, item):
                    '''Safe remove specific item from list'''
                    if item in self._list:
                        self._time_reference.remove(item)


                def check_required(self):

                    if self.id is None:
                        print("Requiered variable Root.Boundary_conditions.Pressure_boundary.Value.id does not have value")
                    self.value.check_required()
                    return

                def as_dict(self):
                    return drop_none({"id": self._id,"value": self._value.as_dict(),"time_reference": self._time_reference,})

                class Value(object):
                    '''Values of pressure boundary condition specified per timestep
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
                            print("Requiered variable Root.Boundary_conditions.Pressure_boundary.Value.Value.items does not have value")
                        return

                    def as_dict(self):
                        return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

                    class Value(object):
                        '''Values of pressure boundary condition specified per timestep
                        \nRequired: []
                        \nOptional: []'''
                        def __init__(
                            self,

                        ):
                            pass


                        def check_required(self):

                            return

                        def as_dict(self):
                            return drop_none({})





        class Pressure_cavity(object):
            '''Neumann boundary condition for normal times value for vector-valued PDEs.
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
                    print("Requiered variable Root.Boundary_conditions.Pressure_cavity.items does not have value")
                return

            def as_dict(self):
                return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

            class Value(object):
                '''pressure BC entry
                \nRequired: ['id', 'value']
                \nOptional: []'''
                def __init__(
                    self,
                    id: int = None,
                    value: Optional["Root.Boundary_conditions.Pressure_cavity.Value.Value"] = None
                ):
                    self._id = range_check(type_check(id, int), 0, 2147483646) if id is not None else None
                    self._value = type_check(value, self.Value) if value else self.Value()

                @property
                def id(self):
                    return self._id

                @id.setter
                def id(self, value):
                    ''' 
                    ID for the pressure Neumann boundary condition
                    '''
                    self._id = range_check(type_check(value, int), 0, 2147483646) 

                @property
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    ''' 
                    Values of pressure boundary condition as a function of $x,y,z,t$
                    \nRequired: []
                    \nOptional: []
                    '''
                    self._value = type_check(value, self.Value) 

                def check_required(self):

                    if self.id is None:
                        print("Requiered variable Root.Boundary_conditions.Pressure_cavity.Value.id does not have value")
                    self.value.check_required()
                    return

                def as_dict(self):
                    return drop_none({"id": self._id,"value": self._value.as_dict(),})

                class Value(object):
                    '''Values of pressure boundary condition as a function of $x,y,z,t$
                    \nRequired: []
                    \nOptional: []'''
                    def __init__(
                        self,

                    ):
                        pass


                    def check_required(self):

                        return

                    def as_dict(self):
                        return drop_none({})




        class Obstacle_displacements(object):
            '''This is a polymorphic variable, assign an object from its classes to the value
            \nRequired: []
            \nOptional: ['object1', 'object2']'''
            def __init__(
                self,
                value : object = None
            ):
                self._value = class_check(value, [self.Object1, self.Object2]) if value is not None else None

            @property
            def value(self):
                return self._value

            @value.setter
            def value(self, value):
                ''' 
                This is a polymorphic variable, assign an object from its classes to the value
                '''
                self._value = class_check(value, [self.Object1, self.Object2]) 

            def check_required(self):

                if self.value is None:
                    print("Requiered variable Root.Boundary_conditions.Obstacle_displacements.value does not have value")
                else:
                    if type(self.value) not in [['int', 'float', 'list', 'str', 'bool']]:
                        self.value.check_required()
                return

            def as_dict(self):
                return drop_none(self._value.as_dict() if isinstance(self._value, tuple([self.Object1, self.Object2])) else self._value)

            class Object1(object):
                '''Obstacle displacements
                \nRequired: []
                \nOptional: []'''
                def __init__(
                    self,

                ):
                    pass


                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({})


            class Object2(object):
                '''Obstacle displacements
                \nRequired: ['id', 'value']
                \nOptional: ['interpolation']'''
                def __init__(
                    self,
                    id: None = None,
                    value: None = None,
                    interpolation: None = None
                ):
                    self._id = type_check(id, None) if id is not None else None
                    self._value = type_check(value, None) if value is not None else None
                    self._interpolation = type_check(interpolation, None) if interpolation is not None else None

                @property
                def id(self):
                    return self._id

                @id.setter
                def id(self, value):
                    ''' 
                    There is no definition
                    '''
                    self._id = type_check(value, None) 

                @property
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    ''' 
                    There is no definition
                    '''
                    self._value = type_check(value, None) 

                @property
                def interpolation(self):
                    return self._interpolation

                @interpolation.setter
                def interpolation(self, value):
                    ''' 
                    There is no definition
                    '''
                    self._interpolation = type_check(value, None) 

                def check_required(self):

                    if self.id is None:
                        print("Requiered variable Root.Boundary_conditions.Obstacle_displacements.Object2.id does not have value")

                    if self.value is None:
                        print("Requiered variable Root.Boundary_conditions.Obstacle_displacements.Object2.value does not have value")
                    return

                def as_dict(self):
                    return drop_none({"id": self._id,"value": self._value,"interpolation": self._interpolation,})



        class Periodic_boundary(object):
            '''Options for periodic boundary conditions.
            \nRequired: []
            \nOptional: ['enabled', 'tolerance', 'correspondence', 'linear_displacement_offset', 'fixed_macro_strain', 'force_zero_mean']'''
            def __init__(
                self,
                enabled: bool = False,
                tolerance: float = 1e-05,
                correspondence: Optional[Iterable[list]] = None,
                linear_displacement_offset: Optional[Iterable[list]] = None,
                fixed_macro_strain: Optional[Iterable[int]] = None,
                force_zero_mean: bool = False
            ):
                self._enabled = type_check(enabled, bool) if enabled is not None else None
                self._tolerance = type_check(tolerance, float) if tolerance is not None else None
                self._correspondence = [] if correspondence is None else [type_check(i, list) for i in correspondence]
                self._linear_displacement_offset = [] if linear_displacement_offset is None else [type_check(i, list) for i in linear_displacement_offset]
                self._fixed_macro_strain = [] if fixed_macro_strain is None else [type_check(i, int) for i in fixed_macro_strain]
                self._force_zero_mean = type_check(force_zero_mean, bool) if force_zero_mean is not None else None

            @property
            def enabled(self):
                return self._enabled

            @enabled.setter
            def enabled(self, value):
                ''' 
                There is no definition
                '''
                self._enabled = type_check(value, bool) 

            @property
            def tolerance(self):
                return self._tolerance

            @tolerance.setter
            def tolerance(self, value):
                ''' 
                Relative tolerance of deciding periodic correspondence
                '''
                self._tolerance = type_check(value, float) 

            @property
            def correspondence(self):
                return self._correspondence

            @correspondence.setter
            def correspondence(self, value):
                ''' 
                Periodic directions for periodic boundary conditions. If not specified, default to axis-aligned directions.
                \nRequired: []
                \nOptional: ['value']
                '''
                self._correspondence = [type_check(i, list) for i in (type_check(value, list) if value else [])]

            def correspondence_add(self, value):
                '''Add to list '''
                self._correspondence.append(type_check(value, list))

            def correspondence_clear(self):
                '''Clear list (make empty)'''
                self._correspondence.clear()

            def correspondence_pop(self, index=-1):
                '''Remove by index from list'''
                return self._correspondence.pop(index)

            def correspondence_remove(self, item):
                '''Safe remove specific item from list'''
                if item in self._list:
                    self._correspondence.remove(item)


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
                self._linear_displacement_offset = [type_check(i, list) for i in (type_check(value, list) if value else [])]

            def linear_displacement_offset_add(self, value):
                '''Add to list '''
                self._linear_displacement_offset.append(type_check(value, list))

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
            def fixed_macro_strain(self):
                return self._fixed_macro_strain

            @fixed_macro_strain.setter
            def fixed_macro_strain(self, value):
                ''' 
                There is no definition
                \nRequired: []
                \nOptional: ['value']
                '''
                self._fixed_macro_strain = [type_check(i, int) for i in (type_check(value, list) if value else [])]

            def fixed_macro_strain_add(self, value):
                '''Add to list '''
                self._fixed_macro_strain.append(type_check(value, int))

            def fixed_macro_strain_clear(self):
                '''Clear list (make empty)'''
                self._fixed_macro_strain.clear()

            def fixed_macro_strain_pop(self, index=-1):
                '''Remove by index from list'''
                return self._fixed_macro_strain.pop(index)

            def fixed_macro_strain_remove(self, item):
                '''Safe remove specific item from list'''
                if item in self._list:
                    self._fixed_macro_strain.remove(item)


            @property
            def force_zero_mean(self):
                return self._force_zero_mean

            @force_zero_mean.setter
            def force_zero_mean(self, value):
                ''' 
                The periodic solution is not unique, set to true to find the solution with zero mean.
                '''
                self._force_zero_mean = type_check(value, bool) 

            def check_required(self):

                return

            def as_dict(self):
                return drop_none({"enabled": self._enabled,"tolerance": self._tolerance,"correspondence": self._correspondence,"linear_displacement_offset": self._linear_displacement_offset,"fixed_macro_strain": self._fixed_macro_strain,"force_zero_mean": self._force_zero_mean,})



    class Initial_conditions(object):
        '''Initial conditions for the time-dependent problem, imposed on the main variable, its derivative or second derivative
        \nRequired: []
        \nOptional: ['solution', 'velocity', 'acceleration']'''
        def __init__(
            self,
            solution: Optional["Root.Initial_conditions.Solution"] = None,
            velocity: Optional["Root.Initial_conditions.Velocity"] = None,
            acceleration: Optional["Root.Initial_conditions.Acceleration"] = None
        ):
            self._solution = type_check(solution, self.Solution) if solution else self.Solution()
            self._velocity = type_check(velocity, self.Velocity) if velocity else self.Velocity()
            self._acceleration = type_check(acceleration, self.Acceleration) if acceleration else self.Acceleration()

        @property
        def solution(self):
            return self._solution

        @solution.setter
        def solution(self, value):
            ''' 
            initial solution
            \nRequired: []
            \nOptional: ['value']
            '''
            self._solution = type_check(value, self.Solution) 

        @property
        def velocity(self):
            return self._velocity

        @velocity.setter
        def velocity(self, value):
            ''' 
            initial velocity
            \nRequired: []
            \nOptional: ['value']
            '''
            self._velocity = type_check(value, self.Velocity) 

        @property
        def acceleration(self):
            return self._acceleration

        @acceleration.setter
        def acceleration(self, value):
            ''' 
            initial acceleration
            \nRequired: []
            \nOptional: ['value']
            '''
            self._acceleration = type_check(value, self.Acceleration) 

        def check_required(self):

            return

        def as_dict(self):
            return drop_none({"solution": self._solution.as_dict(),"velocity": self._velocity.as_dict(),"acceleration": self._acceleration.as_dict(),})

        class Solution(object):
            '''initial solution
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
                    print("Requiered variable Root.Initial_conditions.Solution.items does not have value")
                return

            def as_dict(self):
                return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

            class Value(object):
                '''A list of (ID, value) pairs defining the initial conditions for the main variable values. Ids are set by selection, and values can be floats or formulas.
                \nRequired: ['id', 'value']
                \nOptional: []'''
                def __init__(
                    self,
                    id: int = None,
                    value: Optional["Root.Initial_conditions.Solution.Value.Value"] = None
                ):
                    self._id = type_check(id, int) if id is not None else None
                    self._value = type_check(value, self.Value) if value else self.Value()

                @property
                def id(self):
                    return self._id

                @id.setter
                def id(self, value):
                    ''' 
                    ID from volume selections
                    '''
                    self._id = type_check(value, int) 

                @property
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    ''' 
                    value of the solution
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._value = type_check(value, self.Value) 

                def check_required(self):

                    if self.id is None:
                        print("Requiered variable Root.Initial_conditions.Solution.Value.id does not have value")
                    self.value.check_required()
                    return

                def as_dict(self):
                    return drop_none({"id": self._id,"value": self._value.as_dict(),})

                class Value(object):
                    '''value of the solution
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
                            print("Requiered variable Root.Initial_conditions.Solution.Value.Value.items does not have value")
                        return

                    def as_dict(self):
                        return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

                    class Value(object):
                        '''value
                        \nRequired: []
                        \nOptional: []'''
                        def __init__(
                            self,

                        ):
                            pass


                        def check_required(self):

                            return

                        def as_dict(self):
                            return drop_none({})





        class Velocity(object):
            '''initial velocity
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
                    print("Requiered variable Root.Initial_conditions.Velocity.items does not have value")
                return

            def as_dict(self):
                return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

            class Value(object):
                '''A list of (ID, value) pairs defining the initial conditions for the first derivative of the main variable values. Ids are set by selection, and values can be floats or formulas.
                \nRequired: ['id', 'value']
                \nOptional: []'''
                def __init__(
                    self,
                    id: int = None,
                    value: Optional["Root.Initial_conditions.Velocity.Value.Value"] = None
                ):
                    self._id = type_check(id, int) if id is not None else None
                    self._value = type_check(value, self.Value) if value else self.Value()

                @property
                def id(self):
                    return self._id

                @id.setter
                def id(self, value):
                    ''' 
                    ID from volume selections
                    '''
                    self._id = type_check(value, int) 

                @property
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    ''' 
                    value od the initial velocity
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._value = range_check(type_check(value, self.Value), 2, 3) 

                def check_required(self):

                    if self.id is None:
                        print("Requiered variable Root.Initial_conditions.Velocity.Value.id does not have value")
                    self.value.check_required()
                    return

                def as_dict(self):
                    return drop_none({"id": self._id,"value": self._value.as_dict(),})

                class Value(object):
                    '''value od the initial velocity
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
                            print("Requiered variable Root.Initial_conditions.Velocity.Value.Value.items does not have value")
                        return

                    def as_dict(self):
                        return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

                    class Value(object):
                        '''value
                        \nRequired: []
                        \nOptional: []'''
                        def __init__(
                            self,

                        ):
                            pass


                        def check_required(self):

                            return

                        def as_dict(self):
                            return drop_none({})





        class Acceleration(object):
            '''initial acceleration
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
                    print("Requiered variable Root.Initial_conditions.Acceleration.items does not have value")
                return

            def as_dict(self):
                return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

            class Value(object):
                '''entries
                \nRequired: ['id', 'value']
                \nOptional: []'''
                def __init__(
                    self,
                    id: int = None,
                    value: Optional["Root.Initial_conditions.Acceleration.Value.Value"] = None
                ):
                    self._id = type_check(id, int) if id is not None else None
                    self._value = type_check(value, self.Value) if value else self.Value()

                @property
                def id(self):
                    return self._id

                @id.setter
                def id(self, value):
                    ''' 
                    ID from volume selections
                    '''
                    self._id = type_check(value, int) 

                @property
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    ''' 
                    value
                    \nRequired: []
                    \nOptional: ['value']
                    '''
                    self._value = range_check(type_check(value, self.Value), 2, 3) 

                def check_required(self):

                    if self.id is None:
                        print("Requiered variable Root.Initial_conditions.Acceleration.Value.id does not have value")
                    self.value.check_required()
                    return

                def as_dict(self):
                    return drop_none({"id": self._id,"value": self._value.as_dict(),})

                class Value(object):
                    '''value
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
                            print("Requiered variable Root.Initial_conditions.Acceleration.Value.Value.items does not have value")
                        return

                    def as_dict(self):
                        return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

                    class Value(object):
                        '''value
                        \nRequired: []
                        \nOptional: []'''
                        def __init__(
                            self,

                        ):
                            pass


                        def check_required(self):

                            return

                        def as_dict(self):
                            return drop_none({})






    class Constraints(object):
        '''soft and hard constraints
        \nRequired: []
        \nOptional: ['soft', 'hard']'''
        def __init__(
            self,
            soft: Optional["Root.Constraints.Soft"] = None,
            hard: Optional[Iterable[str]] = None
        ):
            self._soft = type_check(soft, self.Soft) if soft else self.Soft()
            self._hard = [] if hard is None else [type_check(i, str) for i in hard]

        @property
        def soft(self):
            return self._soft

        @soft.setter
        def soft(self, value):
            ''' 
            list of file containing soft constraints
            \nRequired: []
            \nOptional: ['value']
            '''
            self._soft = type_check(value, self.Soft) 

        @property
        def hard(self):
            return self._hard

        @hard.setter
        def hard(self, value):
            ''' 
            list of file containing hard constraints
            \nRequired: []
            \nOptional: ['value']
            '''
            self._hard = [type_check(i, str) for i in (type_check(value, list) if value else [])]

        def hard_add(self, value):
            '''Add to list '''
            self._hard.append(type_check(value, str))

        def hard_clear(self):
            '''Clear list (make empty)'''
            self._hard.clear()

        def hard_pop(self, index=-1):
            '''Remove by index from list'''
            return self._hard.pop(index)

        def hard_remove(self, item):
            '''Safe remove specific item from list'''
            if item in self._list:
                self._hard.remove(item)


        def check_required(self):

            return

        def as_dict(self):
            return drop_none({"soft": self._soft.as_dict(),"hard": self._hard,})

        class Soft(object):
            '''list of file containing soft constraints
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
                    print("Requiered variable Root.Constraints.Soft.items does not have value")
                return

            def as_dict(self):
                return drop_none([i.as_dict() if isinstance(i, tuple([self.Value])) else i for i in self._items])

            class Value(object):
                '''constraint hdf5 file for soft constraint w||Ax-b||^2. The file must contain these datasets: weight w, local2global, dense/sparse matrix A, and vector b. The colums of b nees to be the same as the dimentionality of the problem. if A is sparse it should contain A_triplets/value A_triplets/cols A_triplets/rows A_triplets/shape
                \nRequired: []
                \nOptional: ['weight', 'data']'''
                def __init__(
                    self,
                    weight: float = 0.0,
                    data: str = ''
                ):
                    self._weight = type_check(weight, float) if weight is not None else None
                    self._data = type_check(data, str) if data is not None else None

                @property
                def weight(self):
                    return self._weight

                @weight.setter
                def weight(self, value):
                    ''' 
                    weight
                    '''
                    self._weight = type_check(value, float) 

                @property
                def data(self):
                    return self._data

                @data.setter
                def data(self, value):
                    ''' 
                    constraint hdf5 file for soft constraint w||Ax-b||^2. The file must contain these datasets: local2global, dense/sparse matrix A, and vector b. The colums of b nees to be the same as the dimentionality of the problem. if A is sparse it should contain A_triplets/value A_triplets/col A_triplets/rows A_triplets/shape
                    '''
                    self._data = type_check(value, str) 

                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({"weight": self._weight,"data": self._data,})




    class Output(object):
        '''output settings
        \nRequired: []
        \nOptional: ['directory', 'log', 'json', 'restart_json', 'paraview', 'data', 'advanced', 'reference', 'stats']'''
        def __init__(
            self,
            directory: str = '',
            log: Optional["Root.Output.Log"] = None,
            json: str = '',
            restart_json: str = '',
            paraview: Optional["Root.Output.Paraview"] = None,
            data: Optional["Root.Output.Data"] = None,
            advanced: Optional["Root.Output.Advanced"] = None,
            reference: Optional["Root.Output.Reference"] = None,
            stats: bool = False
        ):
            self._directory = type_check(directory, str) if directory is not None else None
            self._log = type_check(log, self.Log) if log else self.Log()
            self._json = type_check(json, str) if json is not None else None
            self._restart_json = type_check(restart_json, str) if restart_json is not None else None
            self._paraview = type_check(paraview, self.Paraview) if paraview else self.Paraview()
            self._data = type_check(data, self.Data) if data else self.Data()
            self._advanced = type_check(advanced, self.Advanced) if advanced else self.Advanced()
            self._reference = type_check(reference, self.Reference) if reference else self.Reference()
            self._stats = type_check(stats, bool) if stats is not None else None

        @property
        def directory(self):
            return self._directory

        @directory.setter
        def directory(self, value):
            ''' 
            Directory for output files.
            '''
            self._directory = type_check(value, str) 

        @property
        def log(self):
            return self._log

        @log.setter
        def log(self, value):
            ''' 
            Setting for the output log.
            \nRequired: []
            \nOptional: []
            '''
            self._log = type_check(value, self.Log) 

        @property
        def json(self):
            return self._json

        @json.setter
        def json(self, value):
            ''' 
            File name for JSON output statistics on time/error/etc.
            '''
            self._json = type_check(value, str) 

        @property
        def restart_json(self):
            return self._restart_json

        @restart_json.setter
        def restart_json(self, value):
            ''' 
            File name for JSON output to restart the simulation.
            '''
            self._restart_json = type_check(value, str) 

        @property
        def paraview(self):
            return self._paraview

        @paraview.setter
        def paraview(self, value):
            ''' 
            Output in paraview format
            \nRequired: []
            \nOptional: ['file_name', 'vismesh_rel_area', 'skip_frame', 'high_order_mesh', 'volume', 'surface', 'wireframe', 'fields', 'points', 'options']
            '''
            self._paraview = type_check(value, self.Paraview) 

        @property
        def data(self):
            return self._data

        @data.setter
        def data(self, value):
            ''' 
            File names to write output data to.
            \nRequired: []
            \nOptional: ['solution', 'full_mat', 'stiffness_mat', 'stress_mat', 'state', 'rest_mesh', 'mises', 'nodes', 'advanced', 'file_index_offset']
            '''
            self._data = type_check(value, self.Data) 

        @property
        def advanced(self):
            return self._advanced

        @advanced.setter
        def advanced(self, value):
            ''' 
            Additional output options
            \nRequired: []
            \nOptional: ['timestep_prefix', 'sol_on_grid', 'compute_error', 'sol_at_node', 'vis_boundary_only', 'curved_mesh_size', 'save_solve_sequence_debug', 'save_ccd_debug_meshes', 'save_time_sequence', 'save_nl_solve_sequence', 'spectrum']
            '''
            self._advanced = type_check(value, self.Advanced) 

        @property
        def reference(self):
            return self._reference

        @reference.setter
        def reference(self, value):
            ''' 
            Write out the analytic/numerical ground-truth solution and or its gradient
            \nRequired: []
            \nOptional: ['solution', 'gradient']
            '''
            self._reference = type_check(value, self.Reference) 

        @property
        def stats(self):
            return self._stats

        @stats.setter
        def stats(self, value):
            ''' 
            Saves csv for energy and stats of the non linear solver.
            '''
            self._stats = type_check(value, bool) 

        def check_required(self):

            return

        def as_dict(self):
            return drop_none({"directory": self._directory,"log": self._log.as_dict(),"json": self._json,"restart_json": self._restart_json,"paraview": self._paraview.as_dict(),"data": self._data.as_dict(),"advanced": self._advanced.as_dict(),"reference": self._reference.as_dict(),"stats": self._stats,})

        class Log(object):
            '''Setting for the output log.
            \nRequired: []
            \nOptional: []'''
            def __init__(
                self,

            ):
                pass


            def check_required(self):

                return

            def as_dict(self):
                return drop_none({})


        class Paraview(object):
            '''Output in paraview format
            \nRequired: []
            \nOptional: ['file_name', 'vismesh_rel_area', 'skip_frame', 'high_order_mesh', 'volume', 'surface', 'wireframe', 'fields', 'points', 'options']'''
            def __init__(
                self,
                file_name: str = '',
                vismesh_rel_area: float = 1e-05,
                skip_frame: int = 1,
                high_order_mesh: bool = True,
                volume: bool = True,
                surface: bool = False,
                wireframe: bool = False,
                fields: Optional[Iterable[str]] = None,
                points: bool = False,
                options: Optional["Root.Output.Paraview.Options"] = None
            ):
                self._file_name = type_check(file_name, str) if file_name is not None else None
                self._vismesh_rel_area = type_check(vismesh_rel_area, float) if vismesh_rel_area is not None else None
                self._skip_frame = type_check(skip_frame, int) if skip_frame is not None else None
                self._high_order_mesh = type_check(high_order_mesh, bool) if high_order_mesh is not None else None
                self._volume = type_check(volume, bool) if volume is not None else None
                self._surface = type_check(surface, bool) if surface is not None else None
                self._wireframe = type_check(wireframe, bool) if wireframe is not None else None
                self._fields = [] if fields is None else [type_check(i, str) for i in fields]
                self._points = type_check(points, bool) if points is not None else None
                self._options = type_check(options, self.Options) if options else self.Options()

            @property
            def file_name(self):
                return self._file_name

            @file_name.setter
            def file_name(self, value):
                ''' 
                Paraview output file name
                '''
                self._file_name = type_check(value, str) 

            @property
            def vismesh_rel_area(self):
                return self._vismesh_rel_area

            @vismesh_rel_area.setter
            def vismesh_rel_area(self, value):
                ''' 
                relative area for the upsampled visualisation mesh
                '''
                self._vismesh_rel_area = type_check(value, float) 

            @property
            def skip_frame(self):
                return self._skip_frame

            @skip_frame.setter
            def skip_frame(self, value):
                ''' 
                export every skip_frame-th frames for time dependent simulations
                '''
                self._skip_frame = type_check(value, int) 

            @property
            def high_order_mesh(self):
                return self._high_order_mesh

            @high_order_mesh.setter
            def high_order_mesh(self, value):
                ''' 
                Enables/disables high-order output for paraview. Supported only for isoparametric or linear meshes with high-order solutions.
                '''
                self._high_order_mesh = type_check(value, bool) 

            @property
            def volume(self):
                return self._volume

            @volume.setter
            def volume(self, value):
                ''' 
                Export volumetric mesh
                '''
                self._volume = type_check(value, bool) 

            @property
            def surface(self):
                return self._surface

            @surface.setter
            def surface(self, value):
                ''' 
                Export surface mesh (in 2d polygon)
                '''
                self._surface = type_check(value, bool) 

            @property
            def wireframe(self):
                return self._wireframe

            @wireframe.setter
            def wireframe(self, value):
                ''' 
                Export the wireframe of the mesh
                '''
                self._wireframe = type_check(value, bool) 

            @property
            def fields(self):
                return self._fields

            @fields.setter
            def fields(self, value):
                ''' 
                list of names of fields to export. If empty, all fields are exported.
                \nRequired: []
                \nOptional: ['value']
                '''
                self._fields = [type_check(i, str) for i in (type_check(value, list) if value else [])]

            def fields_add(self, value):
                '''Add to list '''
                self._fields.append(type_check(value, str))

            def fields_clear(self):
                '''Clear list (make empty)'''
                self._fields.clear()

            def fields_pop(self, index=-1):
                '''Remove by index from list'''
                return self._fields.pop(index)

            def fields_remove(self, item):
                '''Safe remove specific item from list'''
                if item in self._list:
                    self._fields.remove(item)


            @property
            def points(self):
                return self._points

            @points.setter
            def points(self, value):
                ''' 
                Export the Dirichlet points
                '''
                self._points = type_check(value, bool) 

            @property
            def options(self):
                return self._options

            @options.setter
            def options(self, value):
                ''' 
                Optional fields in the output
                \nRequired: []
                \nOptional: ['use_hdf5', 'material', 'body_ids', 'contact_forces', 'friction_forces', 'normal_adhesion_forces', 'tangential_adhesion_forces', 'velocity', 'acceleration', 'scalar_values', 'tensor_values', 'discretization_order', 'nodes', 'forces', 'force_high_order', 'jacobian_validity']
                '''
                self._options = type_check(value, self.Options) 

            def check_required(self):

                return

            def as_dict(self):
                return drop_none({"file_name": self._file_name,"vismesh_rel_area": self._vismesh_rel_area,"skip_frame": self._skip_frame,"high_order_mesh": self._high_order_mesh,"volume": self._volume,"surface": self._surface,"wireframe": self._wireframe,"fields": self._fields,"points": self._points,"options": self._options.as_dict(),})

            class Options(object):
                '''Optional fields in the output
                \nRequired: []
                \nOptional: ['use_hdf5', 'material', 'body_ids', 'contact_forces', 'friction_forces', 'normal_adhesion_forces', 'tangential_adhesion_forces', 'velocity', 'acceleration', 'scalar_values', 'tensor_values', 'discretization_order', 'nodes', 'forces', 'force_high_order', 'jacobian_validity']'''
                def __init__(
                    self,
                    use_hdf5: bool = False,
                    material: bool = False,
                    body_ids: bool = False,
                    contact_forces: bool = False,
                    friction_forces: bool = False,
                    normal_adhesion_forces: bool = False,
                    tangential_adhesion_forces: bool = False,
                    velocity: bool = False,
                    acceleration: bool = False,
                    scalar_values: bool = True,
                    tensor_values: bool = True,
                    discretization_order: bool = True,
                    nodes: bool = True,
                    forces: bool = False,
                    force_high_order: bool = False,
                    jacobian_validity: bool = False
                ):
                    self._use_hdf5 = type_check(use_hdf5, bool) if use_hdf5 is not None else None
                    self._material = type_check(material, bool) if material is not None else None
                    self._body_ids = type_check(body_ids, bool) if body_ids is not None else None
                    self._contact_forces = type_check(contact_forces, bool) if contact_forces is not None else None
                    self._friction_forces = type_check(friction_forces, bool) if friction_forces is not None else None
                    self._normal_adhesion_forces = type_check(normal_adhesion_forces, bool) if normal_adhesion_forces is not None else None
                    self._tangential_adhesion_forces = type_check(tangential_adhesion_forces, bool) if tangential_adhesion_forces is not None else None
                    self._velocity = type_check(velocity, bool) if velocity is not None else None
                    self._acceleration = type_check(acceleration, bool) if acceleration is not None else None
                    self._scalar_values = type_check(scalar_values, bool) if scalar_values is not None else None
                    self._tensor_values = type_check(tensor_values, bool) if tensor_values is not None else None
                    self._discretization_order = type_check(discretization_order, bool) if discretization_order is not None else None
                    self._nodes = type_check(nodes, bool) if nodes is not None else None
                    self._forces = type_check(forces, bool) if forces is not None else None
                    self._force_high_order = type_check(force_high_order, bool) if force_high_order is not None else None
                    self._jacobian_validity = type_check(jacobian_validity, bool) if jacobian_validity is not None else None

                @property
                def use_hdf5(self):
                    return self._use_hdf5

                @use_hdf5.setter
                def use_hdf5(self, value):
                    ''' 
                    If true, export the data as hdf5, compatible with paraview >5.11
                    '''
                    self._use_hdf5 = type_check(value, bool) 

                @property
                def material(self):
                    return self._material

                @material.setter
                def material(self, value):
                    ''' 
                    If true, write out material values sampled on the vertices of the mesh
                    '''
                    self._material = type_check(value, bool) 

                @property
                def body_ids(self):
                    return self._body_ids

                @body_ids.setter
                def body_ids(self, value):
                    ''' 
                    Export volumes ids
                    '''
                    self._body_ids = type_check(value, bool) 

                @property
                def contact_forces(self):
                    return self._contact_forces

                @contact_forces.setter
                def contact_forces(self, value):
                    ''' 
                    If true, write out contact forces for surface
                    '''
                    self._contact_forces = type_check(value, bool) 

                @property
                def friction_forces(self):
                    return self._friction_forces

                @friction_forces.setter
                def friction_forces(self, value):
                    ''' 
                    If true, write out friction forces for surface
                    '''
                    self._friction_forces = type_check(value, bool) 

                @property
                def normal_adhesion_forces(self):
                    return self._normal_adhesion_forces

                @normal_adhesion_forces.setter
                def normal_adhesion_forces(self, value):
                    ''' 
                    If true, write out normal adhesion forces for surface
                    '''
                    self._normal_adhesion_forces = type_check(value, bool) 

                @property
                def tangential_adhesion_forces(self):
                    return self._tangential_adhesion_forces

                @tangential_adhesion_forces.setter
                def tangential_adhesion_forces(self, value):
                    ''' 
                    If true, write out tangential adhesion forces for surface
                    '''
                    self._tangential_adhesion_forces = type_check(value, bool) 

                @property
                def velocity(self):
                    return self._velocity

                @velocity.setter
                def velocity(self, value):
                    ''' 
                    If true, write out velocities
                    '''
                    self._velocity = type_check(value, bool) 

                @property
                def acceleration(self):
                    return self._acceleration

                @acceleration.setter
                def acceleration(self, value):
                    ''' 
                    If true, write out accelerations
                    '''
                    self._acceleration = type_check(value, bool) 

                @property
                def scalar_values(self):
                    return self._scalar_values

                @scalar_values.setter
                def scalar_values(self, value):
                    ''' 
                    If true, write out scalar values
                    '''
                    self._scalar_values = type_check(value, bool) 

                @property
                def tensor_values(self):
                    return self._tensor_values

                @tensor_values.setter
                def tensor_values(self, value):
                    ''' 
                    If true, write out tensor values
                    '''
                    self._tensor_values = type_check(value, bool) 

                @property
                def discretization_order(self):
                    return self._discretization_order

                @discretization_order.setter
                def discretization_order(self, value):
                    ''' 
                    If true, write out discretization order
                    '''
                    self._discretization_order = type_check(value, bool) 

                @property
                def nodes(self):
                    return self._nodes

                @nodes.setter
                def nodes(self, value):
                    ''' 
                    If true, write out node order
                    '''
                    self._nodes = type_check(value, bool) 

                @property
                def forces(self):
                    return self._forces

                @forces.setter
                def forces(self, value):
                    ''' 
                    If true, write out all variational forces on the FE mesh
                    '''
                    self._forces = type_check(value, bool) 

                @property
                def force_high_order(self):
                    return self._force_high_order

                @force_high_order.setter
                def force_high_order(self, value):
                    ''' 
                    If true, force write out high-order mesh, might break the output
                    '''
                    self._force_high_order = type_check(value, bool) 

                @property
                def jacobian_validity(self):
                    return self._jacobian_validity

                @jacobian_validity.setter
                def jacobian_validity(self, value):
                    ''' 
                    If true, perform robust Jacobian check on the deformed elements and mark elements with non-positive Jacobian.
                    '''
                    self._jacobian_validity = type_check(value, bool) 

                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({"use_hdf5": self._use_hdf5,"material": self._material,"body_ids": self._body_ids,"contact_forces": self._contact_forces,"friction_forces": self._friction_forces,"normal_adhesion_forces": self._normal_adhesion_forces,"tangential_adhesion_forces": self._tangential_adhesion_forces,"velocity": self._velocity,"acceleration": self._acceleration,"scalar_values": self._scalar_values,"tensor_values": self._tensor_values,"discretization_order": self._discretization_order,"nodes": self._nodes,"forces": self._forces,"force_high_order": self._force_high_order,"jacobian_validity": self._jacobian_validity,})



        class Data(object):
            '''File names to write output data to.
            \nRequired: []
            \nOptional: ['solution', 'full_mat', 'stiffness_mat', 'stress_mat', 'state', 'rest_mesh', 'mises', 'nodes', 'advanced', 'file_index_offset']'''
            def __init__(
                self,
                solution: str = '',
                full_mat: str = '',
                stiffness_mat: str = '',
                stress_mat: str = '',
                state: str = '',
                rest_mesh: str = '',
                mises: str = '',
                nodes: str = '',
                advanced: Optional["Root.Output.Data.Advanced"] = None,
                file_index_offset: int = 0
            ):
                self._solution = type_check(solution, str) if solution is not None else None
                self._full_mat = type_check(full_mat, str) if full_mat is not None else None
                self._stiffness_mat = type_check(stiffness_mat, str) if stiffness_mat is not None else None
                self._stress_mat = type_check(stress_mat, str) if stress_mat is not None else None
                self._state = type_check(state, str) if state is not None else None
                self._rest_mesh = type_check(rest_mesh, str) if rest_mesh is not None else None
                self._mises = type_check(mises, str) if mises is not None else None
                self._nodes = type_check(nodes, str) if nodes is not None else None
                self._advanced = type_check(advanced, self.Advanced) if advanced else self.Advanced()
                self._file_index_offset = type_check(file_index_offset, int) if file_index_offset is not None else None

            @property
            def solution(self):
                return self._solution

            @solution.setter
            def solution(self, value):
                ''' 
                Main variable solution. Unrolled [xyz, xyz, ...] using PolyFEM ordering. If reorder_nodes exports the solution with the same order the vertices of the input mesh as a #n x d file
                '''
                self._solution = type_check(value, str) 

            @property
            def full_mat(self):
                return self._full_mat

            @full_mat.setter
            def full_mat(self, value):
                ''' 
                System matrix without boundary conditions. Doesn't work for nonlinear problems
                '''
                self._full_mat = type_check(value, str) 

            @property
            def stiffness_mat(self):
                return self._stiffness_mat

            @stiffness_mat.setter
            def stiffness_mat(self, value):
                ''' 
                System matrix with boundary conditions. Doesn't work for nonlinear problems
                '''
                self._stiffness_mat = type_check(value, str) 

            @property
            def stress_mat(self):
                return self._stress_mat

            @stress_mat.setter
            def stress_mat(self, value):
                ''' 
                Exports stress
                '''
                self._stress_mat = type_check(value, str) 

            @property
            def state(self):
                return self._state

            @state.setter
            def state(self, value):
                ''' 
                Writes the complete state in PolyFEM hdf5 format, used to restart the sim
                '''
                self._state = type_check(value, str) 

            @property
            def rest_mesh(self):
                return self._rest_mesh

            @rest_mesh.setter
            def rest_mesh(self, value):
                ''' 
                Writes the rest mesh in MSH format, used to restart the sim
                '''
                self._rest_mesh = type_check(value, str) 

            @property
            def mises(self):
                return self._mises

            @mises.setter
            def mises(self, value):
                ''' 
                File name to write per-node Von Mises stress values to.
                '''
                self._mises = type_check(value, str) 

            @property
            def nodes(self):
                return self._nodes

            @nodes.setter
            def nodes(self, value):
                ''' 
                Writes the FEM nodes
                '''
                self._nodes = type_check(value, str) 

            @property
            def advanced(self):
                return self._advanced

            @advanced.setter
            def advanced(self, value):
                ''' 
                advanced options
                \nRequired: []
                \nOptional: ['reorder_nodes']
                '''
                self._advanced = type_check(value, self.Advanced) 

            @property
            def file_index_offset(self):
                return self._file_index_offset

            @file_index_offset.setter
            def file_index_offset(self, value):
                ''' 
                Starting file index offset for output files. Set automatically by restart JSON so that file numbering continues from the previous run.
                '''
                self._file_index_offset = type_check(value, int) 

            def check_required(self):

                return

            def as_dict(self):
                return drop_none({"solution": self._solution,"full_mat": self._full_mat,"stiffness_mat": self._stiffness_mat,"stress_mat": self._stress_mat,"state": self._state,"rest_mesh": self._rest_mesh,"mises": self._mises,"nodes": self._nodes,"advanced": self._advanced.as_dict(),"file_index_offset": self._file_index_offset,})

            class Advanced(object):
                '''advanced options
                \nRequired: []
                \nOptional: ['reorder_nodes']'''
                def __init__(
                    self,
                    reorder_nodes: bool = False
                ):
                    self._reorder_nodes = type_check(reorder_nodes, bool) if reorder_nodes is not None else None

                @property
                def reorder_nodes(self):
                    return self._reorder_nodes

                @reorder_nodes.setter
                def reorder_nodes(self, value):
                    ''' 
                    Reorder nodes accodring to input
                    '''
                    self._reorder_nodes = type_check(value, bool) 

                def check_required(self):

                    return

                def as_dict(self):
                    return drop_none({"reorder_nodes": self._reorder_nodes,})



        class Advanced(object):
            '''Additional output options
            \nRequired: []
            \nOptional: ['timestep_prefix', 'sol_on_grid', 'compute_error', 'sol_at_node', 'vis_boundary_only', 'curved_mesh_size', 'save_solve_sequence_debug', 'save_ccd_debug_meshes', 'save_time_sequence', 'save_nl_solve_sequence', 'spectrum']'''
            def __init__(
                self,
                timestep_prefix: str = 'step_',
                sol_on_grid: float = -1.0,
                compute_error: bool = True,
                sol_at_node: int = -1,
                vis_boundary_only: bool = False,
                curved_mesh_size: bool = False,
                save_solve_sequence_debug: bool = False,
                save_ccd_debug_meshes: bool = False,
                save_time_sequence: bool = True,
                save_nl_solve_sequence: bool = False,
                spectrum: bool = False
            ):
                self._timestep_prefix = type_check(timestep_prefix, str) if timestep_prefix is not None else None
                self._sol_on_grid = type_check(sol_on_grid, float) if sol_on_grid is not None else None
                self._compute_error = type_check(compute_error, bool) if compute_error is not None else None
                self._sol_at_node = type_check(sol_at_node, int) if sol_at_node is not None else None
                self._vis_boundary_only = type_check(vis_boundary_only, bool) if vis_boundary_only is not None else None
                self._curved_mesh_size = type_check(curved_mesh_size, bool) if curved_mesh_size is not None else None
                self._save_solve_sequence_debug = type_check(save_solve_sequence_debug, bool) if save_solve_sequence_debug is not None else None
                self._save_ccd_debug_meshes = type_check(save_ccd_debug_meshes, bool) if save_ccd_debug_meshes is not None else None
                self._save_time_sequence = type_check(save_time_sequence, bool) if save_time_sequence is not None else None
                self._save_nl_solve_sequence = type_check(save_nl_solve_sequence, bool) if save_nl_solve_sequence is not None else None
                self._spectrum = type_check(spectrum, bool) if spectrum is not None else None

            @property
            def timestep_prefix(self):
                return self._timestep_prefix

            @timestep_prefix.setter
            def timestep_prefix(self, value):
                ''' 
                Prefix for output file names for each time step, the final file is step_i.[vtu|vtm] where i is the time index.
                '''
                self._timestep_prefix = type_check(value, str) 

            @property
            def sol_on_grid(self):
                return self._sol_on_grid

            @sol_on_grid.setter
            def sol_on_grid(self, value):
                ''' 
                exports the solution sampled on a grid, specify the grid spacing
                '''
                self._sol_on_grid = type_check(value, float) 

            @property
            def compute_error(self):
                return self._compute_error

            @compute_error.setter
            def compute_error(self, value):
                ''' 
                Enables the computation of the error. If no reference solution is provided, return the norms of the solution
                '''
                self._compute_error = type_check(value, bool) 

            @property
            def sol_at_node(self):
                return self._sol_at_node

            @sol_at_node.setter
            def sol_at_node(self, value):
                ''' 
                Write out solution values at a specific node. the values will be written in the output JSON file
                '''
                self._sol_at_node = type_check(value, int) 

            @property
            def vis_boundary_only(self):
                return self._vis_boundary_only

            @vis_boundary_only.setter
            def vis_boundary_only(self, value):
                ''' 
                saves only elements touching the boundaries
                '''
                self._vis_boundary_only = type_check(value, bool) 

            @property
            def curved_mesh_size(self):
                return self._curved_mesh_size

            @curved_mesh_size.setter
            def curved_mesh_size(self, value):
                ''' 
                upsample curved edges to compute mesh size
                '''
                self._curved_mesh_size = type_check(value, bool) 

            @property
            def save_solve_sequence_debug(self):
                return self._save_solve_sequence_debug

            @save_solve_sequence_debug.setter
            def save_solve_sequence_debug(self, value):
                ''' 
                saves AL internal steps, for debugging
                '''
                self._save_solve_sequence_debug = type_check(value, bool) 

            @property
            def save_ccd_debug_meshes(self):
                return self._save_ccd_debug_meshes

            @save_ccd_debug_meshes.setter
            def save_ccd_debug_meshes(self, value):
                ''' 
                saves AL internal steps, for debugging
                '''
                self._save_ccd_debug_meshes = type_check(value, bool) 

            @property
            def save_time_sequence(self):
                return self._save_time_sequence

            @save_time_sequence.setter
            def save_time_sequence(self, value):
                ''' 
                saves timesteps
                '''
                self._save_time_sequence = type_check(value, bool) 

            @property
            def save_nl_solve_sequence(self):
                return self._save_nl_solve_sequence

            @save_nl_solve_sequence.setter
            def save_nl_solve_sequence(self, value):
                ''' 
                saves obj after every nonlinear iteration, for debugging
                '''
                self._save_nl_solve_sequence = type_check(value, bool) 

            @property
            def spectrum(self):
                return self._spectrum

            @spectrum.setter
            def spectrum(self, value):
                ''' 
                exports the spectrum of the matrix in the output JSON. Works only if POLYSOLVE_WITH_SPECTRA is enabled
                '''
                self._spectrum = type_check(value, bool) 

            def check_required(self):

                return

            def as_dict(self):
                return drop_none({"timestep_prefix": self._timestep_prefix,"sol_on_grid": self._sol_on_grid,"compute_error": self._compute_error,"sol_at_node": self._sol_at_node,"vis_boundary_only": self._vis_boundary_only,"curved_mesh_size": self._curved_mesh_size,"save_solve_sequence_debug": self._save_solve_sequence_debug,"save_ccd_debug_meshes": self._save_ccd_debug_meshes,"save_time_sequence": self._save_time_sequence,"save_nl_solve_sequence": self._save_nl_solve_sequence,"spectrum": self._spectrum,})


        class Reference(object):
            '''Write out the analytic/numerical ground-truth solution and or its gradient
            \nRequired: []
            \nOptional: ['solution', 'gradient']'''
            def __init__(
                self,
                solution: Optional[Iterable[str]] = None,
                gradient: Optional[Iterable[str]] = None
            ):
                self._solution = [] if solution is None else [type_check(i, str) for i in solution]
                self._gradient = [] if gradient is None else [type_check(i, str) for i in gradient]

            @property
            def solution(self):
                return self._solution

            @solution.setter
            def solution(self, value):
                ''' 
                reference solution used to compute errors
                \nRequired: []
                \nOptional: ['value']
                '''
                self._solution = [type_check(i, str) for i in (type_check(value, list) if value else [])]

            def solution_add(self, value):
                '''Add to list '''
                self._solution.append(type_check(value, str))

            def solution_clear(self):
                '''Clear list (make empty)'''
                self._solution.clear()

            def solution_pop(self, index=-1):
                '''Remove by index from list'''
                return self._solution.pop(index)

            def solution_remove(self, item):
                '''Safe remove specific item from list'''
                if item in self._list:
                    self._solution.remove(item)


            @property
            def gradient(self):
                return self._gradient

            @gradient.setter
            def gradient(self, value):
                ''' 
                gradient of the reference solution to compute errors
                \nRequired: []
                \nOptional: ['value']
                '''
                self._gradient = [type_check(i, str) for i in (type_check(value, list) if value else [])]

            def gradient_add(self, value):
                '''Add to list '''
                self._gradient.append(type_check(value, str))

            def gradient_clear(self):
                '''Clear list (make empty)'''
                self._gradient.clear()

            def gradient_pop(self, index=-1):
                '''Remove by index from list'''
                return self._gradient.pop(index)

            def gradient_remove(self, item):
                '''Safe remove specific item from list'''
                if item in self._list:
                    self._gradient.remove(item)


            def check_required(self):

                return

            def as_dict(self):
                return drop_none({"solution": self._solution,"gradient": self._gradient,})



    class Input(object):
        '''input data
        \nRequired: []
        \nOptional: ['data']'''
        def __init__(
            self,
            data: Optional["Root.Input.Data"] = None
        ):
            self._data = type_check(data, self.Data) if data else self.Data()

        @property
        def data(self):
            return self._data

        @data.setter
        def data(self, value):
            ''' 
            input to restart time dependent sim
            \nRequired: []
            \nOptional: ['state', 'reorder']
            '''
            self._data = type_check(value, self.Data) 

        def check_required(self):

            return

        def as_dict(self):
            return drop_none({"data": self._data.as_dict(),})

        class Data(object):
            '''input to restart time dependent sim
            \nRequired: []
            \nOptional: ['state', 'reorder']'''
            def __init__(
                self,
                state: str = '',
                reorder: bool = False
            ):
                self._state = type_check(state, str) if state is not None else None
                self._reorder = type_check(reorder, bool) if reorder is not None else None

            @property
            def state(self):
                return self._state

            @state.setter
            def state(self, value):
                ''' 
                input state as hdf5
                '''
                self._state = type_check(value, str) 

            @property
            def reorder(self):
                return self._reorder

            @reorder.setter
            def reorder(self, value):
                ''' 
                reorder input data
                '''
                self._reorder = type_check(value, bool) 

            def check_required(self):

                return

            def as_dict(self):
                return drop_none({"state": self._state,"reorder": self._reorder,})



    class Tests(object):
        '''Used to test to compare different norms of solutions.
        \nRequired: []
        \nOptional: ['err_h1', 'err_h1_semi', 'err_l2', 'err_linf', 'err_linf_grad', 'err_lp', 'margin', 'time_steps']'''
        def __init__(
            self,
            err_h1: float = 0.0,
            err_h1_semi: float = 0.0,
            err_l2: float = 0.0,
            err_linf: float = 0.0,
            err_linf_grad: float = 0.0,
            err_lp: float = 0.0,
            margin: float = 1e-05,
            time_steps: Optional["Root.Tests.Time_steps"] = None
        ):
            self._err_h1 = type_check(err_h1, float) if err_h1 is not None else None
            self._err_h1_semi = type_check(err_h1_semi, float) if err_h1_semi is not None else None
            self._err_l2 = type_check(err_l2, float) if err_l2 is not None else None
            self._err_linf = type_check(err_linf, float) if err_linf is not None else None
            self._err_linf_grad = type_check(err_linf_grad, float) if err_linf_grad is not None else None
            self._err_lp = type_check(err_lp, float) if err_lp is not None else None
            self._margin = type_check(margin, float) if margin is not None else None
            self._time_steps = type_check(time_steps, self.Time_steps) if time_steps else self.Time_steps()

        @property
        def err_h1(self):
            return self._err_h1

        @err_h1.setter
        def err_h1(self, value):
            ''' 
            Reference h1 solution's norm.
            '''
            self._err_h1 = type_check(value, float) 

        @property
        def err_h1_semi(self):
            return self._err_h1_semi

        @err_h1_semi.setter
        def err_h1_semi(self, value):
            ''' 
            Reference h1 seminorm solution's norm.
            '''
            self._err_h1_semi = type_check(value, float) 

        @property
        def err_l2(self):
            return self._err_l2

        @err_l2.setter
        def err_l2(self, value):
            ''' 
            Reference $L^2$ solution's norm.
            '''
            self._err_l2 = type_check(value, float) 

        @property
        def err_linf(self):
            return self._err_linf

        @err_linf.setter
        def err_linf(self, value):
            ''' 
            Reference $L^\\infty$ solution's norm.
            '''
            self._err_linf = type_check(value, float) 

        @property
        def err_linf_grad(self):
            return self._err_linf_grad

        @err_linf_grad.setter
        def err_linf_grad(self, value):
            ''' 
            Reference $L^\\infty$ solution's gradient norm.
            '''
            self._err_linf_grad = type_check(value, float) 

        @property
        def err_lp(self):
            return self._err_lp

        @err_lp.setter
        def err_lp(self, value):
            ''' 
            Reference $L^8$ solution's gradient norm.
            '''
            self._err_lp = type_check(value, float) 

        @property
        def margin(self):
            return self._margin

        @margin.setter
        def margin(self, value):
            ''' 
            Reference tolerance used in tests.
            '''
            self._margin = type_check(value, float) 

        @property
        def time_steps(self):
            return self._time_steps

        @time_steps.setter
        def time_steps(self, value):
            ''' 
            This is a polymorphic variable, assign an object from its classes to the value
            \nRequired: []
            \nOptional: ['int', 'string']
            '''
            self._time_steps = type_check(value, self.Time_steps) 

        def check_required(self):

            return

        def as_dict(self):
            return drop_none({"err_h1": self._err_h1,"err_h1_semi": self._err_h1_semi,"err_l2": self._err_l2,"err_linf": self._err_linf,"err_linf_grad": self._err_linf_grad,"err_lp": self._err_lp,"margin": self._margin,"time_steps": self._time_steps.as_dict(),})

        class Time_steps(object):
            '''This is a polymorphic variable, assign an object from its classes to the value
            \nRequired: []
            \nOptional: ['int', 'string']'''
            def __init__(
                self,
                value : object = None
            ):
                self._value = class_check(value, [int, string]) if value is not None else None

            @property
            def value(self):
                return self._value

            @value.setter
            def value(self, value):
                ''' 
                This is a polymorphic variable, assign an object from its classes to the value
                '''
                self._value = class_check(value, [int, string]) 

            def check_required(self):

                if self.value is None:
                    print("Requiered variable Root.Tests.Time_steps.value does not have value")
                else:
                    if type(self.value) not in [['int', 'float', 'list', 'str', 'bool']]:
                        self.value.check_required()
                return

            def as_dict(self):
                return drop_none(self._value.as_dict() if isinstance(self._value, tuple([])) else self._value)



