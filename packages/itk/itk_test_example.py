#example code to be pasted into a python terminal to test itk filters
#generally used to instaniate filters inorder lookup variable set methods

import itk
#image setup
dim = 2
pixeltype = itk.UC
kernel = itk.stle(dim, 5)
filename = "/home/mates/Desktop/brains.jpg"
reader = itk.ImageFileReader[itk.Image[pixeltype, dim]].New()
reader.SetFileName(filename)
reader.Update()

im = reader.GetOutput()
inImg = itk.Image[pixeltype, dim]
outImg = inImg

size_ = itk.Size[dim]()
size_.SetElement(0,150)
size_.SetElement(1,150)
region_ = itk.ImageRegion[dim]()
region_.SetSize(size_)

#filter
filt = itk.IsolatedConnectedImageFilter[inImg, outImg].New(im)
filt.SetReplaceValue(120)
filt.SetLower(155)
filt.SetUpperValueLimit(235)
filt.SetSeed1([120,120])
filt.SetSeed2([140,140])
filt.Update()

filt2 = itk.ConnectedThresholdImageFilter[itk.Image[pixeltype, dim], itk.Image[pixeltype, dim]].New(im)
filt2.SetSeed([100,100])
filt2.SetReplaceValue(100)
filt2.SetLower(150)
filt2.SetUpper(250)
filt2.Update()

#write to file
writer = itk.ImageFileWriter[itk.Image[pixeltype, dim]].New(filt.GetOutput(), FileName="/home/mates/Desktop/output.jpg")
writer.Update()
