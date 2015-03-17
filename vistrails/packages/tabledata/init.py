from __future__ import division

from vistrails.core.bundles.pyimport import py_import
from vistrails.core.modules.utils import make_modules_dict
from vistrails.core.packagemanager import get_package_manager
from vistrails.core.upgradeworkflow import UpgradeWorkflowHandler

try:
    py_import('numpy', {
            'pip': 'numpy',
            'linux-debian': 'python-numpy',
            'linux-ubuntu': 'python-numpy',
            'linux-fedora': 'numpy'})
except ImportError: # pragma: no cover
    pass

from .common import _modules as common_modules
from .convert import _modules as convert_modules
from .operations import _modules as operation_modules
from .read import _modules as read_modules
from .write import _modules as write_modules


_modules = [common_modules,
            convert_modules,
            operation_modules,
            read_modules,
            write_modules]

if get_package_manager().has_package( # pragma: no branch
        'org.vistrails.vistrails.spreadsheet'):
    from .viewer import _modules as viewer_modules
    _modules.append(viewer_modules)

_modules = make_modules_dict(*_modules)


def handle_module_upgrade_request(controller, module_id, pipeline):
    old_module = pipeline.modules[module_id]
    if (old_module.name == 'JSONFile' and old_module.version != '0.1.5' and
            old_module.namespace == 'read'):
        from vistrails.core.db.action import create_action
        from vistrails.core.modules.module_registry import get_module_registry
        from .read.read_json import JSONObject

        reg = get_module_registry()
        new_desc = reg.get_descriptor(JSONObject)
        new_module = controller.create_module_from_descriptor(
                new_desc,
                old_module.location.x, old_module.location.y)
        actions = UpgradeWorkflowHandler.replace_generic(
                controller, pipeline,
                old_module, new_module)

        new_function = controller.create_function(new_module,
                                                  "key_name",
                                                  ["_key"])
        actions.append(create_action([('add', new_function,
                                       'module', new_module.id)]))
        return actions

    module_remap = {
            'read|csv|CSVFile': [
                (None, '0.1.1', 'read|CSVFile', {
                    'src_port_remap': {
                        'self': 'value'},
                })
            ],
            'read|numpy|NumPyArray': [
                (None, '0.1.1', 'read|NumPyArray', {
                    'src_port_remap': {
                        'self': 'value'},
                })
            ],
            'read|CSVFile': [
                ('0.1.1', '0.1.2', None, {
                    'src_port_remap': {
                        'self': 'value'},
                }),
                ('0.1.3', '0.1.5', None, {})
            ],
            'read|NumPyArray': [
                ('0.1.1', '0.1.2', None, {
                    'src_port_remap': {
                        'self': 'value'},
                })
            ],
            'read|ExcelSpreadsheet': [
                ('0.1.1', '0.1.2', None, {
                    'src_port_remap': {
                        'self': 'value'},
                }),
                ('0.1.3', '0.1.4', None, {})
            ],
            'read|JSONFile': [
                (None, '0.1.5', 'read|JSONObject')
            ],
        }

    return UpgradeWorkflowHandler.remap_module(controller,
                                               module_id,
                                               pipeline,
                                               module_remap)
