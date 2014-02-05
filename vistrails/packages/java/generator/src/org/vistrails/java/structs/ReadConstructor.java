package org.vistrails.java.structs;

import java.util.Collections;
import java.util.List;

import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamWriter;

import org.vistrails.java.XMLSerializable;

public class ReadConstructor implements XMLSerializable {

    public final List<ReadParam> parameters;

    public ReadConstructor(List<ReadParam> readParams)
    {
        this.parameters = Collections.unmodifiableList(readParams);
    }

    @Override
    public void write_xml(XMLStreamWriter out) throws XMLStreamException
    {
        out.writeStartElement("Constructor");
        for(ReadParam param : parameters)
            param.write_xml(out);
        out.writeEndElement();
    }

}
