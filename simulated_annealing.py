import numpy as np
import random


#Function to parse the input file netlist file and return all needed info:
#(number of components, number of nets, the placement grid, and the nets connections details.)
def parse_netlist(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    header = list(map(int,lines[0].split()))
    num_cells, num_nets, rows, cols = header
    nets = []
    for line in lines[1:]:
        nets.append(list(map(int,line.split(()))))
    return num_cells, num_nets, rows, cols, nets

#Function for random initial placement of cells.
def initial_placement(num_cells, rows, cols):
    grid = np.full((rows, cols), -1)  # -1 indicates an empty cell
    cell_positions = np.full((num_cells, 2), -1)  # New structure for cell_positions

    for cell_id in range(num_cells):
        while True:
            x, y = np.random.randint(rows), np.random.randint(cols)
            if grid[x, y] == -1:
                grid[x, y] = cell_id
                cell_positions[cell_id] = [x, y]
                break
    return grid, cell_positions
