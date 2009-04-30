#!/usr/bin/python
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


import os, sys

# PyObjC
import objc
from PyObjCTools import NibClassBuilder, AppHelper
import Foundation
from Foundation import NSSearchPathForDirectoriesInDomains

# If the bundle is an alias bundle, we need to tweak the search path
bundle = Foundation.NSBundle.mainBundle()
bundleInfo = bundle.infoDictionary()
if bundleInfo['PyOptions']['alias']:
    root = os.path.dirname(bundle.bundlePath())
    root = os.path.join(root, '..')
    root = os.path.normpath(root)
    sys.path[0:0] = ['%s/src' % root]

if bundleInfo['PyOptions']['alias']:
    import PyObjCTools.Debugging as d
    d.installVerboseExceptionHandler()


import AppDelegate
import StatusLevelWindow
import PickerWindow

if __name__ == "__main__":
    AppHelper.runEventLoop()

# vim:ts=4:sw=4:et:
