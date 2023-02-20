import csv
import numpy as np

import ivcurves.utils as utils


def solution():
    r"""
    This is a test solution.
    """
    parameters = 1 + np.zeros((32, 6))
    header = 'Index,photocurrent,saturation_current,resistance_series,resistance_shunt,n,cells_in_series'.split(',')

    for name in utils.get_filenames_in_directory(utils.TEST_SETS_DIR):
        with open(f'{name}.csv', 'w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(header)
            for idx, row in enumerate(parameters):
                writer.writerow([1 + idx] + list(row))


if __name__ == '__main__':
    solution()
