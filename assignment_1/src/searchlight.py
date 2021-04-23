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
    center_v = np.array([radius] * 3)
    center_iv = center_v[np.newaxis]
    point_vj = np.mgrid[0:diameter, 0:diameter, 0:diameter].reshape(3, -1)
    point_jv = point_vj.T
    dist_ij = cdist(center_iv, point_jv)
    dist_j = dist_ij[0]
    # Select points within radius (including boundary)
    radius_plus_epsilon = radius * (1 + 1e-10)
    flt_j = dist_j < radius_plus_epsilon
    return point_jv[flt_j] - center_v


if __name__ == '__main__':
    points = build_searchlight_indices()
    print(points)
