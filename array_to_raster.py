#a function that will turn an array t a georeferenced raster to be used within a GIS
#in_array is the array to be converted 
#ref_raster is a raster containing a spatial reference that you wish the array to have
#out array is the name and directory the file will be written to 

def array_to_raster(in_array, ref_raster, out_raster):
    src=rasterio.open(ref_raster)
    llpnt = arcpy.Point(src.bounds[0], src.bounds[1])
    cellsize=src.transform[0]
    sr=arcpy.Describe(ref_raster).spatialReference
    resultRast = arcpy.NumPyArrayToRaster(in_array, llpnt, cellsize, cellsize)    
    arcpy.DefineProjection_management(resultRast, sr)
    resultRast.save(out_raster)
