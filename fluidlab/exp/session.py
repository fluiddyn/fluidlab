"""Experiment session (:mod:`fluidlab.exp.session`)
===================================================

.. todo::

   Improve :class:`fluidlab.exp.session.Session` to produce a nice
   file `session.h5`.

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
import csv
import time
from copy import copy

import numpy as np
import matplotlib.pyplot as plt

from fluiddyn.util.logger import Logger
from fluiddyn.io import FLUIDLAB_PATH
from fluiddyn.io.hdf5 import H5File
from fluiddyn.io.mycsv import CSVFile
from fluiddyn.util import time_as_str

class Session(object):
    """Experimental session

    Base class representing an experimental session. A session
    automatically creates or loads files containing data. It contains
    an object `logger` for printing with logging (and possibly sending
    emails).

    It can create managers of data tables for saving, loading and
    plotting data time series (see :class:`fluidlab.exp.session.DataTable`).


    Parameters
    ----------

    path : {None, str}

    name : {None, str}

    info : {None, str}

    save_in_dir : {True, False}

    email_to : {None, str}

    email_title : {None, str}

    email_delay : {None, int}
       Time is second between two emails.

    """
    def __init__(self, path=None, name=None, info=None,
                 save_in_dir=True,
                 email_to=None, email_title=None, email_delay=None,
                 email_server='localhost'):

        if not save_in_dir and path is None:
            path = './'

        if path is None:
            path = FLUIDLAB_PATH
        elif not (path.startswith('.') or path.startswith('/')):
            # !! wrong under Windows ??!!
            path = os.path.join(FLUIDLAB_PATH, path)

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
            # should be initialized in a better way (loaded from files?)
            self.data_tables = {}

        path_log_file = os.path.join(
            self.path, self._base_name_files + 'log.txt')

        print('In session: email_to', email_to)


        self.logger = Logger(path=path_log_file,
                             email_to=email_to, email_title=email_title,
                             email_delay=email_delay, email_server=email_server)

        if self._new_session:
            action = 'Create'
        else:
            action = 'Load'

        self.logger.print_log(
            action + ' experimental session ({})\n'.format(time_as_str()) +
            'path: ' + self.path)

    def get_data_table(self, name=None, **kargs):
        """Create or get a data table.

        See :class:`fluidlab.exp.session.DataTable`.

        """
        if name not in self.data_tables:
            self.data_tables[name] = DataTable(name, session=self, **kargs)

        return self.data_tables[name]


class DataTable(object):
    """Data table for time series

    Parameters
    ----------

    name : {None, str}, optional
      Name of the date table.

    path : {None, str}, optional
      Path of a directory or of a file.

    session : {None, fluidlab.exp.session.Session}, optional
      A session used to get its path.

    extension : {None, 'csv'}, optional
      An extension defining in which format the data is saved.

    fieldnames : {None, array_like}, optional
      An array_like of strings.

    add_time : {True, False}, optional

    add_clock : {True, False}, optional

    """

    _supported_extensions = ['csv']

    def __init__(self, name=None, path=None, session=None, extension=None,
                 fieldnames=None, add_time=True, add_clock=True):
        plt.ion()

        if session is not None and path is not None:
            raise ValueError(
                'Only one of the arguments `session` and `path` '
                'has to be given.')
        elif session is None and path is None:
            raise ValueError(
                'At least one of the arguments `session` or `path` '
                'has to be given.')
        elif session is not None:
            path = session.path

        if path is None or os.path.isdir(path):
            name = name or 'data'

            name, extension_name = os.path.splitext(name)
            extension_name = extension_name[1:]

            if len(extension_name) != 0 and extension is not None:
                if extension_name != extension:
                    raise ValueError(
                        'extension is inconsistent with the extension '
                        'got from the name')
            if len(extension_name) == 0 and extension is None:
                extension = 'csv'
            else:
                extension = extension_name

        elif os.path.isfile(path):
            # path should correspond to a data table file
            if name is not None:
                raise ValueError(
                    'If path points towards a file, `name` should be None '
                    'because it is loaded from the file.')

            if extension is not None:
                raise ValueError(
                    'If path points towards a file, `extension` should be '
                    'None because it is guessed from the file name.')

            # we have to load `name` from the file
            name = os.path.split(path)
            name, extension = os.path.splitext(name)
            extension = extension[1:]

        if extension not in self._supported_extensions:
            raise ValueError('The extension of the file is not supported.')

        path = path or FLUIDLAB_PATH

        if os.path.isdir(path):
            path = os.path.join(path, name + '.' + extension)

        if fieldnames is not None:
            if add_clock and 'clock' not in fieldnames:
                fieldnames.insert(0, 'clock')
            if add_time and 'time' not in fieldnames:
                fieldnames.insert(0, 'time')

        if not os.path.isfile(path):
            # we have to create the file
            if fieldnames is None:
                raise ValueError(
                    'For new data table, the argument '
                    '`fieldnames` has to be given.')

            with open(path, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
        else:
            # the file already exists
            with open(path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                if fieldnames is not None and fieldnames != reader.fieldnames:
                    raise ValueError(
                        '`fieldnames` does not correspond to the content '
                        'of the file.')

        self.path = path
        self.name = name
        self.extension = extension
        self.fieldnames = fieldnames

        varnames = copy(fieldnames)
        if 'time' in varnames:
            varnames.remove('time')
        if 'clock' in varnames:
            varnames.remove('clock')
        self.varnames = varnames

        self.add_time = add_time
        self.add_clock = add_clock

        self.figures = []

    def init_figure(self, varnames=None):
        """Initialize a figure to follow the evolution of variables."""

        if varnames is None:
            varnames = self.varnames

        fig = self.plot_vs_time(varnames)

        fig._varnames = varnames
        self.figures.append(fig)

    def get_nb_times_saved(self):
        with open(self.path) as f:
            num_lines = sum(1 for line in f)

        return num_lines - 1

    def update_figures(self):
        """Update all active figures of the data table."""
        for fig in self.figures:
            ax = fig.get_axes()[0]
            varnames = fig._varnames
            nb_points_plotted = fig._nb_points_plotted
            nb_times = self.get_nb_times_saved()
            nb_points_to_plot = nb_times - nb_points_plotted

            assert nb_points_to_plot >= 0

            if nb_points_to_plot == 0:
                continue

            if self.add_time:
                fieldnames = ['time'] + varnames
            elif self.add_clock:
                fieldnames = ['clock'] + varnames

            d = self.load(fieldnames, skiptimes=nb_points_plotted)

            if self.add_time:
                time = d.pop('time')
            elif self.add_clock:
                time = d.pop('clock')
            else:
                time = np.arange(
                    nb_points_plotted, nb_points_plotted + nb_points_to_plot,
                    dtype=int)

            for k in varnames:
                ax.plot(time, d[k], 'x' + fig._colors[k])

            fig._nb_points_plotted += nb_points_to_plot
            fig.canvas.draw()

        plt.show()

    def save(self, dict_to_save):
        """Save the data contained in the dict `dict_to_save`."""

        if self.add_clock and 'clock' not in dict_to_save:
            dict_to_save['clock'] = time.clock()
        if self.add_time and 'time' not in dict_to_save:
            dict_to_save['time'] = time.time()

        with open(self.path, 'a') as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=self.fieldnames)
            writer.writerow(dict_to_save)

    def load(self, fieldnames=None, skiptimes=0):
        """Load the data contained in the files as a dict."""
        if fieldnames is None:
            fieldnames = self.fieldnames

        with CSVFile(self.path) as f:
            d = f.load_as_dict(keys=fieldnames, skiptimes=skiptimes)

        return d

    def plot_vs_time(self, varnames=None):
        """Plot the evolution of variables."""
        if varnames is None:
            varnames = self.varnames

        if self.add_time:
            fieldnames = ['time'] + varnames
        elif self.add_clock:
            fieldnames = ['clock'] + varnames

        d = self.load(fieldnames)

        if self.add_time:
            time = d.pop('time')
        elif self.add_clock:
            time = d.pop('clock')
        else:
            arr = d.popitem()
            time = np.arange(arr.size, dtype=int)

        fig = plt.figure()
        fig._nb_points_plotted = time.size
        ax = plt.gca()

        fig._colors = {}
        for k in varnames:
            line = ax.plot(time, d[k])[0]
            fig._colors[k] = line.get_color()

        ax.set_xlabel('time')
        plt.legend(varnames, loc=3)
        plt.show()
        return fig


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
    session = Session(name='Test1', save_in_dir=True)

    # session.logger.print_log('Hello.', 1, 3.14, end='')
    # session.logger.print_log('   This is the end...')

    dt = session.get_data_table(
        'table0', fieldnames=['R1', 'R2'])

    dt.init_figure()
    
    # dt.save({'R1': 1, 'R2': 0})
    # dt.save({'R1': 2, 'R2': 1})

    # dt = session.get_data_table(
    #     'table2', fieldnames=['R3'])

    # dt.save({'R3': 2})

    
