from java.awt import Color, Dialog, Font, Toolkit
from javax.swing import ImageIcon, JDialog, JLabel

from javagui.utils import FontMetricsImpl


# We are not going to use java.awt.SplashScreen here
# It is very inconvenient as it is supposed to get instanced by the JVM which I
# can't trigger here


class JSplashScreen(JDialog):
    font = Font('Dialog', Font.PLAIN, 14)
    fontMetrics = FontMetricsImpl(font)

    def __init__(self, image_path, msg):
        JDialog.__init__(self)
        self.setUndecorated(True)
        self.setAlwaysOnTop(True)
        self.setModalityType(Dialog.ModalityType.APPLICATION_MODAL)

        icon = ImageIcon(image_path)
        w = icon.getIconWidth()
        h = icon.getIconHeight()

        self.getContentPane().setLayout(None)
        self._message = JLabel(msg)
        self.getContentPane().add(self._message)
        self._message.setBounds(
                10, h - 10 - self.fontMetrics.getAscent(),
                w - 10, self.fontMetrics.getHeight())
        self._message.setForeground(Color.white)
        self._image = JLabel(icon)
        self.getContentPane().add(self._image)
        self._image.setBounds(0, 0, w, h)

        screen = Toolkit.getDefaultToolkit().getScreenSize()
        newX = (screen.width - w)/2
        newY = (screen.height - h)/2
        self.setBounds(newX, newY, w, h)

    def _set_message(self, msg):
        self._message.setText(msg)
    message = property(fset=_set_message)

    def finish(self, new_window=None):
        self.setVisible(False)
        if new_window is not None:
            # TODO : focus the new window
            pass
        self.dispose()
