import numpy as np
import random
import cProfile
import pstats
import matplotlib.pyplot as plt
import imageio


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


# def plot_grid(grid, t, frames):
#     plt.figure(figsize=(10, 8))
#     for i in range(grid.shape[0]):
#         for j in range(grid.shape[1]):
#             cell_id = grid[i, j]
#             plt.text(j, grid.shape[0] - 1 - i, str(cell_id), ha='center', va='center', fontsize=15, fontweight='bold', color='red')
#
#     plt.xticks(range(grid.shape[1]), fontsize=8)
#     plt.yticks(range(grid.shape[0]), fontsize=8)
#     plt.grid(False)
#     plt.title('Placement Grid')
#     plt.savefig(f'/Users/amna_elsaqa/PycharmProjects/simulated_annealing/images/img_{t}.png')
#     image = imageio.v2.imread(f'/Users/amna_elsaqa/PycharmProjects/simulated_annealing/images/img_{t}.png')
#     frames.append(image)


def calculate_wirelength(grid, nets, cell_positions):
    r, c = grid.shape
    total_wirelength = 0
    for net in nets:
        # Initialize the nets minimum (x,y) coordinates with infinity, and the maximum with negative infinity.
        x_min, y_min = r, c
        x_max, y_max = 0, 0

        for cell in net[1:]:  # Skip the first element as it's the number of components
            if cell_positions[cell][0] < x_min:
                x_min = cell_positions[cell][0]
            if cell_positions[cell][1] < y_min:
                y_min = cell_positions[cell][1]
            if cell_positions[cell][0] > x_max:
                x_max = cell_positions[cell][0]
            if cell_positions[cell][1] > y_max:
                y_max = cell_positions[cell][1]
        hpwl = (x_max - x_min) + (y_max - y_min)
        total_wirelength += hpwl

    return total_wirelength


def perform_random_move(grid, cell_positions):
    rows, cols = grid.shape
    cell_id = np.random.choice(range(len(cell_positions)))
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


def simulated_annealing(frames, time, grid, cell_positions, nets, cooling_rate, num_nets):
    current_wirelength = calculate_wirelength(grid, nets, cell_positions)
    current_temp = 500 * current_wirelength
    final_temp = (5e-6 * current_wirelength) / num_nets
    final_wirelength = 0
    while current_temp > final_temp:
        for _ in range(10 * len(cell_positions)):  # moves per temperature = 10 * number of cells.
            # Perform a random move
            new_grid, new_cell_positions = perform_random_move(grid.copy(), cell_positions.copy())
            # Calculate new wirelength
            new_wirelength = calculate_wirelength(grid, nets, new_cell_positions)

            delta = new_wirelength - current_wirelength

            if delta < 0 or np.random.rand() > (1-np.exp(-delta / current_temp)):
                # time += 1
                # Accept the change if change in wirelength is less than 0.
                grid, cell_positions = new_grid, new_cell_positions
                # plot_grid(new_grid, time, frames)
                current_wirelength = new_wirelength

            # Calculate rejection probability.
            # elif np.random.rand() > (1-np.exp(-delta / current_temp)):
            #     grid, cell_positions = new_grid, new_cell_positions
            #     current_wirelength = new_wirelength

        # Update the temperature
        current_temp *= cooling_rate
        final_wirelength = current_wirelength
    return grid, cell_positions, final_wirelength


def main():
    with cProfile.Profile() as profile:
        time = 0
        frames = []
        num_cells, num_nets, rows, cols, nets = parse_netlist('d1.txt')
        grid, cell_positions = initial_placement(num_cells, rows, cols)
        print('Random Placement (before annealing)')
        display_grid(grid)
        print(f'Initial Total Wire Length: {calculate_wirelength(grid, nets, cell_positions)}')
        # Save the initial placement as an image
        # plot_grid(grid, time, frames)
        final_grid, final_positions, final_wirelength = simulated_annealing(frames, time, grid, cell_positions, nets, 0.95, num_nets)
        print('After annealing:')
        display_grid(final_grid)
        print(f'Final Total Wire Length: {final_wirelength}')
        # imageio.mimsave('/Users/amna_elsaqa/PycharmProjects/simulated_annealing/gif/example.gif', frames, fps=5)
    results = pstats.Stats(profile)
    results.sort_stats(pstats.SortKey.TIME)
    results.print_stats()


if __name__ == "__main__":
    main()
