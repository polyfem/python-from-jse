import json
import textwrap

class ClassGenerator(object):
    def __init__(self, class_name : str, doc : str, required, optional):
        self._class_name = class_name.capitalize()
        self._doc = f"""{doc}
    \\nRequired: {required}
    \\nOptional: {optional}"""
        self._init_input = []
        self._init_body = []
        self._property_setter = []
        self._as_dict = []
        self._inner_classes = []
        self._check_required = []
        self._enum = ""

    def set_enum(self, node):
        enum = []
        for option in node._optional:
            enum.append(
                f'{option.upper()} = "{option}"'
            )

        INDENT = " " * 8
        enum_body = (",\n").join(
            INDENT + p for p in enum
        )

        result = f"""
    class {node.name.capitalize()}(str, Enum):
{enum_body}
    """
        self._enum = result

    def set_init_list(self, node):
        #type = node.type if node.type != "string" else "str"
        if not self._init_input:
            allowed_classes = []
            dict_condition = []
            for k in node._optional:
                if k == "str" or k == "int" or k == "float" or k == "bool":
                    allowed_classes.append(k)
                else:
                    allowed_classes.append("self." + k.capitalize())
                    dict_condition.append("self." + k.capitalize())
                    

            allowed_classes = ", ".join(allowed_classes)
            dict_condition = ", ".join(dict_condition)

            self._init_input.append(
                'items : list = None'
            )
            self._init_body.append(
                f'self._items = [class_check(i, [{allowed_classes}]) for i in (type_check(items, list) if items else [])]'
            )
            self._as_dict.append(
                f'[i.as_dict() if isinstance(i, tuple([{dict_condition}])) else i for i in self._items]'
            )

        """ def __init__(self, items=None):
            self._list = list(items) if items else [] """
        """ [i.as_dict() for i in self._list] """

    def set_init_polymorphic(self, node, path):
        if not self._init_input:
            allowed_classes = []
            dict_condition = []
            for k in node._optional:
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
    
    def set_init(self, node, path):
        type = node.type if node.type != "string" else "str"
        child = node
        for value in node._optional.values():
            child = value
        #for objects and lists with polymorphism
        if node.type == "object" or (node.type == "list" and (len(node._optional) > 1 or child.type == "object") or node.type == "polymorphic"):
            self._init_input.append(
                f'{node.name}: Optional["{path}"] = None'
            )
            self._init_body.append(
                f'self._{node.name} = type_check({node.name}, self.{node.name.capitalize()}) if {node.name} else self.{node.name.capitalize()}()'
            )
            self._as_dict.append(
                f'"{node.name}": self._{node.name}.as_dict(),'
            )
        #for lists without polymorphism
        elif node.type == "list" and len(node._optional) == 1:
            #default = node.default if node.default else None
            #(child,) = node._optional.values()
            child_type = child.type if child.type != "string" else "str"
            self._init_input.append(
                f'{node.name}: Optional[Iterable[{child_type}]] = None'
            )
            self._init_body.append(
                f'self._{node.name} = [] if {node.name} is None else [type_check(i, {child_type}) for i in {node.name}]'
            )
            self._as_dict.append(
                f'"{node.name}": self._{node.name},'
            )
        #For string with options
        elif node.type == "string" and len(node._optional) > 0:
            self.set_enum(node)
            self._init_input.append(
                f'{node.name}: {node.name.capitalize()} = {node.default}'
            )
            self._init_body.append(
                f'self._{node.name} = enum_check({node.name}, self.{node.name.capitalize()})'
            )
            self._as_dict.append(
                f'"{node.name}": self._{node.name}.value if self._{node.name} is not None else None,'
            )
        #For file types with extensions limit
        elif node.type == "string" and node.extensions:
            type = "str"
            self._init_input.append(
                f'{node.name}: {type} = {node.default}'
            )
            self._init_body.append(
                f'self._{node.name} = extension_check(type_check({node.name}, str), {node.extensions}) if {node.name} is not None else None'
            )
            self._as_dict.append(
                f'"{node.name}": self._{node.name},'
            )
        #For other types (string, int and float)
        else :
            self._init_input.append(
                    f'{node.name}: {type} = {float(node.default) if type == "float" and node.default is not None else node.default}'
                )
            if node.min is not None or node.max is not None:
                self._init_body.append(
                    f'self._{node.name} = range_check(type_check({node.name}, {type}), {node.min}, {node.max}) if {node.name} is not None else None'
                )
            else:
                self._init_body.append(
                    f'self._{node.name} = type_check({node.name}, {type}) if {node.name} is not None else None'
                )
            self._as_dict.append(
                f'"{node.name}": self._{node.name},'
            )
    
    def set_check_required_polymorphic(self, path):
        if not self._check_required:
            type_list = ["int", "float", "list", "str", "bool"]

            self._check_required.append(
                    f"""
        if self.value is None:
            print("Requiered variable {path}.value does not have value")
        else:
            if type(self.value) not in [{type_list}]:
                self.value.check_required()"""
                )

    def set_check_required_list(self, path):
        if not self._check_required:
            type_list = ["int", "float", "list", "str", "bool"]
            
            self._check_required.append(
                    f"""
        if self.items:
            for item in self.items:
                if type(item) not in [{type_list}]:
                    item.check_required()
        else:
            print("Requiered variable {path}.items does not have value")"""
                    )

    def set_check_required(self, node, path):
        child = node
        for value in node._optional.values():
            child = value
        #for objects and lists with polymorphism
        if node.type == "object" or (node.type == "list" and (len(node._optional) > 1 or child.type == "object") or node.type == "polymorphic"):
            self._check_required.append(
                f"self.{node.name}.check_required()"
            )
        #for lists without polymorphism
        elif node.type == "list" and len(node._optional) == 1:
            self._check_required.append(
                f"""
        if self.{node.name}:
            print("Requiered variable {path} does not have value")"""
                )
        else :
            self._check_required.append(
                f"""
        if self.{node.name} is None:
            print("Requiered variable {path} does not have value")"""
                )

    def set_property_setter_list(self, node):
        if not self._property_setter:
            allowed_classes =  ["self." + k.capitalize() for k in node._optional]
            allowed_classes = ", ".join(allowed_classes)

            self._property_setter.append(
            f""" 
    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, items : list):
        ''' Replace the list '''
        self._items = [class_check(i, [{allowed_classes}]) for i in (type_check(items, list) if items else [])]

    def add(self, item : object):
        ''' Add to the list '''
        self._items.append(class_check(item, [{allowed_classes}]))

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
    
    def set_property_setter_polymorphic(self, node):
        if not self._property_setter:
            allowed_classes =  [("self." + k.capitalize() if k[-1].isdigit() else k) for k in node._optional]
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
        {node.doc}
        '''
        {inside_setter} """
        )

    def set_property_setter(self, node):
        type = node.type if node.type != "string" else "str"
        child = node
        required_optional = ""
        for value in node._optional.values():
            child = value

        if type == "object" or type == "polymorphic" or type == "list":
            type_check = f'self.{node.name.capitalize()}'
            required_optional = f"""
        \\nRequired: {list(node._required)}
        \\nOptional: {list(node._optional)}"""
        else:
            type_check = type

        if node.type == "list" and len(node._optional) == 1 and child.type != "object":
            child_type = child.type if child.type != "string" else "str"
            inside_setter = f"""self._{node.name} = [type_check(i, {child_type}) for i in (type_check(value, list) if value else [])]

    def {node.name}_add(self, value):
        '''Add to list '''
        self._{node.name}.append(type_check(value, {child_type}))
            
    def {node.name}_clear(self):
        '''Clear list (make empty)'''
        self._{node.name}.clear()

    def {node.name}_pop(self, index=-1):
        '''Remove by index from list'''
        return self._{node.name}.pop(index)

    def {node.name}_remove(self, item):
        '''Safe remove specific item from list'''
        if item in self._list:
            self._{node.name}.remove(item)
        """
        #for strings with options
        elif node.type == "string" and len(node._optional) > 0:
            inside_setter = f"self._{node.name} = enum_check(value, self.{node.name.capitalize()})"
        #for file names with extensions limit
        elif node.type == "string" and node.extensions:
            inside_setter = f"self._{node.name} = extension_check(type_check(value, str), {node.extensions})"
        #for other types
        else:
            if node.min is not None or node.max is not None:
                inside_setter = f"self._{node.name} = range_check(type_check(value, {type_check}), {node.min}, {node.max})"
            else:
                inside_setter = f"self._{node.name} = type_check(value, {type_check})"
        
        self._property_setter.append(
            f""" 
    @property
    def {node.name}(self):
        return self._{node.name}

    @{node.name}.setter
    def {node.name}(self, value):
        ''' 
        {node.doc}{required_optional}
        '''
        {inside_setter} """
        )

    def set_inner_classes(self, inner_class):
        self._inner_classes.append(
            inner_class
        )

    def generate(self, type):
        INDENT = "    "
        init_input = (",\n").join(
            INDENT * 2 + p for p in self._init_input
        )

        init_body = ("\n").join(
            INDENT * 2 + p for p in self._init_body
        )

        check_required = ("\n").join(
            INDENT * 2 + p for p in self._check_required
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

    def check_required(self):
{check_required}
        return

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
        self.min = None
        self.max = None
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

    def set_min(self, value):
        self.min = value

    def set_max(self, value):
        self.max = value

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

        if len(parts) > 0 and parts[-1] != "*":
            raise ValueError(
                "Specification file does not conform to the required hierarchy.\n"
                f'Variable "{parts[-1]}" defined before its parent.'
            )

        return self, None

    def class_generator(self, path = "Root"):
        class_builder = ClassGenerator(self.name, self.doc, list(self._required), list(self._optional))
        for required in self._required.values():
            #print(self.name)
            inner_path_capitalize = path + "." + required.name.capitalize()
            inner_path = path + "." + required.name
            class_builder.set_init(required, inner_path_capitalize)
            class_builder.set_check_required(required, inner_path)
            class_builder.set_property_setter(required)
                
            for value in required._optional.values():
                child = value

            if required.type == "object" or (required.type == "list" and (len(required._optional) > 1 or child.type == "object")) or required.type == "polymorphic":
                inner_class = required.class_generator(inner_path_capitalize)
                inner_class = self.indent(inner_class)
                class_builder.set_inner_classes(inner_class)

        for optional in self._optional.values():
            #print(self.name)
            inner_path_capitalize = path + "." + optional.name.capitalize()
            if self.type == "list":
                class_builder.set_init_list(self)
                class_builder.set_property_setter_list(self)
                class_builder.set_check_required_list(path)
            elif self.type == "polymorphic":
                class_builder.set_init_polymorphic(self, path)
                class_builder.set_property_setter_polymorphic(self)
                class_builder.set_check_required_polymorphic(path)
            else:
                class_builder.set_init(optional, inner_path_capitalize)
                class_builder.set_property_setter(optional)

            for value in optional._optional.values():
                child = value

            if optional.type == "object" or (optional.type == "list" and (len(optional._optional) > 1 or child.type == "object")) or optional.type == "polymorphic":
                inner_class = optional.class_generator(inner_path_capitalize)
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

type_list = ["object", "int", "float", "list", "string", "bool", "file"]
""" setting value of json to the class """
for entry in schema:
    type = entry.get('type')
    if type not in type_list:
        raise ValueError(f'Type "{type}" is not supported by the system. \nAcceptable types: {type_list}')

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

    path.set_min(entry.get('min'))
    path.set_max(entry.get('max'))

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
#print(root.get_optional("geometry").get_optional("nested").name)


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
""" + generated_class

with open("generated_class.py", "w", encoding="utf-8") as f:
    f.write(generated_class)

print(root)

#print(root.get_optional("geometry").get_optional("nested").default)

print(root.get_optional("materials").get_optional("MooneyRivlin").get_optional("id").type)

print(root.get_optional("materials").get_optional("MooneyRivlin").get_optional("elasticity_tensor")
      .get_optional("value").get_required("input").type)

id = root.get_optional("materials").get_optional("MooneyRivlin").get_optional("id")
(x,) = id._optional.values()
print (x)

#print(root.get_optional("geometry").get_optional("mesh_sequence").extensions)

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