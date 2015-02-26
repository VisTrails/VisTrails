###############################################################################
##
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
##  - Neither the name of the University of Utah nor the names of its 
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

# Author: Prabhu Ramachandran
# Copyright (c) 2004, Enthought, Inc.
# License: BSD Style.

"""This module generates the class hierarchy for any given Python
modules.  This can be used (among other things) to generate the
traitified VTK classes in the correct order.

"""

from __future__ import division

import __builtin__


class TreeNode(object):
    """Represents a node in the class tree.

    Stores information on the sub and super classes of a particular
    class.  It also stores the inheritance level of the class inside
    the inheritance tree (essentially how many levels of inheritance
    are there below this class).  This inheritance level is computed
    when the `get_level` method is called.  The `get_level` method
    works only when the parent information is complete.
    
    """

    def __init__(self, klass):
        """Given a class, create a node in the tree.

        Parameters
        ----------
        - klass : `class`

          The class which is represented as a node in the tree.

        """
        self.klass = klass
        self.name = klass.__name__
        self.children = []
        self.parents = []
        # Uninitialized level is set to None
        self.level = None

    def add_parent(self, parent):
        """Add a parent node."""
        assert isinstance(parent, TreeNode)
        if parent not in self.parents:
            self.parents.append(parent)

    def add_child(self, child):
        """Add a child node. """
        assert isinstance(child, TreeNode)
        if child not in self.children:
            self.children.append(child)

    def get_level(self):
        """Returns the inheritance level of the node (an int).  If the
        level has not been set, the method computes it.  Note however,
        that this computation will fail if the parent information is
        incorrect.

        """
        if not self.level:
            if self.parents:
                self.level = max([x.get_level() for x in self.parents]) + 1
            else:
                self.level = 0
        return self.level

    def get_ancestors(self):
        """Returns a list of ancestor nodes from which this class has
        descended.

        """
        def _get_ancestors(node, ancestors):
            ancestors.extend(node.parents)
            for p in node.parents:
                _get_ancestors(p, ancestors)
        ancestors = []
        _get_ancestors(self, ancestors)
        return ancestors


class ClassTree(object):
    """Contains and generates all the class tree information.

    On initialization of the instance, nothing is done.  The classes
    are obtained using the list of modules (or a single module) that
    is used to initialize the instance.  One must then call the
    `create` method to generate the tree structure.  The instance of
    the class also can be treated as an iterator which iterates over
    the nodes of the tree.

    There are two ways in which the tree hierarchy is stored.  A
    dictionary mapping class names to the tree node and a tree
    represented as a list of lists containing the nodes.  The tree is
    organized based on a concept of an inheritance level.  A class
    that has no parent classes (no base classes) is said to be at
    level zero.  If a class inherits successively from 7 classes, it
    is at level 6.  An example of inheritance for a vtkFoo class is
    given below:

      vtkFoo -> vtkBar -> vtkObject -> vtkObjectBase

    Here, vtkObjectBase has an inheritance level of 0 and vtkFoo a
    level of 3.  One can traverse the tree by using the level as an
    index and find all the classes at a particular level.

    Here is some example usage of this class::

        >>> import vtk
        >>> t = ClassTree(vtk)
        >>> t.create()
        >>> print t.get_node('vtkObject').name
        vtkObject
        >>> print t.get_node('vtkObject').parents[0].name
        vtkObjectBase
        >>> print len(t.tree[0])
        1
        >>> t.tree[0][0].name
        vtkObjectBase
    
    """

    def __init__(self, modules):
        """Initialize the instance with the given modules.

        Parameters
        ----------

        - modules : `sequence` of modules or a module

          This is either a single module or a sequence of modules.
          The instance uses these list of modules to generate the
          class tree.
          
        """
        self.nodes = {}
        self.tree = [[]]
        if not hasattr(modules, '__iter__'):
            self.modules = [modules]
        else:
            self.modules = modules

    def __iter__(self):
        return iter(self.nodes.values())

    def _generate_hierarchy(self, klass):
        """Does the hard work of generating the class hierarchy."""
        node = self.get_node(klass.__name__, create=1)
        for base in klass.__bases__:
            base_node = self.get_node_from_class(base, create=1)
            node.add_parent(base_node)
            base_node.add_child(node)
            self._generate_hierarchy(base)

    def get_class(self, name):
        """Given a class name in the given modules returns the class."""
        klass = None
        for m in self.modules:
            if hasattr(m, name):
                return getattr(m, name)
        if hasattr(__builtin__, name):
            klass = getattr(__builtin__, name)
        if not klass:
            try:
                klass = self.nodes[name].klass
            except KeyError:
                raise KeyError, "Cannot find class of name %s"%name
        return klass

    def add_node(self, klass):
        """Create a node for the given class."""
        name = klass.__name__
        if not self.nodes.has_key(name):
            node = TreeNode(klass)
            self.nodes[name] = node
            return node

    def get_node(self, name, create=0):
        """Get a node of the given name.

        Parameters
        ----------

        - name : `str`

          Name of the node to get.

        - create : `boolean`

          If True, a new node will be added if no node of the given
          name is available.  Defaults to False.

        Returns
        -------

        - `TreeNode`

        """
        if self.nodes.has_key(name):
            return self.nodes[name]
        elif create:
            return self.add_node(self.get_class(name))

    def get_node_from_class(self, cls, create=0):
        """Get a node of the given class.

        Parameters
        ----------

        - cls : `class`

          Class of the node to get.

        - create : `boolean`

          If True, a new node will be added if no node of the given
          name is available.  Defaults to False.

        Returns
        -------

        - `TreeNode`

        """
        name = cls.__name__
        if self.nodes.has_key(name):
            return self.nodes[name]
        elif create:
            return self.add_node(cls)

    def create(self, class_names=None):
        """This method generates the class tree given an optional list
        of class names.

        Parameters
        ----------

        - class_names - `list` of `str`

          An optional list of names of the classes to generate the
          tree for.  Defaults to None where the class list is computed
          from the modules.        

        """
        if class_names is None:
            class_names = []
            for m in self.modules:            
                class_names.extend(dir(m))
            
        # Generate the nodes.
        for name in class_names:
            klass = self.get_class(name)
            if klass and hasattr(klass, '__bases__'):
                self._generate_hierarchy(klass)

        # Compute the inheritance level and store the nodes in the tree.
        for node in self:
            d = node.get_level()
            while len(self.tree) <= d:
                self.tree.append([])
            self.tree[d].append(node)

        # Sort the nodes alphabetically.
        def _comp(x, y):
            return cmp(x.name, y.name)
        for nodes in self.tree:
            nodes.sort(_comp)