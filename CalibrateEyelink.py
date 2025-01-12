### CalibrateEyelink

import pylink
# import msvcrt

# print "Trying to connect to EyeLink tracker..."
print "Calibrating EyeLink..."
try:
    tracker = pylink.EyeLink("255.255.255.255")
    # print "Established a passive connection with the eye tracker."
except:
    tracker = pylink.EyeLink("100.1.1.1")
    # print "Established a primary connection with the eye tracker."

# put the tracker in idle mode before we change its parameters
tracker.setOfflineMode()
pylink.pumpDelay(100)

tracker.setFileSampleFilter('LEFT,RIGHT,GAZE,GAZERES,HREF,PUPIL,AREA,STATUS')
tracker.setLinkSampleFilter('LEFT,RIGHT,GAZE,GAZERES,HREF,PUPIL,AREA,STATUS')
tracker.sendCommand("file_sample_data = LEFT,RIGHT,GAZE,GAZERES,HREF,PUPIL,AREA,STATUS")
tracker.sendCommand("link_sample_data = LEFT,RIGHT,GAZE,GAZERES,HREF,PUPIL,AREA,STATUS")

tracker.sendCommand("button_function 5 'accept_target_fixation'")
tracker.setCalibrationType("HV9")

# setCalibrationColors((255, 255, 255), (0, 0, 0))  	#Sets the calibration target and background color
# setTargetSize(int(1920/70), int(1080/300))

# setCalibrationSounds("", "", "")
# setDriftCorrectSounds("", "off", "off")

pylink.openGraphics([1920, 1080], 24)
tracker.doTrackerSetup()
tracker.exitCalibration()
pylink.closeGraphics()
