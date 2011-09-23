############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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

# This is the user-defined hasher for VTK, that takes into account
# incoming and outgoing connections
from core.cache.hasher import Hasher

def vtk_hasher(pipeline, module, chm):
    outgoing_connections = pipeline.graph.edges_from(module.id)
    incoming_connections = pipeline.graph.edges_to(module.id)
    current_hash = Hasher.module_signature(module, chm)
    chashes = [Hasher.connection_signature(pipeline.connections[c_id])
               for (_, c_id) in outgoing_connections]
    chashes += [Hasher.connection_signature(pipeline.connections[c_id])
               for (_, c_id) in incoming_connections]
    compound_hash = Hasher.compound_signature(chashes)
    return Hasher.compound_signature([current_hash, compound_hash])
