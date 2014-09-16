##############################################################################
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

"""Configuration variables for controlling specific things in VisTrails."""
import argparse
import ast
import copy
import re
import shlex
import sys
import weakref

import os.path

from vistrails.core import system
from vistrails.core.utils import Ref, append_to_dict_of_lists
from vistrails.db.domain import DBConfiguration, DBConfigKey, DBConfigStr, \
    DBConfigInt, DBConfigFloat, DBConfigBool

##############################################################################

_docs = {}
_simple_docs = {}
_usage_args = set()

_simple_documentation = """
autoConnect: Automatically connect dragged in modules
autoSave: Automatically save backup vistrails every two minutes
dbDefault: Save vistrails in a database by default
cache: Cache previous results so they may be used in future computations
stopOnError: Stop all workflow execution immediately after first error
executionLog: Track execution provenance when running workflows
errorLog: Write errors to a log file
parameters: List of parameters to use when running workflow
host: The hostname for the database to load the vistrail from
port: The port for the database to load the vistrail from
db: The name for the database to load the vistrail from
user: The username for the database to the load vistrail from
defaultFileType: Default file type/extension for vistrails (.vt or .xml)
enablePackagesSilently: Automatically enable packages when needed
installBundles: Install missing Python dependencies
installBundlesWithPip: Use pip to install missing Python dependencies
upgrades: Attempt to automatically upgrade old workflows
showConnectionErrors: Show error when input value doesn't match type during execution
showVariantErrors: Show error when variant input value doesn't match type during execution
showDebugPopups: Always bring debug messages to the front
showScrollbars: Show scrollbars on the version tree and workflow canvases
shell.fontFace: Console Font
shell.fontSize: Console Font Size
maxRecentVistrails: Number of recent vistrails
maximizeWindows: VisTrails windows should be maximized
multiHeads: Use multiple screens for VisTrails windows
showSplash: Show VisTrails splash screen during startup
migrateTags: Move tags to upgraded versions
upgradeModuleFailPrompt: Alert when a subworkflow upgrade fails
thumbs.autoSave: Save thumbnails of visual results
thumbs.mouseHover: Show thumbnails when mouse is hovering above a version
thumbs.tagsOnly: Store thumbnails only for tagged versions
thumbs.cacheDir: Thumbnail cache directory
thumbs.cacheSize: Thumbnail cache size (MB)
singleInstance: Do not allow more than one instance of VisTrails to run at once
staticRegistry: XML registry file
dotVistrails: User configuration directory
subworkflowsDir: Local subworkflows directory
dataDir: Default data directory
packageDir: System packages directory
userPackageDir: Local packages directory
logDir: Log files directory
fileDir: Default vistrail directory
temporaryDir: Temporary files directory
webRepositoryURL: Web repository URL
webRepositoryUser: Web repository username
repositoryLocalPath: Local package repository directory
repositoryHTTPURL: Remote package repository URL
handlerDontAsk: Do not ask about extension handling at startup
rpcServer: Hostname or ip address where this xml rpc server will work
rpcPort: Port where this xml rpc server will work
rpcLogFile: Log file for XML RPC server
rpcInstances: Number of other instances that vistrails should start
multithread: Server will start a thread for each request
rpcConfig: Config file for server connection options
jobCheckInterval: How often to check for jobs (in seconds)
jobAutorun: Run jobs automatically when they finish
jobRun: Continue running specified job by id
jobList: List running jobs
"""

_documentation = """
subworkflowsDir: Path

    The location where a user's local subworkflows are stored.

autoConnect: Boolean

    Try to automatically connect a newly dragged in module to the rest
    of the workflow.

autoSave: Boolean

    Automatically save vistrails to allow recovery from crashes, etc.

dataDir: Path

    The location that VisTrails uses as a default directory for data.

dbDefault: Boolean

    Use a database as the default storage location for vistrails entities.

defaultFileType: String

    Defaults to .vt but could be .xml.

detachHistoryView: Boolean

    Show the version tree in a separate window

dotVistrails: Path

    The location to look for VisTrails user configurations and
    storage.  Defaults to ~/.vistrails.

host: URL

    The hostname for the database to load the vistrail from

port: Integer

    The port for the database to load the vistrail from

db: String

    The name for the database to load the vistrail from

user: String

    The username for the database to load the vistrail from

enablePackagesSilently: Boolean

    Do not prompt the user to enable packages, just do so
    automatically

showConnectionErrors: Boolean

    Alert the user if the value along a connection doesn't match
    connection types.

showVariantErrors: Boolean

    Alert the user if the value along a connection coming from a
    Variant output matches the input port.

execute: Boolean

    Execute any specified workflows

fileDir: Path

    The location that VisTrails uses as a default directory for
    specifying files.

fixedSpreadsheetCells: Boolean

    Draw spreadsheet cells at a fixed size (for testing).

installBundles: Boolean

    Automatically try to install missing Python dependencies

installBundlesWithPip: Boolean

    Whether to try to use pip to install Python dependencies or use
    distribution support.

batch: Boolean

    Run vistrails in batch mode instead of interactive mode

logDir: Path

    The path that indicates where log files should be stored.

logger: ConfigurationObject

    *Deprecated*

maxMemory: Integer

    *Deprecated*

maximizeWindows: Boolean

    Whether the VisTrails windows should take up the entire screen space

maxRecentVistrails: Integer

    How many recently opened vistrails should be stored for "Open
    Recent" access.

migrateTags: Boolean

    Whether or not the tag on a workflow that was upgraded should be
    moved to point to the upgraded version.

minMemory: Integer

    *Deprecated*

multiHeads: Boolean

    Whether or not to use multiple screens for VisTrails windows.

executionLog: Boolean

    Track execution provenance when running workflows

packageDir: Path

    The directory to look for VisTrails core packages (use
    userPackageDir for user-defined packages)

parameters: String

    List of parameters to use when running workflow

pythonPrompt: Boolean

    *Deprecated*

recentVistrailList: String

    Storage for recent vistrails.  Users should not edit.

repositoryLocalPath: Path

    Path used to locate packages available to be installed

repositoryHTTPURL: URL

    URL used to locate packages available to be installed

reviewMode: Boolean

    *Deprecated* Used to interactively export a pipeline

rootDirectory: Path

    Directory that contains the VisTrails source code.

runningJobsList: String

    Storage for recent vistrails.  Users should not edit

shell: ConfigurationObject

    Settings for the appearance of the VisTrails console

shell.fontFace: String

    The font to be used for the VisTrails console

shell.fontSize: Integer

    The font size used for the VisTrails console

showDebugPopups: Boolean

    Always show the debug popups or only if there is a modal widget.

showMovies: Boolean

    *Deprecated* Set automatic movie creation on the spreadsheet.

showScrollbars: Boolean

    Whether VisTrails should show scrollbars on the version tree and
    workflow canvases.

showSplash: Boolean

    Whether the VisTrails splash screen should be shown on startup.

showSpreadsheetOnly: Boolean

    Whether the VisTrails main window should be hidden

singleInstance: Boolean

    Whether or not VisTrails should only allow one instance to be
    running

spreadsheetDumpCells: Path

    If specified, defines the location for parameter exploration to
    store the cells it generates.

spreadsheetDumpPDF: Boolean

    Whether the spreadsheet should dump images in PDF format

staticRegistry: Path

    If specified, VisTrails uses an XML file defining the VisTrails
    module registry to load modules instead of from the packages
    directly

stopOnError: Boolean

    Whether or not VisTrails stops executing the rest of the workflow
    if it encounters an error in one module.

temporaryDir: Path

    The directory to use for temporary files generated by VisTrails

thumbs: ConfiguationObject

    Settings for generating and saving thumbnail images

thumbs.autoSave: Boolean

    Whether to save thumbnails of results when executing VisTrails

thumbs.cacheDir: Path

    The directory to be used to cache thumbnails

thumbs.cacheSize: Integer

    The size (in MB) of the thumbnail cache

thumbs.mouseHover: Boolean

    Whether to show thumbnails when hovering over a version in the
    version tree

thumbs.tagsOnly: Boolean

    If True, only stores thumbnails for tagged versions.  Otherwise,
    stores thumbnails for all versions.

upgrades: Boolean

    Whether to upgrade old workflows so they work with newer packages

upgradeDelay: Boolean

    Persist upgrade only after other changes

OLDupgradeDelay: Boolean
    If True, will only persist the upgrade when a user makes a
    modification to or executes the workflow.  Otherwise, the upgrade
    will be automatically added to the version tree when a user views
    an upgraded workflow.

upgradeModuleFailPrompt: Boolean

    Whether to alert the user when an upgrade may fail when upgrading
    a subworkflow.

cache: Boolean

    Cache previous results so they may be used in future computations

userPackageDir: Boolean

    The location for user-installed packages (defaults to ~/.vistrails/userpacakges)

debugLevel: Integer

    How much information VisTrails should alert the user about (0:
    Critical errors only, 1: Critical errors and warnings, 2: Critical
    errors, warnings, and log messages).

webRepositoryUser: String

    The default username for logging into a VisTrails web repository
    like crowdLabs

webRepositoryURL: URL

    The URL of the web repository that should be attached to VisTrails
    (e.g. www.crowdlabs.org)

isInServerMode: Boolean

    Indicates whether VisTrails is being run as a server.

useMacBrushedMetalStyle: Boolean

    Whether should use a brushed metal interface (MacOS X only)

withVersionTree: Boolean

    Output the version tree as an image

withWorkflow: Boolean

    Output the workflow graph as an image

outputSettings: ConfigurationObject

    One or more comma-separated key=value parameters

outputDefaultSettings: ConfigurationObject

    One or more comma-separated key=value parameters

rpcServer: URL

    Hostname or ip address where this xml rpc server will work

rpcPort: Integer

    Port where this xml rpc server will work

rpcLogFile: String

    Log file for XML RPC server

rpcInstances: Integer

    Number of other instances that vistrails should start

multithread: Boolean

    Server will start a thread for each request

rpcConfig: String

    Config file for server connection options

jobCheckInterval: Integer:

    How often to check for jobs (in seconds, default=600)

jobAutorun: Boolean

    Run jobs automatically when they finish

jobRun: String

    Continue running specified job by id (use jobList to get)

jobList: Boolean

    List running jobs

"""

class ConfigType(object):
    NORMAL = 0
    SHOW_HIDE = 1
    ON_OFF = 2
    COMMAND_LINE = 3
    COMMAND_LINE_FLAG = 4
    INTERNAL = 5
    STORAGE = 6
    PACKAGE = 7
    SUBOBJECT = 8
    INTERNAL_SUBOBJECT = 9

class ConfigString(object):
    @classmethod
    def from_string(cls, val):
        if not val:
            return None
        return val

    @classmethod
    def to_string(cls, val):
        if val is None:
            return ""
        return val

class ConfigPath(ConfigString):
    pass

class ConfigURL(ConfigString):
    pass

class ConfigField(object):
    def __init__(self, name, default_val, val_type,
                 field_type=ConfigType.NORMAL, category=None, flag=None,
                 nargs=None, widget_type=None,
                 widget_options=None, depends_on=None):
        self.name = name
        self.default_val = default_val
        self.val_type = val_type
        self.field_type = field_type
        self.category = category
        self.flag = flag
        self.nargs = nargs
        self.widget_type = widget_type
        if widget_options is not None:
            self.widget_options = widget_options
        else:
            self.widget_options = {}
        self.depends_on = depends_on

    def from_string(self, str_val):
        if hasattr(self.val_type, "from_string"):
            return self.val_type.from_string(str_val)
        if not str_val:
            return None
        if issubclass(self.val_type, basestring):
            return str_val
        val = ast.literal_eval(str_val)
        if not isinstance(val, self.val_type):
            raise ValueError('Output setting "%s" cannot be parsed to %s' %
                             (self.name, self.val_type.__name__))
        return val

    def to_string(self, val):
        if hasattr(self.val_type, "to_string"):
            return self.val_type.to_string(val)
        elif val is None:
            return ""
        return unicode(val)

class ConfigFieldParent(object):
    def __init__(self, name, sub_fields):
        self.name = name
        self.sub_fields = sub_fields

base_config = {
    "Command-Line":
    [ConfigField("execute", False, bool, ConfigType.COMMAND_LINE_FLAG,
                 flag='-e'),
     ConfigField("batch", False, bool, ConfigType.COMMAND_LINE_FLAG,
                 flag='-b'),
     ConfigField("outputDirectory", None, ConfigPath, flag='-o'),
     ConfigField('outputDefaultSettings', [], str,
                 ConfigType.INTERNAL_SUBOBJECT),
     ConfigField('outputSettings', [], str, ConfigType.SUBOBJECT,
                 flag='-p'),
     # ConfigField("package", [], str, flag='-p', nargs='*'),
     ConfigField("parameters", None, str, ConfigType.COMMAND_LINE),
     ConfigField('showWindow', True, bool, ConfigType.COMMAND_LINE_FLAG),
     ConfigField("withVersionTree", False, bool, ConfigType.COMMAND_LINE_FLAG),
     ConfigField("withWorkflow", False, bool, ConfigType.COMMAND_LINE_FLAG),
     ConfigField("graphsAsPdf", True, bool, ConfigType.COMMAND_LINE_FLAG)],
    "Database":
    [ConfigField("host", None, ConfigURL, ConfigType.COMMAND_LINE),
     ConfigField("port", None, int, ConfigType.COMMAND_LINE),
     ConfigField("db", None, str, ConfigType.COMMAND_LINE),
     ConfigField("user", None, str, ConfigType.COMMAND_LINE)],
    "Server":
    [ConfigField('rpcServer', None, str, ConfigType.COMMAND_LINE),
     ConfigField('rpcPort', 8080, int, ConfigType.COMMAND_LINE),
     ConfigField('rpcLogFile', os.path.join(system.vistrails_root_directory(),
                       'rpcserver.log'), ConfigPath, ConfigType.COMMAND_LINE),
     ConfigField('rpcInstances', 0, int, ConfigType.COMMAND_LINE),
     ConfigField('multithread', None, bool, ConfigType.COMMAND_LINE_FLAG),
     ConfigField('rpcConfig', os.path.join(system.vistrails_root_directory(),
                      'server.cfg'), ConfigPath, ConfigType.COMMAND_LINE)],
    "General":
    [ConfigField('autoSave', True, bool, ConfigType.ON_OFF),
     ConfigField('dbDefault', False, bool, ConfigType.ON_OFF),
     ConfigField('cache', True, bool, ConfigType.ON_OFF),
     ConfigField('stopOnError', True, bool, ConfigType.ON_OFF),
     ConfigField('executionLog', True, bool, ConfigType.ON_OFF),
     ConfigField('errorLog', True, bool, ConfigType.ON_OFF),
     ConfigField('defaultFileType', system.vistrails_default_file_type(), str,
                 widget_type="combo",
                 widget_options={"allowed_values": [".vt", ".xml"],
                                 "label": "Default File Type/Extension"}),
     ConfigField('debugLevel', 0, int, widget_type="combo",
                 widget_options={"allowed_values": [0,1,2],
                                 "label": "Show alerts for",
                                 "remap": {0: "Critical Errors Only",
                                           1: "Critical Errors and Warnings",
                                           2: "Errors, Warnings, and " \
                                           "Debug Messages"}})],
    "Startup":
    [ConfigField('maximizeWindows', False, bool, ConfigType.ON_OFF),
     ConfigField('multiHeads', False, bool, ConfigType.ON_OFF),
     ConfigField('showSplash', True, bool, ConfigType.SHOW_HIDE)],
    "Upgrades":
    [ConfigField('upgrades', True, bool, ConfigType.ON_OFF),
     ConfigField('migrateTags', False, bool, ConfigType.ON_OFF,
                 depends_on="upgrades"),
     ConfigField('upgradeDelay', True, bool, ConfigType.ON_OFF,
                 depends_on="upgrades"),
     ConfigField('upgradeModuleFailPrompt', True, bool, ConfigType.ON_OFF,
                 depends_on="upgrades")],
    "Interface":
    [ConfigField('autoConnect', True, bool, ConfigType.ON_OFF),
     ConfigField('detachHistoryView', False, bool, ConfigType.ON_OFF),
     ConfigField('showConnectionErrors', False, bool, ConfigType.SHOW_HIDE),
     ConfigField('showVariantErrors', True, bool, ConfigType.SHOW_HIDE),
     ConfigField('showDebugPopups', False, bool, ConfigType.SHOW_HIDE),
     ConfigField('showScrollbars', True, bool, ConfigType.SHOW_HIDE),
     ConfigFieldParent('shell',
        [ConfigField('fontFace', system.shell_font_face(), str),
         ConfigField('fontSize', system.shell_font_size(), int)]),
     ConfigField('maxRecentVistrails', 5, int),
     ConfigField('viewOnLoad', "appropriate", str, widget_type='combo',
                 widget_options={"allowed_values": ["appropriate",
                                                    "history",
                                                    "pipeline"],
                                 "label": "Default view after loading vistrail:",
                                 "remap": {"appropriate": "Most Appropriate",
                                           "history": "Always History",
                                           "pipeline": "Always Pipeline"}}),
     ConfigField('enableCustomVersionColors', False, bool, ConfigType.ON_OFF),
     ConfigField('fixedCustomVersionColorSaturation', False,
                 bool, ConfigType.ON_OFF)],
    "Thumbnails":
    [ConfigFieldParent('thumbs',
        [ConfigField('autoSave', True, bool, ConfigType.ON_OFF),
         ConfigField('mouseHover', False, bool, ConfigType.ON_OFF),
         ConfigField('tagsOnly', False, bool, ConfigType.ON_OFF),
         ConfigField('cacheDir', "thumbs", ConfigPath,
                     ConfigType.NORMAL),
         ConfigField('cacheSize', 20, int, widget_type='thumbnailcache')])],
    "Packages":
    [ConfigField('enablePackagesSilently', False, bool, ConfigType.ON_OFF),
     ConfigField('installBundles', True, bool, ConfigType.ON_OFF),
     ConfigField('installBundlesWithPip', False, bool, ConfigType.ON_OFF,
                 depends_on="installBundles"),
     ConfigField('repositoryLocalPath', None, ConfigPath),
     ConfigField('repositoryHTTPURL', "http://www.vistrails.org/packages",
                 ConfigURL)],
    "Paths":
    [ConfigField('dotVistrails', system.default_dot_vistrails(),
                 ConfigPath, flag="-S"),
     ConfigField('subworkflowsDir', "subworkflows", ConfigPath),
     ConfigField('dataDir', None, ConfigPath),
     ConfigField('packageDir', None, ConfigPath),
     ConfigField('userPackageDir', "userpackages", ConfigPath),
     ConfigField('fileDir', None, ConfigPath),
     ConfigField('logDir', "logs", ConfigPath),
     ConfigField('temporaryDir', None,  ConfigPath)],
    "Advanced":
    [ConfigField('singleInstance', True, bool, ConfigType.ON_OFF),
     ConfigField('staticRegistry', None, ConfigPath)],
    "Web Sharing":
    [ConfigField('webRepositoryURL', "http://www.crowdlabs.org", ConfigURL),
     ConfigField('webRepositoryUser', None, str)],
    "Internal":
    [ConfigField('recentVistrailList', None, str, ConfigType.STORAGE),
     ConfigField('isInServerMode', False, bool, ConfigType.INTERNAL),
     ConfigField('isRunningGUI', True, bool, ConfigType.INTERNAL),
     ConfigField('spawned', False, bool, ConfigType.INTERNAL),
     ConfigField('rootDirectory', None, ConfigPath, ConfigType.INTERNAL),
     ConfigField('developerDebugger', False, bool, ConfigType.INTERNAL)],
    "Jobs":
    [ConfigField('jobCheckInterval', 600, int),
     ConfigField('jobAutorun', False, bool),
     ConfigField('jobRun', None, str, ConfigType.COMMAND_LINE),
     ConfigField('jobList', False, bool, ConfigType.COMMAND_LINE_FLAG)],
}

# FIXME make sure that the platform-specific configs are added!
mac_config = {
    "Interface":
    [ConfigField('useMacBrushedMetalStyle', True, bool, ConfigType.ON_OFF)]
}

win_config = { }

linux_config = {
    "General":
    [ConfigField('handlerCheck', None, str, ConfigType.INTERNAL,
                 widget_type="linuxext",
                 widget_options={'label': 'Extension Handler'}),
     ConfigField('handlerDontAsk', None, bool)]
}

all_configs = [base_config, mac_config, win_config, linux_config]

def build_config_obj(d):
    new_d = {}
    for category, fields in d.iteritems():
        for field in fields:
            if isinstance(field, ConfigFieldParent):
                new_d[field.name] = build_config_obj({category:
                                                      field.sub_fields})
            elif (field.field_type == ConfigType.SUBOBJECT or
                  field.field_type == ConfigType.INTERNAL_SUBOBJECT):
                new_d[field.name] = ConfigurationObject()
            else:
                v = field.default_val
                if v is None:
                    val_type = field.val_type
                    if (field.val_type == ConfigPath or
                        field.val_type == ConfigURL):
                        val_type = basestring
                    new_d[field.name] = (v, val_type)
                else:
                    new_d[field.name] = v
    return ConfigurationObject(**new_d)

def get_system_config():
    config = {}
    config.update((k, copy.copy(v)) for k, v in base_config.iteritems())
    if system.systemType in ['Windows', 'Microsoft']:
        sys_config = win_config
    elif system.systemType in ['Linux']:
        sys_config = linux_config
    elif system.systemType in ['Darwin']:
        sys_config = mac_config
    for category, fields in sys_config.iteritems():
        if category not in base_config:
            config[category] = fields
        else:
            config[category].extend(fields)
    return config

def default():
    config = get_system_config()
    retval = build_config_obj(config)
    return retval

def parse_documentation():
    global _docs

    line_iter = iter(_documentation.splitlines())
    line_iter.next()
    for line in line_iter:
        arg_path, arg_type = line.strip().split(':', 1)
        doc_lines = []
        line = line_iter.next()
        while True:
            line = line_iter.next()
            if not line.strip():
                break
            doc_lines.append(line.strip())
        _docs[arg_path] = (arg_type, ' '.join(doc_lines))

def parse_simple_docs():
    global _simple_docs

    line_iter = iter(_simple_documentation.splitlines())
    line = line_iter.next()
    for line in line_iter:
        (arg, doc) = line.strip().split(':', 1)
        _simple_docs[arg] = doc.strip()

def find_help(arg_path):
    if len(_docs) == 0:
        parse_documentation()

    if arg_path in _docs:
        return _docs[arg_path][1]
    return None

def find_simpledoc(arg_path):
    if len(_simple_docs) == 0:
        parse_simple_docs()

    if arg_path in _simple_docs:
        return _simple_docs[arg_path]
    return find_help(arg_path)

def set_field_labels(fields, prefix=""):
    for field in fields:
        if isinstance(field, ConfigFieldParent):
            prefix = "%s%s." % (prefix, field.name)
            set_field_labels(field.sub_fields, prefix=prefix)
        else:
            full_field_name = "%s%s" % (prefix, field.name)
            label = find_simpledoc(full_field_name)
            if label is not None and 'label' not in field.widget_options:
                field.widget_options['label'] = label

for config in all_configs:
    for field_list in config.itervalues():
        set_field_labels(field_list)

class VisTrailsHelpFormatter(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        new_actions = []
        new_actions.append(argparse.Action([], dest="__nowhere__",
                                           metavar="[CONFIGURATION OPTIONS]"))
        for action in actions:
            if action.dest in _usage_args:
                new_actions.append(action)
        argparse.HelpFormatter.add_usage(self, usage, new_actions, groups,
                                         prefix)

class NestedSetKwargs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        orig_dest = self.dest
        nesting = self.dest.split('.')
        while len(nesting) > 1:
            namespace = getattr(namespace, nesting.pop(0))
        self.dest = nesting[0]

        param_splitter = shlex.shlex(values, posix=True)
        param_splitter.whitespace = ','
        param_splitter.whitespace_split = True
        for param in param_splitter:
            key_val_split = param.split('=',1)
            if len(key_val_split) < 2:
                raise ValueError("Expected key=value comma-separated list")
            key, val = key_val_split

            dest = "%s.%s" % (self.dest, key)
            namespace.set_deep_value(dest, val, True)
        self.dest = orig_dest

def nested_action(parser, action_type):
    cls = parser._registry_get('action', action_type)
    if cls is None:
        raise ValueError('Action type "%s" is not defined' % action_type)

    def __call__(self, parser, namespace, values, option_string=None):
        orig_dest = self.dest
        nesting = self.dest.split('.')
        while len(nesting) > 1:
            namespace = getattr(namespace, nesting.pop(0))
        self.dest = nesting[0]
        cls.__call__(self, parser, namespace, values, option_string=None)
        self.dest = orig_dest

    nested_name = "_Nested%s" % cls.__name__[1:]
    nested_cls = type(nested_name, (cls,), {"__call__": __call__})
    return nested_cls

def build_command_line_parser(d, parser=None, prefix="", **parser_args):
    global _usage_args

    # if k is not a command-line-option, skip
    # if k is show/hide, add --show-, --hide- options
    # if k is an on/off, add --option, --no-option flags
    # otherwise, run with k converted to dashed form and store res


    def camel_to_dashes(s):
        # from http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-camel-case/1176023#1176023
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', s)
        return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()


    if parser is None:
        parser = argparse.ArgumentParser(prog='vistrails',
                                         **parser_args)
        parser._my_arg_groups = {}
        parser.add_argument('vistrails', metavar='vistrail', type=str,
                            nargs='*', help="Vistrail to open")
        _usage_args.add('vistrails')


    prefix_dashes = ''
    if prefix:
        prefix_dashes = camel_to_dashes(prefix.replace('.', '-'))

    for category, fields in d.iteritems():
        if category == "Internal":
            # don't deal with these
            continue
        if category == "Command-Line":
            cat_group = parser
        else:
            if category not in parser._my_arg_groups:
                parser._my_arg_groups[category] = \
                                        parser.add_argument_group(category)
            cat_group = parser._my_arg_groups[category]

        for field in fields:
            if isinstance(field, ConfigFieldParent):
                build_command_line_parser({category: field.sub_fields},
                                          parser,
                                          '%s%s.' % (prefix, field.name),
                                          **parser_args)
                continue
            k_dashes = camel_to_dashes(field.name)
            help_str = find_help('%s%s' % (prefix, field.name))
            dest_name = prefix + field.name

            config_type = field.field_type
            if config_type is None:
                config_type = ConfigType.NORMAL
            if (config_type == ConfigType.INTERNAL or \
                config_type == ConfigType.STORAGE or
                config_type == ConfigType.INTERNAL_SUBOBJECT):
                # these are not in the command line
                continue
            elif config_type == ConfigType.ON_OFF:
                k_dashes = camel_to_dashes(field.name)
                group = cat_group.add_mutually_exclusive_group()
                group.add_argument('--%s%s' % (prefix_dashes, k_dashes),
                                   # action="store_true",
                                   action=nested_action(group, "store_true"),
                                   dest=dest_name, help=help_str,
                                   default=argparse.SUPPRESS)
                group.add_argument('--no-%s%s' % (prefix_dashes, k_dashes),
                                   # action="store_false",
                                   action=nested_action(group, "store_false"),
                                   dest=dest_name,
                                   help=("Inverse of --%s%s" %
                                         (prefix_dashes, k_dashes)),
                                   default=argparse.SUPPRESS)
            elif config_type == ConfigType.SHOW_HIDE:
                k_dashes = camel_to_dashes(field.name[4:])
                group = cat_group.add_mutually_exclusive_group()
                group.add_argument('--show-%s%s' % (prefix_dashes, k_dashes),
                                   # action="store_true",
                                   action = nested_action(group, "store_true"),
                                   dest=dest_name, help=help_str,
                                   default=argparse.SUPPRESS)
                group.add_argument('--hide-%s%s' % (prefix_dashes, k_dashes),
                                   # action="store_false",
                                   action=nested_action(group, "store_false"),
                                   dest=dest_name,
                                   help=("Inverse of --show-%s%s" %
                                         (prefix_dashes, k_dashes)),
                                   default=argparse.SUPPRESS)
            else:
                k_dashes = camel_to_dashes(field.name)
                long_arg = '--%s%s' % (prefix_dashes, k_dashes)
                if field.flag is not None:
                    args = (field.flag, long_arg)
                else:
                    args = (long_arg,)
                kwargs = {'dest': dest_name,
                          'help': help_str,
                          'default': argparse.SUPPRESS}
                if (field.val_type != ConfigPath and
                    field.val_type != ConfigURL and
                    field.val_type != str and
                    field.val_type != bool):
                    kwargs["type"] = field.val_type
                if config_type == ConfigType.SUBOBJECT:
                    kwargs["action"] = NestedSetKwargs
                elif config_type == ConfigType.COMMAND_LINE_FLAG:
                    kwargs["action"] = nested_action(cat_group, "store_true")
                else:
                    kwargs["action"] = nested_action(cat_group, "store")
                if field.val_type == ConfigPath:
                    kwargs["metavar"] = "DIR"
                elif field.val_type == ConfigURL:
                    kwargs["metavar"] = "URL"
                if field.nargs is not None:
                    kwargs["nargs"] = field.nargs

                cat_group.add_argument(*args, **kwargs)
                if category == "Command-Line":
                    _usage_args.add(field.name)
    return parser

def build_default_parser():
    parser_args = {"formatter_class": VisTrailsHelpFormatter,
                   "argument_default": argparse.SUPPRESS}
    return build_command_line_parser(get_system_config(), **parser_args)

def build_sphinx_parser():
    # FIXME add system-specific config options somehow
    return build_command_line_parser(base_config)

class ConfigValue(object):
    @staticmethod
    def create(value):
        if isinstance(value, bool):
            obj = ConfigBool()
        elif isinstance(value, basestring):
            obj = ConfigStr()
        elif isinstance(value, int):
            obj = ConfigInt()
        elif isinstance(value, float):
            obj = ConfigFloat()
        elif isinstance(value, list):
            obj = ConfigList()
        elif isinstance(value, ConfigurationObject):
            obj = value
        elif value is None:
            obj = None
        else:
            raise Exception('Cannot create ConfigValue from value "%s"' % value)
        if obj is not None:
            obj.set_value(value)
        return obj

    def get_value(self):
        return self.db_value

    def set_value(self, val):
        self.db_value = val

class ConfigBool(DBConfigBool, ConfigValue):
    def __copy__(self):
        """ __copy__() -> ConfigBool - Returns a clone of itself """
        return ConfigBool.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfigBool.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ConfigBool
        return cp

    @staticmethod
    def convert(_val):
        _val.__class__ = ConfigBool

    def get_value(self):
        return self.db_value.lower() == "true"

    def set_value(self, val):
        self.db_value = unicode(val)

class ConfigInt(DBConfigInt, ConfigValue):
    def __copy__(self):
        """ __copy__() -> ConfigInt - Returns a clone of itself """
        return ConfigInt.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfigInt.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ConfigInt
        return cp

    @staticmethod
    def convert(_val):
        _val.__class__ = ConfigInt

class ConfigStr(DBConfigStr, ConfigValue):
    def __copy__(self):
        """ __copy__() -> ConfigStr - Returns a clone of itself """
        return ConfigStr.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfigStr.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ConfigStr
        return cp

    @staticmethod
    def convert(_val):
        _val.__class__ = ConfigStr

class ConfigFloat(DBConfigFloat, ConfigValue):
    def __copy__(self):
        """ __copy__() -> ConfigFloat - Returns a clone of itself """
        return ConfigFloat.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfigFloat.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ConfigFloat
        return cp

    @staticmethod
    def convert(_val):
        _val.__class__ = ConfigFloat

class ConfigList(DBConfigStr, ConfigValue):
    def __copy__(self):
        """ __copy__() -> ConfigList - Returns a clone of itself """
        return ConfigList.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfigStr.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ConfigList
        return cp

    @staticmethod
    def convert(_val):
        _val.__class__ = ConfigList

    def get_value(self):
        return ast.literal_eval(self.db_value)

    def set_value(self, val):
        self.db_value = unicode(val)

class ConfigKey(DBConfigKey):
    def __init__(self, name, value):
        if isinstance(value, tuple):
            DBConfigKey.__init__(self, name=name)
            self.set_type(value[1])
        else:
            DBConfigKey.__init__(self, name=name,
                                 value=ConfigValue.create(value))
            self.set_type(type(value))

    def __copy__(self):
        """ __copy__() -> ConfigKey - Returns a clone of itself """
        return ConfigKey.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfigKey.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ConfigKey
        cp._type = self._type
        return cp

    @staticmethod
    def convert(_key):
        _key.__class__ = ConfigKey
        if isinstance(_key.db_value, DBConfiguration):
            ConfigurationObject.convert(_key.db_value)
        elif isinstance(_key.db_value, DBConfigBool):
            ConfigBool.convert(_key.db_value)
        elif isinstance(_key.db_value, DBConfigStr):
            ConfigStr.convert(_key.db_value)
        elif isinstance(_key.db_value, DBConfigInt):
            ConfigInt.convert(_key.db_value)
        elif isinstance(_key.db_value, DBConfigFloat):
            ConfigFloat.convert(_key.db_value)
        #FIXME add ConfigList to db and here
        _key.set_type(type(_key.value))

    def _get_value(self):
        if self.db_value is not None:
            return self.db_value.get_value()
        return None
    def _set_value(self, val):
        if not self.check_type(val):
            raise TypeError('Value "%s" does not match type %s' %
                            (val, self._type))
        self.db_value = ConfigValue.create(val)
    value = property(_get_value, _set_value)

    def set_type(self, t):
        if issubclass(t, basestring):
            t = basestring
        self._type = t

    def check_type(self, val):
        return val is None or isinstance(val, self._type)

class ConfigurationObject(DBConfiguration):
    """A ConfigurationObject is an InstanceObject that respects the
    following convention: values that are not 'present' in the object
    should have value (None, type), where type is the type of the
    expected object.

    ConfigurationObject exists so that the GUI can automatically infer
    the right types for the widgets.

    """


    def __init__(self, **kwargs):
        self._in_init = True
        self._unset_keys = {}
        DBConfiguration.__init__(self)
        self._in_init = False
        for k, v in kwargs.iteritems():
            if type(v) == tuple:
                self._unset_keys[k] = v
            else:
                key = ConfigKey(name=k, value=v)
                self.db_add_config_key(key)

        # InstanceObject.__init__(self, *args, **kwargs)
        self.__subscribers__ = {}
        self.vistrails = []

    def __copy__(self):
        """ __copy__() -> ConfigurationObject - Returns a clone of itself """
        return ConfigurationObject.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfiguration.do_copy(self, new_ids, id_scope, id_remap)
        cp._in_init = False
        cp.__class__ = ConfigurationObject
        cp._unset_keys = copy.copy(self._unset_keys)
        cp.__subscribers__ = copy.copy(self.__subscribers__)
        cp.vistrails = copy.copy(self.vistrails)
        return cp

    @staticmethod
    def convert(_config_obj):
        _config_obj._in_init = False
        _config_obj.__class__ = ConfigurationObject
        for _key in _config_obj.db_config_keys:
            ConfigKey.convert(_key)
        _config_obj.__subscribers__ = {}
        _config_obj._unset_keys = {}
        _config_obj.vistrails = []

    def get_value(self):
        return self

    def set_value(self, val):
        # it itself is the value already
        pass

    def matches_type(self, value, t):
        if t == str:
            t = basestring
        return isinstance(value, t)

    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            try:
                return self.get(name)
            except:
                raise AttributeError(name)

    def __setattr__(self, name, value):
        if name == '__subscribers__' or name == '_unset_keys' or name == '_in_init' or name == 'is_dirty' or name == 'vistrails' or self._in_init:
            object.__setattr__(self, name, value)
        else:
            if name in self.db_config_keys_name_index:
                config_key = self.db_config_keys_name_index[name]
                if value is None:
                    self.db_delete_config_key(config_key)
                    self._unset_keys[name] = (None, type(config_key.value))
                else:
                    config_key.value = value
            else:
                if name not in self._unset_keys:
                    self._unset_keys[name] = (None, type(value))
                    # raise AttributeError('Key "%s" was not defined when '
                    #                      'ConfigurationObject was created' %
                    #                      name)
                if (value is not None and
                      not self.matches_type(value, self._unset_keys[name][1])):
                    raise TypeError('Value "%s" does match type "%s" for "%s"' %
                                    (value, self._unset_keys[name][1], name))
                if value is not None:
                    del self._unset_keys[name]
                    config_key = ConfigKey(name=name, value=value)
                    self.db_add_config_key(config_key)
            if name in self.__subscribers__:
                to_remove = []
                for subscriber in self.__subscribers__[name]:
                    obj = subscriber()
                    if obj:
                        obj(name, value)
                    else:
                        to_remove.append(obj)
                for ref in to_remove:
                    self.__subscribers__[name].remove(ref)

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        seen_keys = set()
        for name in self.keys():
            seen_keys.add(name)
            if name not in other.keys():
                return False
            val1 = getattr(self, name)
            val2 = getattr(other, name)
            if type(val1) != type(val2):
                return False
            if val1 != val2:
                return False
        for name in other.keys():
            if name not in seen_keys:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __contains__(self, k):
        return self.has(k)

    def __getitem__(self, k):
        return self.get(k)

    def __setitem__(self, k, v):
        return self.__setattr__(k, v)

    def update(self, other):
        for name, other_key in other.db_config_keys_name_index.iteritems():
            if (isinstance(other_key.value, ConfigurationObject) and
                    self.has(name)):
                self.get(name).update(other_key.value)
            else:
                self.__setattr__(name, other_key.value)

    def unsubscribe(self, field, callable_):
        """unsubscribe(field, callable_): remove observer from subject
        """
        self.__subscribers__[field].remove(weakref.ref(callable_))

    def subscribe(self, field, callable_):
        """subscribe(field, callable_): call observer callable_ when
        self.field is set.
        """
        append_to_dict_of_lists(self.__subscribers__, field,
                                Ref(callable_))

    def has(self, key):
        """has(key) -> bool.

        Returns true if key has valid value in the object.
        """

        return key in self.db_config_keys_name_index

    def get(self, key):
        if key in self._unset_keys:
            return self._unset_keys[key]
        config_key = self.db_config_keys_name_index[key]
        return config_key.value

    def is_unset(self, keys_str):
        keys = keys_str.split('.')
        config = self
        for key in keys[:-1]:
            config = config.get(key)
        return keys[-1] in config._unset_keys

    def get_deep_value(self, keys_str):
        # keys_str is something like "thmbs.cacheDir"
        keys = keys_str.split('.')
        config = self
        for key in keys:
            config = config.get(key)
        return config

    def has_deep_value(self, keys_str):
        # keys_str is something like "thmbs.cacheDir"
        keys = keys_str.split('.')
        config = self
        for key in keys:
            if config.has(key):
                config = config.get(key)
            else:
                return False
        return True

    def set_deep_value(self, keys_str, value, create_if_missing=False):
        keys = keys_str.split('.')
        config = self
        for key in keys[:-1]:
            if config.has(key):
                config = config.get(key)
            elif create_if_missing:
                new_config = ConfigurationObject()
                config.__setattr__(key, new_config)
                config = new_config
            else:
                raise ValueError('No path for key "%s"' % keys_str)
        config.__setattr__(keys[-1], value)

    def check(self, key):
        """check(key) -> obj

        Returns False if key is absent in object, and returns object
        otherwise.
        """

        return self.has(key) and getattr(self, key)

    def allkeys(self):
        """allkeys() -> list of strings

        Returns all options stored in this object.
        """

        return self.db_config_keys_name_index.keys()

    def keys(self):
        """keys(self) -> list of strings
        Returns all public options stored in this object.
        Public options are keys that do not start with a _
        """
        return [k for k in self.db_config_keys_name_index
                if not k.startswith('_')]

# def default():
#     """ default() -> ConfigurationObject
#     Returns the default configuration of VisTrails

#     """

#     base_dir = {
#         'abstractionsDirectory': os.path.join("$DOT_VISTRAILS",
#                                               "subworkflows"),
#         'alwaysShowDebugPopup': False,
#         'autoConnect': True,
#         'autosave': True,
#         'dataDirectory': (None, str),
#         'dbDefault': False,
# #        'debugSignals': False,
#         'defaultFileType':system.vistrails_default_file_type(),
#         'detachHistoryView': False,
#         'dotVistrails': system.default_dot_vistrails(),
#         'enablePackagesSilently': False,
#         'errorOnConnectionTypeerror': False,
#         'errorOnVariantTypeerror': True,
#         'executeWorkflows': False,
#         'fileDirectory': (None, str),
#         'fixedSpreadsheetCells': False,
# #        'evolutionGraph': (None, str),
#         'installBundles': True,
#         'installBundlesWithPip': False,
#         'interactiveMode': True,
#         'logFile': os.path.join("$DOT_VISTRAILS", "vistrails.log"),
#         'logger': default_logger(),
#         'maxMemory': (None, int),
#         'maximizeWindows': False,
#         'maxRecentVistrails': 5,
#         'migrateTags': False,
#         'minMemory': (None, int),
#         'multiHeads': False,
#         'nologger': False,
#         'packageDirectory': (None, str),
#         'pythonPrompt': False,
#         'recentVistrailList': (None, str),
#         'repositoryLocalPath': (None, str),
#         'repositoryHTTPURL': "http://www.vistrails.org/packages",
#         'reviewMode': False,
#         'rootDirectory': (None, str),
#         'runningJobsList': (None, str),
#         'shell': default_shell(),
#         'showScrollbars': True,
#         'showMovies': True,
#         'showSplash': True,
#         'showSpreadsheetOnly': False,
#         'singleInstance': True,
#         'spreadsheetDumpCells': (None, str),
#         'spreadsheetDumpPDF': False,
#         'staticRegistry': (None, str),
#         'stopOnError': True,
#         'temporaryDirectory': (None, str),
#         'thumbs': default_thumbs(),
#         'upgradeOn': True,
#         'upgradeDelay': True,
#         'upgradeModuleFailPrompt': True,
#         'useCache': True,
#         'userPackageDirectory': os.path.join("$DOT_VISTRAILS", "userpackages"),
#         'verbosenessLevel': (None, int),
# #        'workflowGraph': (None, str),
# #        'workflowInfo': (None, str),
#         'webRepositoryLogin': (None, str),
#         'webRepositoryURL': "http://www.crowdlabs.org",
#         'isInServerMode': False,
#         }
#     specific_dir = add_specific_config(base_dir)
#     return ConfigurationObject(**specific_dir)

# def default_logger():
#     """default_logger() -> ConfigurationObject
#     Returns the default configuration for the VisTrails logger

#     """
#     logger_dir = {
#         'dbHost': '',
#         'dbName': '',
#         'dbPasswd': '',
#         'dbPort': 0,
#         'dbUser': '',
#         }
#     return ConfigurationObject(**logger_dir)

# def default_shell():
#     """default_shell() -> ConfigurationObject
#     Returns the default configuration for the VisTrails shell
#
#     """
#     if system.systemType == 'Linux':
#         shell_dir = {
#             'font_face': 'Fixed',
#             'font_size': 12,
#             }
#     elif system.systemType in ['Windows', 'Microsoft']:
#         shell_dir = {
#             'font_face': 'Courier New',
#             'font_size': 8,
#             }
#     elif system.systemType == 'Darwin':
#         shell_dir = {
#             'font_face': 'Monaco',
#             'font_size': 12,
#             }
#     else:
#         raise VistrailsInternalError('system type not recognized')
#     return ConfigurationObject(**shell_dir)

# def default_thumbs():
#     """default_thumbs() -> ConfigurationObject
#     Returns the default configuration for VisTrails Pipelines Thumbnails
#     """
#     thumbs_dir = {
#                   'autoSave': True,
#                   'cacheDirectory': os.path.join("$DOT_VISTRAILS", "thumbs"),
#                   'cacheSize': 20,
#                   'mouseHover': False,
#                   'tagsOnly': False,
#                 }
#     return ConfigurationObject(**thumbs_dir)

def add_specific_config(base_dir):
    """add_specific_config() -> dict

    Returns a dict with other specific configuration to the current
    platform added to base_dir

    """
    newdir = dict(base_dir)
    if system.systemType == 'Darwin':
        newdir['useMacBrushedMetalStyle'] = True

    return newdir

def get_vistrails_persistent_configuration():
    """get_vistrails_persistent_configuration() -> ConfigurationObject or None
    Returns the persistent configuration of the application. It returns None if
    configuration was not found (when running as a bogus application
    for example.
    Notice that this function should be use only to write configurations to
    the user's startup.xml file. Otherwise, use get_vistrails_configuration  or
    get_vistrails_temp_configuration.

    """
    from vistrails.core.application import get_vistrails_application
    app = get_vistrails_application()
    if hasattr(app, 'configuration'):
        return app.configuration
    else:
        return None

def get_vistrails_temp_configuration():
    """get_vistrails_temp_configuration() -> ConfigurationObject or None
    Returns the temp configuration of the application. It returns None if
    configuration was not found (when running as a bogus application
    for example. The temp configuration is the one that is used just for the
    current session and is not persistent. To make changes persistent,
    use get_vistrails_persistent_configuration() instead.

    """
    from vistrails.core.application import get_vistrails_application
    app = get_vistrails_application()
    if hasattr(app, 'temp_configuration'):
        return app.temp_configuration
    else:
        return None

get_vistrails_configuration = get_vistrails_temp_configuration

import os
import tempfile
import unittest

class TestConfiguration(unittest.TestCase):
    def test_config(self):
        conf = ConfigurationObject(a="blah", b=3.45, c=1, d=True)
        self.assertEqual(conf.a, "blah")
        self.assertAlmostEqual(conf.b, 3.45)
        self.assertEqual(conf.c, 1)
        self.assertEqual(conf.d, True)

    def test_default(self):
        conf = default()
        self.assertEqual(conf.showWindow, True)
        self.assertEqual(conf.maxRecentVistrails, 5)

    def test_has(self):
        conf = default()
        self.assertTrue(conf.has("showWindow"))
        self.assertFalse(conf.has("reallyDoesNotExist"))

    def test_check(self):
        conf = default()
        self.assertTrue(conf.check("showWindow"))
        self.assertFalse(conf.check("showDebugPopups"))
        self.assertFalse(conf.check("thumbs.mouseHover"))

    def test_update(self):
        conf1 = default()
        conf2 = ConfigurationObject(showDebugPopups=True,
                                    logDir="/tmp",
                                    thumbs=ConfigurationObject(
                                        autoSave=True,
                                        cacheDir="/tmp",
                                        cacheSize=10,
                                        mouseHover=True,
                                        tagsOnly=False))

        conf1.update(conf2)
        self.assertTrue(conf1.showDebugPopups)
        self.assertEqual(conf1.logDir, "/tmp")
        self.assertEqual(conf1.thumbs.mouseHover, True)

        conf2.showWindow = False
        self.assertTrue(conf1.showWindow)

    def test_type_mismatch(self):
        conf = default()
        with self.assertRaises(TypeError):
            conf.showWindow = 1

        # allowing this now
        # with self.assertRaises(AttributeError):
        #     conf.reallyDoesNotExist = True

    def test_serialize(self):
        from vistrails.db.persistence import DAOList
        conf1 = default()
        (fd, fname) = tempfile.mkstemp()
        os.close(fd)
        try:
            dao = DAOList()
            dao.save_to_xml(conf1, fname, {})
            conf2 = dao.open_from_xml(fname, ConfigurationObject.vtType)
            ConfigurationObject.convert(conf2)
        finally:
            os.unlink(fname)

        self.assertEqual(conf1, conf2)

    def test_copy(self):
        conf1 = default()
        conf2 = copy.copy(conf1)
        self.assertEqual(conf1, conf2)
        self.assertItemsEqual(conf1._unset_keys.keys(),
                              conf2._unset_keys.keys())

    def test_parser(self):
        if sys.version_info < (2, 7):
            self.skipTest("argparse on Python 2.6: bug 10680")
        p = build_command_line_parser(base_config)
        with self.assertRaises(SystemExit) as e:
            p.parse_args(["-h"])
        self.assertEqual(e.exception.code, 0)
        with self.assertRaises(SystemExit) as e:
            p.parse_args(["--db-default", "--no-db-default"])
        self.assertEqual(e.exception.code, 2)

    def test_parse_into_config(self):
        p = build_command_line_parser(base_config)
        config = default()
        self.assertFalse(config.dbDefault)
        p.parse_args(args=["--db-default", "--dot-vistrails", "/tmp"],
                     namespace=config)
        self.assertTrue(config.dbDefault)
        self.assertEqual(config.dotVistrails, "/tmp")

    def test_parse_output_settings(self):
        p = build_command_line_parser(base_config)
        config = default()
        p.parse_args(args=["-p", "file.series=false"],
                     namespace=config)
        self.assertTrue(config.outputSettings.has("file"))
        self.assertTrue(config.outputSettings.file.has("series"))
        self.assertEqual(config.outputSettings.file.series, "false")

    def test_multiple_params(self):
        p = build_command_line_parser(base_config)
        config = default()
        p.parse_args(args=["-p", "file.series=false",
                           "-p", "file.suffix=.png"],
                     namespace=config)
        self.assertTrue(config.outputSettings.has("file"))
        self.assertTrue(config.outputSettings.file.has("series"))
        self.assertTrue(config.outputSettings.file.has("suffix"))
        self.assertEqual(config.outputSettings.file.series, "false")
        self.assertEqual(config.outputSettings.file.suffix, ".png")

    def test_comma_sep_params(self):
        p = build_command_line_parser(base_config)
        config = default()
        p.parse_args(args=["-p", 'file.series=false,other.separator=","'],
                     namespace=config)
        self.assertTrue(config.outputSettings.has("file"))
        self.assertTrue(config.outputSettings.file.has("series"))
        self.assertEqual(config.outputSettings.file.series, "false")
        self.assertTrue(config.outputSettings.has("other"))
        self.assertTrue(config.outputSettings.other.has("separator"))
        self.assertEqual(config.outputSettings.other.separator, ",")


if __name__ == '__main__':
    unittest.main()

