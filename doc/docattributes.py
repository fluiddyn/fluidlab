
from __future__ import print_function

from fluidlab.instruments.features import Feature

from docutils.statemachine import ViewList
from sphinx.domains.python import PythonDomain


def mangle_docstrings(app, what, name, obj, options, lines,
                      reference_offset=[0]):

    if what == 'attribute' and isinstance(obj, Feature):
        # print('docattributes mangle_docstrings', what, name)

        if obj.__doc__ is not None:
            lines[:] = obj.__doc__.split('\n')


class DocAttributesDomain(PythonDomain):
    name = 'docattributes'

    def __init__(self, *a, **kw):
        super(DocAttributesDomain, self).__init__(*a, **kw)

        objtype = 'attribute'
        base_directive = self.directives[objtype]

        class directive(base_directive):
            def run(self):
                env = self.state.document.settings.env

                name = self.arguments[0]
                currmodule = env.ref_context.get('py:module')
                currclass = env.ref_context.get('py:class')
                cls = env.app.import_object(currmodule + '.' + currclass)
                name_attr = name.split('.')[1]
                obj = cls.__dict__[name_attr]
                lines = list(self.content)
                mangle_docstrings(env.app, objtype, name, obj, None, lines)
                self.content = ViewList(lines, self.content.parent)

                return base_directive.run(self)

        self.directives[objtype] = directive


def setup(app):
    app.connect('autodoc-process-docstring', mangle_docstrings)
    app.add_domain(DocAttributesDomain)
