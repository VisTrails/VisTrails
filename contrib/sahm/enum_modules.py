from core.modules.basic_modules import String
from enum_widget import build_enum_widget

class MyEnum(String):
    _input_ports = [('value', '(gov.usgs.sahm:MyEnum:DataInput)')]
    _widget_class = build_enum_widget('MyEnumWidget', 
                                      ['abc', 'def', 'ghi'])

    @staticmethod
    def get_widget_class():
        return MyEnum._widget_class
