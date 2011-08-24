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
<%text><!--###############################################################################
##
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
-->
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
