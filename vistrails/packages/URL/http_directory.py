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

# https://gist.github.com/remram44/6540454

from __future__ import division

from HTMLParser import HTMLParser
import os
import re

from .https_if_available import build_opener


re_url = re.compile(r'^(([a-zA-Z_-]+)://([^/]+))(/.*)?$')

def resolve_link(link, url):
    m = re_url.match(link)
    if m is not None:
        if not m.group(4):
            # http://domain -> http://domain/
            return link + '/'
        else:
            return link
    elif link[0] == '/':
        # /some/path
        murl = re_url.match(url)
        return murl.group(1) + link
    else:
        # relative/path
        if url[-1] == '/':
            return url + link
        else:
            return url + '/' + link


class ListingParser(HTMLParser):
    """Parses an HTML file and build a list of links.

    Links are stored into the 'links' set. They are resolved into absolute
    links.
    """
    def __init__(self, url):
        HTMLParser.__init__(self)

        if url[-1] != '/':
            url += '/'
        self.__url = url
        self.links = set()

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for key, value in attrs:
                if key == 'href':
                    if not value:
                        continue
                    value = resolve_link(value, self.__url)
                    self.links.add(value)
                    break


def download_directory(url, target, insecure=False):
    def mkdir():
        if not mkdir.done:
            try:
                os.mkdir(target)
            except OSError:
                pass
            mkdir.done = True
    mkdir.done = False

    opener = build_opener(insecure=insecure)
    response = opener.open(url)

    if response.info().type == 'text/html':
        contents = response.read()

        parser = ListingParser(url)
        parser.feed(contents)
        for link in parser.links:
            link = resolve_link(link, url)
            if link[-1] == '/':
                link = link[:-1]
            if not link.startswith(url):
                continue
            name = link.rsplit('/', 1)[1]
            if '?' in name:
                continue
            mkdir()
            download_directory(link, os.path.join(target, name), insecure)
        if not mkdir.done:
            # We didn't find anything to write inside this directory
            # Maybe it's a HTML file?
            if url[-1] != '/':
                end = target[-5:].lower()
                if not (end.endswith('.htm') or end.endswith('.html')):
                    target = target + '.html'
                with open(target, 'wb') as fp:
                    fp.write(contents)
    else:
        buffer_size = 4096
        with open(target, 'wb') as fp:
            chunk = response.read(buffer_size)
            while chunk:
                fp.write(chunk)
                chunk = response.read(buffer_size)


###############################################################################

import unittest


class TestLinkResolution(unittest.TestCase):
    def test_absolute_link(self):
        self.assertEqual(
                resolve_link('http://website.org/p/test.txt',
                             'http://some/other/url'),
                'http://website.org/p/test.txt')
        self.assertEqual(
                resolve_link('http://website.org',
                             'http://some/other/url'),
                'http://website.org/')

    def test_absolute_path(self):
        self.assertEqual(
                resolve_link('/p/test.txt', 'http://some/url'),
                'http://some/p/test.txt')
        self.assertEqual(
                resolve_link('/p/test.txt', 'http://some/url/'),
                'http://some/p/test.txt')
        self.assertEqual(
                resolve_link('/p/test.txt', 'http://site'),
                'http://site/p/test.txt')
        self.assertEqual(
                resolve_link('/p/test.txt', 'http://site/'),
                'http://site/p/test.txt')

    def test_relative_path(self):
        self.assertEqual(
                resolve_link('some/file', 'http://site/folder'),
                'http://site/folder/some/file')
        self.assertEqual(
                resolve_link('some/file', 'http://site/folder/'),
                'http://site/folder/some/file')
        self.assertEqual(
                resolve_link('some/dir/', 'http://site/folder'),
                'http://site/folder/some/dir/')


class TestParser(unittest.TestCase):
    def test_parse(self):
        parser = ListingParser('http://a.remram.fr/test')
        parser.feed("""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><html><head><title>
Index of /test</title></head><body><h1>Index of /test</h1><table><tr><th>
<img src="/icons/blank.gif" alt="[ICO]"></th><th><a href="?C=N;O=D">Name</a>
</th><th><a href="?C=M;O=A">Last modified</a></th><th><a href="?C=S;O=A">Size
</a></th><th><a href="?C=D;O=A">Description</a></th></tr><tr><th colspan="5">
<hr></th></tr><tr><td valign="top"><img src="/icons/back.gif" alt="[DIR]"></td>
<td><a href="/">Parent Directory</a></td><td>&nbsp;</td><td align="right">  - 
</td><td>&nbsp;</td></tr><tr><td valign="top">
<img src="/icons/unknown.gif" alt="[   ]"></td><td><a href="a">a</a></td>
<td align="right">11-Sep-2013 15:46  </td><td align="right">  3 </td><td>&nbsp;
</td></tr><tr><td valign="top"><img src="/icons/unknown.gif" alt="[   ]"></td>
<td><a href="/bb">bb</a></td><td align="right">11-Sep-2013 15:46  </td>
<td align="right">  3 </td><td>&nbsp;</td></tr><tr><td valign="top">
<img src="/icons/folder.gif" alt="[DIR]"></td><td><a href="/cc/">cc/</a></td>
<td align="right">11-Sep-2013 15:46  </td><td align="right">  - </td><td>&nbsp;
</td></tr><tr><td valign="top"><img src="/icons/folder.gif" alt="[DIR]"></td>
<td><a href="http://a.remram.fr/dd">dd/</a></td><td align="right">
11-Sep-2013 15:46  </td><td align="right">  - </td><td>&nbsp;</td></tr><tr>
<th colspan="5"><hr></th></tr></table></body></html>
        """)
        links = set(l for l in parser.links if '?' not in l)
        self.assertEqual(links, set([
                'http://a.remram.fr/',
                'http://a.remram.fr/test/a',
                'http://a.remram.fr/bb',
                'http://a.remram.fr/cc/',
                'http://a.remram.fr/dd',
        ]))
