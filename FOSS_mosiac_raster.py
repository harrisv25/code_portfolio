#a function to mosiac two raster images together. 
  #this function assumes no overlapping of the images
    

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
