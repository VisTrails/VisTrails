##############################################################################
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

"""Configuration variables for controlling specific things in VisTrails.
"""

from __future__ import division

import atexit
import os
import tempfile
import usagestats
import weakref

from vistrails.core import debug
from vistrails.core.system import vistrails_version


usage_report = None


def setup_usage_report():
    """Sets up the usagestats module.
    """
    global usage_report

    # Unpack CA certificate
    fd, certificate_file = tempfile.mkstemp(prefix='vistrails_stats_ca_',
                                            suffix='.pem')
    with open(certificate_file, 'wb') as fp:
        fp.write(_ca_certificate)
    os.close(fd)
    atexit.register(os.remove, certificate_file)

    usage_report = usagestats.Stats(
        '~/.vistrails/usage_stats',
        usagestats.Prompt(
            "\nUploading usage statistics is currently disabled\n"
            "Please help us by providing anonymous usage statistics; "
            "you can enable this\neither from the GUI or by using "
            "--enable-usage-stats\n"
            "If you do not want to see this message again, you can disable "
            "it from the GUI or with --disable-usage-stats\n"
            "Nothing will be uploaded before you opt in.\n"),
        'https://reprozip-stats.poly.edu/',
        version='VisTrails %s' % vistrails_version(),
        unique_user_id=True,
        env_var='VISTRAILS_USAGE_STATS',
        ssl_verify=certificate_file)

    cwd = os.getcwd()
    record_usage(cwd_spaces=b' ' in cwd)
    try:
        cwd.decode('ascii')
    except UnicodeDecodeError:
        record_usage(cwd_ascii=False)
    else:
        record_usage(cwd_ascii=True)


def record_usage(**kwargs):
    """Records some info in the current usage report.
    """
    if usage_report is not None:
        debug.debug("record_usage %r" % (kwargs,))
        usage_report.note(kwargs)


saved_vistrails = weakref.WeakValueDictionary()


def record_vistrail(what, vistrail):
    """Record info about a vistrail we used.
    """
    from vistrails.core.vistrail.controller import VistrailController
    from vistrails.core.vistrail.pipeline import Pipeline
    from vistrails.core.vistrail.vistrail import Vistrail

    if isinstance(vistrail, VistrailController):
        vistrail = vistrail.vistrail

    if what == 'save':
        # Don't report now, but mark it for reporting when it gets closed
        saved_vistrails[id(vistrail)] = vistrail
    elif what == 'close':
        i = id(vistrail)
        if i in saved_vistrails:
            del saved_vistrails[i]
        else:
            return

    if isinstance(vistrail, Vistrail):
        upgrade_from = set()
        upgrade_to = set()
        nb_notes = 0
        nb_paramexplorations = 0
        for annotation in vistrail.annotations:
            if annotation.key == Vistrail.UPGRADE_ANNOTATION:
                upgrade_from.add(annotation.id)
                upgrade_to.add(int(annotation.value))
            elif annotation.key == Vistrail.NOTES_ANNOTATION:
                nb_notes += 1
            elif annotation.key == Vistrail.PARAMEXP_ANNOTATION:
                nb_paramexplorations += 1
        nb_upgrades = upgrade_from - upgrade_to
        usage_report.note(dict(use_vistrail=what,
                               nb_versions=len(vistrail.actionMap),
                               nb_tags=len(vistrail.tags),
                               nb_notes=nb_notes,
                               nb_paramexplorations=nb_paramexplorations,
                               nb_upgrades=nb_upgrades,
                               nb_variables=len(vistrail.vistrail_variables)))
    elif isinstance(vistrail, Pipeline):
        usage_report.note(dict(use_workflow=what,
                               nb_modules=len(vistrail.module_list)))
    else:
        raise TypeError


def submit_usage_report(**kwargs):
    """Submits the current usage report to the usagestats server.
    """
    debug.debug("submit_usage_report %r" % (kwargs,))

    for pkg in ('numpy', 'scipy', 'matplotlib'):
        try:
            pkg_o = __import__(pkg, globals(), locals())
            usage_report.note({pkg: getattr(pkg_o, '__version__', '')})
        except ImportError:
            pass
    try:
        import vtk
        usage_report.note({'vtk': vtk.vtkVersion().GetVTKVersion()})
    except ImportError:
        pass

    usage_report.submit(kwargs,
                        usagestats.OPERATING_SYSTEM,
                        usagestats.SESSION_TIME,
                        usagestats.PYTHON_VERSION)


_ca_certificate = b'''\
-----BEGIN CERTIFICATE-----
MIIDzzCCAregAwIBAgIJAMmlcDnTidBEMA0GCSqGSIb3DQEBCwUAMH4xCzAJBgNV
BAYTAlVTMREwDwYDVQQIDAhOZXcgWW9yazERMA8GA1UEBwwITmV3IFlvcmsxDDAK
BgNVBAoMA05ZVTERMA8GA1UEAwwIUmVwcm9aaXAxKDAmBgkqhkiG9w0BCQEWGXJl
cHJvemlwLWRldkB2Z2MucG9seS5lZHUwHhcNMTQxMTA3MDUxOTA5WhcNMjQxMTA0
MDUxOTA5WjB+MQswCQYDVQQGEwJVUzERMA8GA1UECAwITmV3IFlvcmsxETAPBgNV
BAcMCE5ldyBZb3JrMQwwCgYDVQQKDANOWVUxETAPBgNVBAMMCFJlcHJvWmlwMSgw
JgYJKoZIhvcNAQkBFhlyZXByb3ppcC1kZXZAdmdjLnBvbHkuZWR1MIIBIjANBgkq
hkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1fuTW2snrVji51vGVl9hXAAZbNJ+dxG+
/LOOxZrF2f1RRNy8YWpeCfGbsZqiIEjorBv8lvdd9P+tD3M5sh9L0zQPU9dFvDb+
OOrV0jx59hbK3QcCQju3YFuAtD1lu8TBIPgGEab0eJhLVIX+XU5cYXrfoBmwCpN/
1wXWkUhN91ZVMA0ylATAxTpnoNuMKzfTxT8pyOWajiTskYkKmVBAxgYJQe1YDFA8
fglBNkQuHqP8jgYAniEBCAPZRMMq8WpOtyFx+L9LX9/WcHtAQyDPPb9M81KKgPQq
urtCqtuDKxuqcX9zg4/O8l4nZ50pwaJjbH4kMW/wnLzTPvzZCPtJYQIDAQABo1Aw
TjAdBgNVHQ4EFgQUJjhDDOup4P0cdrAVq1F9ap3yTj8wHwYDVR0jBBgwFoAUJjhD
DOup4P0cdrAVq1F9ap3yTj8wDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOC
AQEAeKpTiy2WYPqevHseTCJDIL44zghDJ9w5JmECOhFgPXR9Hl5Nh9S1j4qHBs4G
cn8d1p2+8tgcJpNAysjuSl4/MM6hQNecW0QVqvJDQGPn33bruMB4DYRT5du1Zpz1
YIKRjGU7Of3CycOCbaT50VZHhEd5GS2Lvg41ngxtsE8JKnvPuim92dnCutD0beV+
4TEvoleIi/K4AZWIaekIyqazd0c7eQjgSclNGgePcdbaxIo0u6tmdTYk3RNzo99t
DCfXxuMMg3wo5pbqG+MvTdECaLwt14zWU259z8JX0BoeVG32kHlt2eUpm5PCfxqc
dYuwZmAXksp0T0cWo0DnjJKRGQ==
-----END CERTIFICATE-----
'''
