import numpy as np
import vtk
from tecio.tecio_szl import create_ordered_zone, open_file, zone_write_double_values, close_file, FD_DOUBLE
from vtk.util import numpy_support as nps


def write_szplt(outFilename, ndims, varnames, vardatas):
    print('  Passing values to write')
    file_handle = open_file(str(outFilename), "title", varnames) 
    zone = create_ordered_zone(file_handle, "Zone", (int(ndims[0]), int(ndims[1]), int(ndims[2])), None,
                            [FD_DOUBLE for i in range(len(var_names))])
    for i, vardata in enumerate(vardatas):
        zone_write_double_values(file_handle, zone, i+1, vardata)
    print('  Writing start')
    close_file(file_handle)
    
    print('  Done Writing')

def get_points(output):
    num_points = output.GetNumberOfPoints()
    points = np.empty((num_points,3))
    for i in range(num_points):
        # GetPoint returns a 3-value Tuple (x,y,z)
        points[i] = output.GetPoint(i)
    return points.transpose()

if __name__ == "__main__":
    import os
    import sys
    from pathlib import Path
    if True:
        print(len(sys.argv))
    in_dir =  Path(sys.argv[0]) if len(sys.argv)>1 else Path('.')
    out_dir = Path(sys.argv[1]) if len(sys.argv)>2 else Path('converted')

    os.makedirs(out_dir, exist_ok=True)
    vtk_files_list = [f for f in os.listdir(in_dir) if f.endswith('.vtk')]
    print(" List of Files")
    for file in vtk_files_list:
        print("  " + file)


    for file in vtk_files_list:
        print(" Converting " + file)
        reader = vtk.vtkRectilinearGridReader()
        reader.SetFileName(in_dir/file)
        reader.Update()
        vtk_dataset = reader.GetOutput()
        points = get_points(vtk_dataset)

        pd = vtk_dataset.GetPointData()

        var_vals = [points[0], points[1], points[2]]
        var_names = ['x', 'y', 'z']
        for i in range(pd.GetNumberOfArrays()):
            arr = pd.GetArray(i)
            var_names.append(arr.GetName())
            var_vals.append(nps.vtk_to_numpy(arr))

        write_szplt(out_dir/(Path(file).stem + ".szplt"), vtk_dataset.GetDimensions(), var_names, var_vals)
            
    
    print(" All Done!")