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
import ctypes.util

IOKit = ctypes.cdll.LoadLibrary(ctypes.util.find_library('IOKit'))

#
# Types
#
__darwin_natural_t = ctypes.c_uint# /usr/include/ppc/_types.h:44
natural_t = __darwin_natural_t    # /usr/include/mach/ppc/vm_types.h:87
mach_port_name_t = natural_t      # /usr/include/mach/port.h:93
mach_port_t = mach_port_name_t    # /usr/include/mach/port.h:115
io_object_t = mach_port_t         # /System/Library/Frameworks/IOKit.framework/
                                  #   Versions/A/Headers/IOTypes.h:145
io_connect_t = mach_port_t        # /System/Library/Frameworks/IOKit.framework/
                                  #   Versions/A/Headers/IOTypes.h:151
io_iterator_t = io_object_t       # /System/Library/Frameworks/IOKit.framework/
                                  #   Versions/A/Headers/IOTypes.h:152
io_registry_entry_t = io_object_t # /System/Library/Frameworks/IOKit.framework/
                                  #   Versions/A/Headers/IOTypes.h:153
kern_return_t = ctypes.c_int      # /usr/include/mach/ppc/kern_return.h:65
IOOptionBits  = ctypes.c_uint32   # /System/Library/Frameworks/
                                  #   IOKit.framework/Headers/IOTypes.h:65
IOReturn = kern_return_t          # /System/Library/Frameworks/
                                  #   IOKit.framework/Headers/IOReturn.h:45
class __CFDictionary(ctypes.Structure):
    pass
CFDictionaryRef = \
    ctypes.POINTER(__CFDictionary)# /System/Library/Frameworks/CoreFoundation.
                                  #   framework/Headers/CFDictionary.h:187
CFMutableDictionaryRef = \
    ctypes.POINTER(__CFDictionary)# /System/Library/Frameworks/CoreFoundation.  
                                  #   framework/Headers/CFDictionary.h:193
class __CFAllocator(ctypes.Structure):
    pass
CFAllocatorRef = \
    ctypes.POINTER(__CFAllocator) # /System/Library/Frameworks/CoreFoundation.
                                  #   framework/Headers/CFBase.h:233   
class __CFString(ctypes.Structure):
    pass
CFStringRef = \
    ctypes.POINTER(__CFString) 
class __CFType(ctypes.Structure):
    pass
CFTypeRef = \
    ctypes.POINTER(__CFType)
CFTypeRef = ctypes.c_void_p    
class __CFNumber(ctypes.Structure):
    pass
CFNumberRef = \
    ctypes.POINTER(__CFNumber)
CFNumberType = ctypes.c_int    
Boolean = ctypes.c_ubyte


#
# Constants
#
MACH_PORT_NULL = 0                # /usr/include/mach/port.h:130
#kCFAllocatorDefault = ctypes.cast(IOKit.kCFAllocatorDefault, CFAllocatorRef)
#kCFAllocatorDefault = IOKit.kCFAllocatorDefault
kCFAllocatorDefault = None # FIXME: Get above to work?
kCFNumberSInt64Type = 4

class IOKitError(Exception):
    def __init__(self, result, function, message=None):
        self.result      = result
        self.function    = function
        self.message     = message
    def __str__(self):
        msg = "%s returned %s" % (self.function, self.result)
        if self.message:
            msg += " (" + self.message + ")"
        return msg    


def __returnSingletonOrTupleAndRaiseOnNonZeroErrCheck(res, func, args):
    if res != 0:
        raise IOKitError(res, func.name)
    r = map(lambda x: x[1],
            filter(lambda x: x[0][0] == 2, 
                   zip(func.args, args)))
    if r:
        if len(r) == 1:
            return r[0]
        return tuple(r)
    return None

def __raiseOnNullErrCheck(res, func, args):
    if res == 0 or res == None:
        if True: #isinstance(func.restype, ctypes.POINTER):
            msg = "%s returned NULL" % func.name
        else:
            msg = None
        raise IOKitError(res, func.name, msg)
    return res

def __raiseOnIOReturnError(res, func, args):
    if res != 0:
        # FIXME: There are some ways of interpreting the return code
        raise IOKitError(res, func.name, '%s did not return 0' % func.name)

# kern_return_t IOServiceClose( io_connect_t connect );
# IOKit.framework/Versions/A/Headers/IOKitLib.h
IOServiceClose_t = ctypes.CFUNCTYPE(  
    IOReturn,                  # return value
    io_connect_t,              # connect
    )
IOServiceClose_args = ((1, "connect"),) 
IOServiceClose = IOServiceClose_t(
    ("IOServiceClose", IOKit),
    IOServiceClose_args)
IOServiceClose.args     = IOServiceClose_args
IOServiceClose.name     = "IOServiceClose"
IOServiceClose.errcheck = __raiseOnIOReturnError
