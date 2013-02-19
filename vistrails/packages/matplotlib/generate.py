from mako.template import Template
import tempfile
from specs import SpecList

def generate_from_specs(fname, out_fname, template_fname):
    specs = SpecList.read_from_xml(fname)
    
    template = Template(filename=template_fname, 
                        module_directory='/tmp/mako')

    f = open(out_fname, 'w')
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
    run()
