# This is a rough code generation tool that works to generate code used to wrap itk functions for Vistrails
# In order to use this one must:
#   -set generation variables
#   -run script
#   -paste output into desired *Filters.py file
#   -add new filter name to __init__.py file
#
#NOTE: some filters require special calls, params, etc. that are not generated with this code
#      for example, many filters only accept decimal PixelTypes meaning that the
#      filter initialization should be wrapped in a try/except raising a ModuleError
#
# For example filter implementation, check out:
#       http://math.nist.gov/mcsd/savg/software/filters/
#       http://voxel.jouy.inra.fr/darcs/contrib-itk/WrapITK/Python/Tests/

##########################################################
#String Manipulation Methods
##########################################################
def AddSpaces(word):
    output = ""
    for char in word:
        if char.isupper() and word.index(char)!=0:
            output += " %s"%char
        else:
            output += char
    return output

def SplitCap(word):
    temp = word.split("_")
    output = ""
    for elem in temp:
        output += "%s "%elem.capitalize()
    return output.strip()

##########################################################
#SETUP generation variables
##########################################################
#filter_name should be equal to itk.filter_name
filter_name = "BinaryErodeImageFilter"

#designate namespace
namespace = "Filter|Neighborhood"

#some filters require kernel inputs, usually they don't though
has_kernel = True

#usage: {variable name:[variable type, default value, itk filter set method]}
#NOTE: you must look up the itk filter set method (dir(itk.filter_name))
filter_values = {"level":["basic.Float",None, "SetSquaredDistance"],
                 "lower_threshold":["basic.Float",None, "SetUseImageSpacing"]}

##########################################################
#code generation
##########################################################
out_class = """class %s(Module):
    my_namespace = '%s'"""%(filter_name, namespace)

compute = """
    def compute(self):
        im = self.get_input("Input Image")

        #check for input PixelType
        if self.has_input("Input PixelType"):
            inPixelType = self.get_input("Input PixelType")
        else:
            inPixelType = im.getPixelType()

        #check for output PixelType
        if self.has_input("Output PixelType"):
            outPixelType = self.get_input("Output PixelType")
        else:
            outPixelType = inPixelType

        #check for dimension
        if self.has_input("Dimension"):
            dim = self.get_input("Dimension")
        else:
            dim = im.getDim()
            """
if has_kernel:
    compute += """
        kernel = self.get_input("Kernel")
        """

compute += """
        #set up filter
        inImgType = itk.Image[inPixelType._type, dim]
        outImgType = itk.Image[outPixelType._type, dim]
"""
for param in filter_values:
    #check if default value is set
    if type(filter_values[param][1]).__name__ != "NoneType":
        compute += """
        if self.has_input("%s"):
            %s = self.get_input("%s")
        else:
            %s = %d\n"""%(SplitCap(param), param, SplitCap(param), param, filter_values[param][1])
    else:
        compute += """
        %s = self.get_input("%s")\n"""%(param, SplitCap(param))

if has_kernel:
    compute += """
        self.filter_ = itk.%s[inImgType, outImgType, kernel].New(im.getImg())
        self.filter_.SetKernel(kernel)"""%filter_name

else:
    compute += """
        self.filter_ = itk.%s[inImgType, outImgType].New(im.getImg())"""%filter_name

#set filter values
for param in filter_values:
    compute += """
        self.filter_.%s(%s)"""%(filter_values[param][2], param)

compute += """
        self.filter_.Update()

        #setup output image
        outIm = Image()
        outIm.setImg(self.filter_.GetOutput())
        outIm.setPixelType(outPixelType)
        outIm.setDim(dim)

        #set results
        self.setResult("Output Image", outIm)
        self.setResult("Filter", self)
        self.setResult("Output PixelType", outPixelType)
"""
register = """
    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="%s", namespace=cls.my_namespace)

        reg.add_input_port(cls, "Input Image", (Image, 'Input Image'))
        reg.add_input_port(cls, "Input PixelType", (PixelType, 'Input PixelType'),True)
        reg.add_input_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'),True)
"""%AddSpaces(filter_name)
if has_kernel:
    register += """
        reg.add_input_port(cls, "Kernel", (Kernel, 'Kernel'))
        """

for param in filter_values:
    #check if default value is set
    if type(filter_values[param][1]).__name__ != "NoneType":
        register += """
        reg.add_input_port(cls, "%s", (%s, '%s'),True)"""%(SplitCap(param),\
                                                          filter_values[param][0],\
                                                          SplitCap(param))
    else:
        register += """
        reg.add_input_port(cls, "%s", (%s, '%s'))"""%(SplitCap(param),\
                                                     filter_values[param][0],\
                                                     SplitCap(param))

register += """

        reg.add_output_port(cls, "Output Image", (Image, 'Output Image'))
        reg.add_output_port(cls, "Filter", (Filter, 'Filter'), True)
        reg.add_output_port(cls, "Output PixelType", (PixelType, 'Output PixelType'),True)
"""

##########################################################
#Output
##########################################################
print out_class
print compute
print register
