"""
Experiment session (:mod:`fluidlab.exp.session`)
================================================

.. currentmodule:: fluidlab.exp.session

Provides:

.. autoclass:: Session
   :members:
   :private-members:

.. autoclass:: SessionWithDefaultParams
   :members:
   :private-members:

"""


from fluiddyn.util.logger import Logger


class Session(object):
    def __init__(self, path=None, name=None, info=None,
                 email_to=None, email_title=None, email_delay=None):
        self.logger = Logger(email_to=email_to, email_title=email_title,
                             email_delay=email_delay)

        # in fact, it should be more complicate than that.
        self.path = path
        self.name = name
        self.info = info

        # should be initialized in a better way
        self.data_tables = {}

    def get_data_table(self, name):
        if name not in self.data_tables:
            self.data_tables[name] = DataTable(name, session=self)

        return self.data_tables[name]


class DataTable(object):
    def __init__(self, path=None, name=None, session=None):

        self.name = name = name or 'data'

        if session is not None:
            self.path = session.path

        self.figures = {}

    def init_figure(self, keys):
        raise NotImplementedError

    def save(self, dict_to_save):
        raise NotImplementedError


class SessionWithDefaultParams(Session):

    @classmethod
    def create_default_params(cls):
        raise NotImplementedError

    def __init__(self, params):

        self.params = params

        path = params.path
        name = params.name
        info = params.info
        email_to = params.email.to
        email_title = params.email.title
        email_delay = params.email.delay

        super(SessionWithDefaultParams, self).__init__(
            path=path, name=name, info=info,
            email_to=email_to, email_title=email_title,
            email_delay=email_delay)
