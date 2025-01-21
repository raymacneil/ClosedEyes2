from pickle import FALSE, TRUE
from random import randrange
from numpy.core.defchararray import split
from pywinauto.findwindows    import find_window
from pywinauto.win32functions import SetForegroundWindow
import win32gui
import socket
import numpy as np
import msvcrt
import csv
import os
import pylink
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
from ConsoleTimer import consoleTimer
from psychopy import visual, core, event, sound, prefs
from pylsl import StreamInfo, StreamOutlet
from datetime import datetime
from eyelink_commands import *
from ss_trial_h import *
from ss_helper_funs import *
from load_config_csv import load_cond1_config_file, load_cond2_config_file

#prefs.general['audioLib'] = ['sounddevice']

### List of Cyton (EOG) channels to record
### You can use any subset of channels [1,2,3,4,5,6,7,8]
### N2P, N4P, UP (EOG), DOWN (REFERENCE)
eog_channels = [2,4]

### Color codes for bg / drawing stims
GRY = (0,0,0)
BLK = (-1,-1,-1)
RED = (1,-1,-1)
GRN = (-1,1,-1)
### Create arrays of all horizontal and vertical angles
i = randrange(0,1)
angles_horz = np.array([5.25,8.25,11.25,14.25,17.25])
angles_vert = np.array([1.00,3.25,5.50,7.75,10.00])

### Get stim locations based on angle
SCREEN_RES = (1920, 1080) #(1920, 1080)
SCREEN_WIDTH_CM = 120.65
SCREEN_DIAG_CM = 138.68
EYE_TO_SCREEN_CM = 50.00 # 96.5 (old setup)

FG_COLOUR = GRY
BG_COLOUR = BLK


PPCM = np.sqrt(SCREEN_RES[0]**2. + SCREEN_RES[1]**2.) / SCREEN_DIAG_CM

EL_SAMPLE_RATE = 250
isi = 1.0 / EL_SAMPLE_RATE

# Return to fixation minimum gaze duration (ms)
FIX_RETURN_GAZE_DUR = 250
FIX_RETURN_GAZE_FRAMES = int(FIX_RETURN_GAZE_DUR / (1000 * isi))

UDP_IP = "127.0.0.1"
UDP_PORT_TO_EOG  = 50999
UDP_PORT_FROM_EOG  = 51000 
UDP_PORT_FROM_LR = 51001

lab_recorder_exe = 'C:\\labstreaminglayer\\Apps\\LabRecorder\\build\\Release\\LabRecorder.exe'

# This will ensure that the Command Prompt window will remain selected after PyGame loads
# Makes the program less annoying to use.
def window_enum_handler(hwnd, resultList):
    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) != '':
        resultList.append((hwnd, win32gui.GetWindowText(hwnd)))

def get_app_list(handles=[]):
    mlst=[]
    win32gui.EnumWindows(window_enum_handler, handles)
    for handle in handles:
        mlst.append(handle)
    return mlst

appwindows = get_app_list()


try: 
    handle = win32gui.FindWindow(0, "C:\\WINDOWS\\system32\\CMD.exe - python2  ss_run_h.py")
    win32gui.SetForegroundWindow(handle)
except:
    try: 
        handle = win32gui.FindWindow(0, 'C:\\WINDOWS\\system32\\cmd.exe - python2  C:\\Users\\Visionlab\\Desktop\\ClosedEyes2\\ss_run_h.py')
        win32gui.SetForegroundWindow(handle)
    except:
        pass
    
# Get participant info
print('')

# got_pname = False
got_pname = False
while not got_pname:
    pname = raw_input("Enter participant number: ")
    if len(pname) > 4:
        print("Input Error! Participant number may be 4 digits max.")
    else:
        got_pname = True

# ipd = raw_input("Enter participant's interpupilary distance (mm): ")
ipd = 0
fix_shift = 0 # float(ipd) / 20. # Divide by two and convert to centimeters
cond = 0
# cond = 1
# Uncomment
# Get condition info, display reminders for proper screen/Eyelink setup
print("""
Please select the condition that you wish to run:
1. Eyes open, Markers on & off (alternating), Luminance (1)
2. Eyes open & closed (alternating), Markers off, No Luminance (2) [NOT CURRENTLY AVAILABLE]
""")
while cond == 0:
    try:
        user_cond = int(raw_input("Enter condition number: "))
        if (user_cond > 0 and user_cond < 2)  : #and (user_cond != 2) :
            cond = user_cond
        else:
            raise Exception
    except :
        print("Input Error! Enter a number corresponding to option 1 or 2, if available.")

# Display condition-specific instructions for experimenter
if cond == 1 :
    markers_on = True
    ## Uncomment
    # user_prac = raw_input("Run calibration trials? (y/n) ")
    user_prac = 'Y'
    if user_prac.startswith('y') or user_prac.startswith('Y') :
        run_calib_trials = True
    else :
        print("Skip calibration trials for Condition 1? Press ENTER to continue, ESC to quit.") 
        while True :
            if msvcrt.kbhit() :
                if msvcrt.getch() == b'\x1b' :
                    quit() 
                else :
                    run_calib_trials = False
                    break
else :
    markers_on = False
    run_calib_trials = False
# run_calib_trials = True
edfn = "P" + str(pname) + "_C" + str(cond) + ".edf"
edf_out_path = "C:\\Users\\Visionlab\\Desktop\\ClosedEyes2\\Data\\EDF\\"


# Randomly choose true or false (to be updated with CSV specs)
markersOnFirstBlock = np.random.rand() > 0.5

### Create trial order depending on condition
if cond == 1 :

    print("\nPlease select the config file for Condition 1...")

    trialTargetOrder, trialBlockNumber, trialTargDir, blockNumbers, blockMarkersOn, blockTargDir, calOrderID = load_cond1_config_file()

    if not all(np.size(x) > 0 for x in [trialTargetOrder, trialBlockNumber, trialTargDir, blockNumbers, blockMarkersOn, blockTargDir, calOrderID]) :
        print('')

        print("Config Error! Could not load or parse CSV file successfully. Exiting...")
        exit()

    n_trials = np.size(trialTargetOrder, axis=0)
    num_blocks = np.size(np.unique(trialBlockNumber), axis=0)
    block_length = n_trials/num_blocks

    # Parse for horz and vert separation
    # trialTargetOrder, trialBlockNumber, blockNumbers, blockMarkersOn, blockTargDir
    # IdxBlockEdge = np.array([],dtype=int)
    # IdxBlockEdge = np.nonzero(np.append(np.append(1, np.diff(trialTargDir) != 0),1))[0]
    # NumDirs = np.size(IdxBlockEdge)-1
    # blockNumDirs = np.array([], dtype=int)
    
    # for ii in range(NumDirs):
    #     blockNumDirs = np.append(blockNumDirs, range(int(IdxBlockEdge[ii]),int(IdxBlockEdge[ii+1])))
        
   
   # What's important for required changes, is that it assumes there is a hoirzontal, vertical, and oblique block conditions
   # The code is setup to create an 3 x N blocks
    blockNumbersOrg = blockNumbers
    blockMarkersOnOrg = blockMarkersOn
    blockTargDirOrg = blockTargDir
    trialBlockNumberOrg = trialBlockNumber
    trialTargetOrderOrg = trialTargetOrder
    trialTargDirOrg = trialTargDir
    blockNumbers = split_block_array(blockNumbers, trialTargDir, trialBlockNumber)
    blockMarkersOn = split_block_array(blockMarkersOn, trialTargDir, trialBlockNumber)
    blockTargDir = split_block_array(blockTargDir, trialTargDir, trialBlockNumber)
    trialTargetOrder = split_on_changes(trialTargetOrder, trialTargDir)
    trialBlockNumber = split_on_changes(trialBlockNumber, trialTargDir)
    trialTargDir = split_on_changes(trialTargDir, trialTargDir)

    # IdxBlockDirStart = np.nonzero(np.append(False, np.diff(trialTargDir) != 0))
    # BlockDirStarts = trialBlockNumber[IdxBlockDirStart[0]]
    # dir1_blocks = blockNumbers[0:(int(BlockDirStarts[0])-1)]
    # dir2_blocks = blockNumbers[(int(BlockDirStarts[0])-1):(int(BlockDirStarts[1])-1)]
    # dir3_blocks = blockNumbers[(int(BlockDirStarts[1])-1):]
    # blockNumbers = np.array([dir1_blocks, dir2_blocks, dir3_blocks])
    # blockMarkersOn = np.array([blockMarkersOn[0:(int(BlockDirStarts[0])-1)], blockMarkersOn[(int(BlockDirStarts[0])-1):(int(BlockDirStarts[1])-1)], blockMarkersOn[(int(BlockDirStarts[1])-1):]])
    # blockTargDir = np.array([blockTargDir[0:(int(BlockDirStarts[0])-1)], blockTargDir[(int(BlockDirStarts[0])-1):(int(BlockDirStarts[1])-1)], blockTargDir[(int(BlockDirStarts[1])-1):]])
    # trialBlockNumber = trialBlockNumber.reshape(3,block_length*(BlockDirStarts[0]-1))
    # trialTargDir = trialTargDir.reshape(3,block_length*(BlockDirStarts[0]-1))
    # trialTargetOrder = trialTargetOrder.reshape(3,block_length*(BlockDirStarts[0]-1))
 

    # Setup calibration order
    numCalibTargets = 10
    # numCalibTargets = 3
    numTrialsPerTarget_HorzCalib = 1
    # caliOrderHorz = [3,2,1]
    caliOrderHorz = [5,4,3,2,1,6,7,8,9,10]
                     #5,4,3,2,1,6,7,8,9,10,
                     #5,4,3,2,1,6,7,8,9,10]



else : 
    print("\nPlease select the config file for Condition 2...")

    trialTargetOrder, trialBlockNumber, blockNumbers, blockEyesOpen, blockTargDir = load_cond2_config_file()

    if not all(np.size(x) > 0 for x in [trialTargetOrder, trialBlockNumber, blockNumbers, blockEyesOpen, blockTargDir]) :
        print('')
        print("Config Error! Could not load or parse CSV file successfully. Exiting...")
        exit()

    n_trials = np.size(trialTargetOrder, axis=0)
    num_blocks = np.size(np.unique(trialBlockNumber), axis=0)
    block_length = n_trials/num_blocks

    numCalibTargets = 10
    numTrialsPerTarget_HorzCalib = 1
    caliOrderHorz = [5,4,3,2,1,6,7,8,9,10]
    # blockNumbers = split_block_array(blockNumbers, trialTargDir, trialBlockNumber)
    # blockMarkersOn = split_block_array(blockMarkersOn, trialTargDir, trialBlockNumber)
    # blockTargDir = split_block_array(blockTargDir, trialTargDir, trialBlockNumber)
    # trialTargetOrder = split_on_changes(trialTargetOrder, trialTargDir)
    # trialBlockNumber = split_on_changes(trialBlockNumber, trialTargDir)
    # trialTargDir = split_on_changes(trialTargDir, trialTargDir)


# Output demographics information to CSV
exp_date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
targets_str = ' '.join(str(l) for l in trialTargetOrder)
if cond == 1:
    block_markers_str = ' '.join(str(b) for b in blockMarkersOn)
elif cond == 2:
    block_markers_str = ' '.join(str(b) for b in blockEyesOpen)
else:
    block_markers_str = ''

dems_out = "C:\\Users\\Visionlab\\Desktop\\ClosedEyes2\\ClosedEyes2_Demographics.csv"
dems_exists = os.path.isfile(dems_out)
dems_header = ["Participant","Condition","IPD","Date","Block Size","Block Markers","N Trials"]
dems_row = [pname, str(cond), str(ipd), exp_date, str(block_length), block_markers_str, str(n_trials)]

if not dems_exists :
    with open(dems_out, 'wb') as csvfile :
        demswriter = csv.writer(csvfile, delimiter=',')
        demswriter.writerow(dems_header)

with open(dems_out, 'ab') as csvfile :
    demswriter = csv.writer(csvfile, delimiter=',')
    demswriter.writerow(dems_row)


# eog_to_UDP_str = '['+str(UDP_IP)+','+str(UDP_PORT_TO_EOG)+']'
# eog_from_UDP_str = '['+str(UDP_IP)+','+str(UDP_PORT_FROM_EOG)+']'
eog_UDP_str = '['+str(UDP_IP)+','+str(UDP_PORT_FROM_EOG)+']'
lr_UDP_str = '['+str(UDP_IP)+','+str(UDP_PORT_FROM_LR)+']'
print('')
print("Opening UDP ports for EOG: send=" + eog_UDP_str + ", receive=" + lr_UDP_str)


# Open UDP socket to send record on/off messages to OpenBCI_LSL
socket_eog = socket.socket(socket.AF_INET, # Internet
                           socket.SOCK_STREAM) # TCP
socket_eog.bind((UDP_IP, UDP_PORT_FROM_EOG))
socket_eog.setblocking(0) # set to non-blocking port (for the while loop)
socket_eog.listen(1)


# Open UDP socket to receive exp start/stop messages from LabRecorder
print('')
print('')
print("Opening UDP ports for Lab Recorder: receive=" + lr_UDP_str)
print('')
socket_lr = socket.socket(socket.AF_INET, # Internet
                          socket.SOCK_DGRAM) # UDP
socket_lr.bind((UDP_IP, UDP_PORT_FROM_LR))
socket_lr.setblocking(0) # set to non-blocking port (for the while loop)


### Initialize OpenBCI_LSL
print('')
print('Initializing OpenBCI, perform EOG calibration in popup window.')
print("Please wait for BCI Message...")
print('')

eog_conn = None
try:
    myeog_process = subprocess.Popen(['python2', 'EOG_circuit_testing/StreamSerialEOG.py'])
    # time.sleep(2)
except Exception as e:
    raise

try:
    myeog_plot_process = subprocess.Popen(['python2', 'EOG_circuit_testing/ReceiveAndPlot.py'])
except Exception as e:
    raise

# This will ensure that the Command Prompt window will remain selected after the message is displayed
# Makes the program less annoying to use.
try:
    SetForegroundWindow(find_window(best_match='ss_run_h.py'))
except:
    pass

while 1:
    if msvcrt.kbhit():
        if ord(msvcrt.getch()) == 13: # Enter
            break

### Initialize Eyelink
if cond != 4 :
    print('')
    print("Initializing Eyelink...")
    el_outlet, elTk = InitEyelink(sr=EL_SAMPLE_RATE, fname=edfn)

if cond == 4 :
    print('')
    print("COND 4: skipping Eyelink initialization...")
    print("Select only 'EventMarker' and 'OpenBCI' streams in LabRecorder!")

### Create LSL outlet for event markers
# first create a new stream info (here we set the name to MyMarkerStream,
# the content-type to Markers, 1 channel, irregular sampling rate,
# and string-valued data) The last value would be the locally unique
# identifier for the stream as far as available, e.g.
# program-scriptname-subjectnumber (you could also omit it but interrupted
# connections wouldn't auto-recover). The important part is that the
# content-type is set to 'Markers', because then other programs will know how
#  to interpret the content
try:
    ev_info = StreamInfo('EventMarkers', 'Markers', 1, 0, 'string', 'myuidw43536')
    ev_outlet = StreamOutlet(ev_info)
    ### Pause for experimenter to connect LSL stream
    print("Established LSL event stream outlet.")
    # print("REMINDER: Set Participant (%p) to 'P" + str(pname) + "' and Session (%s) to 'S00" + str(cond) + "'")
    # print('')
    # raw_input("Start recording in LabRecorder now. Press ENTER to continue...")
except:
    print("Could not create LSL outlet.")

print('')
print("Initializing Lab Recorder...")
print("Start stream on LabRecorder to begin experiment (or press 's' to skip & begin without Lab Recorder).")
print('')
lr_exp_string = '[' + pname + "," + str(cond) + ']'
if cond != 4:
    labrecorder_process = subprocess.Popen([lab_recorder_exe, '-c', 'CE_LabRecorderSetting.cfg', '-u', lr_UDP_str, '-e', lr_exp_string])
else:
    labrecorder_process = subprocess.Popen([lab_recorder_exe, '-c', 'CE_LabRecorderSetting_noEL.cfg', '-u', lr_UDP_str, '-e', lr_exp_string])
   
while 1:
    lr_msg = b"D"
    try:
        lr_msg = socket_lr.recv(2) # buffer size is 1 bytes (1 character + null)   
    except:
        pass

    if lr_msg.startswith(b"b"):
        break

    if msvcrt.kbhit():
        if ord(msvcrt.getch()) == 115: # 's'
            break

    if labrecorder_process.poll() is not None :
        print('Lab Recorder has quit, press ENTER to continue without LSL stream recording, or ESC to exit.')
        while 1:
            if msvcrt.kbhit():
                if ord(msvcrt.getch()) == 27: # ESC
                    if openbci_process.poll() is None:
                        openbci_process.kill()
                    quit()
                if ord(msvcrt.getch()) == 13: # Enter
                    break
        break

# This will ensure that the Command Prompt window will remain selected after LabRecorder loads
# Makes the program less annoying to use.
try:
    SetForegroundWindow(find_window(best_match='ss_run2.py'))
except:
    pass

if cond == 4 :
    print('')
    raw_input("COND " +str(cond) + ": Turn off TV now! Press ENTER to continue...")

#create a window
w = visual.Window(monitor="Samsung UN55KU6290", screen=2, size=SCREEN_RES, fullscr=True, color=BG_COLOUR, units="cm")
w.mouseVisible = False

### Create text messages

### Set calibration event messages   
# if calOrderID[0] == 'H':
#     EV_MSG_CAL1 = "horz"
#     STR_CAL1 = "horizontal"
#     if calOrderID[1] == 'V':
#         EV_MSG_CAL2 = "vert"
#         STR_CAL2 = "vertical"
#         EV_MSG_CAL3 = "obli"
#         STR_CAL3 = "oblique"
#     if calOrderID[1] == 'O':
#         EV_MSG_CAL2 = "obli"
#         STR_CAL2 = "oblique"
#         EV_MSG_CAL3 = "vert"
#         STR_CAL3 = "vertical"     
# if calOrderID[0] == 'V':
#     EV_MSG_CAL1 = "vert"
#     STR_CAL1 = "vertical"
#     if calOrderID[1] == 'H':
#         EV_MSG_CAL2 = "horz"
#         STR_CAL2 = "horizontal"
#         EV_MSG_CAL3 = "obli"
#         STR_CAL3 = "oblique"
#     if calOrderID[1] == 'O':
#         EV_MSG_CAL2 = "obli"
#         STR_CAL2 = "oblique"
#         EV_MSG_CAL3 = "horz"
#         STR_CAL3 = "horizontal"
# if calOrderID[0] == 'O':
#     EV_MSG_CAL1 = "obli"
#     STR_CAL1 = "oblique"
#     if calOrderID[1] == 'H':
#         EV_MSG_CAL2 = "horz"
#         STR_CAL2 = "horizontal"
#         EV_MSG_CAL3 = "vert"
#         STR_CAL3 = "vertical"
#     if calOrderID[1] == 'V':
#         EV_MSG_CAL2 = "vert"
#         STR_CAL2 = "vertical"
#         EV_MSG_CAL3 = "horz"
#         STR_CAL3 = "horizontal"

## Create text messages
st_exp_msg = createMessage(w, FG_COLOUR, 'Please wait for experimenter instructions.\nPress any key to continue.')
end_exp_msg = createMessage(w, FG_COLOUR, 'End of Experiment. \nPress any key to exit.')
exit_msg = createMessage(w, FG_COLOUR, 'Exiting...')


# st_cal_msg1 = createMessage(w, FG_COLOUR, 'Press any key to begin ' + STR_CAL1 + ' EOG calibration.')
# end_cal_msg1 = createMessage(w, FG_COLOUR, 'End of ' + STR_CAL1 + ' EOG calibration. \nPress any key to continue.')

# st_cal_msg2 = createMessage(w, FG_COLOUR, 'Press any key to begin ' + STR_CAL2 + ' EOG calibration.')
# end_cal_msg2 = createMessage(w, FG_COLOUR, 'End of ' + STR_CAL2 + ' EOG calibration. \nPress any key to continue.')

# st_cal_msg3 = createMessage(w, FG_COLOUR, 'Press any key to begin ' + STR_CAL3 + ' EOG calibration.')
# end_cal_msg3 = createMessage(w, FG_COLOUR, 'End of ' + STR_CAL3 + ' EOG calibration. \nPress any key to continue.')



# end_cond_msg1 = createMessage(w, FG_COLOUR, 'End of ' + STR_CAL1 + ' eye-movement condition.\nPress any key to continue.')
# end_cond_msg2 = createMessage(w, FG_COLOUR, 'End of ' + STR_CAL2 + ' eye-movement condition.\nPress any key to continue.')
# end_cond_msg3 = createMessage(w, FG_COLOUR, 'End of ' + STR_CAL3 + ' eye-movement condition.\nPress any key to continue.')


# EV_CAL1_MSG_ST = ["cal_" + EV_MSG_CAL1 + "_start"]
# EV_CAL1_MSG_EN = ["cal_" + EV_MSG_CAL1 + "_end"]
# EV_EXP1_MSG_ST = ["exp_" + EV_MSG_CAL1 + "_start"]
# EV_EXP1_MSG_EN = ["exp_" + EV_MSG_CAL1 + "_end"]
# EV_CAL2_MSG_ST = ["cal_" + EV_MSG_CAL2 + "_start"]
# EV_CAL2_MSG_EN = ["cal_" + EV_MSG_CAL2 + "_end"]
# EV_EXP2_MSG_ST = ["exp_" + EV_MSG_CAL2 + "_start"]
# EV_EXP2_MSG_EN = ["exp_" + EV_MSG_CAL2 + "_end"]
# EV_CAL3_MSG_ST = ["cal_" + EV_MSG_CAL3 + "_start"]
# EV_CAL3_MSG_EN = ["cal_" + EV_MSG_CAL3 + "_end"]
# EV_EXP3_MSG_ST = ["exp_" + EV_MSG_CAL3 + "_start"]
# EV_EXP3_MSG_EN = ["exp_" + EV_MSG_CAL3 + "_end"]



# set up a custom graphics envrionment (EyeLinkCoreGraphicsPsychopy) for calibration
genv = EyeLinkCoreGraphicsPsychoPy(elTk, w)

# play feedback beeps during calibration/validation, disabled by default
genv.enableBeep = True
pylink.setCalibrationSounds("", "", "")
# calibration target size 
genv.targetSize = 14
# Configure the calibration target, could be a 'circle', 
# a movie clip ('movie'), a 'picture', or a 'spiral', the default is a circle
genv.calTarget = 'circle'
pylink.openGraphicsEx(genv)
### Start calibration and trial procedures ##################
pylink.beginRealTimeMode(100)

# Begin Eyelink recording (continuous mode, for trial-by-trial, see trial loop functions)
# if cond != 4 :
#     elTk.startRecording(1, 1, 1, 1)


exp_abort = False

if not exp_abort :

    for ii in range(len(calOrderID)) :

        
        EV_MSG_CAL, STR_CAL = set_calibration_messages(calOrderID[ii])
        st_cal_msg = createMessage(w, FG_COLOUR, 'Press any key to begin ' + STR_CAL + ' EOG calibration.')
        end_cal_msg = createMessage(w, FG_COLOUR, 'End of ' + STR_CAL + ' EOG calibration. \nPress any key to continue.')
        end_cond_msg = createMessage(w, FG_COLOUR, 'End of ' + STR_CAL + ' eye-movement condition.\nPress any key to continue.')
        EV_CAL_MSG_ST = ["cal_" + EV_MSG_CAL + "_start"]
        EV_CAL_MSG_EN = ["cal_" + EV_MSG_CAL + "_end"]
        EV_EXP_MSG_ST = ["exp_" + EV_MSG_CAL + "_start"]
        EV_EXP_MSG_EN = ["exp_" + EV_MSG_CAL + "_end"]

        # Run calibration routine
        if not exp_abort and run_calib_trials :

            is_calib = True
            ## Run calibration procedure for Eyelink & EOG linearization
            ev_outlet.push_sample(EV_CAL_MSG_ST) # XDF/LSL event message
            
            if cond != 4 :
                elTk.sendMessage(EV_CAL_MSG_ST) # EDF event message
            
            exp_abort = ss_runcalibs(w, calOrderID[ii], FG_COLOUR, BG_COLOUR, RED, GRN, PPCM, st_cal_msg, end_cal_msg, caliOrderHorz, numCalibTargets, numTrialsPerTarget_HorzCalib, isi, angles_horz, angles_vert, fix_shift, ev_outlet, eog_conn, el_outlet, elTk, EYE_TO_SCREEN_CM)
            ev_outlet.push_sample(EV_CAL_MSG_EN) # XDF/LSL event message
            
            if cond != 4 :
                elTk.sendMessage(EV_CAL_MSG_EN) # EDF event message     

        # Run experiment routine
        if not exp_abort:

            ev_outlet.push_sample(EV_EXP_MSG_ST) # XDF/LSL event message
            if cond != 4 :
                elTk.sendMessage(EV_EXP_MSG_ST) # EDF event message

            ev_outlet.push_sample(["cond" + str(cond) + "_start"])

            if cond != 4 :

                elTk.sendMessage(["cond" + str(cond) + "_start"])
                if cond == 1:
                    exp_abort = ss_runtrials(w, FG_COLOUR, BG_COLOUR, RED, GRN, PPCM, st_exp_msg, end_cond_msg, trialTargetOrder[ii][0:], trialBlockNumber[ii][0:], blockNumbers[ii][0:], blockMarkersOn[ii][0:], blockTargDir[ii][0:], isi, angles_horz, angles_vert, fix_shift, ev_outlet, eog_conn, el_outlet, elTk, EYE_TO_SCREEN_CM)           
                elif cond == 2:
                    ss_runtrials_cond2(w, FG_COLOUR, BG_COLOUR, RED, GRN, PPCM, st_exp_msg, end_cond_msg, trialTargetOrder[ii][0:], trialBlockNumber[ii][0:], blockNumbers[ii][0:], blockEyesOpen[ii][0:], isi, angles_horz, angles_vert, fix_shift, ev_outlet, eog_conn, el_outlet, elTk)
            
            ev_outlet.push_sample(["cond" + str(cond) + "_end"])
            ev_outlet.push_sample(EV_EXP_MSG_EN)
           
            if cond != 4 :
                elTk.sendMessage(["cond" + str(cond) + "_end"])
                elTk.sendMessage(EV_EXP_MSG_EN)


        # if not exp_abort and run_calib_trials:
        
        #     is_calib = True
        #     ## Run calibration procedure for Eyelink & EOG linearization
        #     ev_outlet.push_sample(EV_CAL2_MSG_ST)
        #     if cond != 4 :
        #         elTk.sendMessage(EV_CAL2_MSG_ST)
        #     exp_abort = ss_runcalibs(w, calOrderID[1], FG_COLOUR, BG_COLOUR, RED, GRN, PPCM, st_cal_msg2, end_cal_msg2, caliOrderHorz, numCalibTargets, numTrialsPerTarget_HorzCalib, isi, angles_horz, angles_vert, fix_shift, ev_outlet, eog_conn, el_outlet, elTk, EYE_TO_SCREEN_CM)
        #     ev_outlet.push_sample(EV_CAL2_MSG_EN)
        #     if cond != 4 :
        #         elTk.sendMessage(EV_CAL2_MSG_EN)
        
        # if not exp_abort:
        #     ev_outlet.push_sample(EV_EXP2_MSG_ST) # XDF/LSL event message
        #     if cond != 4 :
        #         elTk.sendMessage(EV_EXP2_MSG_ST) # EDF event message

        #     ev_outlet.push_sample(["cond" + str(cond) + "_start"])
        #     if cond != 4 :
                
        #         elTk.sendMessage(["cond" + str(cond) + "_start"])

        #         if cond == 1:
        #             exp_abort = ss_runtrials(w, FG_COLOUR, BG_COLOUR, RED, GRN, PPCM, st_exp_msg, end_cond_msg2, trialTargetOrder[1][0:], trialBlockNumber[1][0:], blockNumbers[1][0:], blockMarkersOn[1][0:], blockTargDir[1][0:], isi, angles_horz, angles_vert, fix_shift, ev_outlet, eog_conn, el_outlet, elTk, EYE_TO_SCREEN_CM)           
        #         elif cond == 2:
        #             ss_runtrials_cond2(w, FG_COLOUR, BG_COLOUR, RED, GRN, PPCM, st_exp_msg, end_cond_msg2, trialTargetOrder[1][0:], trialBlockNumber[1][0:], blockNumbers[1][0:], blockEyesOpen[1][0:], isi, angles_horz, angles_vert, fix_shift, ev_outlet, eog_conn, el_outlet, elTk)

        #     ev_outlet.push_sample(["cond" + str(cond) + "_end"])
        #     ev_outlet.push_sample(EV_EXP2_MSG_EN)      
        #     if cond != 4 :
        #         elTk.sendMessage(["cond" + str(cond) + "_end"])
        #         elTk.sendMessage(EV_EXP2_MSG_EN)    

        # if not exp_abort and run_calib_trials:
        
        #     is_calib = True
        #     ## Run calibration procedure for Eyelink & EOG linearization
        #     ev_outlet.push_sample(EV_CAL3_MSG_ST)
        #     if cond != 4 :
        #         elTk.sendMessage(EV_CAL3_MSG_ST)
        #     exp_abort = ss_runcalibs(w, calOrderID[2], FG_COLOUR, BG_COLOUR, RED, GRN, PPCM, st_cal_msg3, end_cal_msg3, caliOrderHorz, numCalibTargets, numTrialsPerTarget_HorzCalib, isi, angles_horz, angles_vert, fix_shift, ev_outlet, eog_conn, el_outlet, elTk, EYE_TO_SCREEN_CM)
        #     ev_outlet.push_sample(EV_CAL3_MSG_EN)
        #     if cond != 4 :
        #         elTk.sendMessage(EV_CAL3_MSG_EN)
        
        # if not exp_abort:
        #     ev_outlet.push_sample(EV_EXP3_MSG_ST) # XDF/LSL event message
        #     if cond != 4 :
        #         elTk.sendMessage(EV_EXP3_MSG_ST) # EDF event message

        #     ev_outlet.push_sample(["cond" + str(cond) + "_start"])
        #     if cond != 4 :
                
        #         elTk.sendMessage(["cond" + str(cond) + "_start"])

        #         if cond == 1:
        #             exp_abort = ss_runtrials(w, FG_COLOUR, BG_COLOUR, RED, GRN, PPCM, st_exp_msg, end_cond_msg3, trialTargetOrder[2][0:], trialBlockNumber[2][0:], blockNumbers[2][0:], blockMarkersOn[2][0:], blockTargDir[2][0:], isi, angles_horz, angles_vert, fix_shift, ev_outlet, eog_conn, el_outlet, elTk, EYE_TO_SCREEN_CM)           
        #         elif cond == 2:
        #             ss_runtrials_cond2(w, FG_COLOUR, BG_COLOUR, RED, GRN, PPCM, st_exp_msg, end_cond_msg3, trialTargetOrder[2][0:], trialBlockNumber[2][0:], blockNumbers[2][0:], blockEyesOpen[2][0:], isi, angles_horz, angles_vert, fix_shift, ev_outlet, eog_conn, el_outlet, elTk)

        #     ev_outlet.push_sample(["cond" + str(cond) + "_end"])
        #     ev_outlet.push_sample(EV_EXP3_MSG_EN)      
        #     if cond != 4 :
        #         elTk.sendMessage(["cond" + str(cond) + "_end"])
        #         elTk.sendMessage(EV_EXP3_MSG_EN)

# Ask if we would like to run Cond 2 (Non-Illuminated)
run_cond2 = False
if not exp_abort :
    if cond == 1:

        try:
            msg = 'EDF data is transfering from EyeLink Host PC...'
            edfTransfer = visual.TextStim(w, text=msg, color='white')
            edfTransfer.draw()
            w.flip()
            pylink.pumpDelay(500)
        except Exception as e:
            raise

        event.clearEvents()    
        exp_quit = False
        while not exp_quit :
            end_exp_msg.draw()  # automatically draw every frame
            w.flip()
            keys = event.getKeys()  # get keys from event buffer

            if keys:
                exp_quit = True

        w.close()
        w.mouseVisible = True

        # user_prac = raw_input("End of Condition 1. Run Condition 2 now? (y/n) ")
        # if user_prac.startswith('y') or user_prac.startswith('Y') :
        #     run_cond2 = True
        #     cond = 2
        # else :
        #     user_prac = raw_input("Really skip Condition 2? (y/n)") 
        #     if user_prac.startswith('n') or user_prac.startswith('N') :
        #         run_cond2 = True

        # if run_cond2 :
        #     exit_cond2 = False
        #     print("\nPlease select the config file for Condition 2...")

        #     trialTargetOrder, trialBlockNumber, blockNumbers, blockEyesOpen = load_cond2_config_file()

        #     if not all(np.size(x) > 0 for x in [trialTargetOrder, trialBlockNumber, blockNumbers, blockEyesOpen]) :
        #         print('')
        #         print("Config Error! Could not load or parse CSV file successfully. Exiting...")
        #         exit_cond2 = True

        #     n_trials = np.size(trialTargetOrder, axis=0)
        #     num_blocks = np.size(np.unique(trialBlockNumber), axis=0)
        #     block_length = n_trials/num_blocks

        #     print("""
        #     Press ENTER to begin 15 minute period of dark adaptation, 
        #     Press S to skip and begin Cond 2 immediately,
        #     Press ESC to abort Cond 2 and exit.
        #     """)
        #     wait_cond2 = False
        #     while True :
        #         if msvcrt.kbhit() :
        #             ch = msvcrt.getch() 
        #             if ch == b'\x1b' :
        #                 run_cond2 = False
        #                 exit_cond2 = True
        #             elif ch == 's' : 
        #                 break
        #             elif ch == '\r' :
        #                 wait_cond2 = True
        #                 break
            
        #     if not exit_cond2 :
        #         if wait_cond2 :
        #             consoleTimer(15,0) # 15 minute timer coundown in console

        #         print('')
        #         raw_input("COND " +str(cond) + ": Turn off TV now! Press ENTER to continue...")

        #         block_markers_str = ' '.join(str(b) for b in blockEyesOpen)
        #         dems_row = [pname, str(cond), str(ipd), exp_date, str(block_length), block_markers_str, str(n_trials)]
        #         with open(dems_out, 'ab') as csvfile :
        #             demswriter = csv.writer(csvfile, delimiter=',')
        #             demswriter.writerow(dems_row)

        #         #create a window
        #         w = visual.Window(monitor="Samsung UN55KU6290", screen=1, size=SCREEN_RES, fullscr=True, color=BG_COLOUR, units="cm")
        #         w.mouseVisible = False

        #         # Run trials
        #         ev_outlet.push_sample(["cond" + str(cond) + "_start"])
        #         if cond != 4 :
        #             elTk.sendMessage(["cond" + str(cond) + "_start"])
        #             ss_runtrials_cond2(w, FG_COLOUR, BG_COLOUR, RED, GRN, PPCM, st_exp_msg, end_exp_msg, trialTargetOrder, trialBlockNumber, blockNumbers, blockEyesOpen, isi, TOFFSETX_HORZ_SM, TOFFSETX_HORZ_LG, fix_shift, ev_outlet, eog_conn, el_outlet, elTk)           
        #         else :
        #             ss_runtrials_cond2(w, FG_COLOUR, BG_COLOUR, RED, GRN, PPCM, st_exp_msg, end_exp_msg, trialTargetOrder, trialBlockNumber, blockNumbers, blockEyesOpen, isi, TOFFSETX_HORZ_SM, TOFFSETX_HORZ_LG, fix_shift, ev_outlet, eog_conn, None, None)                
        #         ev_outlet.push_sample(["cond" + str(cond) + "_end"])
        #         if cond != 4 :
        #             elTk.sendMessage(["cond" + str(cond) + "_end"])


# ev_outlet.push_sample(["exp_end"])
# if cond != 4 :
#     elTk.sendMessage(["exp_end"])

# End Eyelink recording after trials are complete (continuous mode only, for trial-by-trial see trial functions)
# if cond != 4 :
#     elTk.stopRecording()

# end_message.setAutoDraw(False)
# exit_message.setAutoDraw(True)
if exp_abort or (run_cond2 is not False):
    try:
        exit_msg.draw()
        w.flip()
    except :
        pass


### Terminate Eyelink stream
pylink.endRealTimeMode()

if cond != 4 :
    elTk.setOfflineMode()     

    # download EDF file to Display PC and put it in local folder ('edfData')
    if exp_abort or (run_cond2 is not False):
        try:
            msg = 'EDF data is transfering from EyeLink Host PC...'
            edfTransfer = visual.TextStim(w, text=msg, color='white')
            edfTransfer.draw()
            w.flip()
            pylink.pumpDelay(500)
        except Exception as e:
            raise
         
    # Close the file and transfer it to Display PC
    elTk.closeDataFile()
    elTk.receiveDataFile(edfn, edf_out_path+edfn)
    elTk.close()

    if exp_abort or (run_cond2 is not False):
        try:
            w.flip()
        except:
            pass

if exp_abort or (run_cond2 is not False):
    try:
        w.close()
        w.mouseVisible = True
    except:
        pass

if labrecorder_process.poll() is None :
    time.sleep(2)
    print("")
    print('Waiting for Lab Recorder, stop recording stream to end experiment.')
    print("")
    
    while 1:
        lr_msg = b"D"
        try:
            lr_msg = socket_lr.recv(2) # buffer size is 1 bytes (1 character + null)
        except:
            pass
        
        if lr_msg.startswith(b"e"):
            break

        if labrecorder_process.poll() is not None :
            break

# Terminate Lab Recorder if needed
if labrecorder_process.poll() is None :
    labrecorder_process.kill()

print('Exiting program...')
print('')

#cleanup
core.quit()