import numpy as np
import random


'''Function to parse the input file netlist file and return all needed info:
(number of components, number of nets, the placement grid, and the nets connections details.)'''
def parse_netlist(filename):
    with open(filename, 'r') as file:
        lines = file.reaslines()
    header = list(map(int,lines[0].split()))
    num_cells, num_nets, rows, cols = header
    nets = []
    for line in lines[1:]:
        nets.append(list(map(int,line.split(()))))
    return num_cells, num_nets, rows, cols, nets
