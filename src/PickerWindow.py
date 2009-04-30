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

class PickerWindow(NSWindow):
    def initWithContentRect_styleMask_backing_defer_(
            self, contentRect, aStyle, bufferingType, deferFlag):
        # NSBorderlessWindowMask avoids title bar
        self = super(PickerWindow, self).\
            initWithContentRect_styleMask_backing_defer_(
                    contentRect,
                    NSBorderlessWindowMask, 
                    NSBackingStoreBuffered,
                    NO)
        self.setBackgroundColor_(NSColor.colorWithDeviceRed_green_blue_alpha_(
            0.0, 0.0, 0.0, 0.7))
        self.setOpaque_(NO)
        # No shadow
        self.setHasShadow_(YES)
        # Put ourselves towards the very front of all windows on screen
        self.setLevel_(NSStatusWindowLevel)
        return self
    def canBecomeKeyWindow(self):
        return YES
