--#############################################################################
--
-- Copyright (C) 2014-2016, New York University.
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
--  - Neither the name of the New York University nor the names of its
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
-- generated automatically by auto_dao.py

CREATE TABLE port_spec(
    id int,
    name varchar(22),
    type varchar(255),
    spec varchar(255),
    parent_type char(16),
    vt_id int,
    parent_id int
);

CREATE TABLE module(
    id int,
    cache int,
    name varchar(255),
    parent_type char(16),
    vt_id int,
    parent_id int
);

CREATE TABLE session(
    id int,
    user varchar(255),
    ip varchar(255),
    vis_ver varchar(255),
    ts_start datetime,
    tsEnd datetime,
    machine_id int,
    log_id int,
    vt_id int
);

CREATE TABLE port(
    id int,
    type varchar(255),
    moduleId int,
    moduleName varchar(255),
    sig varchar(255),
    parent_type char(16),
    vt_id int,
    parent_id int
);

CREATE TABLE log_tbl(
    id int,
    vt_id int
);

CREATE TABLE machine(
    id int,
    name varchar(255),
    os varchar(255),
    architecture varchar(255),
    processor varchar(255),
    ram int,
    log_id int,
    vt_id int
);

CREATE TABLE add_tbl(
    id int,
    what varchar(255),
    object_id int,
    par_obj_id int,
    par_obj_type char(16),
    action_id int,
    vt_id int
);

CREATE TABLE other(
    id int,
    okey varchar(255),
    value varchar(255),
    parent_type char(16),
    vt_id int,
    parent_id int
);

CREATE TABLE location(
    id int,
    x DECIMAL(18,12),
    y DECIMAL(18,12),
    parent_type char(16),
    vt_id int,
    parent_id int
);

CREATE TABLE wf_exec(
    id int,
    ts_start datetime,
    ts_end datetime,
    wfVersion int,
    vistrail_id int,
    vistrail_name varchar(255),
    session_id int,
    vt_id int
);

CREATE TABLE parameter(
    id int,
    pos int,
    name varchar(255),
    type varchar(255),
    val varchar(8192),
    alias varchar(255),
    parent_type char(16),
    vt_id int,
    parent_id int
);

CREATE TABLE function(
    id int,
    pos int,
    name varchar(255),
    parent_type char(16),
    vt_id int,
    parent_id int
);

CREATE TABLE workflow(
    id int,
    name varchar(255),
    vt_id int
);

CREATE TABLE action(
    id int,
    prev_id int,
    date datetime,
    user varchar(255),
    parent_type char(16),
    vt_id int,
    parent_id int
);

CREATE TABLE annotation(
    id int,
    akey varchar(255),
    value varchar(255),
    parent_type char(16),
    vt_id int,
    parent_id int
);

CREATE TABLE change_tbl(
    id int,
    what varchar(255),
    old_obj_id int,
    new_obj_id int,
    par_obj_id int,
    par_obj_type char(16),
    action_id int,
    vt_id int
);

CREATE TABLE macro(
    id int,
    name varchar(255),
    descrptn varchar(255),
    vt_id int
);

CREATE TABLE connection_tbl(
    id int,
    parent_type char(16),
    vt_id int,
    parent_id int
);

CREATE TABLE tag(
    name varchar(255),
    time int,
    vt_id int
);

CREATE TABLE exec(
    id int,
    ts_start datetime,
    ts_end datetime,
    module_id int,
    module_name varchar(255),
    wf_exec_id int,
    vt_id int
);

CREATE TABLE vistrail(
    id int not null auto_increment primary key,
    version char(16),
    name varchar(255)
);

CREATE TABLE delete_tbl(
    id int,
    what varchar(255),
    object_id int,
    par_obj_id int,
    par_obj_type char(16),
    action_id int,
    vt_id int
);

