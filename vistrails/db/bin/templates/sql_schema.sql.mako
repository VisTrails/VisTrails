--#############################################################################
--
-- Copyright (C) 2006-2011, University of Utah. 
-- All rights reserved.
-- Contact: contact@vistrails.org
--
-- This file is part of VisTrails.
--
-- "Redistribution and use in source and binary forms, with or without 
-- modification, are permitted provided that the following conditions are met:
--
--  - Redistributions of source code must retain the above copyright notice, 
--    this list of conditions and the following disclaimer.
--  - Redistributions in binary form must reproduce the above copyright 
--    notice, this list of conditions and the following disclaimer in the 
--    documentation and/or other materials provided with the distribution.
--  - Neither the name of the University of Utah nor the names of its 
--    contributors may be used to endorse or promote products derived from 
--    this software without specific prior written permission.
--
-- THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
-- AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
-- THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
-- PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
-- CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
-- EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
-- PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
-- OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
-- WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
-- OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
-- ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
--
--#############################################################################

CREATE TABLE `vistrails_version`(`version` char(16)) engine=InnoDB;
INSERT INTO `vistrails_version`(`version`) VALUES ('${version}');

CREATE TABLE thumbnail(
    id int not null auto_increment primary key,
    file_name varchar(255),
    image_bytes mediumblob,
    last_modified datetime
) engine=InnoDB;

-- generated automatically by auto_dao.py

% for obj in objs:
CREATE TABLE ${obj.getName()}(
% for i, prop in enumerate(obj.getSQLProperties() + obj.getSQLChoices()):
    % if prop.isChoice():
    % if prop.isInverse():
    % if i != len(obj.getSQLProperties() + obj.getSQLChoices()) - 1:    
    ${prop.getSpec().getColumn()} ${prop.getSpec().getType()},
    % else:
    ${prop.getSpec().getColumn()} ${prop.getSpec().getType()}
    % endif
    % endif
    % else:
    % if i != len(obj.getSQLProperties() + obj.getSQLChoices()) - 1:
    % if prop.isAutoInc():
    ${prop.getColumn()} ${prop.getType()} not null auto_increment primary key,
    % else:
    ${prop.getColumn()} ${prop.getType()},
    % endif
    % else:
    % if prop.isAutoInc():
    ${prop.getColumn()} ${prop.getType()} not null auto_increment primary key
    % else:
    ${prop.getColumn()} ${prop.getType()}
    % endif
    % endif
    % endif
% endfor
) engine=InnoDB;

% endfor