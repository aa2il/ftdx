#! /usr/bin/python3 -u
################################################################################
#
# FTDX - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Gui to control/configure various rigs.
#
################################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
################################################################################

import sys
from ft_cat2 import *
if sys.version_info[0]==3:
    from tkinter import *
else:
    from Tkinter import *
import time
from pprint import pprint
import argparse
import rig_io.socket_io as socket_io

import pyaudio
import wave
from settings import *

################################################################################

# Was playing with usb audio but this is not complete
class USB_AUDIO:
    def __init__(self,P):

        print("USB_AUDIO Init")

        self.p = pyaudio.PyAudio()

        self.list_devices()
        sys.exit(0)

    def list_devices(self):
        p=self.p
        print("\n---------------------- Record devices -----------------------")
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        print('Num dev=',numdevices)
        for i in range(0, numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                dev = p.get_device_info_by_host_api_device_index(0, i)
                name=dev['name']
                #print(dev)
                #dev = p.get_device_info_by_host_api_device_index(0, i).get('name')
                print("\nInput Device id ", i, " - ",name)

                if name.find('USB Audio CODEC')>=0:
                        print('*** There it is ***',i)
                        index = i
                        print(dev)

        print("-------------------------------------------------------------")

        import alsaaudio

        print(repr('hw:2,0'))
        device = alsaaudio.PCM(card="hw:3.0")
        print(device)
        
################################################################################

# Structure to contain processing params
class PARAMS:
    def __init__(self):

        # Process command line args
        # Can add required=True to anything that is required
        arg_proc = argparse.ArgumentParser()
        arg_proc.add_argument("-rig", help="Connection Type",
                              type=str,default=["ANY"],nargs='+',
                              choices=CONNECTIONS + RIGS)
        arg_proc.add_argument("-port", help="Connection Port",
                              type=int,default=0)
        args = arg_proc.parse_args()

        if len(args.rig)==1:
            if args.rig[0] in RIGS:
                self.rig        = args.rig[0]
                self.connection = 'DIRECT'
            else:
                self.connection = args.rig[0]
        if len(args.rig)>=2:
            self.rig       = args.rig[1]
        else:
            self.rig       = None
        self.PORT          = args.port
        self.host          = 0
        self.baud          = 0
        self.Done          = False

        # Read config file
        self.RCFILE=os.path.expanduser("~/.ftdxrc")
        self.SETTINGS=None
        try:
            with open(self.RCFILE) as json_data_file:
                self.SETTINGS = json.load(json_data_file)
        except:
            print(self.RCFILE,' not found - need call!\n')
            s=SETTINGS(None,self)
            while not self.SETTINGS:
                try:
                    s.win.update()
                except:
                    pass
                time.sleep(.01)
            print('Settings:',self.SETTINGS)

        self.MY_CALL      = self.SETTINGS['MY_CALL']
        #self.LOG_NAME     = os.path.expanduser( args.log.replace('[MYCALL]',self.MY_CALL ) )
        #sys,exit(0)
        
        if True:
            print('args.rig=',args.rig)
            print('connection=',self.connection)
            print('rig=',self.rig)
            #sys.exit(0)

################################################################################

def WatchDog(P):
    print('Watch Dog ....',P.Done)
    if not P.Done:

        # Read radio status
        if P.sock.connection!='NONE':
            #print 'Watch Dog - reading radio status ...', P.sock.connection
            socket_io.read_radio_status(P.sock)
            #print 'Woof Woof:',P.sock.freq, P.sock.band, P.sock.mode, P.sock.wpm
            
        # Reset timer
        threading.Timer(1.0, WatchDog, args=(P,)).start()
    
################################################################################

# Begin exec code
print("\n***********************************************************************************")
print("\nStarting FTDX  ...")
P=PARAMS()
print("P=",pprint(vars(P)))
print(' ')

#usb_audio=USB_AUDIO(P)

# Put up the root window
cat=ft_cat2(P)
#print "P=",pprint(vars(P))

# Watch Dog timer
#WatchDog(P)

P.root.mainloop()
sys.exit(0)

