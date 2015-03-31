"""
Serie of arrays (:mod:`fluidlab.postproc.serieofarrays`)
========================================================

.. currentmodule:: fluidlab.postproc.serieofarrays


Provides:

.. autoclass:: SerieOfArrays
   :members:
   :private-members:


"""

from __future__ import division, print_function

import os
from glob import glob

from copy import copy

import itertools

# import numpy as np
import scipy


class SerieOfArrays(object):
    """Serie of arrays used for post-processing.

    Parameters
    ----------
    (for the __init__ method)

    path : str
        The path of the base directory or of a file example.

    Notes
    -----
    ???

    Attributes
    ----------
    path_dir : str
        The path of the base directory.

    """
    def __init__(self, path):
        if os.path.isfile(path):
            self.path_dir, self.filename_given = os.path.split(path)
        elif os.path.isdir(path):
            self.path_dir = path
            self.filename_given = glob(path + '/*')[0].split('/')[-1]
        else:
            raise ValueError('The provided path does not exist:\n'
                             + path)

        if '.' in self.filename_given:
            self.extension_file = self.filename_given.split('.')[-1]
        else:
            self.extension_file = ''


class SerieOfArraysFromFiles(SerieOfArrays):
    """Serie of arrays saved in files (images, netcdf, etc.).


    Parameters
    ----------
    (for the __init__ method)

    path : str
        The path of the base directory or of a file example.

    index_slices : None or iterable of iterables
        Series of slides (start, end, step).

    Attributes
    ----------
    path_dir : str
        The path of the base directory.

    index_slices : list of list
        Lists of slides "[start, end, step]" (one for each index).
        This list can be changed to loop over different sets of files.

    """
    def __init__(self, path, index_slices=None):

        super(SerieOfArraysFromFiles, self).__init__(path)

        self.base_name = ''.join(
            itertools.takewhile(str.isalpha, self.filename_given))

        # remove base_name
        remains = self.filename_given[len(self.base_name):]

        # remove extension
        if self.extension_file != '':
            remains = remains[:-(1+len(self.extension_file))]

        # serie separator_base_index
        if not str.isdigit(remains[0]):
            self.separator_base_index = remains[0]
            remains = remains[1:]
        else:
            self.separator_base_index = ''

        self.index_types = []
        self.index_lens = []
        self.index_separators = []
        while len(remains) != 0:
            if str.isdigit(remains[0]):
                test_type = str.isdigit
                self.index_types.append('digit')
            elif str.isalpha(remains[0]):
                test_type = str.isalpha
                self.index_types.append('alpha')
            index = ''.join(itertools.takewhile(test_type, remains))
            self.index_lens.append(len(index))
            remains = remains[len(index):]
            if len(remains) > 0:
                if not str.isalnum(remains[0]):
                    self.index_separators.append(remains[0])
                    remains = remains[1:]
                else:
                    self.index_separators.append('')
        self.index_separators.append('')

        self.nb_indices = len(self.index_types)

        str_glob_indices = ''
        for separator in self.index_separators:
            str_glob_indices = str_glob_indices + '*' + separator

        str_glob = (self.base_name + self.separator_base_index
                    + str_glob_indices)
        if self.extension_file != '':
            str_glob = str_glob + '.' + self.extension_file
        str_glob = os.path.join(self.path_dir, str_glob)
        paths = glob(str_glob)
        if not paths:
            raise ValueError(
                'There is no data in the provided path directory: '+str_glob)

        file_names = [os.path.basename(p) for p in paths]
        file_names.sort()

        indices_all_files = [
            self.compute_indices_from_filename(file_name)
            for file_name in file_names]

        indices_indices = zip(*indices_all_files)
        self.index_slices_all_files = []
        for i_ind in range(self.nb_indices):
            self.index_slices_all_files.append(
                [min(indices_indices[i_ind]),
                 max(indices_indices[i_ind])+1, 1])

        if index_slices is None:
            self.index_slices = copy(self.index_slices_all_files)
        else:
            self.index_slices = index_slices

    def get_array_from_name(self, name):
        return scipy.misc.imread(os.path.join(self.path_dir, name))

    def get_array_from_indices(self, indices):
        return self.get_array_from_name(
            self.compute_name_from_indices(indices))

    def get_paths_all_files(self):
        str_glob = os.path.join(self.path_dir, self.base_name+'*')
        paths = glob(str_glob)
        paths.sort()
        return paths

    def verify_all_fields_present(self):
        raise ValueError('Not yet implemented.')

    def __iter__(self):
        lists = [range(*s) for s in self.index_slices]
        for l in itertools.product(*lists):
            yield self.compute_name_from_indices(l)

    def iter_indices(self):
        lists = [range(*s) for s in self.index_slices]
        for l in itertools.product(*lists):
            yield l

    def iter_name_files(self):
        lists = [range(*s) for s in self.index_slices]
        for l in itertools.product(*lists):
            yield self.compute_name_from_indices(l)

    def iter_path_files(self):
        lists = [range(*s) for s in self.index_slices]
        for l in itertools.product(*lists):
            yield os.path.join(
                self.path_dir, self.compute_name_from_indices(l))

    def compute_strindices_from_indices(self, indices):
        nb_indices = len(indices)
        if nb_indices != len(self.index_types):
            raise ValueError('Too many or not enough indexes given')

        str_indices = ''
        for i in range(nb_indices):
            if self.index_types[i] == 'digit':
                code_format = '{:0' + str(self.index_lens[i]) + 'd}'
                str_index = code_format.format(indices[i])
            elif self.index_types[i] == 'alpha':
                if indices[i] > 25:
                    raise ValueError('"alpha" index larger than 25.')
                str_index = chr(ord('a') + indices[i])
            else:
                raise Exception('The type should be "digit" or "alpha".')

            str_indices += str_index + self.index_separators[i]
        return str_indices

    def compute_name_from_indices(self, indices):

        name_file = (self.base_name + self.separator_base_index
                     + self.compute_strindices_from_indices(indices))
        if self.extension_file != '':
            name_file = name_file + '.' + self.extension_file

        return name_file

    def compute_indices_from_filename(self, file_name):
        str_indices = file_name[len(self.base_name):]

        if self.separator_base_index != '':
            str_indices = str_indices[1:]

        if self.extension_file != '':
            str_indices = str_indices[:-(len(self.extension_file)+1)]

        remains = str_indices
        indices = []
        for i_ind in range(self.nb_indices):
            if self.index_types[i_ind] == 'digit':
                test_type = str.isdigit
            elif self.index_types[i_ind] == 'alpha':
                test_type = str.isalpha
            else:
                raise Exception('The type should be "digit" or "alpha".')

            index = ''.join(itertools.takewhile(test_type, remains))
            remains = remains[len(index):]
            if self.index_separators[i_ind] != '':
                remains = remains[1:]

            if self.index_types[i_ind] == 'digit':
                index = int(index)
            elif self.index_types[i_ind] == 'alpha':
                index = ord(index) - ord('a')

            indices.append(index)

        assert len(remains) == 0
        return indices

    def isfile(self, path):
        if not os.path.isabs(path):
            path = os.path.join(self.path_dir, path)
        return os.path.exists(path)


class SeriesOfArrays(object):
    def __init__(self, serie_arrays, give_indslices_from_indserie):
        self.serie_arrays = serie_arrays
        self.give_indslices_from_indserie = give_indslices_from_indserie

        iserie = 0
        cond = True
        while cond:
            iserie += 1
            serie_arrays.index_slices = (
                self.give_indslices_from_indserie(iserie))
            name_files = [name for name in serie_arrays.iter_name_files()]
            cond = all([serie_arrays.isfile(name) for name in name_files])

        self.nb_series = iserie

    def __iter__(self):
        for iserie in range(self.nb_series):
            self.serie_arrays.index_slices = \
                self.give_indslices_from_indserie(iserie)
            yield self.serie_arrays


if __name__ == '__main__':

    path = (
        os.environ['HOME'] +
        # '/useful/save'
        '/Dev/Matlab/Demo/UVMAT_DEMO04_PIV_challenge_2005_CaseC/'
        'Images'
        '/c001a.png'
    )

    serie_arrays = SerieOfArraysFromFiles(path)

    # def give_indslices_from_indserie(iserie):
    #     indslices = copy(serie_arrays.index_slices_all_files)
    #     indslices[0] = [iserie, iserie+1, 1]
    #     return indslices

    # series = SeriesOfArrays(serie_arrays, give_indslices_from_indserie)

    # for serie in series:
    #     print([name for name in serie])

    # print('\nOther test')

    # def give_indslices_from_indserie(iserie):
    #     indslices = copy(serie_arrays.index_slices_all_files)
    #     indslices[0] = [iserie, iserie+2, 1]
    #     indslices[1] = [1]
    #     return indslices

    # series = SeriesOfArrays(serie_arrays, give_indslices_from_indserie)

    # for serie in series:
    #     print([name for name in serie])
