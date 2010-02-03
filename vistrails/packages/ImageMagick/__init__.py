############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
"""ImageMagick package for VisTrails.

This package defines a set of modules that perform some of the
operations exposed by the ImageMagick package.

"""

import core.configuration
import core.requirements

identifier = 'edu.utah.sci.vistrails.imagemagick'
name = 'ImageMagick'
version = '0.9.3'
configuration = core.configuration.ConfigurationObject(quiet=False,
                                                       path=(None, str))
