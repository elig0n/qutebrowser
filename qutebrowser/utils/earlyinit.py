# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.

"""Things which need to be done really early (e.g. before importing Qt).

These functions are supposed to get called in the order they're in this file.
At the very start, we aren't even sure about the Python version used, so we
import more exotic modules later.
"""

import os
import sys


# First we check the version of Python. This code should run fine with python2
# and python3. We don't have Qt available here yet, so we just print an error
# to stdout.
def check_python_version():
    """Check if correct python version is run."""
    if sys.hexversion < 0x03030000:
        print("Fatal error: At least Python 3.3 is required to run "
              "qutebrowser, but {} is installed!".format(
                  '.'.join(map(str, sys.version_info[:3]))))
        sys.exit(1)


# At this point we can be sure we have all python 3.3 features available.
# Now we initialize the faulthandler as early as possible, so we theoretically
# could catch segfaults occuring later.
def init_faulthandler():
    """Enable faulthandler module if available.

    This print a nice traceback on segfauls.
    """
    import faulthandler
    from signal import SIGUSR1
    if sys.stderr is not None:
        # When run with pythonw.exe, sys.stderr can be None:
        # https://docs.python.org/3/library/sys.html#sys.__stderr__
        # If we'd enable faulthandler in that case, we just get a weird
        # exception, so we don't enable faulthandler if we have no stdout.
        #
        # FIXME at the point we have our config/data dirs, we probably should
        # re-enable faulthandler to write to a file. Then we can also display
        # crashes to the user at the next start.
        return
    faulthandler.enable()
    if hasattr(faulthandler, 'register'):
        # If available, we also want a traceback on SIGUSR1.
        faulthandler.register(SIGUSR1)


# Now the faulthandler is enabled we fix the Qt harfbuzzing library, before
# importing any Qt stuff.
def fix_harfbuzz():
    """Fix harfbuzz issues.

    This switches to an older (but more stable) harfbuzz font rendering engine
    instead of using the system wide one.

    This fixes crashes on various sites.
    See https://bugreports.qt-project.org/browse/QTBUG-36099
    """
    if sys.platform.startswith('linux'):
        os.environ['QT_HARFBUZZ'] = 'old'


# At this point we can safely import Qt stuff, but we can't be sure it's
# actually available.
# Here we check if QtCore is available, and if not, print a message to the
# console.
def check_pyqt_core():
    """Check if PyQt core is installed."""
    import textwrap
    import traceback
    try:
        import PyQt5.QtCore  # pylint: disable=unused-variable
    except ImportError:
        print(textwrap.dedent("""
            Fatal error: PyQt5 is required to run qutebrowser but could not
            be imported! Maybe it's not installed?

            On Debian:
                apt-get install python3-pyqt5 python3-pyqt5.qtwebkit

            On Archlinux:
                pacman -S python-pyqt5 qt5-webkit
                or install the qutebrowser package from AUR

            On Windows:
                Use the installer by Riverbank computing or the standalone
                qutebrowser exe.

                http://www.riverbankcomputing.co.uk/software/pyqt/download5

            For other distributions:
                Check your package manager for similiarly named packages.
            """).strip())
        if '--debug' in sys.argv:
            print()
            traceback.print_exc()
        sys.exit(1)


# Now we can be sure QtCore is available, so we can print dialogs on errors, so
# people only using the GUI notice them as well.
def check_pyqt_webkit():
    """Check if PyQt WebKit is installed."""
    from PyQt5.QtWidgets import QApplication, QMessageBox
    import textwrap
    import traceback
    try:
        import PyQt5.QtWebKit  # pylint: disable=unused-variable
    except ImportError:
        app = QApplication(sys.argv)
        msgbox = QMessageBox(QMessageBox.Critical, "qutebrowser: Fatal error!",
                             textwrap.dedent("""
            Fatal error: QtWebKit is required to run qutebrowser but could not
            be imported! Maybe it's not installed?

            On Debian:
                apt-get install python3-pyqt5.qtwebkit

            On Archlinux:
                pacman -S qt5-webkit

            For other distributions:
                Check your package manager for similiarly named packages.
            """).strip())
        if '--debug' in sys.argv:
            print()
            traceback.print_exc()
        msgbox.resize(msgbox.sizeHint())
        msgbox.exec_()
        app.quit()
