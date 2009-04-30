#    Clonioator, a simple rsync based backup UI for OS X
#
#    Copyright (C) 2009 Christian L. Jacobsen
#
#    This file is part of MacroExpander
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

# Load the framework relative to the executable in the .app bundle
import objc
objc.loadBundle("WiiRemote", globals(),
    bundle_path=objc.pathForFramework(
    u'@executable_path@/../../Frameworks/WiiRemote.framework'))

class Enumerate(object):
    def __init__(self, names):
        e = enumerate([s.strip() for s in names.split(',')])
        for number, name in e:
            setattr(self, name, number)
            length = number
        self.length = number + 1

    def __len__(self):
        return self.length


WiiButtonType = Enumerate('''
    WiiRemoteAButton,
    WiiRemoteBButton,
    WiiRemoteOneButton,
    WiiRemoteTwoButton,
    WiiRemoteMinusButton,
    WiiRemoteHomeButton,
    WiiRemotePlusButton,
    WiiRemoteUpButton,
    WiiRemoteDownButton,
    WiiRemoteLeftButton,
    WiiRemoteRightButton,
    
    WiiNunchukZButton,
    WiiNunchukCButton,
    
    WiiClassicControllerXButton,
    WiiClassicControllerYButton,
    WiiClassicControllerAButton,
    WiiClassicControllerBButton,
    WiiClassicControllerLButton,
    WiiClassicControllerRButton,
    WiiClassicControllerZLButton,
    WiiClassicControllerZRButton,
    WiiClassicControllerUpButton,
    WiiClassicControllerDownButton,
    WiiClassicControllerLeftButton,
    WiiClassicControllerRightButton,
    WiiClassicControllerMinusButton,
    WiiClassicControllerHomeButton,
    WiiClassicControllerPlusButton
    ''')

# vim:ts=4:sw=4:et:
