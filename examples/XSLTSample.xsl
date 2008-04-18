<?xml version="1.0"?>
<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="UTF-8"/>
  <xsl:template match="/">
    <html>
      <head><title>XSLT Sample</title></head>
      <body>
         <h2>The Sequence for the Given Gene is: </h2>
                <ul>
                  <li>
        <xsl:value-of select="DDBJXML/SEQUENCE"/> 
                  </li>
                </ul>
<h3>Please fill in the following inputs and Submit:</h3>
<xsl:text disable-output-escaping="yes"><![CDATA[
  <form method="post" action="http://geon01.sdsc.edu:8164/pt2/jsp/ptf.jsp">      
                <b>Program: </b><input name="program" size="20" type="text"><BR>
                <b>Database: </b><input name="database" size="20" type="text"><BR>
                <b>Query: </b><input name="query" size="20" type="text"><BR>
                <INPUT TYPE="submit" VALUE="Make BLAST search using the specified inputs">        
</form>
]]></xsl:text>   
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
