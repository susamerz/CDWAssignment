import numpy as np
from scipy.spatial.distance import cdist


def build_searchlight_indices(radius=2):
    """Build searchlight indices in 3D.

    Parameters
    ----------
    radius:
        Radius of searchlight

    Returns
    -------
    indices:
       Grid point indices within the radius.
       Origin is in the middle of the searchlight.
    """
    diameter = 2 * radius + 1
    center_point = np.array([radius] * 3)
    grid_points = np.mgrid[0:diameter, 0:diameter, 0:diameter].reshape(3, -1).T
    # Add extra axis to center point to match cdist function
    distances = cdist(center_point[np.newaxis], grid_points)[0]
    # Select points within radius (including boundary)
    radius_plus_epsilon = radius * (1 + 1e-10)
    flt = distances < radius_plus_epsilon
    return grid_points[flt] - center_point


if __name__ == '__main__':
    points = build_searchlight_indices()
    print(points)
