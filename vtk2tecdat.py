import re
import numpy as np


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
                    z=np.append(z, np.array(line.split(), dtype=float))
                except ValueError:
                    readz=0
                    print('  Reading variable names')
                    pass

            # reading y point coordinates
            elif ready == 1 and len(y) <= int(npts[1]):
                try:
                    y=np.append(y, np.array(line.split(), dtype=float))
                except ValueError:
                    ready = 0
                    pass

            # reading x point coordinates
            elif readx == 1 and len(x) <= int(npts[0]):
                try:
                    x=np.append(x, np.array(line.split(), dtype=float))
                except ValueError:
                    readx = 0
                    pass

            elif (line.find('Z_COORDINATES') != -1):  # flag to write "Z_COORDINATES"
                readz = 1
                print('  Reading z-coordinates')

            elif (line.find('Y_COORDINATES') != -1):  # flag to write "Y_COORDINATES"
                ready = 1
                print('  Reading y-coordinates')

            elif (line.find('X_COORDINATES') != -1):  # flag to write "X_COORDINATES"
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

    return npts, varnames, X, Y, Z

## writing part
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
                    if (regex.search(line) == None):
                        outFile.write(line)
                elif (line.find('SCALARS') != -1):
                    writeflag = 1
    print('  Done')


if __name__ == "__main__":
    import sys
    import os

    # print(sys.argv[1:])
    # print(len(sys.argv[1:]))
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
            npts, varnames, X, Y, Z = readvtk(file)
            write_dat(file, file[:-3] + 'dat', npts, varnames, X, Y, Z)
            bashCommand = "tec360 -convert " + file[:-3] + "dat" + " -o " + file[:-3] + "szplt &"
            print(bashCommand)
            os.system(bashCommand)

    print(" All Done!")
