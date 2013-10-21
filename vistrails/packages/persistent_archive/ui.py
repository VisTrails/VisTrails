from file_archive.viewer import StoreViewerWindow

from .common import get_default_store


store = get_default_store()
viewer = StoreViewerWindow(store)


def show_viewer():
    viewer.show()
