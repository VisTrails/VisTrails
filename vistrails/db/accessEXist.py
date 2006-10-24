"""
TODO: Document this module. The documentation mentions "parts of
the code courtesy Brad Clements". We seriously need to figure out
whether we have permission to use this or if we should just scrap
it."""

#Author: Mayank Maheshwary
#Parts of code courtesy Brad Clements

import urllib2, base64, urllib, urlparse, httplib, xmlrpclib, types

class InstanceObject(object):
#    def __new__(cls, object={}):        
#       return object.__new__(cls, object)
    def __init__(self, **kw):
        self.__dict__.update(kw)

#eXistConstants = InstanceObject(host="http://localhost",
#                                userid="admin",
#                                password="",
#                                base_path="/exist/servlet",
#                                xmlrpc_base_path="/exist/xmlrpc",
#                                port=8080)

class eXist_Connector(object):
    """Access class for eXist"""

    def __init__(self, server, user, passwd):

        self.eXistConstants = InstanceObject(host=server,
                                userid=user,
                                password=passwd,
                                base_path="/exist/servlet",
                                xmlrpc_base_path="/exist/xmlrpc",
                                port=8080)
        
        authinfo = urllib2.HTTPPasswordMgrWithDefaultRealm()
        authinfo.add_password(None,
                              self.eXistConstants.host,
                              self.eXistConstants.userid,
                              self.eXistConstants.password)

        authHandler = urllib2.HTTPBasicAuthHandler(authinfo)

        opener = urllib2.build_opener(authHandler)
        s = self.eXistConstants.userid+':'+ self.eXistConstants.password
        z = base64.encodestring(s)[:-1] # strip trailing 12
        opener.addheaders.append(('Authorization', 'Basic %s' % z))
        self.http_headers = {'Authorization':'Basic %s' % z}
        self.opener = opener

        #print eXistConstants.host[:7]
        #print eXistConstants.host[7:]
        # also create an xmlrpc Server object
        xmlrpc_uri = '%s%s:%s@%s:%d%s' % ( self.eXistConstants.host[:7], # http://
                                           self.eXistConstants.userid,
                                           self.eXistConstants.password,
                                           self.eXistConstants.host[7:],
                                           self.eXistConstants.port,
                                           self.eXistConstants.xmlrpc_base_path )
        try:
            self.xmlrpc = xmlrpclib.Server(xmlrpc_uri)
        except IOError, xmlrpclib.Fault:
            raise

    def generate_db_path(self, application=None):
        """Return the database path component given an application"""
        path = "/db"
        if application:
            path += '/%s' % application

#        if subpath:
#            if isinstance(subpath, (types.ListType, types.TupleType)):
#                subpath = "/".join(subpath)

#            path += '/%s' % subpath

        return path

    def construct_org_path(self, application=None, query=None):

        #print "\nReached here"
        path = self.generate_db_path(application=application)

        url = "%s:%d%s%s" % ( self.eXistConstants.host, self.eXistConstants.port, self.eXistConstants.base_path, path)

        if query:
            data = urllib.urlencode(query)
            url += '?%s' % data

        return url

    def create_user(self, username, passwd, groups, home=None):
        self.xmlrpc.setUser(username, passwd, groups)
        
    def create_folder(self, application=None):
        """Create specified folder"""
        path = self.generate_db_path(application=application)
        self.xmlrpc.createCollection(path)

    def put_file(self, xmlFile, application):
        """Put specified file"""
        path = self.generate_db_path(application=application)
        #print path
        self.xmlrpc.parse(xmlFile, path)
        
    def put_file_overwrite(self, xmlFile, overwrite, application):
        """Put specified file"""
        path = self.generate_db_path(application=application)
        self.xmlrpc.parse(xmlFile, path, overwrite)

    def get_file(self, name, parameters):
        path = self.generate_db_path(application=name)
        r = self.xmlrpc.getDocument(path, parameters)
        return r.data
    
    def get_file_as_string(self, name, prettyPrint):
        path = self.generate_db_path(application=name)
        result = self.xmlrpc.getDocumentAsString(path, prettyPrint)
        return result
    
    def list_folders(self, application=None):
        """Return a list of folder names"""
        path = self.generate_db_path(application=application)
        try:
            r = self.xmlrpc.getCollectionDesc(path)
        except xmlrpclib.Fault, e:
            raise
        return r.get('collections', [])

    def list_files(self, application=None):
        """Return a list of files in the path"""
        path = self.generate_db_path(application=application)
        try:
            r = self.xmlrpc.getCollectionDesc(path)
        except xmlrpclib.Fault, e:
            raise
        return r.get('documents', [])

    def file_exists(self, application):
        path = self.generate_db_path(application=application)
	return self.xmlrpc.hasDocument(path)

    def remove_file(self, name):
        path = self.generate_db_path(application=name)
        self.xmlrpc.remove(path)

    def remove_folder(self, name):
        path = self.generate_db_path(application=name)
        self.xmlrpc.removeCollection(path)

    def execute_query(self, xquery, params={}):
        #"""Returns a reference to the generated result set"""
        #print xquery
        id = self.xmlrpc.executeQuery(xquery, params)
        #print id
        try:
            #res = self.xmlrpc.retrieve(id, 0, {})
            print id
        finally:
            self.xmlrpc.releaseQueryResult(id)
        #return res.data

    def execute(self, application=None):
        """Execute an xquery stored in eXist, return result as string"""
        path = self.generate_db_path(application=application)
        params = {}
        r = self.xmlrpc.execute(path, params)
        try:
            res = self.xmlrpc.retrieve(r['id'], 0, {})
        finally:
            self.xmlrpc.releaseQueryResult(r['id'])
        return res.data

    def move_file(self, application=None, dest_filename=None):
        """Moves specified file"""
        src_path = self.generate_db_path(application=application)
        dest_path = self.generate_db_path()
        self.xmlrpc.moveResource(src_path, dest_path, dest_filename)

    def xupdate_file(self, application=None, xupdate=''):
        path = self.generate_db_path(application=application)
        print path
        #print xupdate
        return self.xmlrpc.xupdateResource(path, xupdate)

    def http_request(self, url, method="GET", body=None, extra_headers=None, extra_args=None):
        """Open an HTTPConnection to server, splits url into parts and adds headers as appropriate
        
        extra_args can be a dictionary """
        
        parts = urlparse.urlparse(url)
        scheme, location, path, parameters, query, fragment = parts
        
        if scheme == 'https':
            http = httplib.HTTPSConnection(location)
        else: http = httplib.HTTPConnection(location)
         
        if extra_args:
            extra_args = urllib.urlencode(extra_args)
            if not query:
                query = extra_args
            else:
                query = "%s&%s" % (query, extra_args)
                
        if query and not body:
            body = query
                    
        if not extra_headers:
            extra_headers = {}

        #print http
        print method
        print location
        print path
        print body
        print extra_headers
        extra_headers.update(self.http_headers)
        #print extra_headers
        http.request(method, path, body, extra_headers )
        #errcode, errmsg, headers = con.getreply()
        return http.getresponse()
