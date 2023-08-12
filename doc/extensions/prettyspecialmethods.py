# This is a fork of https://github.com/sphinx-contrib/prettyspecialmethods / https://pypi.org/project/sphinxcontrib-prettyspecialmethods/
# Specifically, it is based off the modified version linked from this issue:
# https://github.com/sphinx-contrib/prettyspecialmethods/issues/16

"""
    sphinxcontrib.prettyspecialmethods
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Shows special methods as the python syntax that invokes them

    :copyright: Copyright 2018 by Thomas Smith
    :license: MIT, see LICENSE for details.
"""

# import pbr.version
import sphinx.addnodes as SphinxNodes
from docutils import nodes
from docutils.nodes import Text
from typing import TYPE_CHECKING, Tuple
import sphinx.domains.python
from sphinx.domains.python import py_sig_re
from docutils.parsers.rst import directives
import sphinx.ext.autodoc


# __version__ = pbr.version.VersionInfo(
#     'prettyspecialmethods').version_string()


ATTR_TOC_SIG = '_prettyspecialmethods_sig'
CONF_SIG_PREFIX = 'prettyspecialmethods_signature_prefix'


def self_identifier(name = 'self'):
    # Format like a parameter, though we cannot use desc_parameter because it
    # causes error in html emitter
    return SphinxNodes.desc_sig_name('', name)


# Parameter nodes cannot be used outside of a parameterlist, because it breaks
# the html emitter.  So we unpack their contents.
# Better than astext() because it preserves references.
def unwrap_parameter(parameters_node, index = 0):
    if len(parameters_node.children) > index:
        return parameters_node.children[index].children
    return ()


# For keywords/builtins and punctuation that describes the operator and should
# be formatted similar to a method or attribute's name.
# For example, in the case of `del self[index]`: `del`, `[` and `]` should be
# formatted like the method name `__delitem__` would have been formatted.
def operator_name(str):
    return SphinxNodes.desc_name('', '', Text(str))
def operator_punctuation(str):
    return SphinxNodes.desc_name('', '', Text(str))


# For punctuation that is not part of the operator
def punctuation(str):
    return SphinxNodes.desc_sig_punctuation('', str)


def patch_node(node, text=None, children=None, *, constructor=None):
    if constructor is None:
        constructor = node.__class__

    if text is None:
        text = node.text

    if children is None:
        children = node.children

    return constructor(
        node.source,
        text,
        *children,
        **node.attributes,
    )


def function_transformer(new_name):
    def xf(name_node, parameters_node):
        return (
            patch_node(name_node, new_name, ()),
            patch_node(parameters_node, '', [
                self_identifier(),
                *parameters_node.children,
            ])
        )

    return xf


def unary_op_transformer(op):
    def xf(name_node, parameters_node):
        return (
            patch_node(name_node, op, ()),
            self_identifier(),
        )

    return xf


def binary_op_transformer(op):
    def xf(name_node, parameters_node):
        return (
            self_identifier(),
            Text(' '),
            patch_node(name_node, op, ()),
            Text(' '),
            *unwrap_parameter(parameters_node)
        )

    return xf


def brackets(parameters_node):
    return [
        self_identifier(),
        operator_punctuation('['),
        *unwrap_parameter(parameters_node),
        operator_punctuation(']')
    ]


SPECIAL_METHODS = {
    '__getitem__': lambda name_node, parameters_node: (
        brackets(parameters_node)
    ),
    '__setitem__': lambda name_node, parameters_node: (
        *brackets(parameters_node),
        Text(' '),
        operator_punctuation('='),
        Text(' '),
        *unwrap_parameter(parameters_node, 1)
    ),
    '__delitem__': lambda name_node, parameters_node: (
        SphinxNodes.desc_name('', '', Text('del')),
        Text(' '),
        *brackets(parameters_node),
    ),
    '__contains__': lambda name_node, parameters_node: (
        *unwrap_parameter(parameters_node),
        Text(' '),
        SphinxNodes.desc_name('', '', Text('in')),
        Text(' '),
        self_identifier(),
    ),

    '__await__': lambda name_node, parameters_node: (
        SphinxNodes.desc_name('', '', Text('await')),
        Text(' '),
        self_identifier(),
    ),

    '__lt__': binary_op_transformer('<'),
    '__le__': binary_op_transformer('<='),
    '__eq__': binary_op_transformer('=='),
    '__ne__': binary_op_transformer('!='),
    '__gt__': binary_op_transformer('>'),
    '__ge__': binary_op_transformer('>='),

    '__hash__': function_transformer('hash'),
    '__len__': function_transformer('len'),
    '__iter__': function_transformer('iter'),
    '__str__': function_transformer('str'),
    '__repr__': function_transformer('repr'),

    '__add__': binary_op_transformer('+'),
    '__sub__': binary_op_transformer('-'),
    '__mul__': binary_op_transformer('*'),
    '__matmul__': binary_op_transformer('@'),
    '__truediv__': binary_op_transformer('/'),
    '__floordiv__': binary_op_transformer('//'),
    '__mod__': binary_op_transformer('%'),
    '__divmod__': function_transformer('divmod'),
    '__pow__': binary_op_transformer('**'),
    '__lshift__': binary_op_transformer('<<'),
    '__rshift__': binary_op_transformer('>>'),
    '__and__': binary_op_transformer('&'),
    '__xor__': binary_op_transformer('^'),
    '__or__': binary_op_transformer('|'),

    '__neg__': unary_op_transformer('-'),
    '__pos__': unary_op_transformer('+'),
    '__abs__': function_transformer('abs'),
    '__invert__': unary_op_transformer('~'),

    '__call__': lambda name_node, parameters_node: (
        self_identifier(),
        patch_node(parameters_node, '', parameters_node.children)
    ),
    '__getattr__': function_transformer('getattr'),
    '__setattr__': function_transformer('setattr'),
    '__delattr__': function_transformer('delattr'),

    '__bool__': function_transformer('bool'),
    '__int__': function_transformer('int'),
    '__float__': function_transformer('float'),
    '__complex__': function_transformer('complex'),
    '__bytes__': function_transformer('bytes'),

    # could show this as "{:...}".format(self) if we wanted
    '__format__': function_transformer('format'),

    '__index__': function_transformer('operator.index'),
    '__length_hint__': function_transformer('operator.length_hint'),
    '__ceil__': function_transformer('math.ceil'),
    '__floor__': function_transformer('math.floor'),
    '__trunc__': function_transformer('math.trunc'),
    '__round__': function_transformer('round'),

    '__sizeof__': function_transformer('sys.getsizeof'),
    '__dir__': function_transformer('dir'),
    '__reversed__': function_transformer('reversed'),
}


class PyMethod(sphinx.domains.python.PyMethod):
    """
    Replacement for sphinx's built-in PyMethod directive, behaves identically
    except for tweaks to special methods.
    """

    option_spec = sphinx.domains.python.PyMethod.option_spec.copy()
    option_spec.update({
        'selfparam': directives.unchanged_required,
    })

    def _get_special_method(self, sig: str):
        "If this is a special method, return its name, otherwise None"
        m = py_sig_re.match(sig)
        if m is None:
            return None
        prefix, method_name, typeparamlist, arglist, retann = m.groups()
        if method_name not in SPECIAL_METHODS:
            return None
        return method_name

    def get_signature_prefix(self, sig: str) -> list[nodes.Node]:
        prefix = super().get_signature_prefix(sig)
        signature_prefix = getattr(self.env.app.config, CONF_SIG_PREFIX)
        if signature_prefix:
            method_name = self._get_special_method(sig)
            if method_name is not None:
                prefix.append(nodes.Text(signature_prefix))
                prefix.append(SphinxNodes.desc_sig_space())
        return prefix

    def handle_signature(self, sig: str, signode: SphinxNodes.desc_signature) -> Tuple[str, str]:
        method_name = self._get_special_method(sig)

        result = super().handle_signature(sig, signode)

        if method_name is None:
            return result

        sig_rewriter = SPECIAL_METHODS[method_name]
        name_node = signode.next_node(SphinxNodes.desc_name)
        parameters_node = signode.next_node(SphinxNodes.desc_parameterlist)

        replacement = sig_rewriter(name_node, parameters_node)
        parent = name_node.parent
        parent.insert(parent.index(name_node), replacement)
        parameters_node.replace_self(())
        parent.remove(name_node)

        # Generate TOC name by doing the same rewrite w/ typehints stripped from
        # params, then converting to str
        parameters_sans_types = [SphinxNodes.desc_parameter('', '', p.children[0]) for p in parameters_node.children]
        parameters_node_sans_types = SphinxNodes.desc_parameterlist('', '',
            *parameters_sans_types
        )
        replacement_w_out_types = sig_rewriter(name_node, parameters_node_sans_types)
        toc_name = ''.join([node.astext() for node in replacement_w_out_types])
        signode.attributes[ATTR_TOC_SIG] = toc_name

        return result

    def _toc_entry_name(self, sig_node: SphinxNodes.desc_signature):
        # TODO support toc_object_entries_show_parents?
        # How would that work?  Show class name in place of `self`?
        return sig_node.attributes.get(ATTR_TOC_SIG, super()._toc_entry_name(sig_node))


def show_special_methods(app, what, name, obj, skip, options):
    if what == 'class' and name in SPECIAL_METHODS and getattr(obj, '__doc__', None):
        return False


def setup(app):
    app.add_config_value(CONF_SIG_PREFIX, 'implements', True)
    app.connect('autodoc-skip-member', show_special_methods)
    app.registry.add_directive_to_domain('py', 'method', PyMethod)
    # return {'version': __version__, 'parallel_read_safe': True}
    return {'parallel_read_safe': True}
