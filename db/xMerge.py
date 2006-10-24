#  Author:  Erik Anderson

""" This class handles all things necessary to cleanly perform a synchronization of vistrails.
All multi-user support for interaction with an eXist database is handled here.  Upon recieving a 
request to synchronize a vistrail with eXist, this class will first lock the database to prevent
changes from being made while the update is taking place.  After locking the database, the associated
XML is fetched from the database and a VisTrail is formed from it for querying and modification.
If a merge is required, it is performed merging versions and their tags.  Note:  Any macros formed
are currently NOT merged between versions.
After the merge step completes, the vistrail formed from the merge is saved to the local files system
as determined by the localpath variable (or if none is supplied, no save will happen) and the vistrail is
then uploaded to the eXist DB.  If this vistrail does not exist in the database or has not been associated
with an XML file in it, a modal GUI will be created to force the user to make this association (or upload it
as a new file)

Usage:
		from xMerge import existMerge
		merger = existMerge()
		merger.synchronize(localVistrail)
		- or -
		merger.synchronize(pathToLocalVistrailXML)

Note:
		In the first version, the parameter passed to the synchronize method is a Vistrail object to be merged with
		whatever it is associated with in the database.  In the second version, the parameter is just the path and 
		filename of an XML file describing a Vistrail.  This allows 'silent' synchronizes without loading a vistrail
		into the builder.
"""

import DBconfig
from xUpdateFunctions import UpdateFunctions
from xml_parser import XMLParser
from vistrail import Vistrail

class existMerge(object):

	def __init__(self):
		self.dbpath = ""
		self.localPath = ""

	#  Set the local vistrail and store it in a member variable.
	def setLocalVistrail(self, vt):
		self.localVT = vt

	#  Set the remote vistrail and store it in a member variable.
	def setRemoteVistrail(self, vt):
		self.remoteVT = vt

	#  Form a Vistrail from a local file and store both the vistrail and the path to it in 
	#  local variables.
	def setLocalVTFromFile(self, filename):
		self.localpath = filename
		p = XMLParser()
		p.openVistrail(self.localpath)
		self.localVT = p.getVistrail()

	#  Set the remote filepath and form a vistrail from this path.  This will fetch the XML from the 
	#  database, form a Vistrail from it, and store that and the path in member variables.
	def setRemoteVTFromRemotePath(self, remotePath):
		import os
		self.dbpath = remotePath
		update = UpdateFunctions(DBconfig.server, DBconfig.username, DBconfig.password)
		content = update.getDocData(self.dbpath)
		#  Write to a file, load the vistrail, then delete the file.
		f = file("dbtmp.xml", "w")
		f.write(content)
		f.close()
		parser = XMLParser()
		parser.openVistrail("dbtmp.xml")
		self.remoteVT = parser.getVistrail()
		os.remove("dbtmp.xml")

	#  Determine if a merge is needed between the local and remote Vistrails.  Returns Boolean
	def needsMerge(self):
		localTS = int(self.localVT.lastDBTime)
		remoteTS = int(self.remoteVT.lastDBTime)
		if localTS == remoteTS:
			return False
		if remoteTS == 0:
			return False
		return True

	#  Currently, this is a 'dummy' method, but once we figure out how to properly 'lock'
	#  the eXist db, it will perform that function
	def lockDB(self):
		return

	#  Same as above, only this will unlock the db.
	def unlockDB(self):
		return

	#  Calculate and return the difference between the local dbtime and the time in the eXist
	#  database
	def getDiff(self):
		rem = int(self.remoteVT.lastDBTime)
		loc = int(self.localVT.lastDBTime)
		return int(rem - loc)

	#  Perform the actual merging between two vistrails.
	def merge(self):
		if not self.needsMerge():
			return self.localVT

		diff = self.getDiff()
		#  We will end up returning the REMOTE copy as the merged copy
		#  this will allow us to make changes only to the local nodes added
		#  It should often be less modifications than trying to change the 
		#  remote copy.
		for timestep, action in self.localVT.actionMap.iteritems():
			timestep = int(timestep)
			self.localVT.lastDBTime = int(self.localVT.lastDBTime)
			if timestep > self.localVT.lastDBTime:
				#  If the action's timestep is bigger than it's lastDBTime
				#  (it has been added since the last synch) we need to 
				#  do some modification
				newtime = int(timestep + diff)
				if self.localVT.actionMap[timestep].parent > self.localVT.lastDBTime:
					#  If the parent of the node is a new node, we must also
					#  modify this value.
					self.localVT.actionMap[timestep].parent = int(action.parent) + diff
				self.localVT.actionMap[timestep].timestep = newtime
				self.remoteVT.addVersion(self.localVT.actionMap[timestep])
		#  At this point, all new actions have been added to the remote vistrail
		#  Now we need to add tags that were added
		for n, number in self.localVT.tagMap.iteritems():
			#  If the tag is associated with a new node, modify it's id.
			if number > self.localVT.lastDBTime:
				id = number + diff
				self.remoteVT.addTag(n, id)
		#  At this point, the self.remoteVT is the merged vistrail.  Return it.
		return self.remoteVT

	def launchExistUpload(self):
		#  A quick - and - dirty GUI to upload a vistrail to the exist db.
		#  I've modified Mayank's old Upload GUI to handle what we need here.  It's not
		#  exceptionally clean, but it's quite functional.
		from existUploadGUI import Ui_UploadFile
		modalDialog = Ui_UploadFile()
		modalDialog.exec_()
		#  The whole point of doing this is to get a database pathstring out, so save it and close.
		self.dbpath = modalDialog.filename

	def uploadVistrail(self, vt):
		import os
		#  Upload the merged vistrail to the eXist db.  This is where we change the 'lastDBTime' field and
		#  file association tag (if necessary) and then re-serialize to save it locally before a full
		#  upload takes place.
		update = UpdateFunctions(DBconfig.server, DBconfig.username, DBconfig.password)
		vt.lastDBTime = vt.getFreshTimestep() - 1
		if len(vt.remoteFilename) == 0:
			vt.remoteFilename = str(self.dbpath)
		#  If we have a local filename, we need to save to that file and then upload.
		if len(self.localPath) == 0:
			self.localPath = "dbtmp.xml"
		#  Save the file.  If the local path has not been set, it will be deleted later.  If it has been, 
		#  then the file is overwritten (as a normal save)
		vt.serialize(self.localPath)
		#  Unfortunately, the way the eXist stuff is set up, we need to have raw XML content to update the
		#  DB with.  This means we have to serialize and then re-read the file.  Is there a better way?
		f = open(self.localPath, "r")
		con = f.read()
		f.close()
		#  If the filename is 'dbtmp.xml' we know that the localPath has not been set.  So remove the file
		if self.localPath == "dbtmp.xml":
			os.remove(self.localPath)

		#  Now we need to upload the content to the db.
		update.putDoc(vt.remoteFilename, con, True)

		#  And we're done so we can unlock the db now.
		self.unlockDB()

	#  Synchronize the given vistrail with the database.
	def synchronize(self, LVT):
		if type(LVT) == type('str'):
			self.setLocalVTFromFile(LVT)
		else:
			self.setLocalVistrail(LVT)
		self.dbpath = self.localVT.remoteFilename
		if len(self.dbpath) == 0:
			#  The remote Filename has not been set.  We need to upload the file.
			self.launchExistUpload()
			#  Simply upload the file to self.dbpath and return the local vistrail.
			self.uploadVistrail(self.localVT)
			return self.localVT
		
		self.setRemoteVTFromRemotePath(self.dbpath)
		mergedVT = self.merge()
		self.uploadVistrail(mergedVT)
		return mergedVT
