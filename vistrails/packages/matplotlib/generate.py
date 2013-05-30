from mako.template import Template
import sys
from specs import SpecList

def generate_from_specs(fname, out_fname, template_fname):
    specs = SpecList.read_from_xml(fname)
    
    template = Template(filename=template_fname, 
                        module_directory='/tmp/mako')

    f = open(out_fname, 'wb') # 'b' ensures that we always use LF line endings
    f.write(template.render(specs=specs))
    f.close()        

def run(which="all"):
    if which == "all" or which == "plots":
        generate_from_specs("mpl_plots.xml", "plots.py", 
                            "plots_template.py.mako")
    if which == "all" or which == "artists":
        generate_from_specs("mpl_artists.xml", "artists.py", 
                            "artists_template.py.mako")
    
if __name__ == '__main__':
    if len(sys.argv) <= 1:
        run()
    elif len(sys.argv) == 2:
        run(sys.argv[1])
    else:
        raise TypeError("usage: python parse.py [all|artists|plots]")
