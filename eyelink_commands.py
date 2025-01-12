'''
Created on Jul 10, 2012
Updated Aug 17, 2016
@author: SCCN
'''

import pylink
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
from psychopy import sound
import numpy as np
import pylsl, socket, time, subprocess
# import msvcrt


def CalibrateEyelink(tracker):
    # put the tracker in idle mode before we change its parameters
    tracker.setOfflineMode()
    pylink.pumpDelay(100)

    tracker.doTrackerSetup()
    tracker.exitCalibration()



def CalibrateEyelinkPopup() :
    # Hand over tracker to CalibrateEyelink program which performs popup
    proc = subprocess.Popen(['python', 'CalibrateEyelink.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print proc.communicate()[0]

    # Restablish connection with Eyelink tracker
    try:
        tracker = pylink.EyeLink("255.255.255.255")    
        # print "Established a passive connection with the eye tracker."
    except:
        tracker = pylink.EyeLink("100.1.1.1")
        # print "Established a primary connection with the eye tracker."
    
    tracker.setFileSampleFilter('LEFT,RIGHT,GAZE,GAZERES,HREF,PUPIL,AREA,STATUS') 
    tracker.setLinkSampleFilter('LEFT,RIGHT,GAZE,GAZERES,HREF,PUPIL,AREA,STATUS')  
    tracker.sendCommand("file_sample_data = LEFT,RIGHT,GAZE,GAZERES,HREF,PUPIL,AREA,STATUS")
    tracker.sendCommand("link_sample_data = LEFT,RIGHT,GAZE,GAZERES,HREF,PUPIL,AREA,STATUS")

    return tracker


def manual_drift_correction(pos, tracker):
    # """
    # Performs a manual, i.e. spacebar-triggered drift correction.
 
    # Arguments:
    # pos     --  The positionf or the drift-correction target.
 
    # Returns:
    # True if drift correction was successfull, False otherwise.
    # """
    try:
        # The 0 parameters indicate that the display should not be cleared
        # and we should not be allowed to fall back to the set-up screen.
        error = tracker.doDriftCorrect(pos[0], pos[1], 0, 0)
    except:
        error = -1
    #print(error)
    return error
    # A 0 exit code means successful drift correction
    # if error == 27 or error == -1:
    #     return error
    # else:
    #     return 0


def CollectEyelinkSample(outlet, tracker, last_sample_time) :
    try :
        sample = tracker.getNewestSample()
        if sample is not None:
            now = pylsl.local_clock()
            ppd = sample.getPPD()
            el_ts = sample.getTime()
            values = [0,0,0,0, 0, ppd[0],ppd[1], el_ts, now]
            if (sample.isRightSample()) or (sample.isBinocular()):
                values[0:2] = sample.getRightEye().getGaze()
                values[2:4] = sample.getRightEye().getHREF()
                values[4] = sample.getRightEye().getPupilSize()
            
            if el_ts > last_sample_time :
                last_sample_time = el_ts
                outlet.push_sample(pylsl.vectord(values), now, True)

            return (values, last_sample_time)

    except Exception, e:		
        print "connection broke off: ", e
        

def CollectEyelinkSaccades(outlet, tracker, last_sample_time) :
    try :
        tracker.getNextData()
        newEvent = tracker.getFloatData()

        if isinstance(newEvent, pylink.Sample) :
            dist = 0
            now = pylsl.local_clock()
            ppd = newEvent.getPPD()
            el_ts = newEvent.getTime()
            values = [0,0,0,0, 0, ppd[0],ppd[1], el_ts, now]
            if (newEvent.isRightSample()) or (newEvent.isBinocular()):
                values[0:2] = newEvent.getRightEye().getGaze()
                values[2:4] = newEvent.getRightEye().getHREF()
                values[4] = newEvent.getRightEye().getPupilSize()
            if el_ts > last_sample_time :
                last_sample_time = el_ts
                outlet.push_sample(pylsl.vectord(values), now, True)
        elif isinstance(newEvent, pylink.EndSaccadeEvent) :
            Start_Gaze = newEvent.getStartGaze()
            Start_PPD = newEvent.getStartPPD()
            End_Gaze = newEvent.getEndGaze()
            End_PPD = newEvent.getEndPPD()
            dx = (End_Gaze[0] - Start_Gaze[0]) / ((End_PPD[0] + Start_PPD[0])/2.0)
            dy = (End_Gaze[1] - Start_Gaze[1]) / ((End_PPD[1] + Start_PPD[1])/2.0)
            dist = np.sqrt(dx*dx + dy*dy)
        else :
            dist = 0

        return (dist, last_sample_time)

    except Exception, e:		
        print "connection broke off: ", e
        

def InitEyelink(sr, fname) :
    outlet = None 
    edfFileName = fname

    ## Open LSL stream
    try:
        info = pylsl.stream_info("EyeLink","Gaze",9,sr,pylsl.cf_double64,"eyelink-" + socket.gethostname())
        channels = info.desc().append_child("channels")

        channels.append_child("channel") \
            .append_child_value("label", "rightEyeX") \
            .append_child_value("type", "eyetracking")
        channels.append_child("channel") \
            .append_child_value("label", "rightEyeY") \
            .append_child_value("type", "eyetracking")
        channels.append_child("channel") \
            .append_child_value("label", "rightEyeHRefX") \
            .append_child_value("type", "eyetracking")
        channels.append_child("channel") \
            .append_child_value("label", "rightEyeHRefY") \
            .append_child_value("type", "eyetracking")

        channels.append_child("channel") \
            .append_child_value("label", "rightPupilArea") \
            .append_child_value("type", "eyetracking")
        channels.append_child("channel") \
            .append_child_value("label", "pixelsPerDegreeX") \
            .append_child_value("type", "eyetracking")
        channels.append_child("channel") \
            .append_child_value("label", "pixelsPerDegreeY") \
            .append_child_value("type", "eyetracking")
        channels.append_child("channel") \
            .append_child_value("label", "eyelink_timestamp") \
            .append_child_value("type", "eyetracking")
        channels.append_child("channel") \
            .append_child_value("label", "LSL_timestamp") \
            .append_child_value("type", "eyetracking")
            
        outlet = pylsl.stream_outlet(info)
        print "Established LSL outlet for Eyelink data."
    except:
        print "Could not create LSL outlet for Eyelink data."
    
    print "Trying to connect to EyeLink tracker..."
    try:
        tracker = pylink.EyeLink("255.255.255.255")
        print "Established a passive connection with the eye tracker."
    except:
        tracker = pylink.EyeLink("100.1.1.1")
        print "Established a primary connection with the eye tracker."

    # put the tracker in idle mode before we change its parameters
    tracker.setOfflineMode()
    pylink.pumpDelay(100)

    eyelink_ver = tracker.getTrackerVersion()
    if eyelink_ver == 3:
        tvstr = tracker.getTrackerVersionString()
        vindex = tvstr.find("EYELINK CL")
        tracker_software_ver = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))

    tracker.setFileSampleFilter('LEFT,RIGHT,GAZE,GAZERES,HREF,PUPIL,AREA,STATUS')
    tracker.setLinkSampleFilter('LEFT,RIGHT,GAZE,GAZERES,HREF,PUPIL,AREA,STATUS')
    tracker.sendCommand("file_sample_data = LEFT,RIGHT,GAZE,GAZERES,HREF,PUPIL,AREA,STATUS")
    tracker.sendCommand("link_sample_data = LEFT,RIGHT,GAZE,GAZERES,HREF,PUPIL,AREA,STATUS")
    
    tracker.sendCommand("button_function 5 'accept_target_fixation'")
    tracker.setCalibrationType("HV9")
    
    # # set EDF file contents 
    # tracker.sendCommand("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
    # if tracker_software_ver>=4:
    #     tracker.sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,HREF,STATUS,HTARGET")
    # else:
    #     tracker.sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,HREF,STATUS")

    # # set link data (used for gaze cursor) 
    # tracker.sendCommand("link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
    # if tracker_software_ver>=4:
    #     tracker.sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,HREF,AREA,STATUS,HTARGET")
    # else:
    #     tracker.sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,HREF,AREA,STATUS")

    tracker.openDataFile(edfFileName)	
        
    return outlet, tracker