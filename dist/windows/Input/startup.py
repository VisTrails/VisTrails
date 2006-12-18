#!/usr/bin/env python
# Vistrails initialization file
################################################################################

################################################################################
# configuration

# multiHeads
# maximizeWindows
# showMovies
# verbosenessLevel
# pluginList

# configuration.showSplash = False
# configuration.pythonPrompt = True
# configuration.useCache = False

def testHook():
    def printTree(n, indent = 0):
        def iprint(str):
            print '%s%s' % (" " * indent, str)
        iprint('Class: %s' % n.descriptor.name)
        for c in n.children:
            printTree(c, indent+4)
            
    import modules
    import modules.module_registry
    t = modules.module_registry.registry.classTree
    printTree(t)

# addStartupHook(testHook)
addPackage('vtk')
addPackage('pythonCalc')
#make sure ImageMagick is installed on your system before uncommenting
#the line below
#addPackage('ImageMagick')
#addPackage('webServices', 
#           wsdlList=['http://www.xmethods.net/sd/2001/CurrencyExchangeService.wsdl'
#                    ]
#           )
addPackage('spreadsheet')
