package org.vistrails.java.structs;

import java.util.Collections;
import java.util.List;

import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamWriter;

import org.vistrails.java.XMLSerializable;

public class ReadMethod implements XMLSerializable {

    public final String name;
    public final boolean is_static;
    public final String return_type;
    public final List<ReadParam> parameters;

    public ReadMethod(String name, boolean is_static, String return_type,
            List<ReadParam> parameters)
    {
        this.name = name;
        this.is_static = is_static;
        this.return_type = return_type;
        this.parameters = Collections.unmodifiableList(parameters);
    }

    @Override
    public void write_xml(XMLStreamWriter out) throws XMLStreamException
    {
        out.writeStartElement("Method");
        out.writeAttribute("name", name);
        out.writeAttribute("static", is_static?"1":"0");
        out.writeAttribute("return_type", return_type);
        for(ReadParam param : parameters)
            param.write_xml(out);
        out.writeEndElement();
    }

}
