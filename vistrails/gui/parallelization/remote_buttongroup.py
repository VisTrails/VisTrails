from PyQt4 import QtCore


_current_button = None


def _button_state_changed(checkbox):
    def inner(state):
        global _current_button
        state = state == QtCore.Qt.Checked
        if state:
            if checkbox != _current_button:
                if _current_button is not None:
                    _current_button.setChecked(False)
                _current_button = checkbox
        elif checkbox == _current_button:
            _current_button = None
    return inner


def add_to_remote_buttongroup(checkbox):
    QtCore.QObject.connect(checkbox, QtCore.SIGNAL('stateChanged(int)'),
                           _button_state_changed(checkbox))
