#This function was created to calculate how a trail polyline oriented to the slope of its terrain. 
#Essentially, the average direction of each polyline (varied from 0-360 degrees) were compared to
  #the calculated aspect of the trail (ranging from 0-360 degrees)
#The differences between the angles were compared and standardized to a 0-90 degree scale. 
#0 represents parallel alignment and 90 represents perpindicular. 
#the final info is written into the polynine shapefile. 
  #note: a lot of fields are created in this function, then deleted in order to save space.

#ply represents the polyline shapefile needed
#dem represnts the elevation raster needed (used a DEM here)

def trailangle(ply, dem):
#intermediate fields are created and will be deleted whne the final calculation is made. 
    arcpy.AddField_management(ply, "trlOr", "Float", "", "", "", "", "NULLABLE", "REQUIRED")
    arcpy.AddField_management(ply, "trlDir", "Float", "", "", "", "", "NULLABLE", "REQUIRED")
    arcpy.AddField_management(ply, "LocID", "SHORT", "", "", "", "", "NULLABLE", "REQUIRED")
#this was necassary for my specific polylines. Unique ids were needed for every polyline
#the unique ids are used to calculate the average direction of each line
    exp="autoIncrement(!LocID!)"
    cb = """def autoIncrement(var):
        global rec 
        pStart = 1  
        pInterval = 1 
        if (rec == 0):  
            rec = pStart  
        else:  
            rec += pInterval  
        return rec """
    arcpy.CalculateField_management(ply, "LocID", exp, "PYTHON3", cb)
    arcpy.DirectionalMean_stats(ply, "trail_dir.shp", "DIRECTION", "LocID")
    
    arcpy.JoinField_management(ply, "LocID", "trail_dir.shp", "LocID")
    arcpy.CalculateField_management(ply, "trlDir", '!CompassA!', "PYTHON3")
    arcpy.Delete_management("trail_dir.shp")
#aspect was ran and then written into the polylines. 
    outasp=arcpy.sa.Aspect(dem)
    outasp.save("aspec.tif")
    arcpy.AddSurfaceInformation_3d(ply, "aspec.tif", "Z_MEAN", "LINEAR")
    arcpy.AddField_management(ply, "aspect", "Float", "", "", "", "", "NULLABLE", "REQUIRED")
    arcpy.CalculateField_management(ply, "aspect", '!Z_MEAN!', "PYTHON3")
    arcpy.Delete_management("aspec.tif")

#the difference between the trail orientation and aspect was calculated and standardized. 
    arcpy.CalculateField_management(ply, "trlOr", '!trlDir! - !aspect!', "PYTHON3")
    arcpy.AddField_management(ply, "trl_ang", "Float", "", "", "", "", "NULLABLE", "REQUIRED")
    expression = "direction(!trlOr!)"
    codeblock = """def direction(var):
        if var >= 0 and var < 90:
            return var
        elif var >= 90 and var < 180:
            return ((var-180)*-1)
        elif var >= 180 and var < 270:
            return (var-180)
        elif var >= 270 and var < 360:
            return ((var-360)*-1)
        elif var < 0 and var >= -90:
            return (var * -1)
        elif var < -90 and var >= -180:
            return (var+180)
        elif var <-180 and var >= -270:
            return ((var+180)*-1)
        elif var <-270 and var >= -360:
            return (var+360)
        elif var < -360:
            return -99999 """

#all miscilaneous fields were deleted to preserve organization and storage space
    arcpy.CalculateField_management(ply, "trl_ang", expression, "PYTHON3", codeblock)
    arcpy.DeleteField_management(ply, ["trlOr","LocID_1", "trlDir", 
                                              "aspect", "id_1", 
                                              "CompassA", "DirMean", "CirVar", 
                                              "AveX", "AveY", "Z_Mean", "AveLen", 
                                              "Teststat", "RefValue", "PValue",
                                              "UnifTest", "Id"])
