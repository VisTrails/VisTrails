--#############################################################################
--
-- Copyright (C) 2011-2013, NYU-Poly.
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
INSERT INTO `vistrails_version`(`version`) VALUES ('2.0.0');

CREATE TABLE thumbnail(
    id int not null auto_increment primary key,
    file_name varchar(255),
    image_bytes mediumblob,
    last_modified datetime
) engine=InnoDB;

-- generated automatically by auto_dao.py

CREATE TABLE vistrail_variable(
    name varchar(255),
    uuid char(36),
    package varchar(255),
    module varchar(255),
    namespace varchar(255),
    value varchar(8191),
    parent_id char(36),
    entity_id char(36),
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE port_spec(
    id char(36),
    name varchar(255),
    type varchar(255),
    optional int,
    sort_key int,
    min_conns int,
    max_conns int,
    parent_type char(32),
    entity_id char(36),
    entity_type char(16),
    parent_id char(36)
) engine=InnoDB;

CREATE TABLE module(
    id char(36),
    cache int,
    name varchar(255),
    namespace varchar(255),
    package varchar(511),
    version varchar(255),
    parent_type char(32),
    entity_id char(36),
    entity_type char(16),
    parent_id char(36)
) engine=InnoDB;

CREATE TABLE module_descriptor(
    id char(36),
    name varchar(255),
    package varchar(255),
    namespace varchar(255),
    package_version varchar(255),
    version varchar(255),
    base_descriptor_id char(36),
    parent_id char(36),
    entity_id char(36),
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE tag(
    id char(36),
    name varchar(255),
    parent_id char(36),
    entity_id char(36),
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE port(
    id char(36),
    type varchar(255),
    moduleId char(36),
    moduleName varchar(255),
    name varchar(255),
    signature varchar(4095),
    parent_type char(32),
    entity_id char(36),
    entity_type char(16),
    parent_id char(36)
) engine=InnoDB;

CREATE TABLE group_tbl(
    id char(36),
    cache int,
    name varchar(255),
    namespace varchar(255),
    package varchar(511),
    version varchar(255),
    parent_type char(32),
    entity_id char(36),
    entity_type char(16),
    parent_id char(36)
) engine=InnoDB;

CREATE TABLE log_tbl(
    id char(36) not null auto_increment primary key,
    entity_type char(16),
    version char(16),
    name varchar(255),
    last_modified datetime,
    vistrail_id char(36)
) engine=InnoDB;

CREATE TABLE mashup_alias(
    id char(36),
    name varchar(255),
    parent_id char(36),
    entity_id char(36),
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE mashup(
    id char(36),
    name varchar(255),
    version int,
    type varchar(255),
    vtid char(36),
    layout mediumtext,
    geometry mediumtext,
    has_seq int,
    parent_id char(36),
    entity_id char(36),
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE port_spec_item(
    id char(36),
    pos int,
    module varchar(255),
    package varchar(255),
    namespace varchar(255),
    label varchar(4095),
    _default varchar(4095),
    _values mediumtext,
    entry_type varchar(255),
    parent_id char(36),
    entity_id char(36),
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE machine(
    id char(36),
    name varchar(255),
    os varchar(255),
    architecture varchar(255),
    processor varchar(255),
    ram bigint,
    vt_id char(36),
    log_id char(36),
    entity_id char(36),
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE add_tbl(
    id char(36),
    what varchar(255),
    object_id char(36),
    par_obj_id char(36),
    par_obj_type char(16),
    action_id char(36),
    entity_id char(36),
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE other(
    id char(36),
    okey varchar(255),
    value varchar(255),
    parent_type char(32),
    entity_id char(36),
    entity_type char(16),
    parent_id char(36)
) engine=InnoDB;

CREATE TABLE location(
    id char(36),
    x DECIMAL(18,12),
    y DECIMAL(18,12),
    parent_type char(32),
    entity_id char(36),
    entity_type char(16),
    parent_id char(36)
) engine=InnoDB;

CREATE TABLE parameter(
    id char(36),
    pos int,
    name varchar(255),
    type varchar(255),
    val mediumtext,
    alias varchar(255),
    parent_type char(32),
    entity_id char(36),
    entity_type char(16),
    parent_id char(36)
) engine=InnoDB;

CREATE TABLE plugin_data(
    id char(36),
    data varchar(8191),
    parent_type char(32),
    entity_id char(36),
    entity_type char(16),
    parent_id char(36)
) engine=InnoDB;

CREATE TABLE function(
    id char(36),
    pos int,
    name varchar(255),
    parent_type char(32),
    entity_id char(36),
    entity_type char(16),
    parent_id char(36)
) engine=InnoDB;

CREATE TABLE action_annotation(
    id char(36),
    akey varchar(255),
    value varchar(8191),
    action_id char(36),
    date datetime,
    user varchar(255),
    parent_id char(36),
    entity_id char(36),
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE abstraction(
    id char(36),
    cache int,
    name varchar(255),
    namespace varchar(255),
    package varchar(511),
    version varchar(255),
    internal_version varchar(255),
    parent_type char(32),
    entity_id char(36),
    entity_type char(16),
    parent_id char(36)
) engine=InnoDB;

CREATE TABLE workflow(
    id char(36) not null auto_increment primary key,
    entity_id char(36),
    entity_type char(16),
    name varchar(255),
    version char(16),
    last_modified datetime,
    vistrail_id char(36),
    parent_id char(36)
) engine=InnoDB;

CREATE TABLE mashup_action(
    id char(36),
    prev_id char(36),
    date datetime,
    user varchar(255),
    parent_id char(36),
    entity_id char(36),
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE mashuptrail(
    id int not null auto_increment primary key,
    name varchar(255),
    version char(16),
    vt_version char(36),
    last_modified datetime,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE registry(
    id char(36) not null auto_increment primary key,
    entity_type char(16),
    version char(16),
    root_descriptor_id char(36),
    name varchar(255),
    last_modified datetime
) engine=InnoDB;

CREATE TABLE mashup_component(
    id char(36),
    vtid char(36),
    vttype varchar(255),
    vtparent_type char(32),
    vtparent_id int,
    vtpos int,
    vtmid char(36),
    pos int,
    type varchar(255),
    val mediumtext,
    minVal varchar(255),
    maxVal varchar(255),
    stepSize varchar(255),
    strvaluelist mediumtext,
    widget varchar(255),
    seq int,
    parent varchar(255),
    alias_id char(36),
    entity_id char(36),
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE annotation(
    id char(36),
    akey varchar(255),
    value mediumtext,
    parent_type char(32),
    entity_id char(36),
    entity_type char(16),
    parent_id char(36)
) engine=InnoDB;

CREATE TABLE change_tbl(
    id char(36),
    what varchar(255),
    old_obj_id char(36),
    new_obj_id char(36),
    par_obj_id char(36),
    par_obj_type char(16),
    action_id char(36),
    entity_id char(36),
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE group_exec(
    id char(36),
    ts_start datetime,
    ts_end datetime,
    cached int,
    module_id char(36),
    group_name varchar(255),
    group_type varchar(255),
    completed int,
    error varchar(1023),
    machine_id char(36),
    parent_type char(32),
    entity_id char(36),
    entity_type char(16),
    parent_id char(36)
) engine=InnoDB;

CREATE TABLE package(
    id char(36) not null auto_increment primary key,
    name varchar(255),
    identifier varchar(1023),
    codepath varchar(1023),
    load_configuration int,
    version varchar(255),
    description varchar(1023),
    parent_id char(36),
    entity_id char(36),
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE workflow_exec(
    id char(36),
    user varchar(255),
    ip varchar(255),
    session char(36),
    vt_version varchar(255),
    ts_start datetime,
    ts_end datetime,
    parent_id char(36),
    parent_type varchar(255),
    parent_version char(36),
    completed int,
    name varchar(255),
    log_id char(36),
    entity_id char(36),
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE parameter_exploration(
    id char(36),
    action_id char(36),
    name varchar(255),
    date datetime,
    user varchar(255),
    dims varchar(255),
    layout varchar(255),
    parent_id char(36),
    entity_id char(36),
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE loop_exec(
    id char(36),
    ts_start datetime,
    ts_end datetime,
    iteration int,
    completed int,
    error varchar(1023),
    parent_type char(32),
    entity_id char(36),
    entity_type char(16),
    parent_id char(36)
) engine=InnoDB;

CREATE TABLE mashup_action_annotation(
    id char(36),
    akey varchar(255),
    value varchar(8191),
    action_id char(36),
    date datetime,
    user varchar(255),
    parent_id char(36),
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE connection_tbl(
    id char(36),
    parent_type char(32),
    entity_id char(36),
    entity_type char(16),
    parent_id char(36)
) engine=InnoDB;

CREATE TABLE action(
    id char(36),
    prev_id char(36),
    date datetime,
    session char(36),
    user varchar(255),
    parent_id char(36),
    entity_id char(36),
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE delete_tbl(
    id char(36),
    what varchar(255),
    object_id char(36),
    par_obj_id char(36),
    par_obj_type char(16),
    action_id char(36),
    entity_id char(36),
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE vistrail(
    id char(36) not null auto_increment primary key,
    entity_type char(16),
    version char(16),
    name varchar(255),
    last_modified datetime
) engine=InnoDB;

CREATE TABLE module_exec(
    id char(36),
    ts_start datetime,
    ts_end datetime,
    cached int,
    module_id char(36),
    module_name varchar(255),
    completed int,
    error varchar(1023),
    machine_id char(36),
    parent_type char(32),
    entity_id char(36),
    entity_type char(16),
    parent_id char(36)
) engine=InnoDB;

