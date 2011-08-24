#!/usr/bin/env python
###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
import xmlrpclib
import os
from subprocess import Popen, PIPE
from time import sleep
import smtplib
from email.mime.text import MIMEText
import logging
import logging.handlers

class VistrailWatcher(object):
    """
    A class for watching the status of VisTrail Servers running on a machine
    Servers are pinged and if one down, it is restarted
    """

    def __init__(self, server, email_addresses, root_virtual_display=None):
        self.server = server
        self.root_virtual_display = root_virtual_display

        self.email_addresses = email_addresses
        self.sender = "vistrails_server_watcher@%s" % server

        self.proxies = {}
        self.is_down = {}

        self.logger = self.make_logger("vt_watcher.log")

        # find running VisTrails servers
        proc1 = Popen(["ps", "-eaf"], stdout = PIPE)
        proc2 = Popen(["grep", "vistrails_server"], stdin=proc1.stdout, stdout=PIPE)
        proc3 = Popen(["awk", "{print $13}"], stdin=proc2.stdout, stdout=PIPE)
        out, err = proc3.communicate()

        # get the status servers ports (1 less than normal vt server port)
        out = out.strip().split('\n')
        self.ports = [int(x)-1 for x in out[1:]] # exclude multithreaded inst.

        # create proxies
        for port in self.ports:
            self.proxies[port] = xmlrpclib.ServerProxy("http://%s:%d" % \
                                                       (self.server, port))
            self.is_down[port] = False

    def make_logger(self, filename):
        """ create logger instance with log file rotation """

        logger = logging.getLogger("VistrailsWatcher")
        handler = logging.handlers.RotatingFileHandler(filename,
                                                       maxBytes = 1024*1024,
                                                       backupCount=5)
        handler.setFormatter(logging.Formatter('VT Watcher- %(asctime)s '
                                               '%(levelname)-8s %(message)s'))
        handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        return logger

    def send_email(self, msg):
        """ send email notification that server is down """

        if not self.email_addresses:
            return

        # Create a text/plain message
        msg = MIMEText(msg)

        msg['Subject'] = '%s VisTrails Server Down' % self.server
        msg['From'] = self.sender
        msg['To'] = ', '.join(self.email_addresses)

        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        s = smtplib.SMTP('localhost')
        s.sendmail(self.sender, self.email_addresses, msg.as_string())
        s.quit()

    def restart_instance(self, port):
        """ restart VisTrails Single Tread instance on given port """

        self.logger.info("restarting server on port %s" % port)
        script = os.path.join("/server/vistrails/git/scripts",
                              "start_vistrails_xvfb.sh")

        instance_virtual_display = self.root_virtual_display + \
                self.ports.index(port) + 1

        args = [script,":%s" % instance_virtual_display,
                self.server, str(port+1), '0', '0']
        try:
            Popen(args)
            sleep(20)
        except Exception, e:
            self.logger.error("Couldn't start the instance on display:"
                              "%s port: %s") % (instance_virtual_display, port)
            self.logger.error(str(e))

    def watch(self):
        """ ping Single Thread VisTrail servers every 5 mins """

        if not self.ports:
            self.logger.info("no running instances found")
            print "no running instances found"
            return

        self.logger.info("watching %s" % str(self.ports))
        while 1:
            for port in self.ports:
                try:
                    if not self.proxies[port].try_ping():
                        if not self.is_down[port]:
                            # first time down, send email
                            self.send_email("%s:%d is down" % (self.server, port))
                            self.logger.info("%s:%d is down" % (self.server, port))
                            self.restart_instance(port)
                        self.is_down[port] = True
                    else:
                        if self.is_down[port]:
                            self.logger.info("%s:%d is back up" % (self.server, port))
                        self.is_down[port] = False
                except Exception, e:
                    if not self.is_down[port]:
                        # first time down, send email
                        self.send_email("%s:%d is down" % (self.server, port))
                        self.logger.info("%s:%d is down" % (self.server, port))
                        self.restart_instance(port)
                    self.is_down[port] = True
            sleep(60*5)


if __name__ == '__main__':
    vt_watcher = VistrailWatcher("vis-7.sci.utah.edu", ["phillipmates@gmail.com"], root_virtual_display = 6)
    vt_watcher.watch()
