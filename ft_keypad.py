################################################################################
#
# ft_keypad.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Functions related to programming the Yaesu keypad.
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
if sys.version_info[0]==3:
    from tkinter import END
else:
    from Tkinter import END

################################################################################

def GetKeyerMemory(self):
    s=self.sock

    print("\nReading Keyer Memory ...")
    for i in range(6):
        print("GetKeyerMemory: i=",i)
        if i<5:
            if self.sock.connection=='HAMLIB' and False:
                cmd='w KM'+str(i+1)+'\n'
            else:
                cmd='KM'+str(i+1)+';'
        else:
            if self.sock.connection=='HAMLIB' and False:
                cmd='w EX025\n'
            else:
                cmd='EX025;'
                
        #        buf=get_response(s,cmd)
        buf=self.sock.get_response(cmd)
        print("buf=",buf)
        if i<5:
            j=buf.index('}')
            self.Keyer[i]=buf[3:j]
        else:
            j=buf.index(';')
            self.Keyer[i]=buf[5:j]

#        cmd='w EX0245\n'                          # Set cut numbers to 12NO - not sure why this is here?
#        s.send(cmd)
        print("Done.")



def KeyerMemoryDefaults(self,arg):
    print("\Setting Keypad Defaults ",arg)

    MY_CALL     = self.P.MY_CALL
    MY_NAME     = self.P.MY_NAME
    MY_STATE    = self.P.MY_STATE
    MY_SEC      = self.P.MY_SEC
    MY_CQ_ZONE  = self.P.MY_CQ_ZONE
    MY_ITU_ZONE = self.P.MY_ITU_ZONE

    if arg==1:
        # ARRL Intl DX Contest & CQ 160
        Keyer=[MY_CALL,'TU 5NN '+MY_STATE,MY_STATE+MY_STATE,'73','AGN?','0001']
    elif arg==2:
        # NAQP
        Keyer=[MY_CALL,'TU 5NN '+MY_NAME,MY_NAME+MY_NAME,'73','AGN?','0001']
    elif arg==3:
        # IARU HF Champ
        Keyer=[MY_CALL,'TU 5NN '+MY_ITU_ZONE,MY_ITU_ZONE+MY_ITU_ZONE,'73','AGN?','0001']
    elif arg==4:
        # CQ WW
        Keyer=[MY_CALL,'TU 5NN '+MY_CQ_ZONE,MY_CQ_ZONE+MY_CQ_ZONE,'73','AGN?','0001']
    elif arg==5:
        # CQ WPX
        Keyer=[MY_CALL,'TU 5NN 1','001 001','73','AGN?','0001']
    elif arg==6:
        # ARRL 160
        Keyer=[MY_CALL,'TU 5NN '+MY_SEC,MY_SEC+MY_SEC,'73','AGN?','0001']
    else:
        # Regular quick exchanges
        Keyer=[MY_CALL,'RTU 5NN '+MY_STATE,'OP '+MY_NAME,'73','BK','0001']

    for i in range(6):
        self.ekeyer[i].delete(0,END)
        self.ekeyer[i].insert(0,Keyer[i])

    self.Keyer=Keyer;
    print("Done.")

def UpdateKeyerMemory(self):
    s=self.sock;

    print("\nUpdating keypad ...")
    for i in range(6):
        self.Keyer[i] = self.ekeyer[i].get()
        if i<5:
            if self.sock.connection=='HAMLIB':
                cmd='w BY;KM'+str(i+1)+self.Keyer[i]+'}\n'
            else:
                cmd='KM'+str(i+1)+self.Keyer[i]+'};'
        else:
            if self.sock.connection=='HAMLIB':
                cmd='w BY;EX025'+self.Keyer[i]+'\n'
            else:
                cmd='EX025'+self.Keyer[i]+';'
        print("cmd=",cmd)
        #buf=get_response(s,cmd)
        buf=self.sock.get_response(cmd)

    print("Done.")

