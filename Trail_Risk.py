```import os
import rasterio
from rasterio.merge import merge

os.chdir(r"C:\Users\harrivan\Desktop\Data\Output")


import arcpy
from arcpy import env
env.workspace = r"C:\Users\harrivan\Desktop\Data\Output"
env.overwriteOutput = 1
env.qualifiedFieldNames = "UNQUALIFIED"
arcpy.CheckOutExtension("Spatial")

#these are two global variables that get used in many of the later functions
sr=r"C:\Users\harrivan\Desktop\Data\cent_co.prj"
rec = 0

#i needed to project both raster and vector data before all other processes
#output file names became standardardized here
def proj(input_r, output, sr, feat_or_rast):
    if feat_or_rast=="yes":
        arcpy.Project_management(input_r, output+"_prj.shp", sr)
    elif feat_or_rast=="no":
        arcpy.ProjectRaster_management(input_r, output+"_prj.tif",sr)     

        
        
    
#my study area covered a spatial extent that required two DEM images from Earth Explorer
        #these images needed to be joined
        #this is the only function that utilized the rasterio dateset
        #outfile is what you would like the output directory to be named
def mosiac_dem(dem1, dem2, out_file):
    src1=rasterio.open(dem1)
    src2=rasterio.open(dem2)
    sftm=[]
    sftm.append(src1)
    sftm.append(src2)
    mosaic, out_trans = merge(sftm)
    out_meta = src2.meta.copy()
    out_meta.update({"driver": "GTiff","height": mosaic.shape[1],"width": mosaic.shape[2],"transform": out_trans}) 
    with rasterio.open(out_file, "w", **out_meta) as dest:
        dest.write(mosaic)
    return(out_file)

#my features needed to be clipped to the study area to reduce processing time 
    #and limit the visual nonsense
    #different clipping approaches were needed for eith vector or raster datasets
    #additionally, because K_Fact was a joined raster image, the clipping needed
    #to write a raster that only contained the k_factor information insteas of the 
    #rest of the table
    #inbound is the boundary file which contains the extent of the analysis
    #feat_or_raster is a switch file that designates if a file should be treated
    #as a raster or a vector
    #future remodels will remove feat_rast by reading the .shp or .tif at the 
    #end of the files
def clp(infeat, inbound, outfeat, feat_or_rast):
    if infeat.endswith("kf_prj.tif"):
        kf=arcpy.sa.Con(infeat, arcpy.sa.Lookup(infeat,"KFACT"), 0, "KFACT>0")
        extent=arcpy.Describe(inbound).extent
        w = extent.XMin
        s = extent.YMin
        e = extent.XMax
        n = extent.YMax
        arcpy.Clip_management(kf, str(w)+" "+str(s)+" "+str(e)+" "+str(n), 
                                  outfeat+".tif", inbound, "", "ClippingGeometry", "MAINTAIN_EXTENT")
    else:
        if feat_or_rast=="yes":
            arcpy.Clip_analysis(infeat, inbound, outfeat+".shp")
        elif feat_or_rast=="no":
            extent=arcpy.Describe(inbound).extent
            w = extent.XMin
            s = extent.YMin
            e = extent.XMax
            n = extent.YMax
            arcpy.Clip_management(infeat, str(w)+" "+str(s)+" "+str(e)+" "+str(n), 
                                  outfeat+".tif", inbound, "", "ClippingGeometry", "MAINTAIN_EXTENT")

#administrative boundaries were used. Both county information and ranger districts
            #derived from larger datasets needed to be pruned for only the important 
            #study areas. Then thouse boundaries needed to be joined. 
            #the boundary output name will be called in different funtions. 
def boundary(counties, districts, output):
    proj(counties, "cnt", sr, "yes")
    arcpy.Select_analysis("cnt_prj.shp", "sel_counties.shp", 
                          '"COUNTY" = \'JEFFERSON\' Or "COUNTY" = \'BOULDER\' Or "COUNTY" = \'CLEAR CREEK\'')
    
    proj(districts, "rngr", sr, "yes")
    arcpy.Select_analysis("rngr_prj.shp", "sel_dist.shp", 
                          '"RANGERDIST" = \'South Platte Ranger District\'')
    
    arcpy.Union_analysis(["sel_dist.shp", "sel_counties.shp"], output)
    arcpy.Delete_management("sel_dist.shp")
    arcpy.Delete_management("sel_counties.shp")
    arcpy.Delete_management("rngr_prj.shp")
    arcpy.Delete_management("cnt_prj.shp")
    print("Study Area boundary created")


#boundary(r"C:\Users\harrivan\Desktop\Data\Admin\Colorado_County_Boundaries.shp", 
         #r"C:\Users\harrivan\Desktop\Data\Admin\RangerD.shp", "boundaries.shp")

#arcpy.env.extent= "boundaries.shp"
#arcpy.env.mask = "boundaries.shp"

#this deals with the two DEMS by reprojecting and mosiacking them. The tot_dem 
#file name will be used as a primary variable later
def prep_dem(dem1, dem2, out_put):
    proj(dem1, "dem40", sr, "no")
    proj(dem2, "dem41", sr, "no")
    mosiac_dem("dem40_prj.tif","dem41_prj.tif", out_put)
    arcpy.Delete_management("dem40_prj.tif")
    arcpy.Delete_management("dem41_prj.tif")
    arcpy.DefineProjection_management(out_put, sr)
    print("DEMs Mosiaced together")

 

#prep_dem(r"C:\Users\harrivan\Desktop\Data\Elevation\40_106_13_slp", 
         #r"C:\Users\harrivan\Desktop\Data\Elevation\41_106_13_slp", "tot_dem.tif")


#all variables will be be projected and clipped to the extent of the study area
        #standardized naming conventions allow for automated file creation and 
        #incoporation into new functions
        #i also start deleting files that are no longer required to preserve
        #memory capacity. All variables are ready for actual analysis
        #the order of the input variables is important as some of them need
        #to be treated differently. 
def prep_variables(boundary, dem, trl, prec, kf):
    proj(trl, "trl", sr, "yes")
    proj(prec, "prec", sr, "no")
    proj(kf, "kf", sr, "no")
    var_lst=["trl_prj.shp", "tot_dem.tif", "prec_prj.tif", "kf_prj.tif"]
    vector=["yes", "no", "no", "no"]
    outputnames=["in_trails", "in_dem", "in_prec", "in_fact"]
    for i in range(len(var_lst)):
        clp(var_lst[i], boundary, outputnames[i], vector[i])
    arcpy.Delete_management("trl_prj.shp")
    arcpy.Delete_management("tot_dem.tif")
    arcpy.Delete_management("prec_prj.tif")
    arcpy.Delete_management("Lookup_kf_prj1.tif")
    arcpy.Delete_management("kf_prj.tif")
    print("All variables prepared for analysis")
        
#prep_variables("boundaries.shp", "tot_dem.tif", 
               #r"C:\Users\harrivan\Desktop\Data\Trails\Trails\TrailsExport2_26_19.shp",
               #r"C:\Users\harrivan\Desktop\Data\Prism\PRISM_ppt_30yr_normal_800mM2_annual_bil.bil",
               #r"C:\Users\harrivan\Desktop\Data\statsgo\KFACt_1km.tif")

#the trail lines are too long to make any reasonable analysis possble. Therefore
             #the lines needed to be segmented into smaller sections. Per common 
             #literature, 100ft segments seem resonable to make observations
             #regarding trail quality. 
             #there is no specific function in arcpy to cut all lines in a 
             #shapefile by a defined interval. I needed to call a polyline
             #method to return segments and write them to a new shapefile.
             #a case field was used to later summarize and join the smaller lines 
             #back to the original trail file. 
             #sr is the spatial reference
             #distance is the interval length you wish to cut by
def cut_all_lines(infeat, outname, sr, id_field, distance):
    splt_pts=arcpy.CreateFeatureclass_management(env.workspace, outname+"_pnts.shp", "POINT", "", "", "", sr)
    arcpy.AddField_management(splt_pts, id_field, "TEXT", 100, "", "", "", "NULLABLE", "REQUIRED")

    segments=arcpy.CreateFeatureclass_management(env.workspace, outname+"_seg.shp", "POLYLINE", "", "", "", sr)
    arcpy.AddField_management(segments, id_field, "TEXT", 100, "", "", "", "NULLABLE", "REQUIRED")

    cursor = arcpy.da.SearchCursor(infeat, ['SHAPE@', id_field])
    for row in cursor:
        x=distance
        start=0
        finish=distance
        length=row[0].length
        pnt_lst=[]
        while x<length:
            pos=row[0].positionAlongLine(x)
            pnt_lst.append(pos)
            x+=distance
        ins = arcpy.da.InsertCursor(splt_pts,['SHAPE@', id_field])
        Pid=row[1]
        for i in pnt_lst:
            ins.insertRow([i, Pid])
        del ins
        seg_lst=[]
        while finish < length:
            seg=row[0].segmentAlongLine(start, finish)
            seg_lst.append(seg)
            start+=distance
            finish+=distance
        ins2= arcpy.da.InsertCursor(segments,['SHAPE@', id_field])
        for y in seg_lst:
            ins2.insertRow([y, Pid])
        del ins2
    del cursor
    print("Trails have been segmented")

#cut_all_lines("in_trails.shp", "test", sr, "PERMANENT_", 30.48)


#once the segments are created, the raster information averages can be written 
    #into each 100 ft segment
def write_to_feat(infeat, raster_list):
    rasters=raster_list
    for i in rasters:
        if i.endswith("dem.tif"):
            arcpy.AddSurfaceInformation_3d(infeat, i, "AVG_SLOPE", "LINEAR")
        else:
            arcpy.AddSurfaceInformation_3d(infeat, i, "Z_MEAN", "LINEAR")
            arcpy.AddField_management(infeat, str(i[:-4]), "Float", "", "", "", "", "NULLABLE", "REQUIRED")
            arcpy.CalculateField_management(infeat, str(i[:-4]), '!Z_MEAN!', "PYTHON3")
        arcpy.DeleteField_management(infeat,["Z_Mean"])
    print("All rasters have been written into the trails")

#write_to_feat("test_seg.shp", arcpy.ListRasters("in*"))


#the final variable needs to be calculated for each segment. Trail angle 
    #represents the trail's alignment to the slope of the surrounding hill. 
    #a lot of information gets created here, so it needs to be deleted
    #the output should only be a new column in the trail files
def trailangle(ply, dem):
    arcpy.AddField_management(ply, "trlOr", "Float", "", "", "", "", "NULLABLE", "REQUIRED")
    arcpy.AddField_management(ply, "trlDir", "Float", "", "", "", "", "NULLABLE", "REQUIRED")
    arcpy.AddField_management(ply, "LocID", "SHORT", "", "", "", "", "NULLABLE", "REQUIRED")
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
    
    outasp=arcpy.sa.Aspect(dem)
    outasp.save("aspec.tif")
    arcpy.AddSurfaceInformation_3d(ply, "aspec.tif", "Z_MEAN", "LINEAR")
    arcpy.AddField_management(ply, "aspect", "Float", "", "", "", "", "NULLABLE", "REQUIRED")
    arcpy.CalculateField_management(ply, "aspect", '!Z_MEAN!', "PYTHON3")
    arcpy.Delete_management("aspec.tif")

 
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


    arcpy.CalculateField_management(ply, "trl_ang", expression, "PYTHON3", codeblock)
    arcpy.DeleteField_management(ply, ["trlOr","LocID_1", "trlDir", 
                                              "aspect", "id_1", 
                                              "CompassA", "DirMean", "CirVar", 
                                              "AveX", "AveY", "Z_Mean", "AveLen", 
                                              "Teststat", "RefValue", "PValue",
                                              "UnifTest", "Id"])
    print("trailangle finished")
    
#trailangle("test_seg.shp", "in_dem.tif")  

  
#this is where risk is calculated. A simple boolean (1 or 0) analysis 
    #is utilized to define trails that experience conditions that eaither
    #do, or do not contribute to erosion. The number is then tallied for each
    #variable and the result is an aggrigation of total "contributing conditions".
    #in feaat is the populated trails
    #the thresh attributes represents the threshholds that determine good and
    #bad conditions. 
    #field name is the name you wish to name the resulting field
def boo_analysis(infeat, kf_thresh, slp_thresh, precip_thresh, trlAng_thresh, field_name):
    arcpy.AddField_management(infeat, "kf_boo", "Float", "", "", "", "", "NULLABLE", "REQUIRED")
    arcpy.AddField_management(infeat, "slp_boo", "Float", "", "", "", "", "NULLABLE", "REQUIRED")    
    arcpy.AddField_management(infeat, "prec_boo", "Float", "", "", "", "", "NULLABLE", "REQUIRED")    
    arcpy.AddField_management(infeat, "trlA_boo", "Float", "", "", "", "", "NULLABLE", "REQUIRED")
    exp_kf = "kf(!in_fact!)"
    cb_kf = """def kf(var):
        if var >= """+str(kf_thresh)+""":
            return 1
        if var < """+str(kf_thresh)+""":
            return 0"""      
    arcpy.CalculateField_management(infeat, "kf_boo", exp_kf, "PYTHON3", cb_kf)  
    exp_slp = "slp(!Avg_Slope!)"
    cb_slp = """def slp(var):
        if var >= """+str(slp_thresh)+""":
            return 1
        if var < """+str(slp_thresh)+""":
            return 0"""      
    arcpy.CalculateField_management(infeat, "slp_boo", exp_slp, "PYTHON3", cb_slp)    
    exp_prec = "prec(!in_prec!)"
    cb_prec = """def prec(var):
        if var >= """+str(precip_thresh)+""":
            return 1
        if var < """+str(precip_thresh)+""":
            return 0"""      
    arcpy.CalculateField_management(infeat, "prec_boo", exp_prec, "PYTHON3", cb_prec)
    exp_ta = "ta(!trl_ang!)"
    cb_ta = """def ta(var):
        if var <= """+str(trlAng_thresh)+""":
            return 1
        if var > """+str(trlAng_thresh)+""":
            return 0"""      
    arcpy.CalculateField_management(infeat, "trlA_boo", exp_ta, "PYTHON3", cb_ta)
    
    arcpy.AddField_management(infeat, field_name, "Float", "", "", "", "", "NULLABLE", "REQUIRED")
    arcpy.CalculateField_management(infeat, field_name, '!kf_boo! + !slp_boo! + !prec_boo! + !trlA_boo!', "PYTHON3")
    
    arcpy.DeleteField_management(infeat, ["kf_boo", "slp_boo", 
                                                 "prec_boo", "trlA_boo"])
    print("Boolean Analysis complete")

#boo_analysis("test_seg.shp", 0.25, 15, 702.844971, 46, "Risk")    

#this function takes the risk information from the small segments and generalizes
    #it back to the original trails. This information is goiong to be useful for
    #surgical management descisions, but gives an idea of trail infrastructure
    #risk
    #the join field is the case_field used in teh cutting process
def generalize_risk(original_trails, seg_trails, join_field):
    arcpy.Statistics_analysis(seg_trails, "gen_risk.dbf", 
                              [["in_fact", "MEAN"],["Avg_Slope", "MEAN"],
                               ["in_prec", "MEAN"],["trl_ang", "MEAN"],
                               ["Risk", "MEAN"]], join_field)
    arcpy.JoinField_management(original_trails, join_field, "gen_risk.dbf", join_field)
    arcpy.Delete_management("gen_risk.dbf")
    print("Original Trails Populated")
    
#generalize_risk(r"C:\Users\harrivan\Desktop\Data\Trails\Trails\TrailsExport2_26_19.shp", 
                #"test_seg.shp", "PERMANENT_") 


#this function calls all functions. A standard naming convention is used for the 
                #output files so they can easily be fed into the subsequent
                #functions. 
def main():
    import time
    t1=time.time()
    boundary(r"C:\Users\harrivan\Desktop\Data\Admin\Colorado_County_Boundaries.shp", 
         r"C:\Users\harrivan\Desktop\Data\Admin\RangerD.shp", "boundaries.shp")
    arcpy.env.extent= "boundaries.shp"
    arcpy.env.mask = "boundaries.shp"
    prep_dem(r"C:\Users\harrivan\Desktop\Data\Elevation\40_106_13_slp", 
         r"C:\Users\harrivan\Desktop\Data\Elevation\41_106_13_slp", "tot_dem.tif")
    prep_variables("boundaries.shp", "tot_dem.tif", 
               r"C:\Users\harrivan\Desktop\Data\Trails\Trails\TrailsExport2_26_19.shp",
               r"C:\Users\harrivan\Desktop\Data\Prism\PRISM_ppt_30yr_normal_800mM2_annual_bil.bil",
               r"C:\Users\harrivan\Desktop\Data\statsgo\KFACt_1km.tif")
    cut_all_lines("in_trails.shp", "test", sr, "PERMANENT_", 30.48)
    write_to_feat("test_seg.shp", arcpy.ListRasters("in*"))
    trailangle("test_seg.shp", "in_dem.tif") 
    boo_analysis("test_seg.shp", 0.25, 15, 702.844971, 46, "Risk")
    generalize_risk("in_trails.shp", "test_seg.shp", "PERMANENT_") 
    arcpy.Delete_management("in_dem.dbf")
    arcpy.Delete_management("in_fact.dbf")
    arcpy.Delete_management("gen_prec.dbf")
    t2=time.time()
    print('Trail Erosion Risk analysis complete in '+ str(round((t2-t1)/60, 2)) + ' minutes')


main()```
