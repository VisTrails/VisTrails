import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError

class ProteinDataBank(Module):
    pass

class Protein(ProteinDataBank):

    def __init__(self):
        ProteinDataBank.__init__(self)
        self.atoms = {}
        self.sequence = {}
        self.hatoms = {}
        self.author = ''
        self.title = ''
        
    def compute(self):
        pass

    def getAtomOfType(self, type):
        if self.atoms.has_key(type):
            return self.atoms[type]
        else:
            return 0

    def getHetAtomOfType(self, type):
        if self.hatoms.has_key(type):
            return self.hatoms[type]
        else:
            return 0

    def getSequence(self, seqID):
        if self.sequence.has_key(seqID):
            return self.sequence[seqID].__str__()
        else:
            k = self.sequence.keys().__str__()
            str =    'Invalid Sequence ID ' + k

class PDBParser(ProteinDataBank):

    ############################################################################
    # line parsers

    def is_continuation(self, line):
        try:
            int(line[0])
            return True
        except:
            return False

    def parse_ATOM(self, line, protein):
        type = line[-1]
        if protein.atoms.has_key(type):
            protein.atoms[type] = protein.atoms[type] + 1
        else:
            protein.atoms[type] = 1

    def parse_SEQRES(self, line, protein):
        els = len(line)
        seqID = line[2]
        if not protein.sequence.has_key(seqID):
            protein.sequence[seqID] = []
        
        s = protein.sequence[seqID]
        
        i = 4
        while i < len(line):
            s.append(line[i])
            i = i + 1

        protein.sequence[seqID] = s

    def parse_HETATM(self, line, protein):
        type = line[-1]
        if protein.hatoms.has_key(type):
            protein.hatoms[type] = protein.hatoms[type] + 1
        else:
            protein.hatoms[type] = 1

    def parse_AUTHOR(self, line, protein):
        if self.is_continuation(line):
            protein.author += ' ' + ' '.join(line[1:])
        else:
            protein.author = ' '.join(line)

    def parse_TITLE(self, line, protein):
        if self.is_continuation(line):
            protein.title += ' ' + ' '.join(line[1:])
        else:
            protein.title = ' '.join(line)

    def parse_HEADER(self, line, protein):
        protein.pdb_name = line[-1]
        protein.date = line[-2]
        protein.short_title = ' '.join(line[:-2])

    ############################################################################

    def compute(self):
        f = self.getInputFromPort("File")

        p = Protein()

        for l in file(f.name):
            l = l.strip()
            toks = l.split()
            if hasattr(self, 'parse_' + toks[0]):
                getattr(self, 'parse_' + toks[0])(toks[1:], p)

        self.setResult("Protein", p)

class GetAtoms(ProteinDataBank):
    def compute(self):
        prot = self.getInputFromPort("Protein")
        aType = self.getInputFromPort("Atom Type")
        self.setResult("NumAtoms", prot.getAtomOfType(aType))

class GetHetAtoms(ProteinDataBank):
    def compute(self):
        prot = self.getInputFromPort("Protein")
        aType = self.getInputFromPort("Atom Type")
        self.setResult("NumAtoms", prot.getHetAtomOfType(aType))

class GetSequence(ProteinDataBank):
    def compute(self):
        prot = self.getInputFromPort("Protein")
        sID = self.getInputFromPort("SequenceID")
        self.setResult("Sequence", prot.getSequence(sID))

class GetTitle(ProteinDataBank):
    def compute(self):
        prot = self.getInputFromPort("Protein")
        self.setResult("Title", prot.title)

class GetAuthor(ProteinDataBank):
    def compute(self):
        prot = self.getInputFromPort("Protein")
        self.setResult("Title", prot.author)

class GetPDBName(ProteinDataBank):
    def compute(self):
        prot = self.getInputFromPort("Protein")
        self.setResult("name", prot.pdb_name)
