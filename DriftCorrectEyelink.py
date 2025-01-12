### DriftCorrectEyelink

from pylink import *
import sys
# import msvcrt

def main():
    # print "Trying to connect to EyeLink tracker..."
    print "Calibrating EyeLink..."
    try:
        tracker = EyeLink("255.255.255.255")
        # print "Established a passive connection with the eye tracker."
    except:
        tracker = EyeLink("100.1.1.1")
        # print "Established a primary connection with the eye tracker."

    # getEYELINK().setFileSampleFilter('LEFT,RIGHT,GAZE,GAZERES,HREF,PUPIL,AREA,STATUS')
    # getEYELINK().setLinkSampleFilter('LEFT,RIGHT,GAZE,GAZERES,HREF,PUPIL,AREA,STATUS')
    # getEYELINK().sendCommand("file_sample_data = LEFT,RIGHT,GAZE,GAZERES,HREF,PUPIL,AREA,STATUS")
    # getEYELINK().sendCommand("link_sample_data = LEFT,RIGHT,GAZE,GAZERES,HREF,PUPIL,AREA,STATUS")

    # getEYELINK().sendCommand("button_function 5 'accept_target_fixation'")
    # getEYELINK().setCalibrationType("HV9")

    # setCalibrationColors((255, 255, 255), (0, 0, 0))  	#Sets the calibration target and background color
    # setTargetSize(int(1920/70), int(1080/300))

    # setCalibrationSounds("", "", "")
    # setDriftCorrectSounds("", "off", "off")
    pos_x = sys.argv[1]
    pos_y = sys.argv[2]
    openGraphics([1920, 1080], 24)
    while getEYELINK().doDriftCorrect(pos_x, pos_y, 1, 1) != 27 :
        getEYELINK().doTrackerSetup()
    closeGraphics()

if __name__ == "__main__":
    main()


