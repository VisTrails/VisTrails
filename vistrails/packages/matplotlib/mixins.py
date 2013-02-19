class MplBoxplotMixin(object):
    def compute_after():
        if 'patch_artist' in kwargs and kwargs['patch_artist']:
            output['boxPatches'] = output['boxes']
            output['boxes'] = []
        else:
            output['boxPatches'] = []

class MplLinePlotMixin(object):
    def compute_before():
        x = kwargs["x"]
        y = kwargs["y"]
        del kwargs["x"]
        del kwargs["y"]

    def compute_inner():
        lines = matplotlib.pyplot.plot(x, y, **kwargs)

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
