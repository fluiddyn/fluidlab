"""Read older Octave-based experiment session (:mod:`fluidlab.exp.octavesession`)
=================================================================================

Provides:

read_OctMI_session(sessionName, verbose=True)

"""
from __future__ import print_function


from struct import pack, unpack
import numpy as np
from time import strftime, localtime


class OctaveReaderError(NameError):
    """ OctaveReader error """


def colored(string, color):
    if color == "red":
        colorcode = 31
    elif color == "green":
        colorcode = 32
    elif color == "yellow":
        colorcode = 33
    elif color == "blue":
        colorcode = 34
    elif color == "purple":
        colorcode = 35
    elif color == "cyan":
        colorcode = 36
    elif color == "black":
        colorcode = 30
    else:
        return string

    coloredstring = (pack('b', 27) + '[0;' + str(colorcode) + 'm' +
                     string + pack('b', 27) + "[0;0m")
    return coloredstring


def read_header(f, verbose):
    """ Reads Octave binary file header (one per file)

    Format is described in libinterp/corefcn/ls-oct-binary.cc
    recalled below.

    Header (one per file):
    =====================

    object               type            bytes
    ------               ----            -----
    magic number         string             10

    float format         integer             1

    """
    magic_number = str(f.read(10))
    if verbose:
        print('magic number =', magic_number)
    if magic_number != 'Octave-1-L':
        raise OctaveReaderError('UnknownFileFormat')
    float_format = ord(f.read(1))
    if verbose:
        print('float format =', float_format)
    return float_format


def read_scalar_var(f, verbose):
    """ Reads one variable of type 'scalar' from Octave binary file

    See: octave_scalar::load_binary from libinterp/octave-value/ov-scalar.cc
    from GNU Octave source files

    """

    tmp = ord(f.read(1))
    if tmp == 0:
        raise OctaveReaderError('ScalarFormatError')
    dtmp = unpack('d', f.read(8))[0]
    if verbose:
        print('      value:', dtmp)
    return dtmp


def read_matrix_var(f, verbose):
    """ Reads one variable of type 'matrix' from Octave binary file

    See: octave_matrix::load_binary from libinterp/octave-value/ov-re-mat.cc
    from GNU Octave source files

    """

    mdims = unpack('i', f.read(4))[0]
    if verbose:
        print("      mdims:", mdims)
    if mdims == 0:
        raise OctaveReaderError('MatrixFormatError')
    if mdims < 0:
        mdims = -mdims
        dv = unpack('i'*mdims, f.read(4*mdims))
        if verbose:
            print("         dv:", dv)
        tmp = ord(f.read(1))
        if tmp == 0:
            raise OctaveReaderError('MatrixFormatError')
        num_elems = reduce(lambda x, y: x*y, dv)
        if verbose:
            print('  num_elems:', num_elems)
        fortran_vec = unpack('d'*num_elems, f.read(8*num_elems))
        var = np.array(fortran_vec).reshape(dv, order='F')
        if verbose:
            print("     matrix:", var.shape)
        if mdims == 2 and dv[0] == 1:
            var = var.flatten()
    else:
        nr = mdims
        nc = unpack('i', f.read(4))[0]
        tmp = ord(f.read(1))
        if tmp == 0:
            raise OctaveReaderError('MatrixFormatError')
        dv = (nr, nc)
        num_elems = nr*nc
        if verbose:
            print('  num_elems:', num_elems)
        fortran_vec = unpack('d'*num_elems, f.read(8*num_elems))
        var = np.array(fortran_vec).reshape(dv, order='F')
        if verbose:
            print("     matrix:", var.shape)

    return var


def read_scalar_struct_var(f, verbose):
    """ Reads one scalar structure variable from Octave binary file and returns
    it as a dictionnary.

    See: octave_struct::load_binary from libinterp/octave-value/ov-struct.cc
    from GNU Octave source files

    """

    length = unpack('i', f.read(4))[0]
    if verbose:
        print("     length:", length)
    if length == 0:
        raise OctaveReaderError('ScalarStructFormatError')
    if length < 0:
        # ov-struct.cc says we has explicit dimensions in that case
        mdims = -length
        dv = unpack('i'*mdims, f.read(4*mdims))
        if verbose:
            print("         dv:", dv)
        length = unpack('i', f.read(4))[0]
    else:
        dv = (1, 1)

    var = dict()
    if length > 0:
        for j in range(length):
            (name, varvar) = read_var(f, verbose)
            var[name] = varvar
    return var

def read_string_var(f, verbose):
    """ Reads one sq_string variable from Octave binary file

    See: octave_char_matrix_str::load_binary from octinterp/octave-value/ov-str-mat.cc
    from GNU Octave source files

    """

    elements = unpack('i', f.read(4))[0]
    if verbose:
        print('   elements:', elements)
    if elements == 0:
        raise OctaveReaderError('StringFormatError')
    if elements < 0:
        mdims = -elements
        dv = unpack('i'*mdims, f.read(4*mdims))
        if verbose:
            print("         dv:", dv)
        num_elems = reduce(lambda x, y: x*y, dv)
        if verbose:
            print('  num_elems:', num_elems)
        fortran_vec = unpack('c'*num_elems, f.read(num_elems))
        var = np.array(fortran_vec).reshape(dv, order='F')
        if mdims == 2 and dv[0] == 1:
            var = var.flatten().tostring()
        if verbose:
            print('     string:', var)
    else:
        for i in range(elements):
            length = unpack('i', f.read(4))[0]
            if length == 0:
                raise OctaveReaderError('StringFormatError')
            fortran_vec = f.read(length)
            var[i] = str(fortran_vec)
    return var


def read_cell_var(f, verbose):
    """ Reads one Cell variable from Octave binary file and returns it as a list

    See: octave_cell::load_binary from octinterp/octave-value/ov-cell.cc
    from GNU Octave source files

    """

    mdims = unpack('i', f.read(4))[0]
    if mdims >= 0:
        raise OctaveReaderError('CellFormatError')
    if verbose:
        print('      mdims:', mdims)
    mdims = -mdims
    if mdims > 0:
        dv = unpack('i'*mdims, f.read(4*mdims))
        if verbose:
            print("         dv:", dv)
        num_elems = reduce(lambda x, y: x*y, dv)
    else:
        num_elems = 0
    var = list()
    for i in range(num_elems):
        (name, varvar) = read_var(f, verbose)
        if name != '<cell-element>':
            raise OctaveReaderError('CellFormatError')
        var.append(varvar)
    return var

def read_var(f, verbose):
    """ Reads one variable from Octave binary file

    Format is described in libinterp/corefcn/ls-oct-binary.cc
    recalled below.

    Data (one set for each item):
    ============================

    object               type            bytes
    ------               ----            -----
    name_length          integer             4

    name                 string    name_length

    doc_length           integer             4

    doc                  string     doc_length

    global flag          integer             1

    data type            char                1

    In general "data type" is 255, and in that case the next arguments
    in the data set are

    object               type            bytes
    ------               ----            -----
    type_length          integer             4

    type                 string    type_length

    The string "type" is then used with octave_value_typeinfo::lookup_type
    to create an octave_value of the correct type. The specific load/save
    function is then called.

    For backward compatiablity "data type" can also be a value between 1
    and 7, where this defines a hardcoded octave_value of the type

    data type                  octave_value
    ---------                  ------------
    1                          scalar
    2                          matrix
    3                          complex scalar
    4                          complex matrix
    5                          string   (old style storage)
    6                          range
    7                          string

    Except for "data type" equal 5 that requires special treatment, these
    old style "data type" value also cause the specific load/save functions
    to be called. FILENAME is used for error messages.
    """

    name_length = unpack('i', f.read(4))[0]
    name  = str(f.read(name_length))
    if verbose:
        print('* Variable "' + name + '":')
    doc_length = unpack('i', f.read(4))[0]
    doc = str(f.read(doc_length))
    if verbose:
        print('        doc:', doc)
    global_flag = ord(f.read(1))
    if verbose:
        print('     global:', (global_flag == 1))
    data_type = ord(f.read(1))
    if data_type == 1:
        data_type = 'scalar'
    elif data_type == 2:
        data_type = 'matrix'
    elif data_type == 3:
        data_type = 'complex scalar'
    elif data_type == 4:
        data_type = 'complex matrix'
    elif data_type == 5:
        data_type = 'string'
    elif data_type == 6:
        data_type = 'range'
    elif data_type == 7:
        data_type = 'string'
    elif data_type == 255:
        data_type_length = unpack('i', f.read(4))[0]
        data_type = str(f.read(data_type_length))
    else:
        raise OctaveReaderError('UnknownDataType')
    if verbose:
        print('  data_type:', data_type)
    if data_type == 'scalar':
        var = read_scalar_var(f, verbose)
    elif data_type == 'matrix':
        var = read_matrix_var(f, verbose)
    elif data_type == 'scalar struct':
        var = read_scalar_struct_var(f, verbose)
    elif data_type == 'string' or data_type == 'sq_string' or data_type == 'dq_string':
        # sq_string is single-quoted string
        # dq_string is double-quoted string
        # both are charMatrix
        var = read_string_var(f, verbose)
    elif data_type == 'cell':
        var = read_cell_var(f, verbose)
    else:
        raise OctaveReaderError('NotImplemented')

    return (name, var)

def read_octave_binary(path, verbose=False):
    """ Reads an Octave binary file. Returns a dictionnary containing all the variables. """

    data = dict()
    with open(path, 'r') as f:
        float_format = read_header(f, verbose)
        done = False
        while not done:
            try:
                (name, var) = read_var(f, verbose)
                data[name] = var
            except OctaveReaderError as oe:
                done = True
                raise
            except:
                done = True
                pass

    return data


def read_OctMI_session(sessionName, verbose=True):
    filename = sessionName + '_MIstate.octave'
    if verbose:
        print("Loading saved MI session from file `" + filename + "'")
    MI_session = read_octave_binary(filename, False)['MI_session']
    Variables = dict()
    Variables['startTime'] = MI_session['startTime']
    for varname in MI_session['Variables']:
        keyname = varname + '_array'
        Variables[varname] = MI_session[keyname]
    time_fmt = "%A %e %B %Y - %H:%M:%S"
    if MI_session.has_key('t_array'):
        Variables['t'] = MI_session['t_array']
        try:
            Nelem = len(Variables['t'])
        except:
            Nelem = 1
            pass
        if Nelem > 1:
            lt_start = localtime(Variables['t'][0])
            lt_end = localtime(Variables['t'][Nelem-1])
        elif Nelem == 1:
            lt_start = localtime(Variables['t'])
            lt_end = lt_start
        else:
            lt_start = localtime(Variables["startTime"])
            lt_end = lt_start
    if verbose:
        string = strftime(time_fmt, lt_start)
        print(colored("** Start date: " + string, "blue"))
        if Nelem > 0:
            string = strftime(time_fmt, lt_end)
            print(colored("**   End date: " + string, "blue"))
        else:
            print(colored("No logged variables", "red"))

    return Variables


if __name__ == '__main__':
    data_side = read_OctMI_session('W3E8_50Hz_side_1')
    data = read_OctMI_session('W3E8_3')
    dummy = read_OctMI_session('Dummy')
