#this is a funtion used to calculate the topographic position index (TPI) for every cell in an elevation raster
#TPI is a measure of how an idividual cell compares to the surrounding neighbors. It is used to capture topographic
  #features such as cliffs, canyons, spires and the like. 
#this function uses a moving window to average the surrounding cells and compare it to the central cell. 
# the moving window is 11x9, so it captures the 99 surrounding neighbors
  #this may be too large or small depending on the resolution, but the size of the window can be changed

#this only requires the raster as an input


def calc_TIP(inraster):
    #reading the raster file and creating an array
    array=arcpy.RasterToNumPyArray(inraster)
    #creating a temporary zeros array to write the reclassed raster arrays to
    avArray = np.zeros_like(array)
    #removing any NODATA information that will alter the array's usability
    norma=np.where(array<0, 0, array)
    #this is the moving window
    #the demensions were 11x9
    #to create these deminsions, the normalized array is going to be read
    #the starting demensions are set in the first parameter
    #This allows for the window to be fit to the raster demesnions 
    #the mean is going to average all the values of the 99 cells in question
    for row in range(5, norma.shape[0] - 6):    
        for col in range(4, norma.shape[1] - 5):
            win = norma[row - 5:row + 6, col - 4:col + 5]
            avArray[row, col] = win.mean()
    tip_array=array-avArray
    return(tip_array)
    
