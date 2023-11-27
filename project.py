
import numpy as np
import random


#Function to parse the input file netlist file and return all needed info:
#(number of cells, number of nets, the placement grid, and the nets/connections details)
def parse_netlist(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    header = list(map(int,lines[0].split()))
    num_cells, num_nets, num_rows, num_cols = header
    nets = []
    for line in lines[1:]:
        nets.append(list( map(int,line.split()) ))
    return num_cells, num_nets, num_rows, num_cols, nets


#Function for random initial placement of cells.
def initial_random_placement(num_cells, rows, cols):
    grid = np.full((rows, cols), -1)  # -1 indicates an empty cell
    cell_positions = np.full((num_cells, 2), -1)  # New structure for cell_positions

    for cell_id in range(num_cells):
        while True:
            #x, y = np.random.randint(rows), np.random.randint(cols)
            x, y = np.random.randint(low = 0, high = (rows-1)), np.random.randint(low = 0, high = (cols-1))
            if grid[x, y] == -1:
                grid[x, y] = cell_id
                cell_positions[cell_id] = [x, y]
                break
    return grid, cell_positions

def calculate_wirelength_HPWL(nets, cell_positions):
  wirelength = 0;

  for net in nets:

    x_min, y_min = float('inf'), float('inf')
    x_max, y_max = float('-inf'), float('-inf')

    net_size = net[0]
    for i in net_size:
      x = cell_positions[i][1]
      y = cell_positions[i][2]

      x_min, y_min = min(x_min, x), min(y_min, y)
      x_max, y_max = max(x_max, x), max(y_max, y)

    hpwl_wirelength = abs(x_max - x_min) + abs(y_max - y_min)
    wire_length += hpwl_wirelength

  return wire_length

def swap_cells(num_cells, num_rows, num_cols, grid, cell_positions, cell_1, cell_2):
  new_grid = np.full((num_rows, num_cols), 0)
  new_cell_positions = np.full((num_cells, 2), 0)

  new_cell_positions = cell_positions
  new_grid = grid

  x_cell_1 = cell_positions[cell_1][1]
  y_cell_1 = cell_positions[cell_1][2]
  x_cell_2 = cell_positions[cell_2][1]
  y_cell_2 = cell_positions[cell_1][2]

  new_cell_positions[cell_2] = cell_positions[cell_1]
  new_cell_positions[cell_1] = cell_positions[cell_2]

  new_grid[x_cell_1, y_cell_1] = grid[x_cell_2, y_cell_2]
  new_grid[x_cell_2, y_cell_2] = grid[x_cell_1, y_cell_1]

  return new_grid, new_cell_positions

def schedule_temp(temp):
    return temp * 0.95

def simulated_annealing_placement(num_cells, num_nets, num_rows, num_cols, nets):
  grid, cell_positions = initial_random_placement(num_cells, num_rows, num_cols)
  init_cost = calculate_wirelength_HPWL(nets, cell_positions)

  init_temp = 500*init_cost

  final_temp = (5*(10**-6)*(init_cost))/(num_nets)

  temp = init_temp

  new_grid = np.full((num_rows, num_cols), 0)
  new_cell_positions = np.full((num_cells, 2), 0)

  final_grid = np.full((num_rows, num_cols), 0)
  final_cell_positions = np.full((num_cells, 2), 0)

  while(temp > final_temp):
    cell_1 = random.randint(0, (num_cells - 1))
    cell_2 = random.randint(0, (num_cells - 1))

    while(cell_positions[cell_1] == cell_positions[cell_2]):
      cell_1 = random.randint(0, (num_cells - 1))
      cell_2 = random.randint(0, (num_cells - 1))

    wirelength_before_swap = calculate_wirelength_HPWL(nets, cell_positions)
    new_grid, new_cell_positions = swap_cells(num_cells, num_rows, num_cols, grid, cell_positions, cell_1, cell_2)
    wirelength_after_swap = calculate_wirelength_HPWL(nets, new_cell_positions)

    change_wirelength = wirelength_after_swap - wirelength_before_swap

    if(change_wirelength < 0):
      final_grid, final_cell_positions = new_grid, new_cell_positions
      final_wirelength = wirelength_after_swap
    else:
      if random.random() > (1-np.exp(-change_wirelength / temp)):
                final_grid, final_cell_positions = new_grid, new_cell_positions
                final_wirelength = wirelength_after_swap

    temp = schedule_temp()

  return final_grid, final_cell_positions, final_wirelength


def display_grid(grid):
    for row in grid:
        print(' '.join('--' if cell == -1 else f'{cell:02d}' for cell in row))

file_name = "D0.txt"
num_cells, num_nets, num_rows, num_cols, nets = parse_netlist(file_name)

grid, cell_positions = initial_random_placement(num_cells, num_rows, num_cols)
print('Random Placement (before annealing)')
display_grid(grid)
print(f'Initial Total Wire Length: {calculate_wirelength_HPWL(nets,cell_positions)}')

final_grid, final_cell_positions, final_wirelength = simulated_annealing_placement(num_cells, num_nets, num_rows, num_cols, nets)
print('After annealing:')
display_grid(final_grid)
print(f'Final Total Wire Length: {final_wirelength}')
