# Third-party code with minor additions found on:
# http://docs.oracle.com/javase/tutorial/uiswing/layout/spring.html

#
# Copyright (c) 1995, 2008, Oracle and/or its affiliates. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   - Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#   - Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#   - Neither the name of Oracle or the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

"""Utility methods for SpringLayouts.

Provides methods for creating form- or grid-style layouts with SpringLayout.
These utilities are used by several programs, such as SpringBox and
SpringCompactGrid.
"""

from java.lang import System
from javax.swing import Spring, SpringLayout

def printSizes(c):
    """Debugging method.

    Prints to stdout the component's minimum, preferred, and maximum sizes.
    """
    System.out.println("minimumSize = %s" % c.getMinimumSize())
    System.out.println("preferredSize = %s" % c.getPreferredSize())
    System.out.println("maximumSize = %s" % c.getMaximumSize())

def makeGrid(parent,
             rows, cols,
             initialX, initialY,
             xPad, yPad):
    """Aligns the first rows * cols components of parent in a grid.

    Each component is as big as the maximum preferred width and height of the
    components.
    The parent is made just big enough to fit them all.
    """
    # Added by Remi Rampin
    if rows == 0:
        rows = parent.getComponentCount()/cols
    # -

    layout = parent.getLayout()
    if not isinstance(layout, SpringLayout):
        System.err.println("The first argument to makeGrid must use SpringLayout.")
        return

    xPadSpring = Spring.constant(xPad)
    yPadSpring = Spring.constant(yPad)
    initialXSpring = Spring.constant(initialX)
    initialYSpring = Spring.constant(initialY)
    max = rows * cols;

    # Calculate Springs that are the max of the width/height so that all
    # cells have the same size.
    maxWidthSpring = layout.getConstraints(parent.getComponent(0)).getWidth()
    maxHeightSpring = layout.getConstraints(parent.getComponent(0)).getHeight()
    for i in xrange(1, max):
        cons = layout.getConstraints(parent.getComponent(i))

        maxWidthSpring = Spring.max(maxWidthSpring, cons.getWidth())
        maxHeightSpring = Spring.max(maxHeightSpring, cons.getHeight())

    # Apply the new width/height Spring. This forces all the
    # components to have the same size.
    for i in xrange(0, max):
        cons = layout.getConstraints(parent.getComponent(i))

        cons.setWidth(maxWidthSpring)
        cons.setHeight(maxHeightSpring)

    # Then adjust the x/y constraints of all the cells so that they
    # are aligned in a grid.
    lastCons = None
    lastRowCons = None
    for i in xrange(0, max):
        cons = layout.getConstraints(parent.getComponent(i))
        if i % cols == 0: # start of new row
            lastRowCons = lastCons
            cons.setX(initialXSpring)
        else: # x position depends on previous component
            cons.setX(Spring.sum(lastCons.getConstraint(SpringLayout.EAST),
                                 xPadSpring))

        if i / cols == 0: #first row
            cons.setY(initialYSpring)
        else: # y position depends on previous row
            cons.setY(Spring.sum(lastRowCons.getConstraint(SpringLayout.SOUTH),
                                 yPadSpring))
        lastCons = cons

    # Set the parent's size.
    pCons = layout.getConstraints(parent)
    pCons.setConstraint(SpringLayout.SOUTH,
                        Spring.sum(
                            Spring.constant(yPad),
                            lastCons.getConstraint(SpringLayout.SOUTH)))
    pCons.setConstraint(SpringLayout.EAST,
                        Spring.sum(
                            Spring.constant(xPad),
                            lastCons.getConstraint(SpringLayout.EAST)))

# Used by makeCompactGrid. 
def getConstraintsForCell(row, col,
                          parent,
                          cols):
    layout = parent.getLayout()
    c = parent.getComponent(row * cols + col)
    return layout.getConstraints(c)

def makeCompactGrid(parent,
                    rows, cols,
                    initialX, initialY,
                    xPad, yPad):
    """Aligns the first rows * cols components of parent in a grid.

    Each component in a column is as wide as the maximum preferred width of the
    components in that column; height is similarly determined for each row.
    The parent is made just big enough to fit them all.
    """
    # Added by Remi Rampin
    if rows == 0:
        rows = parent.getComponentCount()/cols
    # -

    layout = parent.getLayout()
    if not isinstance(layout, SpringLayout):
        System.err.println("The first argument to makeCompactGrid must use SpringLayout.")
        return

    # Align all cells in each column and make them the same width.
    x = Spring.constant(initialX)
    for c in xrange(0, cols):
        width = Spring.constant(0)
        for r in xrange(0, rows):
            width = Spring.max(width,
                               getConstraintsForCell(r, c, parent, cols).
                               getWidth())
        for r in xrange(0, rows):
            constraints = getConstraintsForCell(r, c, parent, cols)
            constraints.setX(x)
            constraints.setWidth(width)
        x = Spring.sum(x, Spring.sum(width, Spring.constant(xPad)))

    # Align all cells in each row and make them the same height.
    y = Spring.constant(initialY)
    for r in xrange(0, rows):
        height = Spring.constant(0)
        for c in xrange(0, cols):
            height = Spring.max(height,
                                getConstraintsForCell(r, c, parent, cols).
                                getHeight())
        for c in xrange(0, cols):
            constraints = getConstraintsForCell(r, c, parent, cols)
            constraints.setY(y)
            constraints.setHeight(height)
        y = Spring.sum(y, Spring.sum(height, Spring.constant(yPad)))

    # Set the parent's size.
    pCons = layout.getConstraints(parent)
    pCons.setConstraint(SpringLayout.SOUTH, y)
    pCons.setConstraint(SpringLayout.EAST, x)
