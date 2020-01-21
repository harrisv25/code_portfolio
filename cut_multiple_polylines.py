#a function created to iterate through multiple polylines and cut them by a defined disctance interval 
#this function was created in a project in which long polygons needed to be transformed into something analytically appropriate. 
  #871 polyline were cut into thousands in order to analyze line segments at the 100ft scale. 
#this function utilized the arcpy object method "segmentAlongLine" to pull segments of lines and write them to a new shapefile. 
#infeat is the original polyline shapefile
#outname is the name and directory the new shapefile will be saved to. 
#sr is the spatial reference needed for the new shapefile to be created. I utilized a .prj file within this project. 
#id_field is the field from the original shapefile that containes a unique value for each of the original lines. This will be 
  #written to the smaller lines. A summary function could then be utilized post analysis to generalize the results back to the 
    #original polylines. 
# distance is the interval lengh you wish to cut the lines by

def cut_all_lines(infeat, outname, sr, id_field, distance):
    segments=arcpy.CreateFeatureclass_management(env.workspace, outname+"_seg.shp", "POLYLINE", "", "", "", sr)
    arcpy.AddField_management(segments, id_field, "TEXT", 100, "", "", "", "NULLABLE", "REQUIRED")

    cursor = arcpy.da.SearchCursor(infeat, ['SHAPE@', id_field])
    for row in cursor:
        start=0
        finish=distance
        length=row[0].length
        seg_lst=[]
        while finish < length:
            seg=row[0].segmentAlongLine(start, finish)
            seg_lst.append(seg)
            start+=distance
            finish+=distance
        ins= arcpy.da.InsertCursor(segments,['SHAPE@', id_field])
        for y in seg_lst:
            ins.insertRow([y, Pid])
        del ins
    del cursor
