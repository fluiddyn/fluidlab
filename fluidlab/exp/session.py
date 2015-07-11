"""Experiment session (:mod:`fluidlab.exp.session`)
===================================================

.. todo::

   Improve :class:`fluidlab.exp.session.Session` to produce a nice
   `session.h5`.

.. todo::
   Implement a working :class:`fluidlab.exp.session.DataTable` class.


Provides:

.. autoclass:: Session
   :members:
   :private-members:

.. autoclass:: SessionWithDefaultParams
   :members:
   :private-members:

.. autoclass:: DataTable
   :members:
   :private-members:

"""

from __future__ import print_function

import os
from glob import glob

from fluiddyn.util.logger import Logger
from fluiddyn.io import FLUIDLAB_PATH
from fluiddyn.io.hdf5 import H5File
from fluiddyn.util import time_as_str


class Session(object):
    """Experimental session

    Base class representing an experimental session. A session
    automatically creates or loads files containing data. It contains
    a object `logger` for printing with logging (and possibly sending
    emails).

    It contains managers of data tables for saving, loading and
    plotting data time series (see :class:`DataTable`).

    """
    def __init__(self, path=None, name=None, info=None,
                 save_in_dir=True,
                 email_to=None, email_title=None, email_delay=None):

        if not save_in_dir and path is None:
            path = './'

        path = path or FLUIDLAB_PATH

        if name is None:
            name = ''

        if save_in_dir:
            str_for_glob = os.path.join(path, name) + '*/session.h5'
        else:
            str_for_glob = os.path.join(path, name + '_*_session.h5')
        session_files = glob(str_for_glob)

        if len(session_files) > 1:
            raise ValueError('Too many session files...')
        elif len(session_files) == 0:
            self._new_session = True
            if name == '':
                self.name = time_as_str()
            else:
                self.name = name + '_' + time_as_str()

            if save_in_dir:
                self._base_name_files = ''
                self.path = os.path.join(path, self.name)
            else:
                self._base_name_files = self.name + '_'
                self.path = path

            if not os.path.exists(self.path):
                os.makedirs(self.path)

            self.path_session_file = os.path.join(
                self.path, self._base_name_files + 'session.h5')
            with H5File(self.path_session_file, 'a'):
                pass

        else:
            self._new_session = False
            self.path_session_file = session_files[0]

            self._base_name_files = os.path.split(
                self.path_session_file)[1].split('session.h5')[0]

            self.path = os.path.dirname(self.path_session_file)

            if save_in_dir:
                self.name = os.path.split(self.path)[1]
            else:
                self.name = self._base_name_files.strip('_')

        self.info = info

        if self._new_session:
            self.data_tables = {}
        else:
            # should be initialized in a better way (loaded from files)
            self.data_tables = {}

        path_log_file = os.path.join(
            self.path, self._base_name_files + 'log.txt')
        self.logger = Logger(path=path_log_file,
                             email_to=email_to, email_title=email_title,
                             email_delay=email_delay)

    def get_data_table(self, name):
        if name not in self.data_tables:
            self.data_tables[name] = DataTable(name, session=self)

        return self.data_tables[name]


class DataTable(object):
    """Data table for time series

    """
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
    """Not implemented


    """

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


if __name__ == '__main__':
    session = Session(name='test', save_in_dir=False)

    session.logger.print_log('Hello.', 1, 3.14, end='')

    session.logger.print_log('   This is the end...')
