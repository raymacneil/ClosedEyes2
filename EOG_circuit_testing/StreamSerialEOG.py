"""Example program to demonstrate how to send a multi-channel time-series
with proper meta-data to LSL."""
import sys
import getopt

import time
import serial
from random import random as rand

from pylsl import StreamInfo, StreamOutlet, local_clock


def main(argv):
    srate = 250
    name = 'MyEOGCircuit'
    type = 'EOG'
    channel_names = ["H", "V"]
    n_channels = len(channel_names)
    help_string = 'SendData.py -s <sampling_rate> -n <stream_name> -t <stream_type>'
    try:
        opts, args = getopt.getopt(argv, "hs:n:t:", longopts=["srate=", "name=", "type"])
    except getopt.GetoptError:
        print(help_string)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(help_string)
            sys.exit()
        elif opt in ("-s", "--srate"):
            srate = float(arg)
        elif opt in ("-n", "--name"):
            name = arg
        elif opt in ("-t", "--type"):
            type = arg

    # first create a new stream info (here we set the name to BioSemi,
    # the content-type to EEG, 8 channels, 100 Hz, and float-valued data) The
    # last value would be the serial number of the device or some other more or
    # less locally unique identifier for the stream as far as available (you
    # could also omit it but interrupted connections wouldn't auto-recover).
    info = StreamInfo(name, type, n_channels, srate, 'float32', 'myuid2424') 

    # append some meta-data
    info.desc().append_child_value("manufacturer", "MyEOGCircuit")
    chns = info.desc().append_child("channels")
    for label in channel_names:
        ch = chns.append_child("channel")
        ch.append_child_value("label", label)
        ch.append_child_value("unit", "microvolts")
        ch.append_child_value("type", "EOG")
    # info.desc().append_child_value("manufacturer", "MiNa")
    # cap = info.desc().append_child("cap")
    # cap.append_child_value("name", "ComfyCap")
    # cap.append_child_value("size", "54")
    # cap.append_child_value("labelscheme", "10-20")

    # next make an outlet; we set the transmission chunk size to 32 samples and
    # the outgoing buffer size to 360 seconds (max.)
    outlet = StreamOutlet(info)

    try:
        ser = serial.Serial('COM15', 115200) # Used to be COM12
    except :
        print("ERROR: could not connect to serial port")
        return

    print("now sending data...")
    start_time = local_clock()
    sent_samples = 0
    try :
        while True:
            try:
                elapsed_time = local_clock() - start_time
                required_samples = int(srate * elapsed_time) - sent_samples

                if required_samples > 0:
                    x=ser.readline().decode('utf-8', errors='replace')
                    x = x.strip("\r\n").split(", ")
                    dat = [int(v) for v in x]
                    outlet.push_sample(dat)
                    sent_samples += required_samples
                # if required_samples > 0:
                #     # make a chunk==array of length required_samples, where each element in the array
                #     # is a new random n_channels sample vector
                #     mychunk = [[rand() for chan_ix in range(n_channels)]
                #                for samp_ix in range(required_samples)]
                #     # get a time stamp in seconds (we pretend that our samples are actually
                #     # 125ms old, e.g., as if coming from some external hardware)
                #     stamp = local_clock() - 0.125
                #     # now send it and wait for a bit
                #     outlet.push_chunk(mychunk, stamp)
                #     sent_samples += required_samples
                time.sleep(0.002)  
            except KeyboardInterrupt:
                pass
    except :
        pass
    finally:
        ser.close()


if __name__ == '__main__':
    main(sys.argv[1:])

    
