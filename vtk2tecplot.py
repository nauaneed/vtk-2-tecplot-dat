import re
import numpy as np
import linecache
from tecio.tecio_szl import create_ordered_zone, open_file, zone_write_double_values, close_file, FD_DOUBLE


def readvtk_mesh(inputFilename):
    nvar = 0  # number of variables
    x = np.array([])
    y = np.array([])
    z = np.array([])

    readx = 0
    ready = 0
    readz = 0
    readv = 0

    linenum = 0

    ## reading part
    with open(inputFilename, 'r') as infile:
        # to find number of points and their coordinates
        print('  Read start ')
        for line in infile:
            linenum = linenum + 1
            if readv == 1 and len(ivarval) <= totalpoints:
                try:
                    ivarval = np.append(ivarval, [float(i) for i in line.split()])
                except ValueError:
                    readv = 0
                    pass

            # reading z point coordinates
            if readz == 1 and len(z) <= int(npts[2]):
                try:
                    z = np.append(z, np.array(line.split(), dtype=float))
                except ValueError:
                    readz = 0
                    print('  Done reading coordinates ')
                    pass

            # reading y point coordinates
            elif ready == 1 and len(y) <= int(npts[1]):
                try:
                    y = np.append(y, np.array(line.split(), dtype=float))
                except ValueError:
                    ready = 0
                    pass

            # reading x point coordinates
            elif readx == 1 and len(x) <= int(npts[0]):
                try:
                    x = np.append(x, np.array(line.split(), dtype=float))
                except ValueError:
                    readx = 0
                    pass

            elif (line.find('Z_COORDINATES') != -1):  # flag to write "Z_COORDINATES"
                readz = 1
                nvar = nvar + 1
                print('  Reading z-coordinates')

            elif (line.find('Y_COORDINATES') != -1):  # flag to write "Y_COORDINATES"
                ready = 1
                nvar = nvar + 1
                print('  Reading y-coordinates')

            elif (line.find('X_COORDINATES') != -1):  # flag to write "X_COORDINATES"
                readx = 1
                nvar = nvar + 1
                print('  Reading x-coordinates')

            elif (line.find('POINT_DATA') != -1):
                break

            elif (line.find(
                    'DIMENSIONS') != -1):  # # To fine npts(number of points in each direction) and number of variables
                npts = re.findall("\d+", line)
                totalpoints = np.prod([int(i) for i in npts])
                print('  Number of points = ' + ' '.join(npts))

    print('  Generating grid data')

    ## mesh generation part
    X, Y, Z = np.meshgrid(x, y, z)
    # print(X.shape)
    X = np.transpose(X[:, :, :], (2, 0, 1))
    Y = np.transpose(Y[:, :, :], (2, 0, 1))
    Z = np.transpose(Z[:, :, :], (2, 0, 1))
    # print(X.shape)
    X = np.reshape(X, (-1,))
    Y = np.reshape(Y, (-1,))
    Z = np.reshape(Z, (-1,))

    return npts, X, Y, Z, totalpoints, linenum, nvar


def readvtk_var(inputFilename, totalpoints, linenum, varnames, nvar):
    line = linecache.getline(inputFilename, linenum)
    foundvariable = False
    while not foundvariable:
        linenum = linenum + 1
        line = linecache.getline(inputFilename, linenum)
        if (line.find('double') != -1):  # using double as bait to catch variable names
            nvar = nvar + 1
            foundvariable = True
            if (nvar == len(npts) + 1):
                varnames.append(line.split()[1])  # 1st variable name
            elif (nvar > len(npts) + 1):
                varnames.append(line.split()[0])  # subsequent variable names
            print('  Reading Variable ' + varnames[-1])

    regex = re.compile('[qwrtyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM]')
    while regex.search(line) is not None:
        linenum = linenum + 1
        line = linecache.getline(inputFilename, linenum)
    num_points_in_line = len(line.split())
    num_lines_to_read = int(totalpoints / num_points_in_line)
    vardata_partial = np.loadtxt(inputFilename, skiprows=linenum - 1, max_rows=num_lines_to_read)
    if np.mod(totalpoints, num_points_in_line) != 0:
        linenum = linenum + num_lines_to_read
        line = linecache.getline(inputFilename, linenum)
        return linenum, np.append(vardata_partial, [float(i) for i in line.split()]), varnames, nvar
    else:
        return linenum, vardata_partial.flatten(), varnames, nvar


def readvtk_soln(inputFilename, totalpoints, linenum, nvar):
    print('  Reading solution')
    varnames = []
    end_of_file = False
    linenum, vardata, varnames, nvar = readvtk_var(inputFilename, totalpoints, linenum, varnames, nvar)
    vardata = [vardata]
    for i in range(10):
        line = linecache.getline(inputFilename, linenum + i)
        if line.find('double') != -1:
            end_of_file = False
            break
        else:
            end_of_file = True

    while not end_of_file:
        linenum, ivardata, varnames, nvar = readvtk_var(inputFilename, totalpoints, linenum, varnames, nvar)
        vardata = np.append(vardata, [ivardata], axis=0)
        for i in range(10):
            line = linecache.getline(inputFilename, linenum + i)
            if line.find('double') != -1:
                end_of_file = False
                break
            else:
                end_of_file = True

    print('  Read Complete')
    return varnames, vardata


def readvtk(inputFilename):
    nvar = 0  # number of variables
    varnames = []  # names of variables
    x = np.array([])
    y = np.array([])
    z = np.array([])

    iline = 0
    readx = 0
    ready = 0
    readz = 0

    ## reading part
    with open(inputFilename, 'r') as infile:
        # to find number of points and their coordinates
        for line in infile:

            # reading z point coordinates
            if readz == 1 and len(z) <= int(npts[2]):
                try:
                    z = np.append(z, np.array(line.split(), dtype=float))
                except ValueError:
                    readz = 0
                    print('  Reading variable names')
                    pass

            # reading y point coordinates
            elif ready == 1 and len(y) <= int(npts[1]):
                try:
                    y = np.append(y, np.array(line.split(), dtype=float))
                except ValueError:
                    ready = 0
                    pass

            # reading x point coordinates
            elif readx == 1 and len(x) <= int(npts[0]):
                try:
                    x = np.append(x, np.array(line.split(), dtype=float))
                except ValueError:
                    readx = 0
                    pass

            elif (line.find('Z_COORDINATES') != -1):  # flag to write "Z_COORDINATES"
                nvar = nvar + 1
                readz = 1
                print('  Reading z-coordinates')

            elif (line.find('Y_COORDINATES') != -1):  # flag to write "Y_COORDINATES"
                nvar = nvar + 1
                ready = 1
                print('  Reading y-coordinates')

            elif (line.find('X_COORDINATES') != -1):  # flag to write "X_COORDINATES"
                nvar = nvar + 1
                readx = 1
                print('  Reading x-coordinates')

            elif (line.find('double') != -1):  # using double as bait to catch variable names
                nvar = nvar + 1
                if (nvar == len(npts) + 1):
                    varnames.append(line.split()[1])  # 1st variable name

                elif (nvar > len(npts) + 1):
                    varnames.append(line.split()[0])  # subsequent variable names

            elif (line.find(
                    'DIMENSIONS') != -1):  # # To fine npts(number of points in each direction) and number of variables
                npts = re.findall("\d+", line)
                print('  Number of points = ' + ' '.join(npts))
        print('  Variables = ' + ' '.join(varnames))

    print('  Generating grid data')

    ## mesh generation part
    X, Y, Z = np.meshgrid(x, y, z)
    # print(X.shape)
    X = np.transpose(X[:, :, :], (2, 0, 1))
    Y = np.transpose(Y[:, :, :], (2, 0, 1))
    Z = np.transpose(Z[:, :, :], (2, 0, 1))
    # print(X.shape)
    X = np.reshape(X, (-1,))
    Y = np.reshape(Y, (-1,))
    Z = np.reshape(Z, (-1,))
    # print(X.shape)

    return npts, varnames, X, Y, Z


def write_dat(inputFilename, outputFilename, npts, varnames, X, Y, Z):
    writeflag = 0
    print("  Begin write")
    np.set_printoptions(formatter={'float': lambda x: format(x, '6.10E')})
    with open(outputFilename, 'w') as outFile:
        outFile.write('TITLE="3D"\n')

        string = 'VARIABLES = "X" "Y" "Z"'
        for i in range(0, len(varnames)):
            string = string + ' "' + varnames[i] + '"'
        # print(i)
        outFile.write(string + '\n')
        # print('ZONE I='+npts[0]+', J='+npts[1]+', K='+npts[2]+', DATAPACKING=BLOCK')
        outFile.write('ZONE I=' + npts[0] + ', J=' + npts[1] + ', K=' + npts[2] + ', DATAPACKING=BLOCK\n')

        # print(X[int(npts[0])-3:int(npts[0])+3])
        # print(Y[int(npts[0]) - 3:int(npts[0]) + 3])
        # print(Z[int(npts[0])*int(npts[1]) - 3:int(npts[0])*int(npts[1]) + 3])
        print('  Writing grid data:')

        print('   x-coordinate')
        for i in range(0, len(X)):
            outFile.write(str(X[i]) + ' ')
            if ((i + 1) % 9 == 0):
                outFile.write('\n')
        outFile.write('\n')

        print('   y-coordinate')
        for i in range(0, len(Y)):
            outFile.write(str(Y[i]) + ' ')
            if ((i + 1) % 9 == 0):
                outFile.write('\n')
        outFile.write('\n')

        print('   z-coordinate')
        for i in range(0, len(Z)):
            outFile.write(str(Z[i]) + ' ')
            if ((i + 1) % 9 == 0):
                outFile.write('\n')
        outFile.write('\n')

        print('  Copying solution data')
        with open(inputFilename, 'r') as infile:
            regex = re.compile('[qwrtyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM]')
            for line in infile:
                if writeflag == 1:
                    if regex.search(line) is None:
                        outFile.write(line)
                elif line.find('SCALARS') != -1:
                    writeflag = 1
    print('  Done')


def write_szplt(outFilename, X, Y, Z, varnames, vardata, totalpoints):
    var_names = ['X', 'Y', 'Z']
    var_names.extend(varnames)
    print('  Passing values to write')
    file_handle = open_file(outFilename, "Incompact3d_data", var_names)
    zone = create_ordered_zone(file_handle, "Zone", (int(npts[0]), int(npts[1]), int(npts[2])), None,
                               [FD_DOUBLE for i in range(len(var_names))])
    zone_write_double_values(file_handle, zone, 1, X)
    zone_write_double_values(file_handle, zone, 2, Y)
    zone_write_double_values(file_handle, zone, 3, Z)
    for i in range(4, len(varnames) + 4):
        zone_write_double_values(file_handle, zone, i, vardata[i - 4, :])
    print('  Writing start')
    close_file(file_handle)
    print('  Done Writing')


if __name__ == "__main__":
    import sys
    import os

    cwd = '.'
    vtk_files_list = [f for f in os.listdir(cwd) if f.endswith('.vtk')]
    print(" List of Files")
    for file in vtk_files_list:
        print("  " + file)

    if os.name == 'nt':
        for file in vtk_files_list:
            print(" Converting " + file)
            npts, varnames, X, Y, Z = readvtk(file)
            write_dat(file, file[:-3] + 'dat', npts, varnames, X, Y, Z)
    else:
        for file in vtk_files_list:
            print(" Converting " + file)

            if len(sys.argv) > 1:
                if sys.argv[-1] == 'dat':
                    npts, varnames, X, Y, Z = readvtk(file)
                    write_dat(file, file[:-3] + 'dat', npts, varnames, X, Y, Z)
                elif sys.argv[-1] == 'szplt':
                    npts, X, Y, Z, totalpoints, linenum, nvar = readvtk_mesh(file)
                    varnames, vardata = readvtk_soln(file, totalpoints, linenum, nvar)
                    write_szplt(file[:-3] + 'szplt', X, Y, Z, varnames, vardata, totalpoints)
                else:
                    raise Exception("invalid outfile format")
            else:
                npts, X, Y, Z, totalpoints, linenum, nvar = readvtk_mesh(file)
                varnames, vardata = readvtk_soln(file, totalpoints, linenum, nvar)
                write_szplt(file[:-3] + 'szplt', X, Y, Z, varnames, vardata, totalpoints)

    print(" All Done!")
