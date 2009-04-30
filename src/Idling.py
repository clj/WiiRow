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

CoreFoundation = \
    ctypes.cdll.LoadLibrary(ctypes.util.find_library('CoreFoundation'))

# /System/Library/Frameworks/IOKit.framework/
#   Versions/A/Headers/IOKitLib:106
IOMasterPort_t = ctypes.CFUNCTYPE(  
    IOKit.kern_return_t,                # return value
    IOKit.mach_port_t,                  # bootstrapPort
    ctypes.POINTER(IOKit.mach_port_t))  # masterPort
IOMasterPort_args = ((1, "bootstrapPort"), (2, "masterPort"))
IOMasterPort = IOMasterPort_t(
    ("IOMasterPort", IOKit.IOKit),
    IOMasterPort_args)
IOMasterPort.args     = IOMasterPort_args
IOMasterPort.name     = "IOMasterPort"
IOMasterPort.errcheck = IOKit.__returnSingletonOrTupleAndRaiseOnNonZeroErrCheck

# /System/Library/Frameworks/IOKit.framework/
#   Versions/A/Headers/IOKitLib:106
IOServiceGetMatchingServices_t = ctypes.CFUNCTYPE(
    IOKit.kern_return_t,                 # return value
    IOKit.mach_port_t,                   # masterPort
    IOKit.CFDictionaryRef,               # matching,
    ctypes.POINTER(IOKit.io_iterator_t)) # existing
IOServiceGetMatchingServices_args = \
        ((1, "masterPort"), (1, "matching"), (2, "existing"))
IOServiceGetMatchingServices = IOServiceGetMatchingServices_t(
    ("IOServiceGetMatchingServices", IOKit.IOKit),
    IOServiceGetMatchingServices_args)
IOServiceGetMatchingServices.args = IOServiceGetMatchingServices_args
IOServiceGetMatchingServices.name = "IOServiceGetMatchingServices"
IOServiceGetMatchingServices.errcheck = \
    IOKit.__returnSingletonOrTupleAndRaiseOnNonZeroErrCheck

# /System/Library/Frameworks/IOKit.framework/
#   Versions/A/Headers/IOKitLib:1042
IOServiceMatching_t = ctypes.CFUNCTYPE(
    IOKit.CFMutableDictionaryRef,        # return value
    ctypes.c_char_p)                     # name   
IOServiceMatching_args = ((1, "name"),)
IOServiceMatching = IOServiceMatching_t(
    ("IOServiceMatching", IOKit.IOKit),
    IOServiceMatching_args)
IOServiceMatching.errcheck = IOKit.__raiseOnNullErrCheck


# /System/Library/Frameworks/IOKit.framework/
#   Versions/A/Headers/IOKitLib:209
IOIteratorNext_t = ctypes.CFUNCTYPE(
    IOKit.io_object_t,                   # return value
    IOKit.io_iterator_t)                 # iterator 
IOIteratorNext_args = ((1, "iterator"),)
IOIteratorNext = IOIteratorNext_t(
        ("IOIteratorNext", IOKit.IOKit),
        IOIteratorNext_args)


# /System/Library/Frameworks/IOKit.framework/
#   Versions/A/Headers/IOKitLib:884
IORegistryEntryCreateCFProperties_t = ctypes.CFUNCTYPE(
    IOKit.kern_return_t,                 # return value     
    IOKit.io_registry_entry_t,           # entry
    ctypes.POINTER(
        IOKit.CFMutableDictionaryRef),   # properties
    IOKit.CFAllocatorRef,                # allocator
    IOKit.IOOptionBits)                  # options
IORegistryEntryCreateCFProperties_args = \
    ((1, "entry"), (2, "properties"), (1, "allocator"), (1, "options"))
IORegistryEntryCreateCFProperties = IORegistryEntryCreateCFProperties_t(
    ("IORegistryEntryCreateCFProperties", IOKit.IOKit),
    IORegistryEntryCreateCFProperties_args)
IORegistryEntryCreateCFProperties.args = IORegistryEntryCreateCFProperties_args
IORegistryEntryCreateCFProperties.name = "IORegistryEntryCreateCFProperties"
IORegistryEntryCreateCFProperties.errcheck = \
    IOKit.__returnSingletonOrTupleAndRaiseOnNonZeroErrCheck

IOObjectRelease_t = ctypes.CFUNCTYPE(
    IOKit.kern_return_t,                 # return value 
    IOKit.io_object_t)                   # object 
IOObjectRelease_args = ((1, "object"),)
IOObjectRelease = IOObjectRelease_t(
    ("IOObjectRelease", IOKit.IOKit),
    IOObjectRelease_args)
IOObjectRelease.args = IOObjectRelease_args
IOObjectRelease.name = "IOObjectRelease"
IOObjectRelease.errcheck = \
    IOKit.__returnSingletonOrTupleAndRaiseOnNonZeroErrCheck    
# /System/Library/Frameworks/CoreFoundation.framework/
#   Headers/CFDictionary.h:515
CFDictionaryGetValue_t = ctypes.CFUNCTYPE(
    ctypes.c_void_p,                    # return value
    IOKit.CFDictionaryRef,              # theDict
    ctypes.c_void_p)                    # key
CFDictionaryGetValue_args = ((1, "theDict"), (1, "key"))
CFDictionaryGetValue = CFDictionaryGetValue_t(
    ("CFDictionaryGetValue", CoreFoundation),
    CFDictionaryGetValue_args)

CFSTR = CoreFoundation.__CFStringMakeConstantString

CFRetain_t = ctypes.CFUNCTYPE(
    IOKit.CFTypeRef,                    # return value
    IOKit.CFTypeRef)                    # cf  
CFRetain_args = ((1, "cf"),)
CFRetain = CFRetain_t(
    ("CFRetain", CoreFoundation),
    CFRetain_args)

CFRelease_t = ctypes.CFUNCTYPE(
    None,                         # return value  
    IOKit.CFTypeRef)                    # cf  
CFRelease_args = ((1, "cf"),)
CFRelease = CFRelease_t(
    ("CFRelease", CoreFoundation),
    CFRelease_args)

CFNumberGetValue_t = ctypes.CFUNCTYPE(
    IOKit.Boolean,                      # return value
    IOKit.CFNumberRef,                  # number
    IOKit.CFNumberType,                 # theType
    ctypes.c_void_p)                    # valuePtr
CFNumberGetValue_args = ((1, "number"), (1, "theType"), (1, "valuePtr"))
__CFNumberGetValue = CFNumberGetValue_t(
    ("CFNumberGetValue", CoreFoundation),
    CFNumberGetValue_args)
def CFNumberGetValue(number, theType):
    if theType == IOKit.kCFNumberSInt64Type:
        val = ctypes.c_int64()
    else:
        raise Exception("The type is not supported")
    ret = __CFNumberGetValue(number, theType, ctypes.byref(val))
    if ret:
        return val.value
    raise Exception("Unable to get value")

# Essentially: http://macenterprise.org/content/view/121/140/
def getIdleTime():
    masterPort = IOMasterPort(IOKit.MACH_PORT_NULL)
    iter = IOServiceGetMatchingServices(
            masterPort,
            IOServiceMatching("IOHIDSystem"))
    curObj = IOIteratorNext(iter)
    properties = \
            IORegistryEntryCreateCFProperties(curObj, IOKit.kCFAllocatorDefault, 0)
    obj = CFDictionaryGetValue(properties, CFSTR("HIDIdleTime"))

    # On Jaguar CFData was returned, on Panther and later CFNumber. I'll assume
    # that this will not get executed on things earlier than Panther
    if obj:
        CFRetain(obj)
        tHandle = CFNumberGetValue(
                ctypes.cast(obj, IOKit.CFNumberRef),
                IOKit.kCFNumberSInt64Type)
        CFRelease(obj)

    IOObjectRelease(curObj)
    IOObjectRelease(iter)
    CFRelease(properties)

    return tHandle

if __name__ == "__main__":
    # Useful btw:
    # http://webkit.org/blog/20/were-hunting-memory-leaks/
    from time import sleep
    import sys
    time = 0
    while True:
        fill = " " * len(str(time))
        time = getIdleTime() >> 30
        sys.stdout.write(
                "User has been idle for %s seconds%s\r" % (time, fill))
        sys.stdout.flush()
        sleep(1.0)


# vim:ts=4:sw=4:et:
