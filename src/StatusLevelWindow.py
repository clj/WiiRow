#    WiiRow, a WiiRemote frontend for FrontRow and stuff
#
#    Copyright (C) 2009 Christian L. Jacobsen
#
#    This file is part of WiiRow
#
#    Cloninator is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Cloninator is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Cloninator; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import objc
from objc import YES, NO
from Cocoa import *

# See: http://developer.apple.com/samplecode/RoundTransparentWindow/
# and: http://cocoadevcentral.com/articles/000028.php
# and: http://developer.apple.com/samplecode/FunkyOverlayWindow/listing7.html

class StatusLevelWindow(NSWindow):
    def initWithContentRect_styleMask_backing_defer_(
            self, contentRect, aStyle, bufferingType, deferFlag):
        # NSBorderlessWindowMask avoids title bar
        fullscreen = NSScreen.mainScreen().frame()
        self = super(StatusLevelWindow, self).\
            initWithContentRect_styleMask_backing_defer_(
                    fullscreen, 
                    NSBorderlessWindowMask, 
                    NSBackingStoreBuffered,
                    NO)
        # No shadow
        self.setHasShadow_(NO)
        # Put ourselves towards the front of all windows on screen
        self.setLevel_(NSStatusWindowLevel)
        # Ignore mouse events so that they are passed onto other apps
        self.setIgnoresMouseEvents_(YES)
        return self
    def canBecomeKeyWindow(self):
        return NO
