

import json as q1
import cv2
import glob
import numpy as np
import pandas as pd
from PIL import Image
import os


def DeletionOfFilesInAFolder( path   , extension  ):
    
    pathToIterateOver = path   + "*"  +  extension
    
    for individualFilePath in glob.glob(pathToIterateOver):
        os.remove(individualFilePath)
   
    



def fill_hollow_shapes(image ,val ):    
    image = np.uint8(image)
    ret, mask = cv2.threshold(image, 0, val, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled_image = np.zeros_like(image)
    cv2.fillPoly(filled_image, contours, val)
    
    return filled_image

def FuctionToParseTheFileAndGetUseFullInfo(FilePath , SavingPath  ):
    with open(FilePath, 'r') as file:
        for line in file:
            data = q1.loads(line)
            Id = data['id']
            Annotation = data['annotations']
            image_size = (512 , 512) 
            imageForGlomerulus = np.zeros(image_size)
            imageForBloodVessel = np.zeros(image_size)
            orignalImageToBeSaved = np.zeros(image_size)
            for i in range(len(Annotation)):
                type_ = Annotation[i]['type'] 
                co_ordinates = Annotation[i]['coordinates']
                #print(f"id: {Id}, Type : {type_}  ,\nCordinates :{co_ordinates }   ")
                np_Corordinate_array = np.array(co_ordinates)  
                #print( np_Corordinate_array.shape  )
                count=0
                for i in range(np_Corordinate_array.shape[0]):
                    for j in range(np_Corordinate_array.shape[1]):
                        for k in range(np_Corordinate_array.shape[2]):
                            if(count==0):
                                x_c = np_Corordinate_array[i, j, k]
                                count=count+1
                            elif (count==1):
                                y_c=np_Corordinate_array[i, j, k]  
                                if type_ == "glomerulus" :
                                    imageForGlomerulus[y_c , x_c] = 255
                                elif type_ == "blood_vessel":
                                    imageForBloodVessel[y_c , x_c] = 100
                                count=0
            
            
            orignalImageToBeSaved = TwoImageOverlappingAndCheckingResuts(fill_hollow_shapes(imageForGlomerulus , 255 ) , fill_hollow_shapes(imageForBloodVessel , 150)     )
            cv2.imwrite( SavingPath + str(Id) +".png", orignalImageToBeSaved)
                        


def TwoImageOverlappingAndCheckingResuts(PathToImage1 , PathToImage2 ):
   image1 = PathToImage1
   
   heightOfImage1, widthOfImage1 = image1.shape[:2]

   
   image2 = PathToImage2
   image2 = cv2.resize(image2, (widthOfImage1 , heightOfImage1), interpolation=cv2.INTER_AREA)
   
   blendedImage = cv2.addWeighted(image1, 1, image2, 1, 0)
   return blendedImage
    
def ClassifiactionOfWsi(pathOfSavedSegmentedImages, PathToCSVFile , ImageTypeForIteration ,FolderNameToStoreBUTWithoutNum , modeOfreading ):
    #this path is where you have the different folders to 
    #store individual wsi_images to belong to a whole slide image
    PATH = "C:/Users/Crown Tech/Downloads/polygons.jsonl/"
    df = pd.read_csv(PathToCSVFile)
    pathToIterateOver = pathOfSavedSegmentedImages + "*" + ImageTypeForIteration
    max=0
    for iter in df['j']:
        if(max<iter):
            max=iter
    for i in range(6,7):  #orignal Form = for i in range(1,5):
     index = row = 0
     for index, row in df.iterrows():
        ID = row['id']
        WSI_NO = row['source_wsi']
        if WSI_NO == i:
            for iter in glob.glob(pathToIterateOver):
                checkString = pathOfSavedSegmentedImages + ID + ImageTypeForIteration
                if (iter[-16:] == checkString[-16:]):
                    image1 = cv2.imread(pathOfSavedSegmentedImages + iter[-16:], modeOfreading)
                    cv2.imwrite(PATH +  FolderNameToStoreBUTWithoutNum + str(WSI_NO) + "/" + str(ID)   + ".png"  , image1)

            
    
def tiling(pathToCSV  , pathToWSIFolder ,imageType,FolderName ,noOfWSIIamge , Scale   )   :
    
    df = pd.read_csv(PathToCSVFile)
    
    maxIValue = 0 
    maxJValue = 0
    minIValue = 100000000 
    minJValue = 100000000
    
    dictionaryForI_J_CordinatesOfTiles= {}
    for index, row in df.iterrows():
        i_cor = row['i']
        j_cor = row['j']
        WSI_NO = row['source_wsi']
        idOfImage = row['id']
        if WSI_NO == noOfWSIIamge:
            if(maxIValue<i_cor):
                maxIValue=i_cor
            if(maxJValue<j_cor):
                maxJValue=j_cor
            
            if( minIValue>i_cor ):
                minIValue=i_cor
            
            if(minJValue>j_cor):
                minJValue=j_cor
            
            
            
            values = [  i_cor , j_cor  ]
            dictionaryForI_J_CordinatesOfTiles[idOfImage] = values
            
    
    x1 = maxIValue - minIValue
    y1 = maxJValue - minJValue 
    wsi_image = Image.new(Scale, ( x1  , y1 ))

    
    
    for individulaImagePath in glob.glob(pathToWSIFolder + imageType):
        key = individulaImagePath[-16 : -4 ]
        x = dictionaryForI_J_CordinatesOfTiles[key][0] 
        y = dictionaryForI_J_CordinatesOfTiles[key][1]  
        tile_image = Image.open(individulaImagePath)
        wsi_image.paste(tile_image, (x - minIValue  ,  y - minJValue ))
            
    #wsi_image.show()
    

    wsi_image.save(  "C:\\Users\\Crown Tech\\Downloads\\polygons.jsonl\\" +FolderName + "\\" + str(noOfWSIIamge) + '.png' ,"PNG" )    
        
        
        
                 
    
    




FilePath = 'C:/Users/Crown Tech/Downloads/polygons.jsonl/polygons.jsonl'
SavingPath = "C:/Users/Crown Tech/Downloads/polygons.jsonl/Pics/"
#FuctionToParseTheFileAndGetUseFullInfo(FilePath , SavingPath )            



PathToImage1 = "C:/Users/Crown Tech/Downloads/polygons.jsonl/Pics/0a4ddecc55f0.tif"
PathToImage2 = "C:/Users/Crown Tech/Downloads/polygons.jsonl/Pics/0a4ddecc55f0.png"
#TwoImageOverlappingAndCheckingResuts(PathToImage1 , PathToImage2 )


PathForSegmentedImagesImages = "C:/Users/Crown Tech/Downloads/polygons.jsonl/Pics/"
PathToCSVFile = "C:/Users/Crown Tech/Downloads/polygons.jsonl/tile_meta.csv"
#ClassifiactionOfWsi(PathForSegmentedImagesImages , PathToCSVFile ,".png", "WSI_" , 0 )




pathToWSIFolder = "C:/Users/Crown Tech/Downloads/polygons.jsonl/WSI_4/"
#tiling(PathToCSVFile , pathToWSIFolder ,"*.png", "NEW" ,4 , 'L' )




#------------------------ Real Images Working -----------------------------

pathOfRealImages = "C:/Users/Crown Tech/Downloads/polygons.jsonl/RealPics/"
#ClassifiactionOfWsi(pathOfRealImages , PathToCSVFile , ".tif" , "RWSI_" , 0  )



pathToRWSIFolder = "C:/Users/Crown Tech/Downloads/polygons.jsonl/RWSI_6/"
#tiling(PathToCSVFile , pathToRWSIFolder ,"*.png", "REALWSIImages" ,6 , 'L'  )





#------------------------ Real Images Working -----------------------------

#------------------------ Utility Function --------------------------------


path = "D:/temp/"
extension = ".png"
DeletionOfFilesInAFolder( path   , extension  )







#--------------------------------------------------------------------------










