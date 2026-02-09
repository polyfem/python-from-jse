import json
import textwrap

class ClassGenerator(object):
    def __init__(self, class_name : str, doc : str):
        self._class_name = class_name.capitalize()
        self._doc = doc
        self._init_input = []
        self._init_body = []
        self._property_setter = []
        self._as_dict = []
        self._inner_classes = []
        self._enum = ""

    def set_enum(self, variable):
        enum = []
        for option in variable._optional:
            enum.append(
                f'{option.upper()} = "{option}"'
            )

        INDENT = " " * 8
        enum_body = (",\n").join(
            INDENT + p for p in enum
        )

        result = f"""
    class {variable.name.capitalize()}(str, Enum):
{enum_body}
    """
        self._enum = result

    def set_init_list(self, variable):
        #type = variable.type if variable.type != "string" else "str"
        if not self._init_input:
            allowed_classes =  ["self." + k.capitalize() for k in variable._optional]
            allowed_classes = ", ".join(allowed_classes)

            self._init_input.append(
                'items : list = None'
            )
            self._init_body.append(
                f'self._items = [class_check(i, [{allowed_classes}]) for i in (type_check(items, list) if items else [])]'
            )
            self._as_dict.append(
                f'[i.as_dict() for i in self._items]'
            )

        """ def __init__(self, items=None):
            self._list = list(items) if items else [] """
        """ [i.as_dict() for i in self._list] """

    def set_init_polymorphic(self, variable, path):
        if not self._init_input:
            allowed_classes = []
            dict_condition = []
            for k in variable._optional:
                if k[-1].isdigit():
                    allowed_classes.append("self." + k.capitalize())
                    dict_condition.append("self." + k.capitalize())
                else:
                    allowed_classes.append(k)

            allowed_classes = ", ".join(allowed_classes)
            dict_condition = ", ".join(dict_condition)

            self._init_input.append(
                f'value : object = None'
            )
            self._init_body.append(
                f'self._value = class_check(value, [{allowed_classes}]) if value is not None else None'
            )
            self._as_dict.append(
                f'self._value.as_dict() if isinstance(self._value, tuple([{dict_condition}])) else self._value'
            )
    
    def set_init(self, variable, path):
        type = variable.type if variable.type != "string" else "str"
        child = variable
        for value in variable._optional.values():
            child = value
        #for objects and lists with polymorphism
        if variable.type == "object" or (variable.type == "list" and (len(variable._optional) > 1 or child.type == "object") or variable.type == "polymorphic"):
            self._init_input.append(
                f'{variable.name}: Optional["{path}"] = None'
            )
            self._init_body.append(
                f'self._{variable.name} = {variable.name} if {variable.name} else {path}()'
            )
            self._as_dict.append(
                f'"{variable.name}": self._{variable.name}.as_dict(),'
            )
        #for lists without polymorphism
        elif variable.type == "list" and len(variable._optional) == 1:
            #default = variable.default if variable.default else None
            #(child,) = variable._optional.values()
            child_type = child.type if child.type != "string" else "str"
            self._init_input.append(
                f'{variable.name}: Optional[Iterable[{child_type}]] = None'
            )
            self._init_body.append(
                f'self._{variable.name} = [] if {variable.name} is None else [type_check(i, {child_type}) for i in {variable.name}]'
            )
            self._as_dict.append(
                f'"{variable.name}": self._{variable.name},'
            )
        #For string with options
        elif variable.type == "string" and len(variable._optional) > 0:
            self.set_enum(variable)
            self._init_input.append(
                f'{variable.name}: {variable.name.capitalize()} = {variable.default}'
            )
            self._init_body.append(
                f'self._{variable.name} = enum_check({variable.name}, self.{variable.name.capitalize()})'
            )
            self._as_dict.append(
                f'"{variable.name}": self._{variable.name}.value if self._{variable.name} is not None else None,'
            )
        #For file types with extensions limit
        elif variable.type == "string" and variable.extensions:
            type = "str"
            self._init_input.append(
                f'{variable.name}: {type} = {variable.default}'
            )
            self._init_body.append(
                f'self._{variable.name} = extension_check({variable.name}, {variable.extensions}) if {variable.name} is not None else None'
            )
            self._as_dict.append(
                f'"{variable.name}": self._{variable.name},'
            )
        #For other types (string, int and float)
        else :
            #default = variable.default if variable.default else None
            self._init_input.append(
                f'{variable.name}: {type} = {float(variable.default) if type == "float" and variable.default is not None else variable.default}'
            )
            self._init_body.append(
                f'self._{variable.name} = type_check({variable.name}, {type}) if {variable.name} is not None else None'
            )
            self._as_dict.append(
                f'"{variable.name}": self._{variable.name},'
            )
    
    def set_property_setter_list(self, variable):
        if not self._property_setter:
            allowed_classes =  ["self." + k.capitalize() for k in variable._optional]
            allowed_classes = ", ".join(allowed_classes)

            self._property_setter.append(
            f""" 
    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, item : object):
        ''' Add to the list '''
        self._items.append(class_check(item, [{allowed_classes}]))

    # CLEAR (make empty)
    def clear(self):
        '''Clear list (make empty)'''
        self._items.clear()

    def pop(self, index=-1):
        '''Remove by index from list'''
        return self._items.pop(index)

    def remove(self, item):
        '''Safe remove specific item from list'''
        if item in self._items:
            self._items.remove(item) """
            )
    
    def set_property_setter_polymorphic(self, variable):
        if not self._property_setter:
            allowed_classes =  [("self." + k.capitalize() if k[-1].isdigit() else k) for k in variable._optional]
            allowed_classes = ", ".join(allowed_classes)
            inside_setter = f"self._value = class_check(value, [{allowed_classes}])"
            self._property_setter.append(
            f""" 
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        ''' 
        {variable.doc}
        '''
        {inside_setter} """
        )

    def set_property_setter(self, variable):
        type = variable.type if variable.type != "string" else "str"
        child = variable
        for value in variable._optional.values():
            child = value

        if type == "object" or type == "polymorphic" or type == "list":
            type_check = f'self.{variable.name.capitalize()}'
        else:
            type_check = type

        if variable.type == "list" and len(variable._optional) == 1 and child.type != "object":
            child_type = child.type if child.type != "string" else "str"
            inside_setter = f"""self._{variable.name}.append(type_check(value, {child_type}))

    def clear(self):
        '''Clear list (make empty)'''
        self._{variable.name}.clear()

    def pop(self, index=-1):
        '''Remove by index from list'''
        return self._{variable.name}.pop(index)

    def remove(self, item):
        '''Safe remove specific item from list'''
        if item in self._list:
            self._{variable.name}.remove(item)
        """
        #for strings with options
        elif variable.type == "string" and len(variable._optional) > 0:
            inside_setter = f"self._{variable.name} = enum_check(value, self.{variable.name.capitalize()})"
        #for file names with extensions limit
        elif variable.type == "string" and variable.extensions:
            inside_setter = f"self._{variable.name} = extension_check(value, {variable.extensions})"
        #for other types
        else:
            inside_setter = f"self._{variable.name} = type_check(value, {type_check})"
        
        self._property_setter.append(
            f""" 
    @property
    def {variable.name}(self):
        return self._{variable.name}

    @{variable.name}.setter
    def {variable.name}(self, value):
        ''' 
        {variable.doc}
        '''
        {inside_setter} """
        )

    def set_inner_classes(self, inner_class):
        self._inner_classes.append(
            inner_class
        )

    def generate(self, type):
        INDENT = " " * 8
        init_input = (",\n").join(
            INDENT + p for p in self._init_input
        )

        init_body = ("\n").join(
            INDENT + p for p in self._init_body
        )

        property_setter = ("\n").join(
            p for p in self._property_setter
        )

        as_dict = ("").join(
            p for p in self._as_dict
        )

        inner_classes = ("").join(
            p for p in self._inner_classes
        )

        as_dict = as_dict if type == "list" or type == "polymorphic" else "{" + as_dict + "}"

        result = f"""
class {self._class_name}(object):
    '''{self._doc}'''{self._enum}
    def __init__(
        self,
{init_input}
    ):
{init_body}
{property_setter}

    def as_dict(self):
        return drop_none({as_dict})
{inner_classes}
"""
        #print(result)
        return result


class JsonToTreeClass(object):

    def __init__(self, name):
        self.name = name
        self.default = None
        self.type = None
        self._required = {}
        self._optional = {}
        self.doc = "There is no definition"
        self.extensions = []
        # self.camera: str = 'you'

    def __str__(self):
        return self._to_string()

    def _to_string(self, indent=0):
        space = "  " * indent
        result = f"{space}{self.name}\n"

        if self._optional:
            result += f"{space}Optional:\n"
            for key, obj in self._optional.items():
                result += obj._to_string(indent + 1)

        if self._required:
            result += f"{space}Required:\n"
            for key, obj in self._required.items():
                result += obj._to_string(indent + 1)

        return result

    def set_doc(self, discription : str):
        self.doc = discription

    def set_default(self, value):
        self.default = value

    def set_type(self, value):
        self.type = value

    def set_extensions(self, value):
        self.extensions = value

    def indent(self, code):
        return textwrap.indent(
            textwrap.dedent(code),
            "    ",
            lambda line: line.strip() != ""
        )

    def add_required(self, var_name):
        var_obj = JsonToTreeClass(var_name)
        self._required[var_name] = var_obj

    def get_required(self, var_name):
        return self._required.get(var_name)
    
    def add_optional(self, var_name):
        var_obj = JsonToTreeClass(var_name)
        self._optional[var_name] = var_obj

    def get_optional(self, var_name):
        return self._optional.get(var_name)
    
    def make_it_polymorphic(self):
        polymorph = JsonToTreeClass(self.name)
        polymorph.doc = "This is a polymorphic variable, assign an object from its classes to the value"
        polymorph.type = "polymorphic"
        if self.type != "object":
            self.name = self.type
        else:
            self.name = self.type + "1"
        polymorph.add_optional(self.name)
        polymorph._optional[self.name] = self
        return polymorph

    def find_var_replace(self, part, value):
        required = self.get_required(part)
        optional = self.get_optional(part)
        if required is not None:
            self._required[part] = value
        elif optional is not None:
            self._optional[part] = value

    #Finding the variable in the tree
    def find_var(self, parts: list):
        if not parts:
            return self, None

        #handling list routing
        if (parts[0] == "*" and len(parts) > 1) or (self.type == "polymorphic" and len(parts) > 0):
            #A condition for rest of the if to work with polymorphic type
            if self.type == "polymorphic":
                parts = ["*"] + parts
                
            for child in self._optional.values():
                required = child.get_required(parts[1])
                optional = child.get_optional(parts[1])

                if required is not None:
                    node, parent = required.find_var(parts[2:])
                    return node, self

                if optional is not None:
                    node, parent = optional.find_var(parts[2:])
                    return node, self

        required = self.get_required(parts[0])
        optional = self.get_optional(parts[0])

        if required is not None:
            node, parent = required.find_var(parts[1:])
            return node, parent or self

        if optional is not None:
            node, parent = optional.find_var(parts[1:])
            return node, parent or self

        return self, None

    def class_generator(self, path = "Root"):
        class_builder = ClassGenerator(self.name, self.doc)
        for required in self._required.values():
            #print(self.name)
            inner_path = path + "." + required.name.capitalize()
            class_builder.set_init(required, inner_path)
            class_builder.set_property_setter(required)
                
            for value in required._optional.values():
                child = value

            if required.type == "object" or (required.type == "list" and (len(required._optional) > 1 or child.type == "object")) or required.type == "polymorphic":
                inner_class = required.class_generator(inner_path)
                inner_class = self.indent(inner_class)
                class_builder.set_inner_classes(inner_class)

        for optional in self._optional.values():
            #print(self.name)
            inner_path = path + "." + optional.name.capitalize()
            if self.type == "list":
                class_builder.set_init_list(self)
                class_builder.set_property_setter_list(self)
            elif self.type == "polymorphic":
                class_builder.set_init_polymorphic(self, path)
                class_builder.set_property_setter_polymorphic(self)
            else:
                class_builder.set_init(optional, inner_path)
                class_builder.set_property_setter(optional)

            for value in optional._optional.values():
                child = value

            if optional.type == "object" or (optional.type == "list" and (len(optional._optional) > 1 or child.type == "object")) or optional.type == "polymorphic":
                inner_class = optional.class_generator(inner_path)
                inner_class = self.indent(inner_class)
                class_builder.set_inner_classes(inner_class)

        print(path)
        return class_builder.generate(self.type)
        """ optional = self.get_optional(parts[0])
        if optional == "No set":
            self.add_optional(parts[0])
            optional = self.get_optional(parts[0])
        return optional.find_optional_var(parts[1:]) """
        

"""
    def show_all_grades(self):
        for course, grade in self.grades.items():
            print(f"{course}: {grade}")
""" 

root = JsonToTreeClass("root")
geometry = JsonToTreeClass("geometry")
#root.add_required("geometry", geometry)

#geometry.name = "hasan"
#print(root.get_required("geometry").name)

schema_file = "Untitled-1.json"
#schema_file = "input-spec.json"
with open(schema_file) as f:
    schema = json.load(f)

""" setting value of json to the class """
for entry in schema:
    name = "root" if entry['pointer'] == "/" else entry['pointer']
    #print(name)
    parts = [name] if name == 'root' else name.strip('/').split('/')
    #print(parts[-1])

    if parts[-1] == 'root':
        path = root
        parent = root
    else:
        path, parent = root.find_var(parts)

    #handling list variables
    if path.type == "list" and parts[-1] == '*':
        if entry.get('type_name'):
            path.add_optional(entry.get('type_name'))
            path = path.get_optional(entry.get('type_name'))
        else: 
            path.add_optional("value")
            path = path.get_optional("value")

    #handeling polymorfic variables
    if path.type == "polymorphic":
        if entry.get('type') != "object":
            routing = entry.get('type')
        else:
            routing = entry.get('type') + str(len(path._optional) + 1)
        path.add_optional(routing)
        path = path.get_optional(routing)
        
    elif path.type is not None:
        polymorph = path.make_it_polymorphic()
        if entry.get('type') != "object":
            routing = entry.get('type')
        else:
            routing = entry.get('type') + "2"
        polymorph.add_optional(routing)
        parent.find_var_replace(polymorph.name, polymorph)
        path = polymorph.get_optional(routing)

    if entry.get('required'):
        for value in entry.get('required'):
            #optional = JsonToTreeClass(value)
            path.add_required(value)
            #print(path.get_optional(value).name)

    if entry.get('optional'):
        for value in entry.get('optional'):
            #optional = JsonToTreeClass(value)
            path.add_optional(value)
            #print(path.get_optional(value).name)

    if entry.get('options'):
        for value in entry.get('options'):
            #optional = JsonToTreeClass(value)
            path.add_optional(value)
            #print(path.get_optional(value).name)

    doc = entry.get('doc')
    if doc:
        path.set_doc(doc)
        
    default = entry.get('default')
    path.set_default(default)
    
    type = entry.get('type') if entry.get('type') != "file" else "string"
    path.set_type(type)
    
    extensions = entry.get('extensions')
    path.set_extensions(extensions)

    if (len(parts) > 1 and parts[-2] == '*') or parent.type == "polymorphic":
        for child in parent._optional.values():
            child.find_var_replace(parts[-1], path)

    #print (path.name)

"""
    if entry['pointer'] == "/":
        root = JsonToTreeClass("root")
        if entry.get('optional'):
            print(entry['optional']) 
"""
print(root.get_optional("geometry").get_optional("nested").name)


generated_class = root.class_generator()

generated_class = """
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

def type_check(variable, tp):
    if not isinstance(variable, tp):
        raise TypeError(f"Expected type '{tp.__name__}', but got '{type(variable).__name__}'")
    return variable
""" + generated_class

with open("generated_class.py", "w", encoding="utf-8") as f:
    f.write(generated_class)

print(root)

print(root.get_optional("geometry").get_optional("nested").default)

print(root.get_optional("materials").get_optional("MooneyRivlin").get_optional("id").type)

print(root.get_optional("materials").get_optional("MooneyRivlin").get_optional("elasticity_tensor")
      .get_optional("value").get_required("input").type)

id = root.get_optional("materials").get_optional("MooneyRivlin").get_optional("id")
(x,) = id._optional.values()
print (x)

print(root.get_optional("geometry").get_optional("mesh_sequence").extensions)

#print(root.get_required("time").get_optional("int3").type)
#print(root._optional["ali"])
""" 
tree = {'children': {}, 'props': {}, 'required': [], 'optional': []}
for entry in schema:
    ptr = entry['pointer'].strip('/')
    parts = ptr.split('/') if ptr else []
    node = tree
    for part in parts[:-1]:
        node = node['children'].setdefault(part, {'children': {}, 'props': {}, 'required': [], 'optional': []})
    if entry.get('type') == 'object':
        if entry.get('required'):
            node['required'] = entry['required']
        if entry.get('optional'):
            node['optional'] = entry['optional']
    else:
        last = parts[-1]
        node['props'][last] = entry
 """

#print(root._type)
#print(root.get_optional("geometry")._type)
#print(schema)