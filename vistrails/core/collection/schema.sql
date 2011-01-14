create table entity(id integer primary key, type integer, name text, user integer, mod_time text, create_time text, size integer, description text, url text);
create table entity_children(parent integer, child integer);
create table type_map(id integer, type string);