import sounddevice as sd
import numpy as np
import pyautogui as cur
import numpy.fft as fft
import matplotlib.pyplot as plt
import time as t
import math
import queue
from scipy import signal


volumeLimit = 10
switchLimit = 1200
highLimit = 260
movementFactor = 100

clickLimit = 700
axis = False
cur.FAILSAFE = False
cooldown = 0

dominantFreqQ = queue.LifoQueue(1)

b,a = signal.butter(6, 90, fs=20000, btype='high', analog=False)

def queueSound(indata, frames, time, status):
    global axis, cooldown

    data = signal.lfilter(b, a,indata[:,0])
    spectrum = fft.fft(data)
    magnitudes  = abs(spectrum)

    freq = abs(fft.fftfreq(len(spectrum),1/samplerate))
    num = 6
    index = np.argpartition(magnitudes, -num)[-num:]
    dominantFreq = min(freq[index])
    volume = np.sum(magnitudes[index])

    if(volume>volumeLimit):
        
        if dominantFreq > switchLimit:
            if cooldown < 0:
                axis = not axis
                cooldown = 1
                print("Switching axis")

        if dominantFreq > clickLimit and dominantFreq < switchLimit:
            cur.click()
            cooldown = cooldown - 1
            print("Click")
        elif dominantFreq < clickLimit:
            dominantFreqQ.put((dominantFreq, volume))
            cooldown = cooldown - 1
    else:
         dominantFreqQ.put((0,0))


    

def moveCursor():
    global axis
    try:
        freq_volume = dominantFreqQ.get_nowait()
        freq = freq_volume[0]
        volume = freq_volume[1]
        print(freq)
        print(volume)
    except queue.Empty:
        return    
    if freq >1:
        moveAmount = volume*(freq-highLimit)/400
        if moveAmount>0:
             moveAmount=moveAmount*2.5

        if axis:    
                cur.move(0,-moveAmount)
        else:
                cur.move(moveAmount,0)
        return 
    return

stream = sd.InputStream(callback=queueSound,blocksize=2000,samplerate=20000)
samplerate = stream.samplerate

with stream:
    while True:
        moveCursor()
