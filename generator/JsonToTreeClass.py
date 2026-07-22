import importlib.util
import json
import keyword
from pathlib import Path
import re
import textwrap


def _load_local_symbol(module_name, symbol_name):
    module_path = Path(__file__).with_name(f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(f"_json_schema_generator_{module_name}", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, symbol_name)


expand_api_aliases = _load_local_symbol("api_aliases", "expand_api_aliases")

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
        and node.type_name in (None, "ValueWithUnit")
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
    def __init__(self, class_name : str, doc : str, required, optional, required_field_sets=None):
        self._class_name = py_class_name(class_name)
        doc = self.doc_text(doc)
        required_text = required_field_sets if required_field_sets and len(required_field_sets) > 1 else required
        self._doc = f"""{doc}
    \\nRequired: {required_text}
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

    def inline_allowed_components(self, node):
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

        return allowed, schemas

    def inline_allowed_expr(self, node):
        allowed, schemas = self.inline_allowed_components(node)
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
        if not self._init_input:
            allowed_classes = []
            dict_condition = []
            object_schemas = []
            uses_inline_check = False
            for k, child in node._optional.items():
                if is_inline_polymorphic(child):
                    uses_inline_check = True
                    inline_allowed, inline_schemas = self.inline_allowed_components(child)
                    allowed_classes.extend(inline_allowed)
                    object_schemas.extend(inline_schemas)
                elif k in PRIMITIVE_TYPE_EXPRESSIONS:
                    allowed_classes.append(PRIMITIVE_TYPE_EXPRESSIONS[k])
                    if k == "list" and is_structured_list_node(child):
                        allowed_classes.append("self." + py_class_name(k))
                        dict_condition.append("self." + py_class_name(k))
                elif child.type in PRIMITIVE_TYPE_EXPRESSIONS:
                    allowed_classes.append(PRIMITIVE_TYPE_EXPRESSIONS[child.type])
                else:
                    if child.type is not None:
                        allowed_classes.append("self." + py_class_name(k))
                        dict_condition.append("self." + py_class_name(k))
                    

            allowed_classes = ", ".join(allowed_classes)
            dict_condition = ", ".join(dict_condition)
            object_schemas = ", ".join(object_schemas)

            self._init_input.append(
                'items : list = None'
            )
            if uses_inline_check:
                self._init_body.append(
                    f'self._items = [inline_check(i, [{allowed_classes}], [{object_schemas}]) for i in (type_check(items, list) if items else [])]'
                )
                self._as_dict.append(
                    '[inline_as_dict(i) for i in self._items]'
                )
            else:
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
                    if child.type is not None:
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
        python_type = node.type if node.type != "string" else "str"
        name = self.field_name(node)
        class_name = py_class_name(node.name)
        child = node
        for value in node._optional.values():
            child = value
        #for objects and lists with polymorphism
        if is_inline_polymorphic(node):
            allowed_expr, schemas_expr = self.inline_allowed_expr(node)
            default = "_UNSET" if node.has_default else self.default_literal(node, "object")
            self._init_input.append(
                f'{name}: object = {default}'
            )
            if node.has_default:
                self._init_body.append(
                    f'self._{name} = None if {name} is _UNSET else inline_check({name}, {allowed_expr}, {schemas_expr}) if {name} is not None else None'
                )
            else:
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
                f'self._{name} = type_check({name}, self.{class_name}) if isinstance({name}, self.{class_name}) else self.{class_name}({name}) if {name} is not None else None'
            )
            self._as_dict.append(
                f'"{node.name}": self._{name}.as_dict() if self._{name} is not None else None,'
            )
        elif node.type == "object" or (node.type == "list" and (len(node._optional) > 1 or child.type in ("object", "polymorphic"))):
            self._init_input.append(
                f'{name}: Optional["{path}"] = None'
            )
            self._init_body.append(
                f'self._{name} = type_check({name}, self.{class_name}) if {name} is not None else None'
            )
            self._as_dict.append(
                f'"{node.name}": self._{name}.as_dict() if self._{name} is not None else None,'
            )
        #for lists without polymorphism
        elif node.type == "list" and len(node._optional) == 1:
            #default = node.default if node.default else None
            #(child,) = node._optional.values()
            child_type = child.type if child.type != "string" else "str"
            if child.type is None:
                self._init_input.append(
                    f'{name}: Optional[Iterable[object]] = _UNSET'
                )
                self._init_body.append(
                    f'self._{name} = None if {name} is _UNSET else list_check({name})'
                )
            else:
                self._init_input.append(
                    f'{name}: Optional[Iterable[{child_type}]] = _UNSET'
                )
                self._init_body.append(
                    f'self._{name} = None if {name} is _UNSET else [type_check(i, {child_type}) for i in list_check({name})]'
                )
            self._as_dict.append(
                f'"{node.name}": self._{name},'
            )
        #For string with options
        elif node.type == "string" and len(node._optional) > 0:
            self.set_enum(node)
            default = "_UNSET" if node.has_default else self.default_literal(node, python_type)
            self._init_input.append(
                f'{name}: "{class_name}" = {default}'
            )
            if node.has_default:
                self._init_body.append(
                    f'self._{name} = None if {name} is _UNSET else enum_check({name}, self.{class_name})'
                )
            else:
                self._init_body.append(
                    f'self._{name} = enum_check({name}, self.{class_name})'
                )
            self._as_dict.append(
                f'"{node.name}": self._{name}.value if self._{name} is not None else None,'
            )
        #For file types with extensions limit
        elif node.type == "string" and node.extensions:
            python_type = "str"
            default = "_UNSET" if node.has_default else self.default_literal(node, python_type)
            self._init_input.append(
                f'{name}: {python_type} = {default}'
            )
            if node.has_default:
                self._init_body.append(
                    f'self._{name} = None if {name} is _UNSET else extension_check(type_check({name}, str), {node.extensions}) if {name} is not None else None'
                )
            else:
                self._init_body.append(
                    f'self._{name} = extension_check(type_check({name}, str), {node.extensions}) if {name} is not None else None'
                )
            self._as_dict.append(
                f'"{node.name}": self._{name},'
            )
        elif node.type is None:
            default = "_UNSET" if node.has_default else self.default_literal(node, "object")
            self._init_input.append(
                    f'{name}: object = {default}'
                )
            if node.has_default:
                self._init_body.append(
                    f'self._{name} = None if {name} is _UNSET else {name}'
                )
            else:
                self._init_body.append(
                    f'self._{name} = {name}'
                )
            self._as_dict.append(
                f'"{node.name}": self._{name},'
            )
        #For other types (string, int and float)
        else :
            default = "_UNSET" if node.has_default else self.default_literal(node, python_type)
            self._init_input.append(
                    f'{name}: {python_type} = {default}'
                )
            if node.has_default:
                if node.min is not None or node.max is not None:
                    self._init_body.append(
                        f'self._{name} = None if {name} is _UNSET else range_check(type_check({name}, {python_type}), {node.min}, {node.max}) if {name} is not None else None'
                    )
                else:
                    self._init_body.append(
                        f'self._{name} = None if {name} is _UNSET else type_check({name}, {python_type}) if {name} is not None else None'
                    )
            else:
                if node.min is not None or node.max is not None:
                    self._init_body.append(
                        f'self._{name} = range_check(type_check({name}, {python_type}), {node.min}, {node.max}) if {name} is not None else None'
                    )
                else:
                    self._init_body.append(
                        f'self._{name} = type_check({name}, {python_type}) if {name} is not None else None'
                    )
            self._as_dict.append(
                f'"{node.name}": self._{name},'
            )
    
    def set_check_required_polymorphic(self, path):
        if not self._check_required:
            type_list = "int, float, list, str, bool, dict"

            self._check_required.append(
                    f"""
        if self.value is None:
            print("Required variable {path}.value does not have value")
        else:
            if type(self.value) not in [{type_list}]:
                self.value.check_required()"""
                )

    def set_check_required_list(self, path):
        if not self._check_required:
            type_list = "int, float, list, str, bool, dict"
            
            self._check_required.append(
                    f"""
        if self.items:
            for item in self.items:
                if type(item) not in [{type_list}]:
                    item.check_required()
        else:
            print("Required variable {path}.items does not have value")"""
                    )

    def set_check_required(self, node, path):
        name = self.field_name(node)
        storage = f"self._{name}"
        child = node
        for value in node._optional.values():
            child = value
        #for objects and lists with polymorphism
        if is_inline_polymorphic(node):
            self._check_required.append(
                f"""
        if {storage} is None:
            print("Required variable {path} does not have value")"""
                )
        elif node.type == "object" or (node.type == "list" and (len(node._optional) > 1 or child.type == "object") or node.type == "polymorphic"):
            self._check_required.append(
                f"""
        if {storage} is None:
            print("Required variable {path} does not have value")
        else:
            {storage}.check_required()"""
            )
        #for lists without polymorphism
        elif node.type == "list" and len(node._optional) == 1:
            self._check_required.append(
                f"""
        if not {storage}:
            print("Required variable {path} does not have value")"""
                )
        else :
            self._check_required.append(
                f"""
        if {storage} is None:
            print("Required variable {path} does not have value")"""
                )

    def set_check_required_alternatives(self, path, required_field_sets):
        conditions = []
        descriptions = []
        for required_fields in required_field_sets:
            fields = [py_identifier(field) for field in required_fields]
            conditions.append(
                "(" + " and ".join(f"self._{field} is not None" for field in fields) + ")"
            )
            descriptions.append(", ".join(required_fields))

        condition = " or ".join(conditions)
        description = "; ".join(descriptions)
        self._check_required.append(
            f"""
        if not ({condition}):
            print("Required variable {path} must satisfy one required field set: {description}")"""
        )

    def set_property_setter_list(self, node):
        if not self._property_setter:
            allowed_classes = []
            object_schemas = []
            uses_inline_check = False
            for k, child in node._optional.items():
                if is_inline_polymorphic(child):
                    uses_inline_check = True
                    inline_allowed, inline_schemas = self.inline_allowed_components(child)
                    allowed_classes.extend(inline_allowed)
                    object_schemas.extend(inline_schemas)
                elif k in PRIMITIVE_TYPE_EXPRESSIONS:
                    allowed_classes.append(PRIMITIVE_TYPE_EXPRESSIONS[k])
                    if k == "list" and is_structured_list_node(child):
                        allowed_classes.append("self." + py_class_name(k))
                elif child.type in PRIMITIVE_TYPE_EXPRESSIONS:
                    allowed_classes.append(PRIMITIVE_TYPE_EXPRESSIONS[child.type])
                else:
                    if child.type is not None:
                        allowed_classes.append("self." + py_class_name(k))
            allowed_classes = ", ".join(allowed_classes)
            object_schemas = ", ".join(object_schemas)
            item_check = (
                f"inline_check(i, [{allowed_classes}], [{object_schemas}])"
                if uses_inline_check
                else f"class_check(i, [{allowed_classes}])"
            )
            add_check = (
                f"inline_check(item, [{allowed_classes}], [{object_schemas}])"
                if uses_inline_check
                else f"class_check(item, [{allowed_classes}])"
            )

            self._property_setter.append(
            f""" 
    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, items : list):
        ''' Replace the list '''
        self._items = [{item_check} for i in (type_check(items, list) if items else [])]

    def add(self, item : object):
        ''' Add to the list '''
        self._items.append({add_check})

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
        {inside_setter}"""
        )

    def set_property_setter(self, node):
        python_type = node.type if node.type != "string" else "str"
        name = self.field_name(node)
        class_name = py_class_name(node.name)
        child = node
        required_optional = ""
        doc = self.doc_text(node.doc)
        for value in node._optional.values():
            child = value

        if node.type is None:
            self._property_setter.append(
                f"""
    @property
    def {name}(self):
        return self._{name}

    @{name}.setter
    def {name}(self, value):
        '''
        {doc}
        '''
        self._{name} = value"""
            )
            return

        if python_type == "object" or python_type == "polymorphic" or python_type == "list":
            type_check_expr = f'self.{class_name}'
            required_optional = f"""
        \\nRequired: {list(node._required)}
        \\nOptional: {list(node._optional)}"""
        else:
            type_check_expr = python_type

        if node.type == "list" and len(node._optional) == 1 and child.type not in ("object", "polymorphic"):
            child_type = child.type if child.type != "string" else "str"
            if child.type is None:
                list_assignment = f"self._{name} = list_check(value)"
                add_assignment = f"self._{name}.append(value)"
            else:
                list_assignment = f"self._{name} = [type_check(i, {child_type}) for i in list_check(value)]"
                add_assignment = f"self._{name}.append(type_check(value, {child_type}))"
            inside_setter = f"""{list_assignment}

    def {name}_add(self, value):
        '''Add to list '''
        {add_assignment}
            
    def {name}_clear(self):
        '''Clear list (make empty)'''
        self._{name}.clear()

    def {name}_pop(self, index=-1):
        '''Remove by index from list'''
        return self._{name}.pop(index)

    def {name}_remove(self, item):
        '''Safe remove specific item from list'''
        if item in self._{name}:
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
                inside_setter = f"self._{name} = range_check(type_check(value, {type_check_expr}), {node.min}, {node.max})"
            else:
                inside_setter = f"self._{name} = type_check(value, {type_check_expr})"
        
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
        {inside_setter}"""
        )

    def set_inner_classes(self, inner_class):
        self._inner_classes.append(
            inner_class
        )

    def generate(self, node_type):
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

        as_dict = as_dict if node_type == "list" or node_type == "polymorphic" else "{" + as_dict + "}"

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
        return result


class JsonToTreeClass(object):

    def __init__(self, name):
        self.name = name
        self.default = None
        self.has_default = False
        self.type = None
        self._required = {}
        self._optional = {}
        self.doc = "There is no definition"
        self.extensions = []
        self.min = None
        self.max = None
        self.type_name = None
        self.variant_fields = None
        self.required_field_sets = []
        self.pending_variant_fields = {}
        self.pending_list_item_fields = {}

    def __str__(self):
        return self._to_string()

    def clone(self, name=None, include_pending=True, _seen=None):
        _seen = _seen or {}
        node_id = id(self)
        if node_id in _seen:
            return _seen[node_id]

        cloned = JsonToTreeClass(name or self.name)
        _seen[node_id] = cloned
        cloned.default = self.default
        cloned.has_default = self.has_default
        cloned.type = self.type
        cloned.doc = self.doc
        cloned.extensions = list(self.extensions) if self.extensions else self.extensions
        cloned.min = self.min
        cloned.max = self.max
        cloned.type_name = self.type_name
        cloned.variant_fields = list(self.variant_fields) if self.variant_fields is not None else None
        cloned.required_field_sets = [list(fields) for fields in self.required_field_sets]
        if include_pending:
            cloned.pending_variant_fields = {
                key: value.clone(key, include_pending=False, _seen=_seen)
                for key, value in self.pending_variant_fields.items()
            }
            cloned.pending_list_item_fields = {
                key: value.clone(key, include_pending=False, _seen=_seen)
                for key, value in self.pending_list_item_fields.items()
            }
        cloned._required = {
            key: value.clone(key, include_pending=include_pending, _seen=_seen)
            for key, value in self._required.items()
        }
        cloned._optional = {
            key: value.clone(key, include_pending=include_pending, _seen=_seen)
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

    def set_doc(self, description : str):
        self.doc = description

    def set_default(self, value, has_default=True):
        self.default = value
        self.has_default = has_default

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
        polymorph.pending_variant_fields = {
            key: value.clone(key, include_pending=False)
            for key, value in self.pending_variant_fields.items()
        }
        polymorph.pending_list_item_fields = {
            key: value.clone(key, include_pending=False)
            for key, value in self.pending_list_item_fields.items()
        }
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
        elif self.type == "polymorphic":
            for child in self._optional.values():
                if child.get_required(part) is not None or child.get_optional(part) is not None:
                    child.find_var_replace(part, value)

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
                    return node, (parent or required) if len(parts) > 2 else self

                if optional is not None:
                    node, parent = optional.find_var(parts[2:])
                    return node, (parent or optional) if len(parts) > 2 else self

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
        required_field_sets = self.required_field_sets if len(self.required_field_sets) > 1 else None
        class_builder = ClassGenerator(
            self.name,
            self.doc,
            list(self._required),
            list(self._optional),
            required_field_sets,
        )
        if required_field_sets:
            class_builder.set_check_required_alternatives(path, required_field_sets)

        for required in self._required.values():
            inner_path_capitalize = path + "." + py_class_name(required.name)
            inner_path = path + "." + required.name
            class_builder.set_init(required, inner_path_capitalize)
            if not required_field_sets:
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR = PROJECT_ROOT / "examples" / "basic_generation"
DEFAULT_SCHEMA_FILE = SPEC_DIR / "input-spec.json"
DEFAULT_GENERATED_DIR = PROJECT_ROOT / "generated"
DEFAULT_OUTPUT_FILE = DEFAULT_GENERATED_DIR / "generated_class.py"
DEFAULT_API_OUTPUT_FILE = DEFAULT_GENERATED_DIR / "generated_api.py"

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

def spec_search_dirs(spec_dir=None, include_dirs=None):
    search_dirs = [Path(spec_dir) if spec_dir is not None else SPEC_DIR]
    for include_dir in include_dirs or []:
        include_dir = Path(include_dir)
        if include_dir not in search_dirs:
            search_dirs.append(include_dir)
    return search_dirs


def load_schema(spec_file, spec_dir=None, include_dirs=None):
    searched_paths = []
    for include_dir in spec_search_dirs(spec_dir, include_dirs):
        include_file = include_dir / spec_file
        searched_paths.append(include_file)
        if include_file.exists():
            with open(include_file, encoding="utf-8") as f:
                return json.load(f)

    searched = ", ".join(str(path) for path in searched_paths)
    raise FileNotFoundError(
        f'Include spec file "{spec_file}" not found. Searched: {searched}'
    )


def expand_includes(
    entries,
    base_pointer="/",
    include_stack=None,
    spec_dir=None,
    include_dirs=None,
):
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

            included_entries = load_schema(
                spec_file,
                spec_dir=spec_dir,
                include_dirs=include_dirs,
            )
            expanded.extend(
                expand_includes(
                    included_entries,
                    pointer,
                    include_stack + [spec_file],
                    spec_dir=spec_dir,
                    include_dirs=include_dirs,
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

def py_function_name(value):
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", str(value))
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return py_identifier(name.lower())

def should_generate_class_for_node(node):
    child = None
    for value in node._optional.values():
        child = value

    return (
        node.type == "object"
        or (
            node.type == "list"
            and (
                len(node._optional) > 1
                or (child is not None and child.type in ("object", "polymorphic"))
            )
        )
        or (node.type == "polymorphic" and not is_inline_polymorphic(node))
    )

def collect_class_tree(node, path=None):
    path = path or ["Root"]
    entries = [(path, node)]

    for child in list(node._required.values()) + list(node._optional.values()):
        if should_generate_class_for_node(child):
            entries.extend(collect_class_tree(child, path + [py_class_name(child.name)]))

    return entries

def generated_api_name_map(class_entries):
    paths = [path for path, _node in class_entries if path != ["Root"]]
    paths.sort(key=lambda path: (len(path), path))
    result = {}
    used = set()

    for path in paths:
        parts = [py_function_name(part) for part in path[1:]]
        for depth in range(1, len(parts) + 1):
            name = "_".join(parts[-depth:])
            if name not in used:
                result[tuple(path)] = name
                used.add(name)
                break

    return result

def api_class_expr(path):
    return ".".join(path)

def default_generator_overrides():
    return {
        "version": 1,
        "schema_patches": [],
        "custom_api_names": [],
        "skip_auto_generated_api_names": [],
        "api_aliases": [],
        "shortcuts": {},
        "groups": {},
    }

def normalized_generator_overrides(overrides=None):
    result = default_generator_overrides()
    if overrides is None:
        return result

    version = overrides.get("version", 1)
    if version != 1:
        raise ValueError(f"Unsupported generator overrides version: {version!r}")

    for key in result:
        if key in overrides:
            result[key] = overrides[key]

    return result

def load_generator_overrides(overrides_file=None):
    if overrides_file is None:
        return default_generator_overrides()

    with open(overrides_file, encoding="utf-8") as f:
        return normalized_generator_overrides(json.load(f))

def patch_field_pointer(target, name):
    target = target or "/"
    if not target.startswith("/"):
        raise ValueError(f"Schema patch target must be a JSON pointer: {target!r}")
    if "/" in name:
        raise ValueError(f"Schema patch field name must not contain '/': {name!r}")
    return f"{target.rstrip('/')}/{name}" if target != "/" else f"/{name}"

def apply_schema_patches(schema_entries, generator_overrides=None):
    overrides = normalized_generator_overrides(generator_overrides)
    patched = [dict(entry) for entry in schema_entries]
    report = []

    for patch in overrides["schema_patches"]:
        patch_id = patch.get("id")
        op = patch.get("op")
        if op != "add_field":
            raise ValueError(f"Unsupported schema patch op: {op!r}")

        target = patch.get("target")
        name = patch.get("name")
        schema = dict(patch.get("schema") or {})
        if not target or not name:
            raise ValueError("add_field schema patch requires target and name")
        if "type" not in schema:
            raise ValueError("add_field schema patch requires schema.type")

        pointer = patch_field_pointer(target, name)
        entry = {"pointer": pointer}
        entry.update(schema)
        patched = [item for item in patched if item.get("pointer") != pointer]
        for item in patched:
            if item.get("pointer") != target or item.get("type") != "object":
                continue
            required = set(item.get("required") or [])
            optional = list(item.get("optional") or [])
            if name not in required and name not in optional:
                optional.append(name)
                item["optional"] = optional
        patched.append(entry)
        report.append({
            "id": patch_id,
            "op": op,
            "pointer": pointer,
            "status": "applied",
        })

    return patched, report

def validate_api_function_name(name):
    if not name or py_identifier(name) != name or keyword.iskeyword(name):
        raise ValueError(f"Invalid API function name: {name!r}")
    return name

def class_tree_manifest(root):
    return [
        {
            "class_path": api_class_expr(path),
            "params": api_all_fields(node),
        }
        for path, node in collect_class_tree(root)
    ]

def generated_api_export_plan(class_entries, generator_overrides=None):
    overrides = normalized_generator_overrides(generator_overrides)
    api_names = generated_api_name_map(class_entries)
    paths_by_name = {
        api_class_expr(path): path
        for path, _node in class_entries
    }
    nodes_by_name = {
        api_class_expr(path): node
        for path, node in class_entries
    }
    generated_name_by_class_path = {
        api_class_expr(path): api_names[tuple(path)]
        for path, _node in class_entries
        if path != ["Root"]
    }

    api_alias_custom_names, api_alias_skip_names = expand_api_aliases(
        overrides["api_aliases"],
        paths_by_name,
        generated_name_by_class_path,
        validate_api_function_name,
    )

    skip_auto_generated_api_names = [
        *overrides["skip_auto_generated_api_names"],
        *api_alias_skip_names,
    ]
    custom_api_names = [
        *overrides["custom_api_names"],
        *api_alias_custom_names,
    ]

    for item in skip_auto_generated_api_names:
        class_path = item["class_path"]
        api_generated_name = item["api_generated_name"]
        if class_path not in generated_name_by_class_path:
            raise ValueError(
                f"skip_auto_generated_api_names references unknown class_path: {class_path!r}"
            )
        actual_name = generated_name_by_class_path[class_path]
        if api_generated_name != actual_name:
            raise ValueError(
                "skip_auto_generated_api_names api_generated_name mismatch: "
                f"{api_generated_name!r} != {actual_name!r}"
            )

    skip_names = {
        (
            item["class_path"],
            item["api_generated_name"],
        )
        for item in skip_auto_generated_api_names
    }

    plan = []
    used = {"config", "unit"}
    for path, node in class_entries:
        if path == ["Root"]:
            continue

        class_path = api_class_expr(path)
        api_generated_name = api_names[tuple(path)]
        exported = (class_path, api_generated_name) not in skip_names
        if exported:
            used.add(api_generated_name)
        plan.append({
            "class_path": class_path,
            "api_generated_name": api_generated_name,
            "api_custom_name": None,
            "kind": "auto",
            "source": "generator",
            "exported": exported,
            "params": api_all_fields(node),
        })

    for item in custom_api_names:
        class_path = item["class_path"]
        if class_path not in paths_by_name:
            raise ValueError(f"custom_api_names references unknown class_path: {class_path!r}")
        api_custom_name = validate_api_function_name(item["api_custom_name"])
        if api_custom_name in used:
            raise ValueError(f"API function name already exists: {api_custom_name!r}")

        path = paths_by_name[class_path]
        node = nodes_by_name[class_path]
        used.add(api_custom_name)
        plan.append({
            "class_path": class_path,
            "api_generated_name": api_names[tuple(path)],
            "api_custom_name": api_custom_name,
            "kind": item.get("_kind", "custom_api_name"),
            "source": item.get("_source", "api_config"),
            "exported": True,
            "params": api_all_fields(node),
        })

    return plan

def generated_api_manifest(root, generator_overrides=None):
    return generated_api_export_plan(
        collect_class_tree(root),
        generator_overrides,
    )

def api_required_fields(node):
    fields = []
    for name, child in node._required.items():
        if name == "type" and node.type_name:
            continue
        if child.has_default:
            continue
        fields.append(name)
    return fields

def api_all_fields(node):
    fields = []
    for name in list(node._required) + list(node._optional):
        if name not in fields:
            fields.append(name)
    return fields

def api_variant_tuple(path, node):
    return (
        f"({api_class_expr(path)}, {node.type_name!r}, "
        f"{tuple(api_required_fields(node))!r}, {tuple(api_all_fields(node))!r})"
    )

def generated_api_field_wrapper_text(class_entries):
    lines = []

    for path, node in class_entries:
        wrappers = []
        for child in list(node._required.values()) + list(node._optional.values()):
            if not should_generate_class_for_node(child):
                continue
            child_path = path + [py_class_name(child.name)]
            wrappers.append(
                f'        "{child.name}": ({child.type!r}, {api_class_expr(child_path)}),\n'
            )

        if wrappers:
            lines.append(f"    {api_class_expr(path)}: {{\n{''.join(wrappers)}    }},\n")

    return "{\n" + "".join(lines) + "}"

def generated_api_list_variants_text(class_entries):
    lines = []

    for path, node in class_entries:
        if node.type != "list":
            continue

        variants = []
        for child in node._optional.values():
            if not should_generate_class_for_node(child):
                continue
            child_path = path + [py_class_name(child.name)]
            variants.append(f"        {api_variant_tuple(child_path, child)},\n")

        if variants:
            lines.append(f"    {api_class_expr(path)}: (\n{''.join(variants)}    ),\n")

    return "{\n" + "".join(lines) + "}"

def generated_api_polymorphic_variants_text(class_entries):
    lines = []

    for path, node in class_entries:
        if node.type != "polymorphic":
            continue

        variants = []
        for child in node._optional.values():
            if not should_generate_class_for_node(child):
                continue
            child_path = path + [py_class_name(child.name)]
            variants.append(f"        {api_variant_tuple(child_path, child)},\n")

        if variants:
            lines.append(f"    {api_class_expr(path)}: (\n{''.join(variants)}    ),\n")

    return "{\n" + "".join(lines) + "}"

def generated_api_class_type_names_text(class_entries):
    lines = []

    for path, node in class_entries:
        if not node.type_name:
            continue
        if "type" not in api_all_fields(node):
            continue
        lines.append(f"    {api_class_expr(path)}: {node.type_name!r},\n")

    return "{\n" + "".join(lines) + "}"

def api_shortcut_name_options(path):
    if path == ["Root"]:
        return []

    current = py_function_name(path[-1])

    if len(path) >= 4 and current == "item":
        parent = py_function_name(path[-2])
        if parent.endswith("_boundary"):
            base = parent[: -len("_boundary")]
            return [
                base,
                f"{py_function_name(path[-3])}_{base}",
                "_".join(py_function_name(part) for part in path[1:]),
            ]

    if len(path) >= 4:
        parent = py_function_name(path[-2])
        if parent.endswith("_selection"):
            base = parent[: -len("_selection")]
            owner = py_function_name(path[-3])
            return [
                f"{base}_{current}",
                f"{owner}_{base}_{current}",
                "_".join(py_function_name(part) for part in path[1:]),
            ]

    if len(path) == 3 and path[1] == "Output":
        return [
            f"output_{current}",
            "_".join(py_function_name(part) for part in path[1:]),
        ]

    return []

def generated_api_shortcut_factories_text(class_entries, api_names, extra_used=None):
    used = set(api_names.values()) | set(extra_used or ()) | {"config", "unit"}
    lines = []

    for path, _node in class_entries:
        for name in api_shortcut_name_options(path):
            if name in used:
                continue
            used.add(name)
            lines.append(
                f"""
def {name}(*args, **kwargs):
    return _construct({api_class_expr(path)}, *args, **kwargs)
"""
            )
            break

    return "".join(lines)

def generated_api_field_aliases_text(class_entries):
    lines = []

    for path, node in class_entries:
        field_names = set(node._required) | set(node._optional)
        aliases = []
        for child in list(node._required.values()) + list(node._optional.values()):
            field_name = py_function_name(child.name)
            if not field_name.endswith("_boundary"):
                continue

            alias = field_name[: -len("_boundary")]
            if not alias or alias in field_names:
                continue

            aliases.append(f'        "{alias}": "{child.name}",\n')

        if aliases:
            lines.append(f"    {api_class_expr(path)}: {{\n{''.join(aliases)}    }},\n")

    return "{\n" + "".join(lines) + "}"

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

def mark_required_field_set(node, entry):
    required_fields = list(entry.get("required") or [])
    if required_fields and required_fields not in node.required_field_sets:
        node.required_field_sets.append(required_fields)

def replace_field(target, field_name, field_node):
    cloned = field_node.clone(field_name, include_pending=False)
    if target.get_required(field_name) is not None:
        target._required[field_name] = cloned
    elif target.get_optional(field_name) is not None:
        target._optional[field_name] = cloned
    elif target.type == "polymorphic":
        for child in target._optional.values():
            if child.get_required(field_name) is not None or child.get_optional(field_name) is not None:
                replace_field(child, field_name, field_node)
    else:
        target._optional[field_name] = cloned

def apply_pending_fields(parent, child, entry_type):
    for field_name, field_node in parent.pending_variant_fields.items():
        replace_field(child, field_name, field_node)

    if not parent.pending_list_item_fields:
        return

    if entry_type == "list":
        child.add_optional(LIST_ITEM_NAME)
        target = child.get_optional(LIST_ITEM_NAME)
    else:
        target = child

    for field_name, field_node in parent.pending_list_item_fields.items():
        replace_field(target, field_name, field_node)

def record_pending_broadcast_field(parent, field_name, field_node, is_wildcard_child):
    if is_wildcard_child:
        parent.pending_list_item_fields[field_name] = field_node.clone(field_name, include_pending=False)
        for child in parent._optional.values():
            if child.type == "list":
                child.pending_list_item_fields[field_name] = field_node.clone(field_name, include_pending=False)
                child.add_optional(LIST_ITEM_NAME)
                replace_field(child.get_optional(LIST_ITEM_NAME), field_name, field_node)

def prune_variant_fields(node, visited=None):
    visited = visited or set()
    node_id = id(node)
    if node_id in visited:
        return
    visited.add(node_id)

    if node.variant_fields is not None:
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

def build_tree(schema_entries, spec_dir=None, include_dirs=None):
    root = JsonToTreeClass("root")
    schema = expand_includes(
        schema_entries,
        spec_dir=spec_dir,
        include_dirs=include_dirs,
    )

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
    for entry in schema:
        entry_type = entry.get('type')
        if entry_type not in type_list:
            raise ValueError(f'Type "{entry_type}" is not supported by the system. \nAcceptable types: {type_list}')

        name = "root" if entry['pointer'] == "/" else entry['pointer']
        parts = [name] if name == 'root' else name.strip('/').split('/')

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

        # Handle list variables.
        if path.type == "list" and parts[-1] == '*':
            parent = path
            if type_name:
                used_list_type_name = True
                if path.get_optional(type_name) is None:
                    placeholder = path.get_optional(LIST_ITEM_NAME)
                    if placeholder is not None:
                        path._optional[type_name] = placeholder.clone(type_name)
                    else:
                        path.add_optional(type_name)
                apply_pending_fields(path, path.get_optional(type_name), entry_type)
                path = path.get_optional(type_name)
                path.type_name = type_name
            else: 
                path.add_optional(LIST_ITEM_NAME)
                path = path.get_optional(LIST_ITEM_NAME)

        if (
            parts[-1] == "*"
            and parent is not None
            and parent.type == "list"
            and path.name == LIST_ITEM_NAME
            and path.type is not None
            and not type_name
            and (entry_type != "object" or path.type == "object")
        ):
            routing = (
                f"object{len(parent._optional) + 1}"
                if entry_type == "object"
                else "string"
                if entry_type == "file"
                else entry_type
            )
            parent.add_optional(routing)
            path = parent.get_optional(routing)

        if type_name and not used_list_type_name and entry_type == "object" and path.type is None:
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
            replacement_node = path
            path = placeholder

        # Handle polymorphic variables.
        if path.type == "polymorphic":
            replacement_node = path
            polymorphic_parent = path
            if type_name and entry_type == "object":
                routing = type_name
            elif entry_type != "object":
                routing = entry_type
            else:
                routing = entry_type + str(len(path._optional) + 1)
            path.add_optional(routing)
            path = path.get_optional(routing)
            apply_pending_fields(polymorphic_parent, path, entry_type)
            if type_name and entry_type == "object":
                path.type_name = type_name
            
        elif (
            path.type is not None
            and not (
                entry_type == "object"
                and path.type == "object"
                and not type_name
                and not entry.get('required')
                and entry.get('optional')
            )
        ):
            if type_name and entry_type == "object" and path.name == type_name and path.type == "object":
                routing = None
                path.type_name = type_name
            else:
                existing_variant_name = path.name if path.name != parts[-1] else None
                polymorph = path.make_it_polymorphic(existing_variant_name)
                if type_name and entry_type == "object":
                    routing = type_name
                elif entry_type != "object":
                    routing = entry_type
                else:
                    routing = entry_type + "2"
                polymorph.add_optional(routing)
                if not (len(parts) > 1 and parts[-2] == '*'):
                    parent.find_var_replace(polymorph.name, polymorph)
                path = polymorph.get_optional(routing)
                apply_pending_fields(polymorph, path, entry_type)
                if type_name and entry_type == "object":
                    path.type_name = type_name
                replacement_node = polymorph

        if entry_type == "object":
            mark_variant_fields(path, entry)
            mark_required_field_set(path, entry)

        if entry.get('required'):
            for value in entry.get('required'):
                path.add_required(value)

        if entry.get('optional'):
            for value in entry.get('optional'):
                path.add_optional(value)

        if entry.get('options'):
            for value in entry.get('options'):
                path.add_optional(value)

        doc = entry.get('doc')
        if doc:
            path.set_doc(doc)
            
        default = entry.get('default')
        path.set_default(default, 'default' in entry)
        
        node_type = entry_type if entry_type != "file" else "string"
        path.set_type(node_type)
        
        extensions = entry.get('extensions')
        path.set_extensions(extensions)

        path.set_min(entry.get('min'))
        path.set_max(entry.get('max'))

        if (len(parts) > 1 and parts[-2] == '*') or parent.type == "polymorphic":
            replacement_node = replacement_node or path
            field_name = parts[-1]
            is_wildcard_child = len(parts) > 1 and parts[-2] == '*'
            record_pending_broadcast_field(
                parent,
                field_name,
                replacement_node,
                is_wildcard_child,
            )
            for child in parent._optional.values():
                if child.type_name and field_name == "type":
                    child.find_var_replace(field_name, replacement_node.clone(field_name))
                else:
                    child.find_var_replace(field_name, replacement_node)

    prune_variant_fields(root)
    apply_type_name_defaults(root)
    return root

def generated_class_text(root):
    generated_class = root.class_generator()
    prelude = """
from typing import Optional, Iterable
from enum import Enum
import json

_UNSET = object()

def drop_none(d):
    return {k: v for k, v in d.items() if v is not None} if type(d) == dict else d

def list_check(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]

def extension_check(filename, extensions):
    if filename in (None, ""):
        return None
    if not filename.endswith(tuple(extensions)):
        raise ValueError(
            f"Invalid file extension: {filename!r}. "
            f"Allowed extensions are: {extensions}"
        )
    return filename

def class_check(value, allowed):
    if float in allowed and isinstance(value, int) and not isinstance(value, bool):
        return float(value)
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

    if float in allowed and isinstance(value, int) and not isinstance(value, bool):
        return float(value)

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
    if value in (None, ""):
        return None
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
    if tp is float and isinstance(variable, int) and not isinstance(variable, bool):
        return float(variable)
    if not isinstance(variable, tp):
        raise TypeError(f"Expected type '{tp.__name__}', but got '{type(variable).__name__}'")
    return variable
"""
    return prelude + generated_class

def generated_api_text(root, generator_overrides=None):
    class_entries = collect_class_tree(root)
    api_names = generated_api_name_map(class_entries)
    export_plan = generated_api_export_plan(class_entries, generator_overrides)
    factory_lines = []

    class_paths = {
        api_class_expr(path): path
        for path, _node in class_entries
    }

    for entry in export_plan:
        if not entry["exported"]:
            continue
        api_name = entry["api_custom_name"] or entry["api_generated_name"]
        path = class_paths[entry["class_path"]]
        class_path = api_class_expr(path)
        factory_lines.append(
            f"""
def {api_name}(*args, **kwargs):
    return _construct({class_path}, *args, **kwargs)
"""
        )

    field_wrappers_text = generated_api_field_wrapper_text(class_entries)
    field_aliases_text = generated_api_field_aliases_text(class_entries)
    list_variants_text = generated_api_list_variants_text(class_entries)
    polymorphic_variants_text = generated_api_polymorphic_variants_text(class_entries)
    class_type_names_text = generated_api_class_type_names_text(class_entries)
    factories = "".join(factory_lines)
    shortcut_factories = generated_api_shortcut_factories_text(
        class_entries,
        api_names,
        extra_used=[
            entry["api_custom_name"]
            for entry in export_plan
            if entry["api_custom_name"]
        ],
    )
    return f'''"""User-friendly factories for the generated Root class.

This file is generated from the same schema tree as generated_class.py.
Factories only construct generated class objects; defaults and validation stay
in generated_class.py.
"""

import builtins
import importlib.util
import sys
from pathlib import Path

try:
    from .generated_class import Root
except ImportError:
    from generated_class import Root


_MISSING_MODULE = object()


def _load_module_from_path(module_name, module_path):
    previous_module = sys.modules.get(module_name, _MISSING_MODULE)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError("Could not load %s from %s" % (module_name, module_path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        _restore_module(module_name, previous_module)
        raise
    return module


def _restore_module(module_name, previous_module):
    if previous_module is _MISSING_MODULE:
        sys.modules.pop(module_name, None)
    else:
        sys.modules[module_name] = previous_module


def _load_model_builder():
    source_file = Path(__file__).resolve()
    for parent in source_file.parents:
        for generator_dir in (
            parent / "generator",
            parent / "python-from-jse" / "generator",
        ):
            model_builder_path = generator_dir / "model_builder.py"
            if not model_builder_path.exists():
                continue

            previous_modules = {{
                name: sys.modules.get(name, _MISSING_MODULE)
                for name in ("id_relationships", "selection_refs")
            }}
            try:
                for dependency_name in ("id_relationships", "selection_refs"):
                    dependency_path = generator_dir / (dependency_name + ".py")
                    if dependency_path.exists():
                        _load_module_from_path(dependency_name, dependency_path)
                module = _load_module_from_path(
                    "_generated_api_model_builder",
                    model_builder_path,
                )
            finally:
                for name, previous_module in previous_modules.items():
                    _restore_module(name, previous_module)

            return module.ModelBuilder

    raise ModuleNotFoundError(
        "Could not find python-from-jse/generator/model_builder.py "
        "from generated API file %s" % source_file
    )


ModelBuilder = _load_model_builder()


class _GeneratedApiProxy:
    def __init__(self, namespace):
        self._namespace = namespace

    def __getattr__(self, name):
        try:
            return self._namespace[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


_FIELD_WRAPPERS = {field_wrappers_text}
_FIELD_ALIASES = {field_aliases_text}
_LIST_VARIANTS = {list_variants_text}
_POLYMORPHIC_VARIANTS = {polymorphic_variants_text}
_CLASS_TYPE_NAMES = {class_type_names_text}


def _construct(cls, *args, **kwargs):
    if kwargs:
        type_name = _CLASS_TYPE_NAMES.get(cls)
        if type_name is not None and "type" not in kwargs:
            kwargs = dict(kwargs)
            kwargs["type"] = type_name
        kwargs = _wrap_kwargs(cls, kwargs)
    return cls(*args, **kwargs)


def _wrap_kwargs(cls, kwargs):
    values = dict(kwargs)

    for alias, target in _FIELD_ALIASES.get(cls, {{}}).items():
        if alias in values:
            if target in values:
                raise TypeError(f"Use either {{alias!r}} or {{target!r}}, not both")
            values[target] = values.pop(alias)

    if "items" in values and cls in _LIST_VARIANTS and isinstance(values["items"], builtins.list):
        values["items"] = [_wrap_list_item(cls, item) for item in values["items"]]

    for key, (kind, wrapper) in _FIELD_WRAPPERS.get(cls, {{}}).items():
        if key in values:
            values[key] = _wrap_value(values[key], kind, wrapper)

    return values


def _wrap_value(value, kind, wrapper):
    if value is None or isinstance(value, wrapper):
        return value

    if kind == "list":
        if isinstance(value, builtins.list):
            return wrapper(items=[_wrap_list_item(wrapper, item) for item in value])
        return wrapper(items=[_wrap_list_item(wrapper, value)])

    if kind == "polymorphic":
        if isinstance(value, builtins.dict):
            variants = _POLYMORPHIC_VARIANTS.get(wrapper, ())
            if variants:
                return wrapper(_construct(_select_variant(value, variants), **value))
        return wrapper(value)

    if kind == "object" and isinstance(value, builtins.dict):
        return _construct(wrapper, **value)

    return value


def _wrap_list_item(wrapper, item):
    variants = _LIST_VARIANTS.get(wrapper, ())
    for cls, _type_name, _required, _fields in variants:
        if isinstance(item, cls):
            return item
    if not isinstance(item, builtins.dict):
        if len(variants) == 1:
            cls, _type_name, required, _fields = variants[0]
            if not required:
                return _construct(cls, item)
        return item

    return _construct(_select_variant(item, variants), **item)


def _select_variant(data, variants):
    if not variants:
        raise TypeError(f"No generated variants are available for {{data!r}}")

    type_value = data.get("type")
    if type_value is not None:
        for cls, type_name, _required, _fields in variants:
            if type_value in (type_name, cls.__name__):
                return cls

    keys = set(data)
    best_cls = None
    best_score = (-1, -1)
    for cls, _type_name, required, fields in variants:
        required = set(required)
        if not required.issubset(keys):
            continue
        score = (len(required), len(keys.intersection(fields)))
        if score > best_score:
            best_cls = cls
            best_score = score

    if best_cls is not None:
        return best_cls

    raise TypeError(f"Could not choose a generated variant for keys {{sorted(keys)!r}}")


def unit(value, unit):
    return {{"value": value, "unit": unit}}


_CONFIG_SECTION_SHORTCUTS = {{
    "time": {{
        "time_tend": "tend",
        "time_dt": "dt",
    }},
    "contact": {{
        "contact_enabled": "enabled",
        "contact_dhat": "dhat",
    }},
}}
_CONFIG_SECTION_WRAPPER_NAMES = {{
    "time": "Time",
    "contact": "Contact",
}}


def _config_section_wrapper(section):
    wrapper_name = _CONFIG_SECTION_WRAPPER_NAMES[section]
    return getattr(Root, wrapper_name, None)


def _expand_config_shortcuts(kwargs):
    values = dict(kwargs)

    for section, shortcuts in _CONFIG_SECTION_SHORTCUTS.items():
        section_values = {{}}
        used_shortcuts = []
        for shortcut, target in shortcuts.items():
            if shortcut in values:
                section_values[target] = values.pop(shortcut)
                used_shortcuts.append(shortcut)

        if not section_values:
            continue

        if section in values:
            raise TypeError(
                f"Use either {{section!r}} or flat config shortcuts {{used_shortcuts!r}}, not both"
            )

        wrapper = _config_section_wrapper(section)
        if wrapper is None:
            raise TypeError(
                f"Config shortcut section {{section!r}} is not available in this generated API"
            )
        if wrapper in _POLYMORPHIC_VARIANTS:
            values[section] = _wrap_value(section_values, "polymorphic", wrapper)
        else:
            values[section] = _construct(wrapper, **section_values)

    return values


def config(**kwargs):
    return _construct(Root, **_expand_config_shortcuts(kwargs))


def model(**kwargs):
    api_module = sys.modules.get(__name__)
    if api_module is None:
        api_module = _GeneratedApiProxy(globals())
    return ModelBuilder(api_module, **kwargs)
{factories}
{shortcut_factories}'''

def generate(
    schema_file=DEFAULT_SCHEMA_FILE,
    output_file=DEFAULT_OUTPUT_FILE,
    api_output_file=DEFAULT_API_OUTPUT_FILE,
    generator_overrides_file=None,
    manifest_dir=None,
    generator_overrides=None,
    include_spec_dirs=None,
):
    with open(schema_file, encoding="utf-8") as f:
        schema_entries = json.load(f)

    if generator_overrides is None:
        generator_overrides = load_generator_overrides(generator_overrides_file)
    else:
        generator_overrides = normalized_generator_overrides(generator_overrides)
    schema_entries, schema_patch_report = apply_schema_patches(
        schema_entries,
        generator_overrides,
    )
    root = build_tree(
        schema_entries,
        spec_dir=Path(schema_file).parent,
        include_dirs=include_spec_dirs,
    )
    generated_class = generated_class_text(root)
    generated_api = generated_api_text(root, generator_overrides)
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(generated_class)

    api_output_file = Path(api_output_file)
    api_output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(api_output_file, "w", encoding="utf-8") as f:
        f.write(generated_api)

    manifest_dir = Path(manifest_dir) if manifest_dir is not None else api_output_file.parent
    manifest_dir.mkdir(parents=True, exist_ok=True)
    init_file = manifest_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text(
            '"""Generated Python API artifacts."""\n',
            encoding="utf-8",
        )
    with open(manifest_dir / "schema_patch_report.json", "w", encoding="utf-8") as f:
        json.dump(schema_patch_report, f, indent=2)
        f.write("\n")
    with open(manifest_dir / "class_tree_manifest.json", "w", encoding="utf-8") as f:
        json.dump(class_tree_manifest(root), f, indent=2)
        f.write("\n")
    with open(manifest_dir / "generated_api_manifest.json", "w", encoding="utf-8") as f:
        json.dump(generated_api_manifest(root, generator_overrides), f, indent=2)
        f.write("\n")

    print(f"Generated {output_file}")
    print(f"Generated {api_output_file}")
    return generated_class


if __name__ == "__main__":
    generate()
