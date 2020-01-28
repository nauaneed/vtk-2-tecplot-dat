def vtk2tecdat(inputFilename, outputFilename):
    import re
    import sys
    import numpy as np
    nvar = 0  # number of variables
    varnames = []  # names of variables

    iline = 0
    readx = 0
    ready = 0
    readz = 0
    writeflag = 0

    ## reading part
    with open(inputFilename, 'r') as infile:
        l = []
        # to find number of points and their coordinates
        for line in infile:
            if ("npts" in locals()):  # if number of points have already been found

                if (line.find('double') != -1):  # using double as bait to catch variable names
                    nvar = nvar + 1
                    if (nvar == len(npts) + 1):
                        varnames.append(line.split()[1])  # 1st variable name

                    elif (nvar > len(npts) + 1):
                        varnames.append(line.split()[0])  # subsequent variable names

                # reading z point coordinates
                if readz == 1:
                    for t in line.split():
                        try:
                            l.append(float(t))
                        except ValueError:
                            pass

                    if len(l) == int(npts[2]):
                        z = np.asarray(l)
                        del l
                        l = []
                        readz = 0
                        print('  Reading variable names')
                        # print(z)

                # reading y point coordinates
                elif ready == 1:
                    for t in line.split():
                        try:
                            l.append(float(t))
                        except ValueError:
                            pass

                    if len(l) == int(npts[1]):
                        y = np.asarray(l)
                        del l
                        l = []
                        ready = 0
                        # print(y)

                # reading x point coordinates
                elif readx == 1:
                    for t in line.split():
                        try:
                            l.append(float(t))
                        except ValueError:
                            pass

                    if len(l) == int(npts[0]):
                        x = np.asarray(l)
                        del l
                        l = []
                        readx = 0
                        # print(x)

                if (line.find('Z_COORDINATES') != -1):  # flag to write "Z_COORDINATES"
                    readz = 1
                    print('  Reading z-coordinates')

                elif (line.find('Y_COORDINATES') != -1):  # flag to write "Y_COORDINATES"
                    ready = 1
                    print('  Reading y-coordinates')

                elif (line.find('X_COORDINATES') != -1):  # flag to write "X_COORDINATES"
                    readx = 1
                    print('  Reading x-coordinates')

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

    ## writing part
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


import os

cwd = '.'
text_files = [f for f in os.listdir(cwd) if f.endswith('.vtk')]
print(" List of Files")
for file in text_files:
    print("  " + file)

if os.name == 'nt':
    for file in text_files:
        print(" Converting " + file)
        vtk2tecdat(file, file[:-3] + 'dat')
else:
    for file in text_files:
        print(" Converting " + file)
        vtk2tecdat(file, file[:-3] + 'dat')
        bashCommand = "tec360 -convert " + file[:-3] + "dat" + " -o " + file[:-3] + "szplt &"
        print(bashCommand)
        os.system(bashCommand)

print(" All Done!")
