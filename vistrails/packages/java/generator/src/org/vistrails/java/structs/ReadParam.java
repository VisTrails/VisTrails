package org.vistrails.java.structs;

import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamWriter;

import org.vistrails.java.JavaReflect;
import org.vistrails.java.XMLSerializable;

public class ReadParam implements XMLSerializable {

    public final Class<?> type;
    public final String name;

    public ReadParam(Class<?> type, String name)
    {
        this.type = type;
        this.name = name;
    }

    @Override
    public void write_xml(XMLStreamWriter out) throws XMLStreamException
    {
        out.writeStartElement("Parameter");
        out.writeAttribute("name", name);
        out.writeAttribute("type", JavaReflect.format_type(type));
        out.writeEndElement();
    }

}
