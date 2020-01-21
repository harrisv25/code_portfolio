#A function that will iterate through a list of files and clip them to the same extent
  #this will not work correctly for files in a geodatabase
  #infeat needs to be a list of either shapefiles or raster images.
  #the function will deliniate files based on whether or not they end with ".shp". 
  #in boundary needs to be a file which represents the bounding box to clip to
  #outfeat is the name and directory the file will save to. 
  #NOTE: the raster files can be clipped to the exent of the bounding box or to the geometric shape of the inbound file. 
  #extent_type refers to whether or not the rasters should be clipped to the box or the shape.
    #use "MAINTAIN_EXTENT" to clip to shape
    #use "NO_MAINTAIN_EXTENT" to clip to the bounding box

import arcpy
def clp(infeat, inbound, outfeat, extent_type):
    if infeat.endswith(".shp"):
        arcpy.Clip_analysis(infeat, inbound, outfeat+".shp")
    else:
        extent=arcpy.Describe(inbound).extent
        w = extent.XMin
        s = extent.YMin
        e = extent.XMax
        n = extent.YMax
        arcpy.Clip_management(infeat, str(w)+" "+str(s)+" "+str(e)+" "+str(n), 
                              outfeat+".tif", inbound, "", "ClippingGeometry", "MAINTAIN_EXTENT")
