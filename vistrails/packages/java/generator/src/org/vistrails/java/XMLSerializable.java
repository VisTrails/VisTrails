package org.vistrails.java;

import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamWriter;

/**
 * Interface for objects that we serialize to an XML file.
 */
public interface XMLSerializable {

    /**
     * Serializes this object to an XML node in the given stream.
     */
    public void write_xml(XMLStreamWriter out) throws XMLStreamException;

}
