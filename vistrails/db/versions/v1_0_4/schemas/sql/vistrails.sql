--#############################################################################
--
-- Copyright (C) 2011-2014, NYU-Poly.
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
INSERT INTO `vistrails_version`(`version`) VALUES ('1.0.4');

CREATE TABLE thumbnail(
    id int not null auto_increment primary key,
    file_name varchar(255),
    image_bytes mediumblob,
    last_modified datetime
) engine=InnoDB;

-- generated automatically by auto_dao.py

CREATE TABLE mashup_alias(
    id int,
    name varchar(255),
    parent_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE group_tbl(
    id int,
    cache int,
    name varchar(255),
    namespace varchar(255),
    package varchar(511),
    version varchar(255),
    parent_type char(32),
    entity_id int,
    entity_type char(16),
    parent_id int
) engine=InnoDB;

CREATE TABLE add_tbl(
    id int,
    what varchar(255),
    object_id int,
    par_obj_id int,
    par_obj_type char(16),
    action_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE group_exec(
    id int,
    ts_start datetime,
    ts_end datetime,
    cached int,
    module_id int,
    group_name varchar(255),
    group_type varchar(255),
    completed int,
    error varchar(1023),
    machine_id int,
    parent_type char(32),
    entity_id int,
    entity_type char(16),
    parent_id int
) engine=InnoDB;

CREATE TABLE parameter(
    id int,
    pos int,
    name varchar(255),
    type varchar(255),
    val mediumtext,
    alias varchar(255),
    parent_type char(32),
    entity_id int,
    entity_type char(16),
    parent_id int
) engine=InnoDB;

CREATE TABLE vistrail(
    id int not null auto_increment primary key,
    entity_type char(16),
    version char(16),
    name varchar(255),
    last_modified datetime
) engine=InnoDB;

CREATE TABLE module(
    id int,
    cache int,
    name varchar(255),
    namespace varchar(255),
    package varchar(511),
    version varchar(255),
    parent_type char(32),
    entity_id int,
    entity_type char(16),
    parent_id int
) engine=InnoDB;

CREATE TABLE port(
    id int,
    type varchar(255),
    moduleId int,
    moduleName varchar(255),
    name varchar(255),
    signature varchar(4095),
    parent_type char(32),
    entity_id int,
    entity_type char(16),
    parent_id int
) engine=InnoDB;

CREATE TABLE pe_function(
    id int,
    module_id int,
    port_name varchar(255),
    is_alias int,
    parent_type char(32),
    parent_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE workflow(
    id int not null auto_increment primary key,
    entity_id int,
    entity_type char(16),
    name varchar(255),
    version char(16),
    last_modified datetime,
    vistrail_id int,
    parent_id int
) engine=InnoDB;

CREATE TABLE mashup_action(
    id int,
    prev_id int,
    date datetime,
    user varchar(255),
    parent_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE change_tbl(
    id int,
    what varchar(255),
    old_obj_id int,
    new_obj_id int,
    par_obj_id int,
    par_obj_type char(16),
    action_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE package(
    id int not null auto_increment primary key,
    name varchar(255),
    identifier varchar(1023),
    codepath varchar(1023),
    load_configuration int,
    version varchar(255),
    description varchar(1023),
    parent_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE loop_exec(
    id int,
    ts_start datetime,
    ts_end datetime,
    parent_type char(32),
    entity_id int,
    entity_type char(16),
    parent_id int
) engine=InnoDB;

CREATE TABLE connection_tbl(
    id int,
    parent_type char(32),
    entity_id int,
    entity_type char(16),
    parent_id int
) engine=InnoDB;

CREATE TABLE action(
    id int,
    prev_id int,
    date datetime,
    session int,
    user varchar(255),
    parent_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE port_spec(
    id int,
    name varchar(255),
    type varchar(255),
    optional int,
    depth int,
    sort_key int,
    min_conns int,
    max_conns int,
    parent_type char(32),
    entity_id int,
    entity_type char(16),
    parent_id int
) engine=InnoDB;

CREATE TABLE log_tbl(
    id int not null auto_increment primary key,
    entity_type char(16),
    version char(16),
    name varchar(255),
    last_modified datetime,
    vistrail_id int
) engine=InnoDB;

CREATE TABLE loop_iteration(
    id int,
    ts_start datetime,
    ts_end datetime,
    iteration int,
    completed int,
    error varchar(1023),
    parent_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE pe_parameter(
    id int,
    pos int,
    interpolator varchar(255),
    value mediumtext,
    dimension int,
    parent_type char(32),
    parent_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE workflow_exec(
    id int,
    user varchar(255),
    ip varchar(255),
    session int,
    vt_version varchar(255),
    ts_start datetime,
    ts_end datetime,
    parent_id int,
    parent_type varchar(255),
    parent_version int,
    completed int,
    name varchar(255),
    log_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE location(
    id int,
    x DECIMAL(18,12),
    y DECIMAL(18,12),
    parent_type char(32),
    entity_id int,
    entity_type char(16),
    parent_id int
) engine=InnoDB;

CREATE TABLE function(
    id int,
    pos int,
    name varchar(255),
    parent_type char(32),
    entity_id int,
    entity_type char(16),
    parent_id int
) engine=InnoDB;

CREATE TABLE action_annotation(
    id int,
    akey varchar(255),
    value varchar(8191),
    action_id int,
    date datetime,
    user varchar(255),
    parent_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE control_parameter(
    id int,
    name varchar(255),
    value mediumtext,
    parent_type char(32),
    entity_id int,
    entity_type char(16),
    parent_id int
) engine=InnoDB;

CREATE TABLE plugin_data(
    id int,
    data varchar(8191),
    parent_type char(32),
    entity_id int,
    entity_type char(16),
    parent_id int
) engine=InnoDB;

CREATE TABLE delete_tbl(
    id int,
    what varchar(255),
    object_id int,
    par_obj_id int,
    par_obj_type char(16),
    action_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE vistrail_variable(
    name varchar(255),
    uuid char(36),
    package varchar(255),
    module varchar(255),
    namespace varchar(255),
    value varchar(8191),
    parent_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE module_descriptor(
    id int,
    name varchar(255),
    package varchar(255),
    namespace varchar(255),
    package_version varchar(255),
    version varchar(255),
    base_descriptor_id int,
    parent_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE tag(
    id int,
    name varchar(255),
    parent_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE port_spec_item(
    id int,
    pos int,
    module varchar(255),
    package varchar(255),
    namespace varchar(255),
    label varchar(4095),
    _default varchar(4095),
    _values mediumtext,
    entry_type varchar(255),
    parent_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE mashup_component(
    id int,
    vtid int,
    vttype varchar(255),
    vtparent_type char(32),
    vtparent_id int,
    vtpos int,
    vtmid int,
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
    alias_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE mashup(
    id int,
    name varchar(255),
    version int,
    type varchar(255),
    vtid int,
    layout mediumtext,
    geometry mediumtext,
    has_seq int,
    parent_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE machine(
    id int,
    name varchar(255),
    os varchar(255),
    architecture varchar(255),
    processor varchar(255),
    ram bigint,
    vt_id int,
    log_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE other(
    id int,
    okey varchar(255),
    value varchar(255),
    parent_type char(32),
    entity_id int,
    entity_type char(16),
    parent_id int
) engine=InnoDB;

CREATE TABLE abstraction(
    id int,
    cache int,
    name varchar(255),
    namespace varchar(255),
    package varchar(511),
    version varchar(255),
    internal_version varchar(255),
    parent_type char(32),
    entity_id int,
    entity_type char(16),
    parent_id int
) engine=InnoDB;

CREATE TABLE mashuptrail(
    id int not null auto_increment primary key,
    name char(36),
    version char(16),
    vt_version int,
    last_modified datetime,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE registry(
    id int not null auto_increment primary key,
    entity_type char(16),
    version char(16),
    root_descriptor_id int,
    name varchar(255),
    last_modified datetime
) engine=InnoDB;

CREATE TABLE annotation(
    id int,
    akey varchar(255),
    value mediumtext,
    parent_type char(32),
    entity_id int,
    entity_type char(16),
    parent_id int
) engine=InnoDB;

CREATE TABLE parameter_exploration(
    id int,
    action_id int,
    name varchar(255),
    date datetime,
    user varchar(255),
    dims varchar(255),
    layout varchar(255),
    parent_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE mashup_action_annotation(
    id int,
    akey varchar(255),
    value varchar(8191),
    action_id int,
    date datetime,
    user varchar(255),
    parent_id int,
    entity_id int,
    entity_type char(16)
) engine=InnoDB;

CREATE TABLE module_exec(
    id int,
    ts_start datetime,
    ts_end datetime,
    cached int,
    module_id int,
    module_name varchar(255),
    completed int,
    error varchar(1023),
    machine_id int,
    parent_type char(32),
    entity_id int,
    entity_type char(16),
    parent_id int
) engine=InnoDB;

