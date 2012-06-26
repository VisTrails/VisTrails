from java.lang import Runnable
from javax.swing import SwingUtilities, ImageIcon
from java.awt.image import BufferedImage
from java.awt.event import FocusListener, KeyEvent, KeyListener


# We have to pass something implementing Runnable to invokeLater()
# This class is used to wrap a Python method as a Runnable
class PyFuncRunner(Runnable):
    def __init__(self, func):
        self.runner = func;

    def run(self):
        self.runner()


def run_on_edt(func):
    """Runs a Python method or Java Runnable on the Event Dispatch Thread.

    Returns after the function has finished, using
    SwingUtilities.invokeAndWait()
    """
    if not isinstance(func, Runnable):
        func = PyFuncRunner(func)

    if SwingUtilities.isEventDispatchThread():
        func.run()
    else:
        SwingUtilities.invokeAndWait(func)


def resized_icon(image, size):
    if isinstance(image, basestring):
        image = ImageIcon(image)
    if image.getIconWidth() == size.width and image.getIconHeight() == size.height:
        return image

    bi = BufferedImage(
            size.width,
            size.height,
            BufferedImage.TYPE_INT_ARGB)
    g = bi.createGraphics()
    g.scale(float(size.width) / image.getIconWidth(),
            float(size.height) / image.getIconHeight())
    image.paintIcon(None, g, 0, 0)
    g.dispose()

    return ImageIcon(bi)


class InputValidationListener(KeyListener, FocusListener):
    def __init__(self, callback):
        self._callback = callback

    # Implementation of KeyListener

    # @Override
    def keyTyped(self, e):
        pass

    # @Override
    def keyPressed(self, e):
        if e.getKeyCode() == KeyEvent.VK_ENTER:
            self._callback()

    # @Override
    def keyReleased(self, e):
        pass

    # Implementation of FocusListener

    # @Override
    def focusGained(self, e):
        pass

    # @Override
    def focusLost(self, e):
        self._callback()
