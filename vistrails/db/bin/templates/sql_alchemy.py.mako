###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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

from vistrails.core.bundles import py_import

sqlalchemy = py_import('sqlalchemy', 
                       {'pip': 'SQLAlchemy',
                        'linux-debian': 'python-sqlalchemy',
                        'linux-ubuntu': 'python-sqlalchemy',
                        'linux-fedora': 'python-sqlalchemy'})
import sqlalchemy.types

metadata = sqlalchemy.MetaData()
tables = {'vistrails_version': \
          sqlalchemy.Table('vistrails_version', metadata,
                           sqlalchemy.Column('version', sqlalchemy.String(16))),
          'thumbnail': \
          sqlalchemy.Table('thumbnail', metadata,
                           # autoincrement defaults to True
                           sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
                           sqlalchemy.Column('file_name', sqlalchemy.String(255)),
                           sqlalchemy.Column('image_bytes', sqlalchemy.LargeBinary(2 ** 24)),
                           sqlalchemy.Column('last_modified', sqlalchemy.DateTime())),
% for obj in objs:
          '${obj.getName()}': \
          sqlalchemy.Table('${obj.getName()}', metadata,
% for i, prop in enumerate(obj.getSQLProperties() + obj.getSQLChoices()):
% if prop.isChoice():
% if prop.isInverse():
                           sqlalchemy.Column('${prop.getSpec().getColumn()}',
                                  sqlalchemy.types.${prop.getSpec().getType().upper()}),
% endif
% else:
                           sqlalchemy.Column('${prop.getColumn()}',
                                  sqlalchemy.types.${prop.getType().upper()},
% if prop.isAutoInc():
                                  autoincrement=True,
                                  primary_key=True,
% endif
                                  ),
% endif
% endfor
                           ),
% endfor
         }
