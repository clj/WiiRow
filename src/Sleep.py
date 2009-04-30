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

import ctypes
import IOKitWrapper as IOKit

# io_connect_t IOPMFindPowerManagement( mach_port_t master_device_port );
# IOKit.framework/Versions/A/Headers/pwr_mgt/IOPMLib.h
IOPMFindPowerManagement_t = ctypes.CFUNCTYPE(  
    IOKit.io_connect_t,                 # return value
    IOKit.mach_port_t,                  # master_device_port
    )
IOPMFindPowerManagement_args = ((1, "master_device_port"),) 
IOPMFindPowerManagement = IOPMFindPowerManagement_t(
    ("IOPMFindPowerManagement", IOKit.IOKit),
    IOPMFindPowerManagement_args)
IOPMFindPowerManagement.args     = IOPMFindPowerManagement_args
IOPMFindPowerManagement.name     = "IOPMFindPowerManagement"
IOPMFindPowerManagement.errcheck = IOKit.__raiseOnNullErrCheck

# IOReturn IOPMSleepSystem ( io_connect_t fb );
# IOKit.framework/Versions/A/Headers/pwr_mgt/IOPMLib.h
IOPMSleepSystem_t = ctypes.CFUNCTYPE(  
    IOKit.IOReturn,                  # return value
    IOKit.io_connect_t,              # fb
    )
IOPMSleepSystem_args = ((1, "fb"),) 
IOPMSleepSystem = IOPMSleepSystem_t(
    ("IOPMSleepSystem", IOKit.IOKit),
    IOPMSleepSystem_args)
IOPMSleepSystem.args     = IOPMSleepSystem_args
IOPMSleepSystem.name     = "IOPMSleepSystem"
IOPMSleepSystem.errcheck = IOKit.__raiseOnIOReturnError


def SleepSystem():
    port = IOPMFindPowerManagement(0)
    IOPMSleepSystem(port)
    IOServiceClose(port)
