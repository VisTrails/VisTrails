###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah.
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

from __future__ import division

import ast
import itertools
from nbconvert.preprocessors import ExecutePreprocessor
import nbformat
import os


__all__ = ['execute', 'read_metadata']


class VisTrailsPreprocessor(ExecutePreprocessor):
    """
    Executes all the cells in a notebook
    """
    def __init__(self, inputs, **kw):
        self.inputs = inputs
        super(VisTrailsPreprocessor, self).__init__(**kw)

    def preprocess_cell(self, cell, resources, cell_index):
        output = super(VisTrailsPreprocessor, self).preprocess_cell(
            cell, resources, cell_index)
        if cell_index == 0:
            obj = nbformat.NotebookNode()
            obj.cell_type = 'code'
            source = []
            for k, v in self.inputs.iteritems():
                source.append("%s = %r" % (k, v))
            obj.source = '\n'.join(source)
            self.run_cell(obj)
        return output


def execute(notebook_filename, inputs):
    with open(notebook_filename) as fp:
        notebook = nbformat.read(fp, as_version=4)
    preprocessor = VisTrailsPreprocessor(inputs,
                                         timeout=600, kernel_name='python2')
    preprocessor.preprocess(
        notebook,
        {'metadata': {'path': os.path.dirname(notebook_filename)}})
    with open(notebook_filename, 'wt') as fp:
        nbformat.write(notebook, fp)


def visit(metadata, node):
    if not isinstance(node, ast.Assign):
        raise ValueError("First cell contains something other than an "
                         "assignment")
    if len(node.targets) != 1:
        raise ValueError("First cell contains unsupported multiple assignment")
    target = node.targets[0]
    if not isinstance(target, ast.Name):
        raise ValueError("First cell contains unsupported assignment")
    metadata[target.id] = getvalue(node.value)


def getvalue(node):
    if isinstance(node, (ast.List, ast.Tuple)):
        return [getvalue(e) for e in node.elts]
    elif isinstance(node, ast.Dict):
        d = {}
        for k, v in itertools.izip(node.keys, node.values):
            if not isinstance(k, ast.Str):
                return ValueError
            d[k.s] = getvalue(v)
        return d
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.Num):
        return node.n
    else:
        raise ValueError("First cell contains invalid value %s" % node)


def read_metadata(notebook_filename):
    with open(notebook_filename) as fp:
        notebook = nbformat.read(fp, as_version=4)
    metadata = {}
    if len(notebook['cells']) == 0:
        raise ValueError("Notebook contains no cells")
    cell = notebook['cells'][0]
    if cell['cell_type'] != 'code':
        raise ValueError("First cell is not code")
    for node in ast.iter_child_nodes(ast.parse(cell['source'])):
        visit(metadata, node)
    return metadata
