import json
import keyword
from pathlib import Path
import re
import textwrap

def py_identifier(value):
    name = re.sub(r"\W+", "_", str(value)).strip("_")
    if not name:
        name = "value"
    if name[0].isdigit():
        name = f"value_{name}"
    if keyword.iskeyword(name):
        name = f"{name}_"
    return name

def py_class_name(value):
    parts = re.split(r"\W+", str(value))
    name = "".join(part[:1].upper() + part[1:] for part in parts if part)
    if not name:
        name = "Value"
    if name[0].isdigit():
        name = f"Value{name}"
    if keyword.iskeyword(name):
        name = f"{name}_"
    return name

PRIMITIVE_TYPE_EXPRESSIONS = {
    "str": "str",
    "string": "str",
    "int": "int",
    "float": "float",
    "bool": "bool",
    "list": "list",
}

INLINE_PRIMITIVE_TYPES = set(PRIMITIVE_TYPE_EXPRESSIONS)
LIST_ITEM_NAME = "item"

def is_value_with_unit_node(node):
    return (
        node.type == "object"
        and node.type_name is None
        and set(node._required) == {"value", "unit"}
        and not node._optional
    )

def is_inline_polymorphic(node):
    if node.type != "polymorphic" or node.type_name is not None:
        return False

    if not node._optional:
        return False

    for child in node._optional.values():
        if child.type == "list" and not is_structured_list_node(child):
            continue
        if child.type == "list":
            return False
        if child.type in INLINE_PRIMITIVE_TYPES:
            continue
        if is_value_with_unit_node(child):
            continue
        return False

    return True

def is_structured_list_node(node):
    if node.type != "list":
        return False

    if len(node._optional) > 1:
        return True

    child = None
    for value in node._optional.values():
        child = value

    return child is not None and child.type in ("object", "polymorphic")

class ClassGenerator(object):
    def __init__(self, class_name : str, doc : str, required, optional):
        self._class_name = py_class_name(class_name)
        doc = self.doc_text(doc)
        self._doc = f"""{doc}
    \\nRequired: {required}
    \\nOptional: {optional}"""
        self._init_input = []
        self._init_body = []
        self._property_setter = []
        self._as_dict = []
        self._inner_classes = []
        self._check_required = []
        self._enums = []
        self._field_names = {}
        self._field_name_counts = {}

    def default_literal(self, node, type_name):
        if type_name == "float" and node.default is not None:
            return repr(float(node.default))
        return repr(node.default)

    def field_name(self, node):
        key = id(node)
        if key in self._field_names:
            return self._field_names[key]

        base = py_identifier(node.name)
        count = self._field_name_counts.get(base, 0)
        name = base if count == 0 else f"{base}_{count + 1}"
        self._field_name_counts[base] = count + 1
        self._field_names[key] = name
        return name

    def doc_text(self, value):
        return str(value).replace("\\", "\\\\")

    def enum_member_name(self, option, used):
        name = re.sub(r"\W+", "_", str(option).upper()).strip("_")
        if not name:
            name = "VALUE"
        if name[0].isdigit():
            name = f"VALUE_{name}"

        base = name
        index = 2
        while name in used:
            name = f"{base}_{index}"
            index += 1
        used.add(name)
        return name

    def inline_schema_expr(self, node):
        required = list(node._required)
        optional = list(node._optional)
        field_parts = []

        for child in list(node._required.values()) + list(node._optional.values()):
            allowed_expr, schemas_expr = self.inline_allowed_expr(child)
            field_parts.append(
                f'{repr(child.name)}: ({allowed_expr}, {schemas_expr})'
            )

        fields_expr = "{" + ", ".join(field_parts) + "}"
        return (
            "{"
            f'"required": {required!r}, '
            f'"optional": {optional!r}, '
            f'"fields": {fields_expr}'
            "}"
        )

    def inline_allowed_expr(self, node):
        allowed = []
        schemas = []

        if node.type == "polymorphic":
            children = node._optional.values()
        else:
            children = [node]

        for child in children:
            if child.type in PRIMITIVE_TYPE_EXPRESSIONS:
                allowed.append(PRIMITIVE_TYPE_EXPRESSIONS[child.type])
            elif child.type == "list":
                allowed.append("list")
            elif is_value_with_unit_node(child):
                schemas.append(self.inline_schema_expr(child))

        allowed_expr = "[" + ", ".join(allowed) + "]"
        schemas_expr = "[" + ", ".join(schemas) + "]"
        return allowed_expr, schemas_expr

    def set_enum(self, node):
        enum = []
        used_names = set()
        for option in node._optional:
            enum.append(
                f'{self.enum_member_name(option, used_names)} = {repr(option)}'
            )

        INDENT = " " * 8
        enum_body = ("\n").join(
            INDENT + p for p in enum
        )

        result = f"""
    class {py_class_name(node.name)}(str, Enum):
{enum_body}
    """
        self._enums.append(result)

    def set_init_list(self, node):
        #type = node.type if node.type != "string" else "str"
        if not self._init_input:
            allowed_classes = []
            dict_condition = []
            for k, child in node._optional.items():
                if k in PRIMITIVE_TYPE_EXPRESSIONS:
                    allowed_classes.append(PRIMITIVE_TYPE_EXPRESSIONS[k])
                    if k == "list" and is_structured_list_node(child):
                        allowed_classes.append("self." + py_class_name(k))
                        dict_condition.append("self." + py_class_name(k))
                elif child.type in PRIMITIVE_TYPE_EXPRESSIONS:
                    allowed_classes.append(PRIMITIVE_TYPE_EXPRESSIONS[child.type])
                else:
                    allowed_classes.append("self." + py_class_name(k))
                    dict_condition.append("self." + py_class_name(k))
                    

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
            for k, child in node._optional.items():
                if k in PRIMITIVE_TYPE_EXPRESSIONS:
                    allowed_classes.append(PRIMITIVE_TYPE_EXPRESSIONS[k])
                    if k == "list" and is_structured_list_node(child):
                        allowed_classes.append("self." + py_class_name(k))
                        dict_condition.append("self." + py_class_name(k))
                elif child.type in PRIMITIVE_TYPE_EXPRESSIONS:
                    allowed_classes.append(PRIMITIVE_TYPE_EXPRESSIONS[child.type])
                else:
                    allowed_classes.append("self." + py_class_name(k))
                    dict_condition.append("self." + py_class_name(k))

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
        name = self.field_name(node)
        class_name = py_class_name(node.name)
        child = node
        for value in node._optional.values():
            child = value
        #for objects and lists with polymorphism
        if is_inline_polymorphic(node):
            allowed_expr, schemas_expr = self.inline_allowed_expr(node)
            self._init_input.append(
                f'{name}: object = {self.default_literal(node, "object")}'
            )
            self._init_body.append(
                f'self._{name} = inline_check({name}, {allowed_expr}, {schemas_expr}) if {name} is not None else None'
            )
            self._as_dict.append(
                f'"{node.name}": inline_as_dict(self._{name}),'
            )
        elif node.type == "polymorphic":
            self._init_input.append(
                f'{name}: Optional["{path}"] = None'
            )
            self._init_body.append(
                f'self._{name} = type_check({name}, self.{class_name}) if isinstance({name}, self.{class_name}) else self.{class_name}({name}) if {name} is not None else self.{class_name}()'
            )
            self._as_dict.append(
                f'"{node.name}": self._{name}.as_dict(),'
            )
        elif node.type == "object" or (node.type == "list" and (len(node._optional) > 1 or child.type in ("object", "polymorphic"))):
            self._init_input.append(
                f'{name}: Optional["{path}"] = None'
            )
            self._init_body.append(
                f'self._{name} = type_check({name}, self.{class_name}) if {name} else self.{class_name}()'
            )
            self._as_dict.append(
                f'"{node.name}": self._{name}.as_dict(),'
            )
        #for lists without polymorphism
        elif node.type == "list" and len(node._optional) == 1:
            #default = node.default if node.default else None
            #(child,) = node._optional.values()
            child_type = child.type if child.type != "string" else "str"
            self._init_input.append(
                f'{name}: Optional[Iterable[{child_type}]] = None'
            )
            self._init_body.append(
                f'self._{name} = [] if {name} is None else [type_check(i, {child_type}) for i in {name}]'
            )
            self._as_dict.append(
                f'"{node.name}": self._{name},'
            )
        #For string with options
        elif node.type == "string" and len(node._optional) > 0:
            self.set_enum(node)
            self._init_input.append(
                f'{name}: "{class_name}" = {self.default_literal(node, type)}'
            )
            self._init_body.append(
                f'self._{name} = enum_check({name}, self.{class_name})'
            )
            self._as_dict.append(
                f'"{node.name}": self._{name}.value if self._{name} is not None else None,'
            )
        #For file types with extensions limit
        elif node.type == "string" and node.extensions:
            type = "str"
            self._init_input.append(
                f'{name}: {type} = {self.default_literal(node, type)}'
            )
            self._init_body.append(
                f'self._{name} = extension_check(type_check({name}, str), {node.extensions}) if {name} is not None else None'
            )
            self._as_dict.append(
                f'"{node.name}": self._{name},'
            )
        #For other types (string, int and float)
        else :
            self._init_input.append(
                    f'{name}: {type} = {self.default_literal(node, type)}'
                )
            if node.min is not None or node.max is not None:
                self._init_body.append(
                    f'self._{name} = range_check(type_check({name}, {type}), {node.min}, {node.max}) if {name} is not None else None'
                )
            else:
                self._init_body.append(
                    f'self._{name} = type_check({name}, {type}) if {name} is not None else None'
                )
            self._as_dict.append(
                f'"{node.name}": self._{name},'
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
        name = self.field_name(node)
        child = node
        for value in node._optional.values():
            child = value
        #for objects and lists with polymorphism
        if is_inline_polymorphic(node):
            self._check_required.append(
                f"""
        if self.{name} is None:
            print("Requiered variable {path} does not have value")"""
                )
        elif node.type == "object" or (node.type == "list" and (len(node._optional) > 1 or child.type == "object") or node.type == "polymorphic"):
            self._check_required.append(
                f"self.{name}.check_required()"
            )
        #for lists without polymorphism
        elif node.type == "list" and len(node._optional) == 1:
            self._check_required.append(
                f"""
        if self.{name}:
            print("Requiered variable {path} does not have value")"""
                )
        else :
            self._check_required.append(
                f"""
        if self.{name} is None:
            print("Requiered variable {path} does not have value")"""
                )

    def set_property_setter_list(self, node):
        if not self._property_setter:
            allowed_classes =  [
                PRIMITIVE_TYPE_EXPRESSIONS[k] if k in PRIMITIVE_TYPE_EXPRESSIONS else "self." + py_class_name(k)
                for k in node._optional
            ]
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
            allowed_classes =  [
                PRIMITIVE_TYPE_EXPRESSIONS[k]
                if k in PRIMITIVE_TYPE_EXPRESSIONS
                else PRIMITIVE_TYPE_EXPRESSIONS[child.type]
                if child.type in PRIMITIVE_TYPE_EXPRESSIONS
                else "self." + py_class_name(k)
                for k, child in node._optional.items()
            ]
            for k, child in node._optional.items():
                if k == "list" and is_structured_list_node(child):
                    allowed_classes.append("self." + py_class_name(k))
            allowed_classes = ", ".join(allowed_classes)
            inside_setter = f"self._value = class_check(value, [{allowed_classes}])"
            doc = self.doc_text(node.doc)
            self._property_setter.append(
            f""" 
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        ''' 
        {doc}
        '''
        {inside_setter} """
        )

    def set_property_setter(self, node):
        type = node.type if node.type != "string" else "str"
        name = self.field_name(node)
        class_name = py_class_name(node.name)
        child = node
        required_optional = ""
        doc = self.doc_text(node.doc)
        for value in node._optional.values():
            child = value

        if type == "object" or type == "polymorphic" or type == "list":
            type_check = f'self.{class_name}'
            required_optional = f"""
        \\nRequired: {list(node._required)}
        \\nOptional: {list(node._optional)}"""
        else:
            type_check = type

        if node.type == "list" and len(node._optional) == 1 and child.type not in ("object", "polymorphic"):
            child_type = child.type if child.type != "string" else "str"
            inside_setter = f"""self._{name} = [type_check(i, {child_type}) for i in (type_check(value, list) if value else [])]

    def {name}_add(self, value):
        '''Add to list '''
        self._{name}.append(type_check(value, {child_type}))
            
    def {name}_clear(self):
        '''Clear list (make empty)'''
        self._{name}.clear()

    def {name}_pop(self, index=-1):
        '''Remove by index from list'''
        return self._{name}.pop(index)

    def {name}_remove(self, item):
        '''Safe remove specific item from list'''
        if item in self._list:
            self._{name}.remove(item)
        """
        #for strings with options
        elif is_inline_polymorphic(node):
            allowed_expr, schemas_expr = self.inline_allowed_expr(node)
            inside_setter = f"self._{name} = inline_check(value, {allowed_expr}, {schemas_expr})"
        elif node.type == "polymorphic":
            inside_setter = f"self._{name} = type_check(value, self.{class_name}) if isinstance(value, self.{class_name}) else self.{class_name}(value)"
        elif node.type == "string" and len(node._optional) > 0:
            inside_setter = f"self._{name} = enum_check(value, self.{class_name})"
        #for file names with extensions limit
        elif node.type == "string" and node.extensions:
            inside_setter = f"self._{name} = extension_check(type_check(value, str), {node.extensions})"
        #for other types
        else:
            if node.min is not None or node.max is not None:
                inside_setter = f"self._{name} = range_check(type_check(value, {type_check}), {node.min}, {node.max})"
            else:
                inside_setter = f"self._{name} = type_check(value, {type_check})"
        
        self._property_setter.append(
            f""" 
    @property
    def {name}(self):
        return self._{name}

    @{name}.setter
    def {name}(self, value):
        ''' 
        {doc}{required_optional}
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
        if not init_body:
            init_body = INDENT * 2 + "pass"

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

        enums = ("").join(
            p for p in self._enums
        )

        as_dict = as_dict if type == "list" or type == "polymorphic" else "{" + as_dict + "}"

        result = f"""
class {self._class_name}(object):
    '''{self._doc}'''{enums}
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
        self.type_name = None
        self.variant_fields = None
        # self.camera: str = 'you'

    def __str__(self):
        return self._to_string()

    def clone(self, name=None):
        cloned = JsonToTreeClass(name or self.name)
        cloned.default = self.default
        cloned.type = self.type
        cloned.doc = self.doc
        cloned.extensions = list(self.extensions) if self.extensions else self.extensions
        cloned.min = self.min
        cloned.max = self.max
        cloned.type_name = self.type_name
        cloned.variant_fields = list(self.variant_fields) if self.variant_fields is not None else None
        cloned._required = {
            key: value.clone(key)
            for key, value in self._required.items()
        }
        cloned._optional = {
            key: value.clone(key)
            for key, value in self._optional.items()
        }
        return cloned

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
        if var_name in self._required:
            return
        if var_name in self._optional:
            self._required[var_name] = self._optional.pop(var_name)
            return
        var_obj = JsonToTreeClass(var_name)
        self._required[var_name] = var_obj

    def get_required(self, var_name):
        return self._required.get(var_name)
    
    def add_optional(self, var_name):
        if var_name in self._required:
            return
        if var_name in self._optional:
            return
        var_obj = JsonToTreeClass(var_name)
        self._optional[var_name] = var_obj

    def get_optional(self, var_name):
        return self._optional.get(var_name)
    
    def make_it_polymorphic(self, existing_variant_name=None):
        polymorph = JsonToTreeClass(self.name)
        polymorph.doc = "This is a polymorphic variable, assign an object from its classes to the value"
        polymorph.type = "polymorphic"
        if existing_variant_name:
            self.name = existing_variant_name
        elif self.type != "object":
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

        if parts[0] == "*" and self.type is None:
            self.type = "list"

        if parts[0] == "*" and self.type not in ("list", "polymorphic"):
            return self.find_var(parts[1:])

        #handling list routing
        if self.type == "polymorphic" and len(parts) > 0 and parts[0] != "*":
            parts = ["*"] + parts

        if self.type == "polymorphic" and parts[0] == "*":
            list_variant = self.get_optional("list")
            if list_variant is not None:
                try:
                    node, parent = list_variant.find_var(parts)
                    return node, parent or list_variant
                except ValueError:
                    pass

        if parts[0] == "*" and len(parts) > 1:
            if parts[1] == "*":
                for child in self._optional.values():
                    try:
                        node, parent = child.find_var(parts[1:])
                        return node, parent or child
                    except ValueError:
                        pass

            for child in self._optional.values():
                required = child.get_required(parts[1])
                optional = child.get_optional(parts[1])

                if required is not None:
                    node, parent = required.find_var(parts[2:])
                    return node, parent or self if len(parts) > 2 else self

                if optional is not None:
                    node, parent = optional.find_var(parts[2:])
                    return node, parent or self if len(parts) > 2 else self

            for child in self._optional.values():
                if child.type == "polymorphic":
                    try:
                        node, parent = child.find_var(parts[1:])
                        return node, parent or child
                    except ValueError:
                        pass

            if len(parts) == 2 and self._optional:
                first_node = None
                for child in self._optional.values():
                    child.add_optional(parts[1])
                    first_node = first_node or child.get_optional(parts[1])
                return first_node, self

        required = self.get_required(parts[0])
        optional = self.get_optional(parts[0])

        if required is not None:
            node, parent = required.find_var(parts[1:])
            return node, parent or self

        if optional is not None:
            node, parent = optional.find_var(parts[1:])
            return node, parent or self

        if len(parts) == 1 and parts[0] != "*":
            self.add_optional(parts[0])
            return self.get_optional(parts[0]), self

        if len(parts) > 0 and parts[-1] != "*":
            raise ValueError(
                "Specification file does not conform to the required hierarchy.\n"
                f'Variable "{parts[-1]}" defined before its parent.\n'
                f'Current node: "{self.name}" ({self.type}). '
                f"Required: {list(self._required)}. Optional: {list(self._optional)}."
            )

        return self, None

    def class_generator(self, path = "Root"):
        class_builder = ClassGenerator(self.name, self.doc, list(self._required), list(self._optional))
        for required in self._required.values():
            #print(self.name)
            inner_path_capitalize = path + "." + py_class_name(required.name)
            inner_path = path + "." + required.name
            class_builder.set_init(required, inner_path_capitalize)
            class_builder.set_check_required(required, inner_path)
            class_builder.set_property_setter(required)
                
            child = None
            for value in required._optional.values():
                child = value

            if required.type == "object" or (required.type == "list" and (len(required._optional) > 1 or (child is not None and child.type in ("object", "polymorphic")))) or (required.type == "polymorphic" and not is_inline_polymorphic(required)):
                inner_class = required.class_generator(inner_path_capitalize)
                inner_class = self.indent(inner_class)
                class_builder.set_inner_classes(inner_class)

        for optional in self._optional.values():
            #print(self.name)
            inner_path_capitalize = path + "." + py_class_name(optional.name)
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

            child = None
            for value in optional._optional.values():
                child = value

            if optional.type == "object" or (optional.type == "list" and (len(optional._optional) > 1 or (child is not None and child.type in ("object", "polymorphic")))) or (optional.type == "polymorphic" and not is_inline_polymorphic(optional)):
                inner_class = optional.class_generator(inner_path_capitalize)
                inner_class = self.indent(inner_class)
                class_builder.set_inner_classes(inner_class)

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

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR = PROJECT_ROOT / "json-specs"
DEFAULT_SCHEMA_FILE = SPEC_DIR / "input-spec.json"
DEFAULT_OUTPUT_FILE = PROJECT_ROOT / "generated" / "generated_class.py"

SKIP_POINTER_PREFIXES = ("/preset_problem", "/tests")

def pointer_parts(pointer):
    return [] if pointer == "/" else pointer.strip("/").split("/")

def child_pointer(parent_pointer, child_name):
    if parent_pointer == "/":
        return f"/{child_name}"
    return f'{parent_pointer.rstrip("/")}/{child_name}'

def should_skip_pointer(pointer):
    return any(pointer == prefix or pointer.startswith(f"{prefix}/") for prefix in SKIP_POINTER_PREFIXES)

def joined_pointer(base_pointer, pointer):
    if pointer == "/":
        return base_pointer
    if base_pointer == "/":
        return "/" + pointer.strip("/")
    return f'{base_pointer.rstrip("/")}/{pointer.strip("/")}'

def load_schema(spec_file):
    include_file = SPEC_DIR / spec_file
    if not include_file.exists():
        raise FileNotFoundError(f'Include spec file not found: "{include_file}"')

    with open(include_file, encoding="utf-8") as f:
        return json.load(f)

def expand_includes(entries, base_pointer="/", include_stack=None):
    include_stack = include_stack or []
    expanded = []

    for entry in entries:
        pointer = joined_pointer(base_pointer, entry.get("pointer", "/"))
        if should_skip_pointer(pointer):
            continue

        if entry.get("type") == "include":
            spec_file = entry.get("spec_file")
            if not spec_file:
                raise ValueError(f'Include entry at "{pointer}" is missing spec_file.')
            if spec_file in include_stack:
                chain = " -> ".join(include_stack + [spec_file])
                raise ValueError(f"Circular include detected: {chain}")

            included_entries = load_schema(spec_file)
            expanded.extend(
                expand_includes(
                    included_entries,
                    pointer,
                    include_stack + [spec_file]
                )
            )
            continue

        expanded_entry = dict(entry)
        expanded_entry["pointer"] = pointer
        expanded.append(expanded_entry)

    return expanded

def filtered_entry(entry):
    entry = dict(entry)
    pointer = entry.get("pointer", "/")

    for key in ("required", "optional", "options"):
        values = entry.get(key)
        if values:
            entry[key] = [
                value for value in values
                if not should_skip_pointer(child_pointer(pointer, value))
            ]

    return entry

def entry_type_name(entry):
    return entry.get("type_name") or entry.get("#type_name")

def pointer_depth(entry):
    pointer = entry.get("pointer", "/")
    return 0 if pointer == "/" else len(pointer.strip("/").split("/"))

def mark_variant_fields(node, entry):
    fields = []
    for key in ("required", "optional", "options"):
        for field in entry.get(key) or []:
            if field not in fields:
                fields.append(field)

    if fields:
        if node.variant_fields is None:
            node.variant_fields = []
        for field in fields:
            if field not in node.variant_fields:
                node.variant_fields.append(field)

def prune_variant_fields(node, visited=None):
    visited = visited or set()
    node_id = id(node)
    if node_id in visited:
        return
    visited.add(node_id)

    if node.type_name and node.variant_fields is not None:
        node._required = {
            key: node._required[key]
            for key in node.variant_fields
            if key in node._required
        }
        node._optional = {
            key: node._optional[key]
            for key in node.variant_fields
            if key in node._optional
        }

    for child in list(node._required.values()) + list(node._optional.values()):
        prune_variant_fields(child, visited)

def apply_type_name_defaults(node, visited=None):
    visited = visited or set()
    node_id = id(node)
    if node_id in visited:
        return
    visited.add(node_id)

    if node.type_name:
        type_node = node.get_required("type") or node.get_optional("type")
        if type_node is not None and type_node.type == "string":
            type_node.default = node.type_name
            if type_node._optional:
                existing = type_node.get_optional(node.type_name)
                type_node._optional = {
                    node.type_name: existing or JsonToTreeClass(node.type_name)
                }

    for child in list(node._required.values()) + list(node._optional.values()):
        apply_type_name_defaults(child, visited)

def build_tree(schema_entries):
    root = JsonToTreeClass("root")
    schema = expand_includes(schema_entries)

    schema = [
        filtered_entry(entry)
        for entry in schema
        if not should_skip_pointer(entry.get("pointer", "/"))
    ]

    def ensure_pointer(root_node, pointer):
        if pointer == "/":
            return root_node

        node = root_node
        for part in pointer_parts(pointer):
            if part == "*":
                node.add_optional(LIST_ITEM_NAME)
                node = node.get_optional(LIST_ITEM_NAME)
            else:
                node.add_optional(part)
                node = node.get_optional(part)

        return node

    for entry in schema:
        ensure_pointer(root, entry.get("pointer", "/"))

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
            try:
                path, parent = root.find_var(parts)
            except ValueError as exc:
                raise ValueError(f'{exc}\nWhile processing pointer: {entry["pointer"]}') from exc

        replacement_node = None
        type_name = entry_type_name(entry)
        used_list_type_name = False

        #handling list variables
        if path.type == "list" and parts[-1] == '*':
            if type_name:
                used_list_type_name = True
                if path.get_optional(type_name) is None:
                    placeholder = path.get_optional(LIST_ITEM_NAME)
                    if placeholder is not None:
                        path._optional[type_name] = placeholder.clone(type_name)
                    else:
                        path.add_optional(type_name)
                path = path.get_optional(type_name)
                path.type_name = type_name
            else: 
                path.add_optional(LIST_ITEM_NAME)
                path = path.get_optional(LIST_ITEM_NAME)

        if type_name and not used_list_type_name and entry.get('type') == "object" and path.type is None:
            placeholder = path.clone(type_name)
            placeholder.type_name = type_name
            path.type = "polymorphic"
            path.doc = "This is a polymorphic variable, assign an object from its classes to the value"
            path.default = None
            path.extensions = []
            path.min = None
            path.max = None
            path._required = {}
            path._optional = {type_name: placeholder}
            path = placeholder

        #handeling polymorfic variables
        if path.type == "polymorphic":
            replacement_node = path
            if type_name and entry.get('type') == "object":
                routing = type_name
            elif entry.get('type') != "object":
                routing = entry.get('type')
            else:
                routing = entry.get('type') + str(len(path._optional) + 1)
            path.add_optional(routing)
            path = path.get_optional(routing)
            if type_name and entry.get('type') == "object":
                path.type_name = type_name
            
        elif path.type is not None:
            if type_name and entry.get('type') == "object" and path.name == type_name and path.type == "object":
                routing = None
                path.type_name = type_name
            else:
                existing_variant_name = path.name if path.name != parts[-1] else None
                polymorph = path.make_it_polymorphic(existing_variant_name)
                if type_name and entry.get('type') == "object":
                    routing = type_name
                elif entry.get('type') != "object":
                    routing = entry.get('type')
                else:
                    routing = entry.get('type') + "2"
                polymorph.add_optional(routing)
                if not (len(parts) > 1 and parts[-2] == '*'):
                    parent.find_var_replace(polymorph.name, polymorph)
                path = polymorph.get_optional(routing)
                if type_name and entry.get('type') == "object":
                    path.type_name = type_name
                replacement_node = polymorph

        if type_name and entry.get('type') == "object":
            mark_variant_fields(path, entry)

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
            replacement_node = replacement_node or path
            for child in parent._optional.values():
                child.find_var_replace(parts[-1], replacement_node)

        #print (path.name)

    """
        if entry['pointer'] == "/":
            root = JsonToTreeClass("root")
            if entry.get('optional'):
                print(entry['optional']) 
    """
    #print(root.get_optional("geometry").get_optional("nested").name)

    prune_variant_fields(root)
    apply_type_name_defaults(root)
    return root

def generated_class_text(root):
    generated_class = root.class_generator()
    prelude = """
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

def inline_check(value, allowed, object_schemas=None):
    object_schemas = object_schemas or []

    if value is None:
        return value

    if allowed and isinstance(value, tuple(allowed)):
        return value

    if isinstance(value, dict):
        for schema in object_schemas:
            required = schema.get("required", [])
            optional = schema.get("optional", [])
            allowed_keys = set(required + optional)
            if not all(key in value for key in required):
                continue
            if any(key not in allowed_keys for key in value):
                continue

            checked = {}
            for key, item in value.items():
                field_schema = schema.get("fields", {}).get(key)
                if field_schema is None:
                    checked[key] = item
                    continue

                field_allowed, field_object_schemas = field_schema
                checked[key] = inline_check(item, field_allowed, field_object_schemas)
            return checked

    allowed_names = [tp.__name__ for tp in allowed]
    if object_schemas:
        allowed_names.append("dict")
    raise TypeError(
        f"Invalid variable type: {type(value).__name__}. "
        f"Expected {', '.join(allowed_names)}"
    )

def inline_as_dict(value):
    if hasattr(value, "as_dict"):
        return value.as_dict()
    if isinstance(value, dict):
        return drop_none({key: inline_as_dict(item) for key, item in value.items()})
    if isinstance(value, list):
        return [inline_as_dict(item) for item in value]
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
        min_text = f" {min} â‰¤" if min is not None else ""
        max_text = f" â‰¤ {max}" if max is not None else ""

        raise TypeError(f"Value {value} is out of range. Expected{min_text} value{max_text}.")

def type_check(variable, tp):
    if not isinstance(variable, tp):
        raise TypeError(f"Expected type '{tp.__name__}', but got '{type(variable).__name__}'")
    return variable
"""
    return prelude + generated_class

def generate(schema_file=DEFAULT_SCHEMA_FILE, output_file=DEFAULT_OUTPUT_FILE):
    with open(schema_file, encoding="utf-8") as f:
        schema_entries = json.load(f)

    root = build_tree(schema_entries)
    generated_class = generated_class_text(root)
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(generated_class)

    print(f"Generated {output_file}")
    return generated_class


if __name__ == "__main__":
    generate()

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
