--#########################################################################
--
-- Copyright (C) 2006-2010 University of Utah. All rights reserved.
--
-- This file is part of VisTrails.
--
-- This file may be used under the terms of the GNU General Public
-- License version 2.0 as published by the Free Software Foundation
-- and appearing in the file LICENSE.GPL included in the packaging of
-- this file.  Please review the following to ensure GNU General Public
-- Licensing requirements will be met:
-- http://www.opensource.org/licenses/gpl-license.php
--
-- If you are unsure which license is appropriate for your use (for
-- instance, you are interested in developing a commercial derivative
-- of VisTrails), please contact us at vistrails@sci.utah.edu.
--
-- This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
-- WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
--
--##########################################################################

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