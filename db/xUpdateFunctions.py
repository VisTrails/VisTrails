#Author: Mayank Maheshwary

from xml.dom import minidom
from accessEXist import eXist_Connector

#connector = eXist_Connector("admin", "")

class UpdateFunctions(object):
    """Access class for eXist"""

    def __init__(self, server, user, passwd):
        self.connector = eXist_Connector(server, user, passwd)
     
    # Add a specific action to the file in DB
    def addAction(self, source, documentName):

        #actionStr = """<?xml version="1.0" ?>
        #<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
        #<xupdate:append select="document("/db/corie.xml")/visTrail">
        #<xupdate:element name="action">
        #<xupdate:attribute name="date">""" + str(source[0]) + """</xupdate:attribute>
        #<xupdate:attribute name="note">""" + str(source[1]) + """</xupdate:attribute>
        #<xupdate:attribute name="parent">""" + str(source[2]) + """</xupdate:attribute>
        #<xupdate:attribute name="time">""" + str(source[3]) + """</xupdate:attribute>
        #<xupdate:attribute name="user">""" + str(source[4]) + """</xupdate:attribute>
        #<xupdate:attribute name="what">""" + str(source[5]) + """</xupdate:attribute>
        #</xupdate:element>
        #</xupdate:append>
        #</xupdate:modifications>"""
        xquery = """update insert <action date=\"""" + str(source[0]) + """\" note=\"""" + str(source[1]) + """\" parent=\"""" + str(source[2]) + """\" time=\"""" + str(source[3]) + """\" user=\"""" + str(source[4]) + """\" what=\"""" + str(source[5]) + """\"/> into document(\"""" + documentName + """\")//visTrail"""
                
        #print actionStr
        self.connector.execute_query(xquery)
        #url = connector.construct_org_path(application=documentName)
        #print url
        #extra_headers={'content-type':'text/xml'}
        #response = connector.http_request(url=url, method="POST", body=actionStr, extra_headers=extra_headers)
        #if response.status != 200:
        #    print response.status

        #f = file("xupdate.xml", "w")
        #f.write(actionStr)
        #f.close()

    # Add multiple actions to the file in DB
    def addActions(self, source, documentName):

        xquery = """update insert """ + source + """into document(\'""" + documentName + """\')//visTrail"""
        self.connector.execute_query(xquery)

    # Create a new document in Vistrails with the <visTrail /> tag
    def createNewDoc(self, fileName):

        #file = str(user) + str(date) + '.xml'
        file = str(fileName)
        #file = 'blah'
        dom = minidom.getDOMImplementation()

        newDoc = dom.createDocument(None, "visTrail", None)
        top_element = newDoc.documentElement
        #f = open(file, 'w')
        #f.write(top_element.toprettyxml())
        #f.close()
        #f = open(file, 'r')
        #print "reading file %s ..." % file
        #xml = f.read()
        #f.close()

        #connector = sample.eXist_Connector()

        self.connector.put_file(top_element.toprettyxml(), file)

        #xquery = """update insert <action date="12/11/1982" note = "blah" user="noone"></action> into document("/db/corie.xml")//visTrail/action[@time=112]"""
        #print xquery
        #result = connector.execute_query(xquery)
        #print result

    # Create a new user
    def createUser(self, username, passwd, group, home=None):
        self.connector.create_user(username, passwd, group, home)
        
    # Rename a document
    def renameDoc(self, originalDoc, newDoc):
        self.connector.move_file(originalDoc, newDoc)

    # Return True if the document exists
    def docExists(self, docName):
	result = self.connector.file_exists(application=docName)
        return result

    # Get a document as a string
    def getDocString(self, docName):
        result = self.connector.get_file_as_string(name=docName, prettyPrint=1)
        return result

    # Get the document as a file object
    def getDocData(self, docName):
        result = self.connector.get_file(name=docName, parameters={'indent':'yes'})
        return result

    # Get the document as a DOM
    def getDom(self, docName):
        result = self.getDocString(docName)
        resultDom = minidom.parseString(result)
	return resultDom

    # Put a document to the DB. docName is the full path to document, 
    # docContent is the file object, overwrite specifies whether you want to overwrite or not
    def putDoc(self, docName, docContent, overwrite=None):
	if(overwrite == None):
	    self.connector.put_file(docName, docContent)
	else:
	    self.connector.put_file_overwrite(xmlFile=docContent, overwrite=1, application=docName)
	
    # Get a list of files
    def getListOfFiles(self, folder):
        result = self.connector.list_files(application=folder)
        return result

    # Get a list of folders
    def getListOfFolders(self, folder):
        result = self.connector.list_folders(application=folder)
        return result
    
    # The following functions are not being used at this time, but might be useful in the future, especially for single action updates to the DB
    def addModuleAction(self, source, documentName, actionTime):

        #actionStr = """<?xml version="1.0" ?>
        #<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
        #<xupdate:append select="doc("""+documentName+""")/visTrail/action[@time =""" + actionTime + """]">
        #<xupdate:element name="object">
        #<xupdate:attribute name="cache">""" + source[0] + """</xupdate:attribute>
        #<xupdate:attribute name="id">""" + source[1] + """</xupdate:attribute>
        #<xupdate:attribute name="name">""" + source[2] + """</xupdate:attribute>
        #<xupdate:attribute name="x">""" + source[3] + """</xupdate:attribute>
        #<xupdate:attribute name="y">""" + source[4] + """</xupdate:attribute>
        #</xupdate:element>
        #</xupdate:append>
        #</xupdate:modifications>"""

        xquery = """update insert <object cache=\"""" + str(source[0]) + """\" id=\"""" + str(source[1]) + """\" name=\"""" + str(source[2]) + """\" x=\"""" + str(source[3]) + """\" y=\"""" + str(source[4])+ """\"></object> into document(\"""" + documentName + """\")//visTrail/action[@time=""" + str(actionTime) + """]"""
        #print actionStr
        self.connector.execute_query(xquery)

    def moveModuleAction(self, source, documentName, actionTime):

        #actionStr = """<?xml version="1.0" ?>
        #<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
        #<xupdate:append select="doc("""+documentName+""")/visTrail/action[@time =""" + actionTime + """]">
        #<xupdate:element name="move">
        #<xupdate:attribute name="dx">""" + source[0] + """</xupdate:attribute>
        #<xupdate:attribute name="dy">""" + source[1] + """</xupdate:attribute>
        #<xupdate:attribute name="id">""" + source[2] + """</xupdate:attribute>
        #</xupdate:element>
        #</xupdate:append>
        #</xupdate:modifications>"""

        xquery = """update insert <move dx=\"""" + str(source[0]) + """\" dy=\"""" + str(source[1]) + """\" id=\"""" + str(source[2]) + """\"/> into document(\"""" + documentName + """\")//visTrail/action[@time=""" + str(actionTime) + """]"""

        self.connector.execute_query(xquery)


    def addConnectionAction(self, source, documentName, actionTime, objectOrFilter):

        xquery = """update insert <connect id=\"""" + str(source[0]) + """\"/> into document(\"""" + documentName + """\")//visTrail/action[@time=""" + str(actionTime) + """]"""

        self.connector.execute_query(xquery)

        if (objectOrFilter == "objectInput"):
            #actionStr = """<?xml version="1.0" ?>
            #<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
            #<xupdate:append select="doc("""+documentName+""")/visTrail/action[@time =""" + actionTime + """]">
            #<xupdate:element name="connect">
            #<xupdate:attribute name="id">""" + source[0] + """</xupdate:attribute>
            #<xupdate:element name="objectInput">
            #<xupdate:attribute name="destId">""" + source[1] + """</xupdate:attribute>
            #<xupdate:attribute name="name">""" + source[2] + """</xupdate:attribute>
            #<xupdate:attribute name="sourceId">""" + source[3] + """</xupdate:attribute>
            #</xupdate:element>
            #</xupdate:append>
            #</xupdate:modifications>"""

            xquery = """update insert <objectInput destId=\"""" + str(source[1]) + """\" name=\"""" + str(source[2]) + """\" sourceId=\"""" + str(source[3]) + """\"/> into document(\"""" + documentName + """\")//visTrail/action[@time=""" + str(actionTime) + """]/connect[@id=""" + source[0] + """]"""

            self.connector.execute_query(xquery)

        else:
            #actionStr = """<?xml version="1.0" ?>
            #<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
            #<xupdate:append select="doc("""+documentName+""")/visTrail/action[@time =""" + actionTime + """]">
            #<xupdate:element name="connect">
            #<xupdate:attribute name="id">""" + source[0] + """</xupdate:attribute>
            #<xupdate:element name="filterInput">
            #<xupdate:attribute name="destId">""" + source[1] + """</xupdate:attribute>
            #<xupdate:attribute name="destPort">""" + source[2] + """</xupdate:attribute>
            #<xupdate:attribute name="sourceId">""" + source[3] + """</xupdate:attribute>
            #<xupdate:attribute name="sourcePort">""" + source[4] + """</xupdate:attribute>
            #</xupdate:element>
            #</xupdate:append>
            #</xupdate:modifications>"""

            xquery = """update insert <filterInput destId=\"""" + str(source[1]) + """\" name=\"""" + str(source[2]) + """\" sourceId=\"""" + str(source[3]) + """\"/> into document(\"""" + documentName + """\")//visTrail/action[@time=""" + str(actionTime) + """]/connect[@id=""" + source[0] + """]"""

            self.connector.execute_query(xquery)


    #def changeParameterAction(self, source, documentName, actionTime):

        #actionStr = """<?xml version="1.0" ?>
        #<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
        #<xupdate:append select="doc("""+documentName+""")/visTrail/action[@time =""" + actionTime + """]">
        #<xupdate:element name="set">
        #<xupdate:attribute name="function">""" + source[0] + """</xupdate:attribute>
        #<xupdate:attribute name="functionId">""" + source[1] + """</xupdate:attribute>
        #<xupdate:attribute name="moduleId">""" + source[2] + """</xupdate:attribute>
        #<xupdate:attribute name="parameter">""" + source[3] + """</xupdate:attribute>
        #<xupdate:attribute name="parameterId">""" + source[4] + """</xupdate:attribute>
        #<xupdate:attribute name="type">""" + source[5] + """</xupdate:attribute>
        #<xupdate:attribute name="value">""" + source[6] + """</xupdate:attribute>
        #</xupdate:element>
        #</xupdate:append>
        #</xupdate:modifications>"""

        #xquery = """update insert <set function=\"""" + str(source[0]) + """\" functionId=\"""" + str(source[1]) + """\" moduleId=\"""" + str(source[2]) + """\" parameter=\"""" + str(source[3]) + """\" parameterId=\"""" + str(source[4]) + """\" type=\"""" + str(source[5] + """\" value=\"""" + str(source[6] + """\" /> into document(\"""" + documentName + """\")//visTrail/action[@time=""" + str(actionTime) + """]"""
        #print actionStr
        #self.connector.execute_query(xquery)

    def deleteModuleAction(self, source, documentName, actionTime):

        #actionStr = """<?xml version="1.0" ?>
        #<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
        #<xupdate:append select="doc("""+documentName+""")/visTrail/action[@time =""" + actionTime + """]">
        #<xupdate:element name="module">
        #<xupdate:attribute name="moduleId">""" + source[0] + """</xupdate:attribute>
        #</xupdate:element>
        #</xupdate:append>
        #</xupdate:modifications>"""                                        

        xquery = """update insert <module moduleId=\"""" + str(source[0]) + """\" /> into document(\"""" + documentName + """\")//visTrail/action[@time=""" + str(actionTime) + """]"""

        self.connector.execute_query(xquery)


    def deleteFunctionAction(self, source, documentName, actionTime):

        #actionStr = """<?xml version="1.0" ?>
        #<xupdate:modifications xmlns:xupdate="http://www.xmldb.org/xupdate" version="1.0">
        #<xupdate:append select="doc("""+documentName+""")/visTrail/action[@time =""" + actionTime + """]">
        #<xupdate:element name="function">
        #<xupdate:attribute name="functionId">""" + source[0] + """</xupdate:attribute>
        #<xupdate:attribute name="moduleId">""" + source[1] + """</xupdate:attribute>
        #</xupdate:element>
        #</xupdate:append>
        #</xupdate:modifications>"""

        xquery = """update insert <function functionId=\"""" + str(source[0]) + """\" moduleId=\"""" + str(source[1]) + """\" /> into document(\"""" + documentName + """\")//visTrail/action[@time=""" + str(actionTime) + """]"""

        self.connector.execute_query(xquery)


    def deleteConnectionAction(self, source, documentName, actionTime):

        xquery = """update insert <connection connectionId=\"""" + str(source[0]) + """\" /> into document(\"""" + documentName + """\")//visTrail/action[@time=""" + str(actionTime) + """]"""

        connector.execute_query(xquery)

