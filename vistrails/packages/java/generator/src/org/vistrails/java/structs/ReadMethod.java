package org.vistrails.java.structs;

import java.util.Collections;
import java.util.List;

import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamWriter;

import org.vistrails.java.XMLSerializable;

public class ReadMethod implements XMLSerializable {

    public final String name;
    public final String return_type;
    public final List<ReadParam> parameters;

    public ReadMethod(String name, String return_type,
            List<ReadParam> parameters)
    {
        this.name = name;
        this.return_type = return_type;
        this.parameters = Collections.unmodifiableList(parameters);
    }

    @Override
    public void write_xml(XMLStreamWriter out) throws XMLStreamException
    {
        out.writeStartElement("Method");
        out.writeAttribute("name", name);
        out.writeAttribute("return_type", return_type);
        for(ReadParam param : parameters)
            param.write_xml(out);
        out.writeEndElement();
    }

}
