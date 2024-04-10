from tabulate import tabulate

final_vec = [[3, 9, 15, 21, 27], [0.32, 0.86, 1.83, 1.99, 2.61], [0.39, 0.76, 1.73, 2.11, 2.57], [0.2, 0.87, 1.38, 1.83, 3.08]]
print(tabulate(final_vec, tablefmt='fancy_grid'))