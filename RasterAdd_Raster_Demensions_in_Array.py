#create empty array of the raster shape, followed by the number of rasters
raster = np.empty((1974, 1894, 97))

#wraite the raster to the array
for k in range(len(rasters)):
    raster[:,:,k] = rasterio.open(rasters[k], 'r').read()[0]
