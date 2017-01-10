import AppKit
import webbrowser
import logging
import platform
from twisted.internet import reactor

from lbrynet.lbrynet_daemon import DaemonControl
from lbrynet import analytics
from lbrynet import conf


if platform.mac_ver()[0] >= "10.10":
    from LBRYNotify import LBRYNotify


log = logging.getLogger(__name__)


class LBRYDaemonApp(AppKit.NSApplication):
    def finishLaunching(self):
        self.connection = False
        statusbar = AppKit.NSStatusBar.systemStatusBar()
        self.statusitem = statusbar.statusItemWithLength_(AppKit.NSVariableStatusItemLength)
        self.icon = AppKit.NSImage.alloc().initByReferencingFile_(conf.settings.ICON_PATH)
        self.icon.setScalesWhenResized_(True)
        self.icon.setSize_((20, 20))
        self.statusitem.setImage_(self.icon)
        self.menubarMenu = AppKit.NSMenu.alloc().init()
        self.open = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Open", "openui:", "")
        self.menubarMenu.addItem_(self.open)
        self.quit = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Quit", "applicationShouldTerminate:", "")
        self.menubarMenu.addItem_(self.quit)
        self.statusitem.setMenu_(self.menubarMenu)
        self.statusitem.setToolTip_(conf.settings.APP_NAME)

        notify("Starting LBRY")

        DaemonControl.start_server_and_listen(
            launchui=True, use_auth=False,
            analytics_manager=analytics.Manager.new_instance()
        )

    def openui_(self, sender):
        webbrowser.open(conf.settings.UI_ADDRESS)

    # this code is from the example
    # https://pythonhosted.org/pyobjc/examples/Cocoa/Twisted/WebServicesTool/index.html
    def applicationShouldTerminate_(self, sender):
        if reactor.running:
            log.info('Stopping twisted event loop')
            notify("Goodbye!")
            reactor.stop()
            return False
        return True


def notify(msg):
    if platform.mac_ver()[0] >= "10.10":
        try:
            LBRYNotify(msg)
        except AttributeError:
            # when running app source
            print msg