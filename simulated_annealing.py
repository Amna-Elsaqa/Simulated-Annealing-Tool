import numpy as np
import random
import math


# Function to parse the input file netlist file and return all needed info:
# (number of components, number of nets, the placement grid, and the nets connections details.)
def parse_netlist(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    # Read first line in the file which contains (num of cells, num of nets, gird size) and convert values to int.
    header = list(map(int, lines[0].split()))
    num_cells, num_nets, rows, cols = header
    nets = []
    # For the rest of the lines, read the netlist connections details.
    for line in lines[1:]:
        nets.append(list(map(int, line.split(' '))))
    return num_cells, num_nets, rows, cols, nets


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


def display_grid(grid):
    for row in grid:
        print(' '.join('--' if cell == -1 else f'{cell:02d}' for cell in row))


def calculate_wirelength(nets, cell_positions):
    total_wirelength = 0
    for net in nets:
        # Initialize the nets minimum (x,y) coordinates with infinity, and the maximum with negative infinity.
        x_min, y_min = float('inf'), float('inf')
        x_max, y_max = float('-inf'), float('-inf')

        for cell in net[1:]:  # Skip the first element as it's the number of components
            x, y = cell_positions[cell]
            x_min, y_min = min(x_min, x), min(y_min, y)
            x_max, y_max = max(x_max, x), max(y_max, y)

        hpwl = abs(x_max - x_min) + abs(y_max - y_min)
        total_wirelength += hpwl

    return total_wirelength


def perform_random_move(grid, cell_positions):
    rows, cols = grid.shape
    cell_id = random.choice(range(len(cell_positions)))
    x_old, y_old = cell_positions[cell_id]

    # Find a new random position (can be an empty cell)
    while True:
        # Pick a new random move between 0 and rows-1 & 0 and cols-1
        x_new, y_new = np.random.randint(rows), np.random.randint(cols)
        if grid[x_new, y_new] == -1 or (x_new, y_new) != (x_old, y_old):
            break
    grid[x_old, y_old], grid[x_new, y_new] = grid[x_new, y_new], grid[x_old, y_old]
    if grid[x_old, y_old] != -1:
        cell_positions[grid[x_old, y_old]] = [x_old, y_old]
    cell_positions[cell_id] = [x_new, y_new]

    return grid, cell_positions


def simulated_annealing(grid, cell_positions, nets, cooling_rate, num_nets):
    current_wirelength = calculate_wirelength(nets, cell_positions)
    current_temp = 500 * current_wirelength
    final_temp = (5e-6 * current_wirelength) / num_nets
    final_wirelength = 0
    while current_temp > final_temp:
        for _ in range(10 * len(cell_positions)):  # moves per temperature = 10 * number of cells.
            # Perform a random move
            new_grid, new_cell_positions = perform_random_move(grid.copy(), cell_positions.copy())

            # Calculate new wirelength
            new_wirelength = calculate_wirelength(nets, new_cell_positions)

            delta = new_wirelength - current_wirelength

            if delta < 0:
                # Accept the change if change in wirelength is less than 0.
                grid, cell_positions = new_grid, new_cell_positions
                current_wirelength = new_wirelength
            # Calculate rejection probability.
            elif np.random.rand() > (1-np.exp(-delta / current_temp)):
                grid, cell_positions = new_grid, new_cell_positions
                current_wirelength = new_wirelength

        # Update the temperature
        current_temp *= cooling_rate
        final_wirelength = current_wirelength
    return grid, cell_positions, final_wirelength


def main():
    # Example usage
    num_cells, num_nets, rows, cols, nets = parse_netlist('d2.txt')
    grid, cell_positions = initial_placement(num_cells, rows, cols)
    print('Random Placement (before annealing)')
    display_grid(grid)
    print(f'Initial Total Wire Length: {calculate_wirelength(nets,cell_positions)}')
    final_grid, final_positions, final_wirelength = simulated_annealing(grid, cell_positions, nets, 0.95, num_nets)
    print('After annealing:')
    display_grid(final_grid)
    print(f'Final Total Wire Length: {final_wirelength}')


if __name__ == "__main__":
    main()
