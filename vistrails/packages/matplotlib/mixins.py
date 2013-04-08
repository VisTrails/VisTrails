class MplCorrBaseMixin(object):
    def compute_after():
        if 'usevlines' in kwargs and kwargs['usevlines']:
            output = output + (output[2],)
        else:
            output = output + (None, None)

class MplAcorrMixin(MplCorrBaseMixin):
    pass

class MplXcorrMixin(MplCorrBaseMixin):
    pass

class MplBoxplotMixin(object):
    def compute_after():
        if 'patch_artist' in kwargs and kwargs['patch_artist']:
            output['boxPatches'] = output['boxes']
            output['boxes'] = []
        else:
            output['boxPatches'] = []

class MplContourBaseMixin(object):
    def compute_before():
        if self.hasInputFromPort("N") and self.hasInputFromPort("V"):
            del args[-1]

class MplContourMixin(MplContourBaseMixin):
    def compute_inner():
        contour_set = matplotlib.pyplot.contour(*args, **kwargs)
        output = (contour_set, contour_set.collections)

class MplContourfMixin(MplContourBaseMixin):
    def compute_inner():
        contour_set = matplotlib.pyplot.contourf(*args, **kwargs)
        output = (contour_set, contour_set.collections)

class MplPieMixin(object):
    def compute_after():
        if len(output) < 3:
            output = output + ([],)

class MplAnnotateMixin(object):
    def compute_before():
        if self.hasInputFromPort("fancyArrowProperties"):
            kwargs['arrowprops'] = \
                self.getInputFromPort("fancyArrowProperties").props
        elif self.hasInputFromPort("arrowProperties"):
            kwargs['arrowprops'] = \
                self.getInputFromPort("arrowProperties").props

class MplSpyMixin(object):
    def compute_after():
        if "marker" not in kwargs and "markersize" not in kwargs and \
                not hasattr(kwargs["Z"], 'tocoo'):
            output = (output, None)
        else:
            output = (None, output)

class MplBarMixin(object):
    def compute_before(self):
        if not kwargs.has_key('left'):
            kwargs['left'] = range(len(kwargs['height']))
