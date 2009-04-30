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

from objc import *
from Cocoa import *
from Carbon import *
import AppKit
import Foundation

import time
import os

from WiiRemoteFramework import WiiRemote, WiiRemoteDiscovery, WiiButtonType
from EyeTunesFramework import EyeTunes, ETPlaylistCache

import Idling, Sleep

second = 1000000000
IDLE_TIMEOUT = 10 * second

bundle = Foundation.NSBundle.mainBundle()
bundleInfo = bundle.infoDictionary()

if bundleInfo['PyOptions']['alias']:
    def NSDebugLog(str):
        NSLog(str)
else:
    def NSDebugLog(str):
        pass

class LEDAnimator(NSObject):
    def initWithWiiMote_frames_(self, wiimote, frames):
        self = super(LEDAnimator, self).init()
        if type(frames) is list:
            self.frames = self._listIterator(frames)
        else:
            self.frames  = frames
        self.wiimote = wiimote
        self.timer   = None
        return self
    def start(self):
        first = self.frames.next()
        #NSDebugLog(u'start %s' % first)
        self._setLEDs(*first[:4])
        self.timer = NSTimer.\
            scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                    first[4], self, self._nextFrame, None, YES)
    def stop(self):
        self._finish()
    def _nextFrame(self):
        #NSDebugLog(u'_nextFrame')
        try:
            frame = self.frames.next()
            #NSDebugLog(u'  %s' % frame)
            self._setLEDs(*frame[:4])
            self.timer.setFireDate_(NSDate.date().addTimeInterval_(frame[4]))
        except StopIteration:
            self._finish()
    @staticmethod
    def _listIterator(lst):
        for l in lst: yield l
    def _finish(self):
        self.timer.invalidate()
        self._setLEDs(YES, NO, NO, YES)
    def _setLEDs(self, one, two, three, four):
        self.wiimote.setLEDEnabled1_enabled2_enabled3_enabled4_(
                one, two, three, four)


PICKER_MAINMENU   = -1 
PICKER_ITUNESMENU =  0
PICKER_QUARTZMENU =  1

PICKER_MENUITEM_ITUNES = 'iTunes'
PICKER_MENUITEM_QUARTZ = 'Change Background'
PICKER_MENUITEM_HIDE   = 'Hide Background'
PICKER_MENUITEM_SLEEP  = 'Sleep Computer'


PICKER_MENU_MAINMENU = [
        #PICKER_MENUITEM_ITUNES,
        PICKER_MENUITEM_QUARTZ,
        PICKER_MENUITEM_HIDE,
        PICKER_MENUITEM_SLEEP,
        ]

class PickerDataSource(NSObject):
    def init(self):
        self = super(PickerDataSource, self).init()
        self.mainMenu = PICKER_MENU_MAINMENU
        self.quartzCompositions = \
            NSBundle.mainBundle().pathsForResourcesOfType_inDirectory_(
                    'qtz', None)
        self.activeMenu = PICKER_MAINMENU
        self.menu = self.mainMenu
        return self
    def setActiveMenu_(self, menu):
        self.activeMenu = menu
        if menu == PICKER_MAINMENU:
            self.menu = PICKER_MENU_MAINMENU
        elif menu == PICKER_QUARTZMENU:
            self.menu = self.quartzCompositions
        elif menu == PICKER_ITUNESMENU:
            self.menu = EyeTunes.sharedInstance().playlists()
            #self.menu = EyeTunes.sharedInstance().userPlaylists()
            print self.menu
        else:
            raise ArgumentException('Wrong menu ID')
    def tableView_objectValueForTableColumn_row_(
            self, tableView, col, row):
        if self.activeMenu == PICKER_QUARTZMENU:
            return os.path.basename(self.menu[row])[:-4]
        elif self.activeMenu == PICKER_ITUNESMENU:
            return self.menu[row].name()
        else:
            return self.menu[row]
    def numberOfRowsInTableView_(self, tableView):
        return len(self.menu)

class AppDelegate(NSObject):
    theMenu         = IBOutlet()
    theWindow       = IBOutlet()
    #theQCView      = IBOutlet()
    thePickerWindow = IBOutlet()
    thePickerTable  = IBOutlet()

    def closeWiiMoteConnection(self):
        if self.wiimote:
            self.wiimote.closeConnection()
            self.statusItem.setImage_(self.images['notconnected'])

    def resetWiiState(self):
        self.buttonStatus = [0] * len(WiiButtonType)

    def connectWiiMote(self):
        self.resetWiiState()
        self.wiiDiscover.start()
    def connectWiiMote4Timer_(self, theTimer):
        self.connectWiiMote()

    def startDelayedConnect(self, delay=2.0):
        NSTimer.\
            scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                    delay, self, self.connectWiiMote4Timer_, None, NO)

    def cancelForceFeedback4Timer_(self, timer):
        NSDebugLog(u'cancelForceFeedback4Timer_')
        if self.wiimote:
            self.wiimote.setForceFeedbackEnabled_(NO)
    def cancelForceFeedback_(self, seconds):
        NSDebugLog(u'cancelForceFeedback_')
        NSTimer.\
            scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                    seconds, self, self.cancelForceFeedback4Timer_, None, NO)

    def sendKeyboardEvent(self, keyCode, isPressed,
                          shift=False, command=False, 
                          control=False, option=False):
        # For the reason why this is imported here, see:
        # http://www.nabble.com/Leopard-PyObjc---Quartz-td13606880.html
        from Quartz import CGEventCreate, \
                           CGEventCreateKeyboardEvent, \
                           CGEventPost, kCGHIDEventTap
        # This has to happen on tiger due to some bug, see here:
        # http://www.cocoabuilder.com/archive/message/cocoa/2006/10/4/172206
        # However, I htink releasing it from python is bad... as in python
        # would rather do that itself
        #CFRelease(CGEventCreate(NULL))
        delay = 0.02
        if shift:
            event = CGEventCreateKeyboardEvent(NULL, 56, isPressed)
            CGEventPost(kCGHIDEventTap, event);
            time.sleep(delay)
        if command:
            event = CGEventCreateKeyboardEvent(NULL, 55, isPressed)
            CGEventPost(kCGHIDEventTap, event);
            time.sleep(delay)
        if control:
            event = CGEventCreateKeyboardEvent(NULL, 59, isPressed)
            CGEventPost(kCGHIDEventTap, event);
            time.sleep(delay)
        if option:
            event = CGEventCreateKeyboardEvent(NULL, 58, isPressed)
            CGEventPost(kCGHIDEventTap, event);
            time.sleep(delay)
        event = CGEventCreateKeyboardEvent(NULL, keyCode, isPressed)
        CGEventPost(kCGHIDEventTap, event);
        time.sleep(delay)

    def showFullscreenView(self):
        self.fullscreen = True
        self.theQCView.play_(self)
        self.theWindow.orderBack_(self)
        # FIXME: THis does not currently hide the cursor unless
        #        the app is also at the front...
        NSCursor.hide()
        #self.theWindow.orderFront_(self)
    def hideFullscreenView(self):
        self.fullscreen = False
        self.theWindow.orderOut_(self)
        self.theQCView.stop_(self)
        NSCursor.unhide()

    def activatePickerWindow(self):
        self.thePickerWindow.setLevel_(NSStatusWindowLevel)
        app  = NSApplication.sharedApplication()
        app.activateIgnoringOtherApps_(True)
        self.thePickerWindow.center()
        self.thePickerWindow.makeKeyAndOrderFront_(self)
        self.thePickerWindow.makeFirstResponder_(self.thePickerTable)
        self.pickerActive = True

    def deactivatePickerWindow(self):
        self.thePickerWindow.orderOut_(self)
        self.pickerActive = False
    #
    # Application delegate
    #
    def awakeFromNib(self):
        NSDebugLog(u'awakeFromNib')
        # Set up variables
        self.fullscreen      = False
        self.lastKeyPress    = 0
        self.pickerActive    = False
        self.pickerSelection = None
        self.pickerMenuLevel = PICKER_MAINMENU
        # Set up EyeTunes
        self.eyeTunes      = EyeTunes.sharedInstance()
        self.playlistCache = ETPlaylistCache.sharedInstance()
        NSDebugLog('EyeTunes reports iTunes version: ' + 
                   str(self.eyeTunes.versionString()))
        # If we could not get an iTunes version string, don't show the iTunes
        # menu as there will be nothing in it...
        if self.eyeTunes.versionString() == None:
            try:
                PICKER_MENU_MAINMENU.remove(PICKER_MENUITEM_ITUNES)
            except ValueError:
                pass # It is already not there, which is fine
        # Set up the quartz composer view
        import Quartz
        fullscreenFrame = self.theWindow.frame()
        self.theQCView = Quartz.QCView.alloc().initWithFrame_(fullscreenFrame)
        self.theWindow.contentView().addSubview_(self.theQCView)
        quartzComposition = NSBundle.mainBundle().pathForResource_ofType_(
                'Clouds', 'qtz')
        self.theQCView.loadCompositionFromFile_(quartzComposition)
        self.showFullscreenView()
        # Set up the picker window
        self.pickerDataSource = PickerDataSource.alloc().init()
        self.thePickerTable.setDataSource_(self.pickerDataSource)
        # Set up the app launcher watcher
        center = NSWorkspace.sharedWorkspace().notificationCenter()
        center = NSDistributedNotificationCenter.\
              notificationCenterForType_(NSLocalNotificationCenterType)
        center.addObserver_selector_name_object_(
                self,
                self.appLaunched_,
                #NSWorkspaceDidLaunchApplicationNotification,
                None,
                None)
        # Set up the idle timer
        self.lastIdleTime = Idling.getIdleTime()
        self.idleTimer = NSTimer.\
          timerWithTimeInterval_target_selector_userInfo_repeats_(
                  0.5, self, self.idleTick_, None, True)
        NSRunLoop.currentRunLoop().addTimer_forMode_(
                self.idleTimer, Foundation.NSDefaultRunLoopMode)
        NSRunLoop.currentRunLoop().addTimer_forMode_(
                self.idleTimer, AppKit.NSModalPanelRunLoopMode)

    def applicationWillFinishLaunching_(self, sender):
        NSDebugLog(u'applicationWillFinishLaunching_')
    def applicationDidFinishLaunching_(self, sender):
        NSDebugLog(u'applicationDidFinishLaunching_')
        statusItem = NSStatusBar.systemStatusBar().\
            statusItemWithLength_(28.0)
        imagePath = NSBundle.mainBundle().pathForResource_ofType_(
                'notconnected', 'png')
        nc_image = NSImage.alloc().initWithContentsOfFile_(imagePath)
        imagePath = NSBundle.mainBundle().pathForResource_ofType_(
                'connected', 'png')
        c_image = NSImage.alloc().initWithContentsOfFile_(imagePath)
        self.images = {
                'notconnected': nc_image,
                'connected':    c_image
                }

        statusItem.setImage_(nc_image)
        statusItem.setHighlightMode_(TRUE)
        statusItem.setEnabled_(TRUE)
        statusItem.setMenu_(self.theMenu)
        self.statusItem = statusItem

        self.wiimote = None

        NSWorkspace.sharedWorkspace().notificationCenter().\
                 addObserver_selector_name_object_(
                         self, self.receiveSleepNote_,
                         NSWorkspaceWillSleepNotification, NULL)
        # Note: this does not work, as initWithDelegate which it calls is not
        # implemented... :/
        #self.wiiDiscover = WiiRemoteDiscovery.discoveryWithDelegate_(self)
        self.wiiDiscover = WiiRemoteDiscovery.alloc().init()
        self.wiiDiscover.setDelegate_(self)
        self.connectWiiMote()

    def applicationWillTerminate_(self, sender):
        NSDebugLog(u'applicationWillTerminate_')
        if self.wiimote:
            self.wiimote.closeConnection()
    #
    # WiiMote Discovery Delegate
    #
    def willStartWiimoteConnections(self):
        NSDebugLog(u'willStartWiimoteConnections')

    def WiiRemoteDiscovered_(self, wiimote):
        NSDebugLog(u'discovered')
        self.statusItem.setImage_(self.images['connected'])
        self.wiimote = wiimote
        wiimote.setDelegate_(self)
        wiimote.setLEDEnabled1_enabled2_enabled3_enabled4_(
                NO, NO, NO, NO)
        self.timer = NSTimer.\
            scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                    0.9, self, self.doInitSequence, None, NO)

    def doInitSequence(self):
        self.wiimote.setLEDEnabled1_enabled2_enabled3_enabled4_(
                NO, NO, NO, NO)
        def knightRider():
            loops = 5
            while loops:
                for i in range(0, 4):
                    yield [i==0 , i==1, i==2, i==3, 0.1]
                for i in range(2, 0, -1):
                    yield [i==0 , i==1, i==2, i==3, 0.1]
                loops -= 1
        self.animator = LEDAnimator.alloc().\
            initWithWiiMote_frames_(self.wiimote, knightRider())
        self.animator.start()
        # FIXME: I can't seem to turn this off after I've started it...
        #wiimote.setForceFeedbackEnabled_(YES)
        #self.cancelForceFeedback_(2.0)

    @objc.signature('v@:i')
    def WiiRemoteDiscoveryError_(self, code):
        NSDebugLog(u'error')
        self.startDelayedConnect()

    #
    # WiiMote Delegate
    #
    def wiimoteWillSendData(self):
        pass
    def wiimoteDidSendData(self):
        pass

    def wiiRemoteDisconnected_(self, device):
        self.statusItem.setImage_(self.images['notconnected'])
        NSDebugLog(u'wiiRemoteDisconnected_')
        self.startDelayedConnect()

    # See: 
    # http://jimmatthews.wordpress.com/2007/07/12/objcselector-and-objcsignature/
    # and
    # http://developer.apple.com/documentation/developertools/gcc-4.2.1/gcc/Type-encoding.html

    # keyCode or (keyCode, [shift[, command[, control[, option]]]])
    keymap = {
            WiiButtonType.WiiRemoteHomeButton: 
                (53, False, True, False, False),          # Escape key
            WiiButtonType.WiiRemoteUpButton:      126,   # Up key
            WiiButtonType.WiiRemoteDownButton:    125,   # Down key
            WiiButtonType.WiiRemoteLeftButton:    123,   # Left key
            WiiButtonType.WiiRemoteRightButton:   124,   # Right key
            WiiButtonType.WiiRemoteAButton:        36,   # Return key
            WiiButtonType.WiiRemoteBButton:        53,   # Escape key
            WiiButtonType.WiiRemoteMinusButton:  (123, False, True),
            WiiButtonType.WiiRemotePlusButton:   (124, False, True),
            }
    @objc.signature('v@:ii')
    def buttonChanged_isPressed_(self, theType, isPressed):
        NSDebugLog(u'buttonChanged_isPressed_(%d, %d)' % (theType, isPressed))
        self.buttonStatus[theType] = isPressed
        if self.buttonStatus[WiiButtonType.WiiRemoteOneButton] and \
           self.buttonStatus[WiiButtonType.WiiRemoteTwoButton]:
            NSDebugLog(u'closing wii connetion')
            self.closeWiiMoteConnection()
            return
        elif theType == WiiButtonType.WiiRemoteOneButton and \
                isPressed == NO and not self.pickerActive:
            NSDebugLog(u'activating picker window')
            if not self.fullscreen:
                self.showFullscreenView()
            self.activatePickerWindow()
        elif self.pickerActive and isPressed == NO and \
                (theType == WiiButtonType.WiiRemoteAButton or \
                theType == WiiButtonType.WiiRemoteOneButton):
            actMenu = self.pickerDataSource.activeMenu
            idx  = self.pickerSelection
            item = self.pickerSelectedItem
            NSDebugLog(u'Menu selected: idx: %d; item: %s' % (idx, item))
            if actMenu == PICKER_MAINMENU:
                NSDebugLog(u'chaning away from main menu')
                if item == PICKER_MENUITEM_ITUNES:
                    self.pickerDataSource.setActiveMenu_(PICKER_ITUNESMENU)
                    self.thePickerTable.reloadData()
                    self.thePickerTable.selectRowIndexes_byExtendingSelection_(
                            NSIndexSet.indexSetWithIndex_(0), False)
                elif item == PICKER_MENUITEM_QUARTZ:
                    self.pickerDataSource.setActiveMenu_(PICKER_QUARTZMENU)
                    self.thePickerTable.reloadData()
                    self.thePickerTable.selectRowIndexes_byExtendingSelection_(
                            NSIndexSet.indexSetWithIndex_(0), False)
                elif item == PICKER_MENUITEM_HIDE:
                    if self.fullscreen:
                        self.hideFullscreenView()
                    self.deactivatePickerWindow()
                elif item == PICKER_MENUITEM_SLEEP:
                    NSDebugLog(u'closing wii connetion and sleeping system')
                    self.deactivatePickerWindow()
                    self.closeWiiMoteConnection()
                    Sleep.SleepSystem()
            elif actMenu == PICKER_QUARTZMENU:
                NSDebugLog(u'changing quartz composition')
                qc = self.pickerDataSource.quartzCompositions[idx]
                self.theQCView.loadCompositionFromFile_(qc)
                self.deactivatePickerWindow()
        elif self.pickerActive and isPressed == NO and \
                (theType == WiiButtonType.WiiRemoteBButton or \
                theType == WiiButtonType.WiiRemoteTwoButton):
            actMenu = self.pickerDataSource.activeMenu
            if actMenu == PICKER_MAINMENU:
                self.deactivatePickerWindow()
            if actMenu == PICKER_QUARTZMENU or actMenu == PICKER_ITUNESMENU:
                self.pickerDataSource.setActiveMenu_(PICKER_MAINMENU)
                self.thePickerTable.reloadData()
                self.thePickerTable.selectRowIndexes_byExtendingSelection_(
                        NSIndexSet.indexSetWithIndex_(actMenu), False)
        elif self.pickerActive and isPressed == YES and \
                (theType == WiiButtonType.WiiRemoteBButton or \
                 theType == WiiButtonType.WiiRemoteTwoButton or \
                 theType == WiiButtonType.WiiRemoteAButton):
                pass
        else:
            try:
                keyCombo = self.keymap[theType]
                self.lastKeyPress = time.time()
                if type(keyCombo) is tuple:
                    self.sendKeyboardEvent(
                            keyCombo[0], isPressed, *keyCombo[1:])
                else:
                    idleTime = Idling.getIdleTime()
                    self.lastKeyPress = time.time()
                    self.sendKeyboardEvent(keyCombo, isPressed)
            except KeyError:
                pass 

    #
    # System sleep delegate
    #
    # See also: http://developer.apple.com/qa/qa2004/qa1340.html
    def receiveSleepNote_(self, note):
        NSDebugLog(u'receiveSleepNote_')
        if self.wiimote:
            self.wiimote.closeConnection()

    def receiveWakeNote_(self, note):
        NSDebugLog(u'receiveWakeNote')

    #
    # Idle timer functions
    #
    def idleTick_(self, timer):
        idleTime = Idling.getIdleTime()
        now      = time.time()
        #NSDebugLog('idleTick_ - %d (%d)' % (idleTime, self.lastIdleTime))
        if idleTime > IDLE_TIMEOUT and not self.fullscreen:
            NSDebugLog(u'should now show the quartz composer view')
            self.showFullscreenView()
        if self.lastIdleTime > idleTime and self.fullscreen:
            if (now - self.lastKeyPress) < 1.0:
                # We had a recent keystroke from the WiiMote, so pretend that
                # we are still idle, and don't hide the view
                self.lastIdleTime = idleTime
                return
            # This might be better done by seeing if the fullscreen
            # window is getting events? or possibly both to make the detection
            # of events in the case where the window receives them smoother
            NSDebugLog(u'should now hide the quartz composer view')
            self.hideFullscreenView()
            self.deactivatePickerWindow()
        self.lastIdleTime = idleTime

    #
    # Application quit and launch events
    #
    # See: http://developer.apple.com/technotes/tn/tn2050.html#SECNSWORKSPACE
    def appLaunched_(self, note):
        NSDebugLog(u'appLaunched_(%s)' % note.name())
        if note.name() == u'com.apple.FrontRow.FrontRowDidShow' and \
                self.fullscreen:
            NSDebugLog(u'stopping the QCView')
            self.theQCView.stop_(self)
        if note.name() == u'com.apple.FrontRow.FrontRowDidShow' and \
                self.pickerActive:
            self.deactivatePickerWindow()
        if note.name() == u'com.apple.FrontRow.FrontRowWillHide' and \
                self.fullscreen:
            NSDebugLog(u'starting the QCView')
            self.theQCView.start_(self)
    #
    # Picker actions and delgates
    #
    @IBAction
    def selectInPicker_(self, msg):
        NSDebugLog(u'selectInPicker_')
        #NSApplication.sharedApplication().stopModal()

    def tableViewSelectionDidChange_(self, notification):
        NSDebugLog(u'tableViewSelectionDidChange_')
        self.pickerSelection    = self.thePickerTable.selectedRow()
        self.pickerSelectedItem = self.pickerDataSource.\
                tableView_objectValueForTableColumn_row_(
                        None, 0, self.pickerSelection)

