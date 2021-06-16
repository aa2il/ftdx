############################################################################################

# ft_cat2.py - J.B.Attili - 2017

# This module contains everything related to the gui for ftdx.py

import sys
from rig_io.socket_io import *
from rig_io.ft_tables import *
from ft_keypad import *
from rig_io.presets import *
from sound_replay import Mark,ReplayNormal,Slower

if sys.version_info[0]==3:
    from tkinter import *
else:
    from Tkinter import *
import time
from collections import OrderedDict

############################################################################################    

class ft_cat2:
    def __init__(self,P):

        # Init
        P.root       = Tk()
        self.P       = P
        self.parent  = P.root
        #self.parent.title("FTDX-3000 Control by AA2IL")

        # Variables that are used in Tk object callbacks
        self.mode    = StringVar(self.parent)
        
        self.band    = StringVar(self.parent)
        self.ant     = StringVar(self.parent)
        self.station = IntVar(self.parent)
        self.status  = StringVar(self.parent)
        self.frequency   = 0  
        self.ContestMode = 0
        self.mode.set('')
        self.band.set(0)
        self.TxT='Howdy'

        # Open connection to rig - can be via direct serial connection, fldigi, flrig or hamlib
        self.sock = open_rig_connection(P.connection,P.host,P.PORT,P.baud,'FTDX: ',rig=P.rig)
        P.sock = self.sock
        if not self.sock.active:
            sys.exit(0)
        #sys.exit(0)

        # Create the gui
        self.create_gui()
        if P.sock.rig_type2:
            rig=' - '+P.sock.rig_type2
        else:
            rig=''
        self.parent.title("Radio Control by AA2IL"+rig)
        print('$$$$$$$$$$$$$$$$$$$$ GUI is up $$$$$$$$$$$$$$$$$')

    def create_gui(self):
        parent=self.parent

        # Put a label at the top that indicates basic staus of the rig
        Label(parent, textvariable=self.status ).pack(side=TOP)
        get_status(self)

        # Create a frame with buttons to select operating band
        BandFrame = Frame(parent)
        BandFrame.pack(side=TOP)
        for b in bands:

            # Only show bands that the connected rig supports
            if ((b=='10m')   and (self.sock.rig_type2=='TS850'   )) or \
               ((b=='2m' )   and (self.sock.rig_type2=='FTdx3000')) or \
               ((b=='1.25m') and (self.sock.rig_type2=='IC706'   )) or \
               ((b=='33cm')  and (self.sock.rig_type2=='FT991a'  )):
                break
            if ((b in CONTEST_BANDS) or (b in NON_CONTEST_BANDS)) and \
               (self.sock.rig_type2=='IC9700'  ):
                continue
            if (b=='1.25m') or (b=='33cm'):
                continue
            
            Radiobutton(BandFrame, 
                        text=b,
                        indicatoron = 0,
                        variable=self.band, 
                        command=lambda: SelectBand(self),
                        value=b).pack(side=LEFT,anchor=W)

        # Create a frame with buttons to select operating mode
        ModeFrame = Frame(parent)
        ModeFrame.pack(side=TOP)
        for m in modes:
            Radiobutton(ModeFrame, 
                        text=m,
                        indicatoron = 0,
                        variable=self.mode, 
                        command=lambda: SelectMode(self),
                        value=m).pack(side=LEFT,anchor=W)

        # Create a frame with buttons to select antenna
        AntFrame = Frame(parent)
        AntFrame.pack(side=TOP)
        for a in [1,2,3]:
            Radiobutton(AntFrame, 
                        text='Ant'+str(a),
                        indicatoron = 0,
                        variable=self.ant, 
                        command=lambda: SelectAnt(self),
                        value=a).pack(side=LEFT,anchor=W)

        # Create a frame with sliders to adjust tx power, mic and monitor gains
        SliderFrame = Frame(parent)
        SliderFrame.pack(side=TOP)

        self.slider0 = Scale(SliderFrame, 
                             from_=0, to=100, 
                             orient=HORIZONTAL,
                             length=300,
                             label="TX Power",
                             command=self.Slider0CB )
        self.slider0.pack()
        read_tx_pwr(self)
        print(("POWER: %d" % self.tx_pwr))
        self.slider0.set(self.tx_pwr)

        self.slider1 = Scale(SliderFrame, 
                             from_=0, to=100, 
                             orient=HORIZONTAL,
                             length=300,
                             label="Mic Gain",
                             command=self.Slider1CB )
        self.slider1.pack()
        read_mic_gain(self)
        print(("GAIN: %d" % self.gain))
        self.slider1.set(self.gain)

        self.slider2 = Scale(SliderFrame, 
                             from_=0, to=100, 
                             orient=HORIZONTAL,
                             length=300,
                             label="Monitor Level",
                             command=self.Slider2CB )
        self.slider2.pack()
        read_monitor_level(self)
        print(("LEVEL: %d" % self.mon_level))
        self.slider2.set(self.mon_level)

        # Add buttons to read the meter & adjust audio gain
        Button(SliderFrame,
               text="Read Meter",   
               command=self.Read_Meter_Test  ).pack(side=LEFT,anchor=W)
        Button(SliderFrame,
               text="Auto Adj Mic", 
               command=lambda: Auto_Adjust_Mic_Gain(self) ).pack(side=LEFT,anchor=W)

        # Create a frame with buttons to select among several preset AM stations
        StationFrame = Frame(parent)
        StationFrame.pack(side=TOP)

        print("Setting station list...")
        print(stations)
        for s in stations:
            Radiobutton(StationFrame, 
                        text=s,
                        indicatoron = 0,
                        variable=self.station, 
                        command=lambda: SelectStation(self),
                        value=stations[s]).pack(side=LEFT,anchor=W)

        # Create a frame with buttons to support other misc functions
        MiscFrame = Frame(parent)
        MiscFrame.pack(side=TOP)

        Button(MiscFrame,
               text="Contest",   
               command=self.ToggleContest   ).pack(side=LEFT,anchor=W)
        Button(MiscFrame,
               text="CLAR Reset",
               command=lambda: ClarReset(self) ).pack(side=LEFT,anchor=W)
        Button(MiscFrame,
               text="<",         
               command=lambda: SetSubBand(self,1) ).pack(side=LEFT,anchor=W)
        Button(MiscFrame,
               text="|",         
               command=lambda: SetSubBand(self,2) ).pack(side=LEFT,anchor=W)
        Button(MiscFrame,
               text=">",         
               command=lambda: SetSubBand(self,3) ).pack(side=LEFT,anchor=W)

        Button(MiscFrame,
               text="VFO A",     
               command=lambda: SetVFO(self,'A') ).pack(side=LEFT,anchor=S)
        Button(MiscFrame,
               text="VFO B",     
               command=lambda: SetVFO(self,'B') ).pack(side=LEFT,anchor=W)
        Button(MiscFrame,
               text="A->B",     
               command=lambda: SetVFO(self,'A->B') ).pack(side=LEFT,anchor=W)
        Button(MiscFrame,
               text="B->A",     
               command=lambda: SetVFO(self,'B->A') ).pack(side=LEFT,anchor=W)
        Button(MiscFrame,
               text="A<->B",     
               command=lambda: SetVFO(self,'A<->B') ).pack(side=LEFT,anchor=W)
        
        # Create a frame with buttons to support sound replay functions
        SoundFrame = Frame(parent)
        SoundFrame.pack(side=TOP)

#        wav=0;                   # Wave file object
#        p = pyaudio.PyAudio()    # pyaudio object 
#        stream=0;                # streaming object

        Button(SoundFrame,
               text="Keypad",     
               command=self.ProgramKeypadMsgs).pack(side=LEFT,anchor=W)
        Button(SoundFrame,
               text="Presets",     
               command=self.ProgramPresets).pack(side=LEFT,anchor=W)
        Button(SoundFrame,
               text="Mark"  , 
               command=Mark        ).pack(side=LEFT,anchor=W)
        Button(SoundFrame,
               text="Replay", 
               command=ReplayNormal).pack(side=LEFT,anchor=W)
        Button(SoundFrame,
               text="Slow"  , 
               command=Slower      ).pack(side=LEFT,anchor=W)

        # Create a final frame with buttons to support more misc functions
        LastFrame = Frame(parent)
        LastFrame.pack(side=TOP)

        Button(LastFrame,
               text="TEST",
               command=self.TEST).pack(side=LEFT,anchor=W)
        Button(LastFrame,
               text="Restart",
               command=self.Restart).pack(side=LEFT,anchor=W)
        Button(LastFrame,
               text="Update",
               command=self.Update).pack(side=LEFT,anchor=W)
        Button(LastFrame,
               text="QUIT"  ,
               command=self.Quit  ).pack(side=LEFT,anchor=W)

        #print ' ============== Here we go again ============'
        #get_status(self)

    ############################################################################################

    def ToggleContest(self):
        self.ContestMode = 1-self.ContestMode
        print("Content mode=",self.ContestMode)
        SetFilter(self)

    ############################################################################################

    def Read_Meter_Test(self):
        s=self.sock
        print("\nRead Meter Test ...")
    
        for i in range(9):
            val = Read_Meter(self,i)
            print("val= ",val)
        print("Done.")

    ############################################################################################

    def ProgramPresets(self):

        if self.sock.rig_type=='Hamlib':
            print('*** ERROR *** Need to use DIRECT CONNECTION to rig to program presets ***')
            self.Quit()
            sys.exit(0)
        
        if False:
            #tkMessageBox.showerror("Error","No disk space left on device")
            #tkMessageBox.showwarning("Warning","Could not start service")
            tkMessageBox.showinfo("Information","Created in Python.")
            
            #self.MessageWindow()
            #while self.msg_waiting:
            #    time.sleep(0.1)
            self.Quit()
            sys.exit(0)
        
        if False:
            print('Hey!',self.sock.rig_type,self.sock.rig_type2)

            if self.sock.rig_type=='Yaesu':
                read_mem_yaesu(self)
            else:
                read_mem_icom(self)
                
            self.Quit()
            sys.exit(0)

        if False:
            P2 = int2bcd(1000*147130,5,1)
            P2=P2[::-1]
            print('\n147130:',P2,show_hex(P2))
            P2 = int2bcd(449500000,5,1)
            P2=P2[::-1]
            print('449500:',P2,show_hex(P2))
            P10 = int2bcd(10*600,3,1)
            P10=P10[::-1]
            print('600:',P10,show_hex(P10))
            P10 = int2bcd(10*5000,3,1)
            P10=P10[::-1]
            print('5000:',P10,show_hex(P10))
                
            self.Quit()
            sys.exit(0)

        # Set time & date
        if False:
            self.sock.set_date_time()
            #self.Quit()
            #sys.exit(0)

        # Read table of presets - same as for pySDR but we look at a few different fields
        print("\n==================================== Programming Presets ...")
        presets = read_presets2(self.sock.rig_type2,'Presets')
        for line in presets:
            #print line
            ch = line[self.sock.rig_type2]
            if len(ch)>0:
                if ch=='N/A':
                    continue
                    
                ch=int(float(ch))
                grp=line['Group']
                lab=line['Tag']
                if grp!='Satellites':
                    freq=line['Freq1 (KHz)']
                else:
                    freq=line['Downlink']
                mode=line['Mode']
                pl=line['PL']
                chan = int( float(ch) )
                uplink=line['Uplink']
                inverting=line['Inverting']=='Yes'

                #if grp!='Satellites' or ch!=80:
                if grp=='Satellites':
                    continue
                print( '\n############################################################################\nch=',ch)
                if self.sock.rig_type=='Yaesu':
                    #if ch<97 or ch>99:
                    if ch!=84 and ch!=92 and ch!=93 and ch!=96:
                    #if ch!=84:
                        continue
                    write_mem_yaesu(self,grp,lab,chan,freq,mode,pl,uplink,inverting)
                    time.sleep(0.1)
                elif self.sock.rig_type2=='IC9700':
                    #if ch<20:
                    if grp!='Sats' or ch>100:
                        continue
                    write_mem_icom(self,grp,lab,chan,freq,mode,pl,uplink,inverting)
                #self.Quit()
                #sys.exit(0)

        print('Done.')
        
    ############################################################################################

    def MessageWindow(self):

        # Create gui window
        print("\nMessageWindow...")
        self.msgwin=Toplevel(self.parent)
        self.msgwin.title("Msg")

        Label(self.msgwin, text='Hello').grid(row=0, column=0)
        Button(self.msgwin,text="OK",command=self.KillMsgWin).grid(row=1, column=0)
        self.msg_waiting=1
        print('...Done')

    def KillMsgWin(self):
        print("\nKillMsgWin...")

        self.msgwin.destroy()
        self.msg_waiting=0
        print("Done.")

        
    ############################################################################################

    def ProgramKeypadMsgs(self):

        # Init
        print("\nProgramming keypad ...")
        self.ekeyer=[];
        self.Keyer = ['','','','','','']

        # Create gui window
        keywin=Toplevel(self.parent)
        keywin.title("CW Keypad")
        self.keywin=keywin

        # See what's in the keypad
        GetKeyerMemory(self)

        for i in range(6):
            print("Programming Keypad ",i)
            if i<5:
                txt=str(i+1)+":"
            else:
                txt="#:"

            Label(keywin, text=txt).grid(row=i, column=0)
            self.ekeyer.append( Entry(keywin) )
            self.ekeyer[i].grid(row=i, column=1,columnspan=2)
            self.ekeyer[i].insert(0,self.Keyer[i])

            Button(keywin, text="ARRL DX" ,
                   command=lambda: KeyerMemoryDefaults(self,1) ).grid(row=6, column=0)
            Button(keywin, text="NAQP"    ,
                   command=lambda: KeyerMemoryDefaults(self,2) ).grid(row=6, column=1)
            Button(keywin, text="IARU"    ,
                   command=lambda: KeyerMemoryDefaults(self,3) ).grid(row=6, column=2)
            Button(keywin, text="CQ WW"   ,
                   command=lambda: KeyerMemoryDefaults(self,4) ).grid(row=6, column=3)
            Button(keywin, text="CQ WPX"  ,
                   command=lambda: KeyerMemoryDefaults(self,5) ).grid(row=6, column=4)
            Button(keywin, text="ARRL 160m" ,
                   command=lambda: KeyerMemoryDefaults(self,6) ).grid(row=6, column=5)

            Button(keywin, text="Defaults",
                   command=lambda: KeyerMemoryDefaults(self,0) ).grid(row=7, column=0)
            Button(keywin, text="Update"  ,
                   command=lambda: UpdateKeyerMemory(self)  ).grid(row=7, column=1)
            Button(keywin, text="Dismiss" ,
                   command=self.KeywinKill    ).grid(row=7, column=4)

    def KeywinKill(self):
        print("\nKeywinKill...")

        self.ekeyer=[]
        self.keywin.destroy()
        print("Done.")

    ############################################################################################

    def Quit(self):
        global wave_stat,stream,p,wav

        print("\nThat's all Folks!")
        self.P.Done = True

        print("*** Warning - need to update QUIT when we get sound i/o working ***")
#        if wave_stat[0]==1:
#            stream.stop_stream()
#            stream.close()
#            p.terminate()
#            wav.close()

        self.sock.close()
        self.parent.quit()

    def Restart(self):
        self.sock.close()
        self.sock=open_socket(self.port,self.port)
        get_status(self)

    def Update(self):
        get_status(self)

    def Slider0CB(self,arg):
        print('\nSlider 0 CallBack: ...')
        self.tx_pwr=arg
        set_tx_pwr(self)
        print('... Slider 0 CallBack Done.\n')

    def Slider1CB(self,arg):
        print('\nSlider 1 CallBack: ...')
        self.gain=arg
        set_mic_gain(self)
        print('... Slider 1 CallBack Done.\n')

    def Slider2CB(self,arg):
        print('\nSlider 2 CallBack: ...')
        self.mon_level = arg
        set_mon_level(self)
        print('... Slider 2 CallBack Done.\n')

    # Playpen for experimenting
    def TEST(self):

        # Init
        print("\nPlaypen ...")

        # Create gui window
        win=Toplevel(self.parent)
        win.title("Play Pen")

