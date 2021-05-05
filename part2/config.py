from pathlib import Path

## Paths

# The location of the Haxby2001 data
input_data_path = Path('../data')

# The location where the results should be stored
output_data_path = Path('./results')

# The location where the figures should be stored
figure_path = Path('./figures')


## Analysis parameters

# All subjects to include in the analysis
subjects = [1, 2, 3, 4, 5, 6]

# Radius of the searchlight to use
searchlight_radius = 2  # in voxels
