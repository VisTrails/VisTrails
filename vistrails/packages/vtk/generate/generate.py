from mako.template import Template
import sys
from specs import SpecList, VTKModuleSpec


def generate_from_specs(fname, out_fname, template_fname):
    specs = SpecList.read_from_xml(fname, VTKModuleSpec)
    
    template = Template(filename=template_fname, 
                        module_directory='/tmp/mako',
                        default_filters=['decode.latin1'],
                        output_encoding='utf-8')

    f = open(out_fname, 'wb') # 'b' ensures that we always use LF line endings
    f.write('# -*- coding: utf-8 -*-\n\n')
    f.write(template.render(specs=specs))
    f.close()        

def run(which="all"):
    if which == "all" or which == "vtk":
        generate_from_specs("vtk.xml", "../vtk_classes.py",
                            "vtk_template.py.mako")
    
if __name__ == '__main__':
    if len(sys.argv) <= 1:
        run()
    elif len(sys.argv) == 2:
        run(sys.argv[1])
    else:
        raise TypeError("usage: python generate.py [all|vtk]")
