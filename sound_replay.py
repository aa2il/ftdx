############################################################################################

# sound_replay.py - J.B.Attili - 2017

# Functions relating to sound replay buttons - nver really completed this -
# still a work in progress

############################################################################################

import pyaudio
import wave

############################################################################################

CHUNK = 1024
WAV_FILE='capture.wav'

# Status flags for wave capture/paly
wave_stat = [0,0,0,0,0,0,0,0]     
            # Position 0 = 1 if wave file already opened
            # Position 1 = 1 if sound device is opened
            # Position 2 = # channels
            # Position 3 = sample width
            # Position 4 = frame rate of data in wave file
            # Position 5 = no. frames in wave file
            # Position 6 = rate last time ound was replay
            # Position 7 = rate deisred for next replay
wav=0;      # Wave file object
p = pyaudio.PyAudio()   # pyaudio object 
stream=0;   # streaming object

# Routine to mark current position in capture wave file
def Mark():
    global wave_stat
    global wav

    print("Marking...")

    # Re-open file
    if wave_stat[0]==1:
        print("Closing...")
        wav.close()
    wav = wave.open (WAV_FILE, "r")
    (nchan, width, rate, nframes, comptype, compname) = wav.getparams()

#    t = (1.0*nframes)/rate
#    print "t=",t

    wave_stat=[1,wave_stat[1],nchan,width,rate,nframes,wave_stat[6],rate]
#    print wave_stat

    Replay()


# Function to replay last ? sec of capture
def Replay():
    global p,stream,wave_stat

    print("Replaying...",wave_stat)

    # Open sound device
    if wave_stat[1]==0 or wave_stat[6]!=wave_stat[7]:
        if wave_stat[1]==1:
            print("Re-opening sound...")
            stream.stop_stream()
            stream.close()
        else:
            print("Opening sound...")
        nchan  = wave_stat[2]
        width  = wave_stat[3]
        rate2  = wave_stat[7]
        stream = p.open(format=p.get_format_from_width(width),
                        channels=nchan,rate=rate2, output=True)
        wave_stat[1]=1
        wave_stat[6]=rate2
        wave_stat[7]=wave_stat[6]

    # Play last ?-sec
    DT = 5
    rate      = wave_stat[4]
    nframes   = wave_stat[5]
    end_frame = nframes
    start_frame = end_frame - DT*rate
    if start_frame<0:
        start_frame=0
    print(start_frame,end_frame)

    wav.setpos(start_frame)
#    pos=wav.tell()
#    print pos
    while True:
        data = wav.readframes(CHUNK)
        if data == '':
            break
        stream.write(data)
        pos=wav.tell()
#        print pos,nframes
        if pos>end_frame:
            break

def ReplayNormal():
    global wave_stat

    print("Normal replay ...")

    wave_stat[7] = wave_stat[4]
    Replay()


def Slower():
    global wave_stat

    print("Slow replay ...")

    wave_stat[7] = wave_stat[4] / 2
    Replay()



