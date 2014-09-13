"""
Plot an image map of bedrock surface elevation.
"""

from netCDF4 import Dataset
from matplotlib import pyplot as plt
from iceplot import plot as iplt
from iceplot import autoplot as aplt

# load data
nc = Dataset('pism_plot_sample.nc')

# plot
aplt.contour(nc, 'usurf', colors='black')
iplt.icemargin(nc)

# show
nc.close()
plt.show()
