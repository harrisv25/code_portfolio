raster = np.empty((1974, 1894, 97))

for k in range(len(rasters)):
    raster[:,:,k] = rasterio.open(rasters[k], 'r').read()[0]
