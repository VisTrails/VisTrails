""" This will output text with release information ready to be pasted on the
wiki page



"""
from datetime import date
#Release version
VT_VERSION = "2.1.4"
VT_REVISION = "269e4808eca3"

#Sourceforge information
SF_ROOT_URL = "http://downloads.sourceforge.net/project/vistrails/vistrails/"
SF_FOLDER_NAME = "v2.1.1"
SF_DOWNLOAD_URL = "%s%s"%(SF_ROOT_URL,SF_FOLDER_NAME)
#binaries names
MAC_64_BIN = "vistrails-mac-10.6-intel-%s-%s.dmg"%(VT_VERSION, VT_REVISION)
WIN_32_BIN = "vistrails-setup-%s-%s.zip"%(VT_VERSION, VT_REVISION)
WIN_64_BIN = "vistrails-x64-setup-%s-%s.zip"%(VT_VERSION, VT_REVISION)
ALL_PLAT_SRC = "vistrails-src-%s-%s.tar.gz"%(VT_VERSION, VT_REVISION)
#pdf
USERSGUIDE = "VisTrails.pdf"

#sizes
MAC_64_SIZE = "182.3 MB"
WIN_32_SIZE = "125.3 MB"
WIN_64_SIZE = "150 MB"
ALL_PLAT_SIZE = "19.2 MB"
USERSGUIDE_SIZE = "8.7 MB"

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
