############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at contact@vistrails.org.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError

from PDB import *

identifier = 'edu.utah.sci.eranders.proteindatabank'
version = '0.1.0'
name = 'Protein Data Bank'

def initialize(*args, **keywords):
    reg = core.modules.module_registry
    basic = core.modules.basic_modules

    reg.add_module(ProteinDataBank, abstract=True)
    reg.add_module(Protein, abstract=True)

    reg.add_module(PDBParser)
    reg.add_input_port(PDBParser, "File", (basic.File, 'File'))
    reg.add_output_port(PDBParser, "Protein", (Protein, 'Protein'))

    reg.add_module(GetAtoms)
    reg.add_input_port(GetAtoms, "Protein", (Protein, 'Protein'))
    reg.add_input_port(GetAtoms, "Atom Type", (basic.String, 'AtomType'))
    reg.add_output_port(GetAtoms, "NumAtoms", (basic.Integer, 'NumAtoms'))

    reg.add_module(GetHetAtoms)
    reg.add_input_port(GetHetAtoms, "Protein", (Protein, 'Protein'))
    reg.add_input_port(GetHetAtoms, "Atom Type", (basic.String, 'AtomType'))
    reg.add_output_port(GetHetAtoms, "NumAtoms", (basic.Integer, 'NumAtoms'))

    reg.add_module(GetSequence)
    reg.add_input_port(GetSequence, "Protein", (Protein, 'Protein'))
    reg.add_input_port(GetSequence, "SequenceID", (basic.String, 'SequenceID'))
    reg.add_output_port(GetSequence, "Sequence", (basic.String, 'Sequence'))

    reg.add_module(GetTitle)
    reg.add_input_port(GetTitle, "Protein", (Protein, 'Protein'))
    reg.add_output_port(GetTitle, "Title", (basic.String, 'Title'))

    reg.add_module(GetAuthor)
    reg.add_input_port(GetAuthor, "Protein", (Protein, 'Protein'))
    reg.add_output_port(GetAuthor, "Author", (basic.String, 'Author'))

    reg.add_module(GetPDBName)
    reg.add_input_port(GetPDBName, "Protein", (Protein, 'Protein'))
    reg.add_output_port(GetPDBName, "Name", (basic.String, 'Name'))
