package org.vistrails.java.structs;

import java.util.Collections;
import java.util.List;

import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamWriter;

import org.vistrails.java.XMLSerializable;

public class ReadClass implements XMLSerializable {

    public final String fullname;
    public final String superclass;
    public final boolean is_abstract;
    public final List<ReadMethod> methods;
    public final List<ReadConstructor> constructors;

    public ReadClass(String name, String superclass, boolean is_abstract,
            List<ReadMethod> methods, List<ReadConstructor> constructors)
    {
        this.fullname = name;
        this.superclass = superclass;
        this.is_abstract = is_abstract;
        this.methods = Collections.unmodifiableList(methods);
        this.constructors = Collections.unmodifiableList(constructors);
    }

    @Override
    public void write_xml(XMLStreamWriter out) throws XMLStreamException
    {
        out.writeStartElement("Class");
        out.writeAttribute("name", fullname);
        out.writeAttribute("superclass", (superclass != null)?superclass:"");
        out.writeAttribute("abstract", is_abstract?"1":"0");
        for(ReadConstructor constructor : constructors)
            constructor.write_xml(out);
        for(ReadMethod method : methods)
            method.write_xml(out);
        out.writeEndElement();
    }

}
