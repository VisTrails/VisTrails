#!/usr/bin/env python
###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
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
##  - Neither the name of the New York University nor the names of its
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

""" This will output text with release information ready to be pasted on the
wiki page



"""
from datetime import date
#Release version
VT_VERSION = "2.x"
VT_REVISION = "XXXXXXXXXXXX"
#Sourceforge information
SF_ROOT_URL = "http://downloads.sourceforge.net/project/vistrails/vistrails/"
SF_FOLDER_NAME = "v2.x"
SF_DOWNLOAD_URL = "%s%s"%(SF_ROOT_URL,SF_FOLDER_NAME)
#binaries names
MAC_64_BIN = "vistrails-mac-10.6-intel-%s-%s.dmg"%(VT_VERSION, VT_REVISION)
WIN_32_BIN = "vistrails-setup-%s-%s.zip"%(VT_VERSION, VT_REVISION)
WIN_64_BIN = "vistrails-x64-setup-%s-%s.zip"%(VT_VERSION, VT_REVISION)
ALL_PLAT_SRC = "vistrails-src-%s-%s.tar.gz"%(VT_VERSION, VT_REVISION)
#pdf
USERSGUIDE = "VisTrails.pdf"

#sizes
MAC_64_SIZE = "270.2 MB"
WIN_32_SIZE = "173.9 MB"
WIN_64_SIZE = "234.6 MB"
ALL_PLAT_SIZE = "22.3 MB"
USERSGUIDE_SIZE = "8.9 MB"

def create_text():
    today = date.today().strftime("%Y-%m-%d")
    
    text = """|{{Hl4}} colspan="4" |'''%s build %s (%s)'''  [[known_issues|Known Issues]] {{SFReleaseNotes\
       |link=https://sourceforge.net/projects/vistrails/files/vistrails/%s/README/view}} 
|-
"""%(VT_VERSION, VT_REVISION, today, SF_FOLDER_NAME)

    text += """|
* {{zip
  |link=%s/%s
  |text=%s}}
|%s
|i586
|.zip (32-bit Windows)
|-
"""%(SF_DOWNLOAD_URL, WIN_32_BIN, WIN_32_BIN, WIN_32_SIZE)

    text += """|
* {{zip
  |link=%s/%s
  |text=%s}}
|%s
|i586
|.zip (64-bit Windows)
|-
"""%(SF_DOWNLOAD_URL, WIN_64_BIN, WIN_64_BIN, WIN_64_SIZE)

    text += """|
* {{dmg
  |link=%s/%s
  |text=%s}}
|%s
|Mac OS X 10.6+ x64
|.dmg (Mac bundle)
|-
"""%(SF_DOWNLOAD_URL, MAC_64_BIN, MAC_64_BIN, MAC_64_SIZE)

    text += """|
* {{targz
|link=%s/%s
|text=%s}}
|%s
|all
|Source .tar.gz
|-
"""%(SF_DOWNLOAD_URL, ALL_PLAT_SRC, ALL_PLAT_SRC, ALL_PLAT_SIZE)
    text += """|
* {{Pdf
|link=%s/%s
|text=%s}}
|%s
|all
|.pdf
|-
"""%(SF_DOWNLOAD_URL, USERSGUIDE, USERSGUIDE, USERSGUIDE_SIZE)
    print text

if __name__ == "__main__":
    create_text()
