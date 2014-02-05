package org.vistrails.java.structs;

import java.util.Collections;
import java.util.Map;

import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamWriter;

import org.vistrails.java.XMLSerializable;

public class PackageInfos implements XMLSerializable {

    protected final Map<String, ReadClass> classes;

    public PackageInfos(Map<String, ReadClass> classes)
    {
        this.classes = Collections.unmodifiableMap(classes);
    }

    @Override
    public void write_xml(XMLStreamWriter out) throws XMLStreamException
    {
        out.writeStartElement("JavaPackage");
        for(ReadClass clasz : classes.values())
            clasz.write_xml(out);
        out.writeEndElement();
    }

}
