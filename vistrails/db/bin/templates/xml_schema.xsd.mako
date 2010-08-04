<%
def writeElement(prop):
    if prop.isReference():
        if prop.getName() == prop.getReferencedObject().getName():
            return '<xs:element ref="%s" minOccurs="%s" maxOccurs="%s"/>' % \
                (prop.getName(), prop.getMinOccurs(), prop.getMaxOccurs())
        else:
            return ('<xs:element name="%s" ref="%s" minOccurs="%s" ' + \
                        'maxOccurs="%s"/>') % \
                        (prop.getName(), prop.getReferencedObject().getName(), 
                         prop.getMinOccurs(), prop.getMaxOccurs())

    return '<xs:element name="%s" minOccurs="%s" maxOccurs="%s"/>' % \
        (prop.getName(), prop.getMinOccurs(), prop.getMaxOccurs())
%> \\
<%text><!--########################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
#########################################################################-->
</%text>
<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" elementFormDefault="qualified" attributeFormDefault="unqualified">
  % for obj in objs:
  <${obj.getNodeType()} name="${obj.getName()}">
    % if len(obj.getXMLElements()) + len(obj.getXMLAttributes()) + \
	len(obj.getXMLChoices()) > 0:
    <xs:complexType>
      % if len(obj.getXMLElements()) > 0:
      <xs:sequence>
	% for prop in obj.getXMLElements():
        ${writeElement(prop)}
        % endfor
	% for choice in obj.getXMLChoices():
        <xs:choice>
          % for prop in choice.getXMLProperties():
          % if prop.hasSpec() and not prop.isInferred():
          % if prop.getNodeType() == 'xs:attribute':
          <xs:attribute name="${prop.getName()}" \
              type="${prop.getAttributeType()}"${prop.getAttributeUseText()}/>
          % elif prop.getNodeType() == 'xs:element':
          ${writeElement(prop)}
	  % endif
	  % endif
	  % endfor
        </xs:choice>
	% endfor
      </xs:sequence>
      % else:
      % for choice in obj.getXMLChoices():
      <xs:choice>
        % for prop in choice.getXMLProperties():
        % if prop.hasSpec() and not prop.isInferred():
        % if prop.getNodeType() == 'xs:attribute':
        <xs:attribute name="${prop.getName()}" \
           type="${prop.getAttributeType()}"${prop.getAttributeUseText()}/>
        % elif prop.getNodeType() == 'xs:element':
        ${writeElement(prop)}
        % endif
        % endif
        % endfor
      </xs:choice>
      % endfor
      % endif
      % for prop in obj.getXMLAttributes():
      <xs:attribute name="${prop.getName()}" \
         type="${prop.getAttributeType()}"${prop.getAttributeUseText()}/>
      % endfor
    </xs:complexType>
    % endif
  </${obj.getNodeType()}>
  % endfor
</xs:schema>
