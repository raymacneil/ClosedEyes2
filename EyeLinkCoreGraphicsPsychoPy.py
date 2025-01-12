# Copyright (C) 2018-2020 Zhiguo Wang

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version. 
# This program is distribu
# 
# ted in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details. 
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# Rev. March, 2018
# 1. added the print_function for Python 3 support
# 2. use the list(zip(x,y)) function to make sure zip returns a list
# 3. Added an image scaling factor to accommodate all versions of the API
# 4. Added the missing CR adjustment keys (-/+=)
# 5. revised the draw_image_line function
# 6. tracker parameters set at initialization

# Rev. July, 2018
# 1. Force drawing in absolute pixel coordinates, switch back to the units
#    set by the user at the end of the calibration routine.
# 2. Updated the draw camera image function
# 3. Updated the draw lozenge function
# 4. camera image and drawing are all properly scaled

# Rev. August 22, 2018
# 1. Misplacement of calibration targets on Macs
# 2. Misalignment of crosshairs/squares and camera image

# Rev. February 5, 2019
# 1. Misalighnment of crosshairs/squares on Mac

# Rev. September 10, 2019
# 1. clear screen when entering camera setup mode
# 2. tested with PsychoPy version 3.2.2
# 3. Reformatted the calibration instructions to improve code clarity
# 4. Added support for video calibration target

# Rev. Janurary 28, 2020
# 1. added options to change calibration background/target color
# 2. Allow using picture as the calibration target
# 3. allow users to disable the beeps
# 4. Set audio lib to pyo and pygame to prevent sound track issues (when 
#    using movie clip as calibration target)
# 5. deleted lines for setting tracker parameters

# Rev. August 4, 2020
# 1. fixed textStim() compatibility issue for version 2020.1.x 
#    "alignHoriz" and alignVert were depricated from version 2020 (also know as PsychoPy 3.3), 
#    use "alignText", "anchorHoriz" & "anchorVer" instead
# 2. Added a "mouse simulation" warning on screen
# 3. fixed a bug related prefs setting in PsychoPy2
# 4. Show the calibration instructions, even when the camera image is hidden
# 5. prepare the calibration target in memory for faster drawing

from __future__ import division
from __future__ import print_function

import array, string, pylink, os, numpy, psychopy
from psychopy import visual, event, core, sound
from psychopy.tools.coordinatetools import pol2cart
from math import sin, cos, pi
from PIL import Image


# set audio lib to pyo and pygame to pevent soundtrack issues with movie clips
from psychopy import prefs
# for Psychopy2 (version # 1.9.x, there is no hardware module in prefs, use "general" instead
if psychopy.__version__.split('.')[0] == '1':
    prefs.general['audioLib'] = ['pyo', 'pygame']
else:
    prefs.hardware['audioLib'] = ['pyo', 'pygame']
    
    
class EyeLinkCoreGraphicsPsychoPy(pylink.EyeLinkCustomDisplay):
    def __init__(self, tracker, win):
        
        '''Initialize a Custom EyeLinkCoreGraphics  
        
        tracker: an eye-tracker instance
        win: the Psychopy display we plan to use for stimulus presentation  '''
        
        pylink.EyeLinkCustomDisplay.__init__(self)

        # calibration background color and target color
        self.backgroundColor = win.color
        self.foregroundColor = [0,0,0]
        
        # minor version of Pylink: 1-Mac, 11-Win/Linux
        self.pylinkMinorVer = pylink.__version__.split('.')[1]
        
        # major version # for PsychoPy, from version 3.3, the major version is the year of release
        self.psychopyVer = int(psychopy.__version__.split('.')[0])
        
        self.display = win
        self.w, self.h = win.size
        # on Macs with HiDPI screens, force the drawing routine to use the size defined
        # in the monitor instance, as win.size will give the wrong size of the screen
        if os.name == 'posix':
            self.w,self.h = win.monitor.getSizePix()
            
        #self.display.autoLog = False
        # check the screen units of Psychopy, forcing the screen to use 'pix'
        self.units = win.units
        if self.units != 'pix': 
            self.display.setUnits('pix')
        
        # Simple warning beeps
        self.enableBeep = False
        self.__target_beep__ = sound.Sound('Sound_Files\\type.wav')
        self.__target_beep__done__ = sound.Sound('Sound_Files\\qbeep.wav')
        self.__target_beep__error__ = sound.Sound('Sound_Files\\error.wav')
        # self.__target_beep__ = sound.Sound('A', octave=4, secs=0.1, volume=0.5)
        # self.__target_beep__done__ = sound.Sound('E', octave=4, secs=0.1, volume=0.5)
        # self.__target_beep__error__ = sound.Sound('E', octave=6, secs=0.1, volume=0.5)
        
        self.imgBuffInitType = 'I'
        self.imagebuffer = array.array(self.imgBuffInitType)
        self.resizeImagebuffer = array.array(self.imgBuffInitType)
        self.pal = None
        self.img_scaling_factor = 3
        self.size = (192*self.img_scaling_factor, 160*self.img_scaling_factor)
        
        # initial setup for the mouse
        self.display.mouseVisible = False
        self.mouse = event.Mouse(visible=False)
        self.last_mouse_state = -1

        # image title & calibration instructions
        self.msgHeight = self.size[1]/20.0
        self.title = visual.TextStim(self.display,'', height=self.msgHeight, color=[1,1,1],
                                     pos = (0,-self.size[1]/2-self.msgHeight), wrapWidth=self.w, units='pix')

        self.calibInst = visual.TextStim(self.display, height=self.msgHeight, color=[1,1,1],
                                        pos = (20-self.w/2.0, self.h/2.0-20), units='pix',
                                        text = 'Enter: Show/Hide camera image\n' +
                                        'Left/Right: Switch camera view\n' + 
                                        'C: Calibration\n' + 
                                        'V: Validation\n' + 
                                        'O: Start Recording\n' + 
                                        '+=/-: CR threshold\n' + 
                                        'Up/Down: Pupil threshold\n' + 
                                        'Alt+arrows: Search limit')
        
        # show some instruction to let the experimenter know that the tracker
        # is running in mouse simulation mode
        self.msgMouseSim = visual.TextStim(self.display, height=self.msgHeight, color=[1,1,1], units='pix',
                                        text = 'Tracker is simulating gaze using the mouse\n' +
                                        'NO CAMERA IMAGE IS AVAILABLE')
        self.camImgRect = visual.Rect(self.display, width=self.size[0], height=self.size[1], 
                                        lineColor=[1,1,1], units='pix')


        # alignHoriz and alignVert were depricated from version 2020 (also know as PsychoPy 3.3), 
        # use anchorHoriz & anchorVer instead
        if self.psychopyVer > 3:
            self.calibInst.alignText='left'
            self.calibInst.anchorHoriz='left'
            self.calibInst.anchorVert ='top'
        else:
            self.calibInst.alignHoriz='left'
            self.calibInst.alignVert ='top'
        
        # lines for drawing cross hair etc.
        self.line = visual.Line(self.display, start=(0, 0), end=(0,0),
                                lineWidth=2.0, lineColor=[0,0,0], units='pix')

        # configure the calibration target
        self.targetSize = self.w/128.
        self.calTarget = 'circle' # could be 'circle', 'picture', 'spiral', 'movie'
        self.animatedTarget = False # this is like a switch, when it's turned on the animated target is displayed
        self.movieTargetFile = None
        self.pictureTargetFile = None

        # make sure the tracker know the correct screen resolution being used
        self.tracker = tracker
        self.tracker.sendCommand("screen_pixel_coords = 0 0 %d %d" % (self.w-1, self.h-1))
        
        # tracker in mouse simulation mode?
        self.mouse_simulation = False

    def update_cal_target(self):
        ''' make sure target stimuli is already memory when being used by draw_cal_target '''
        
        if self.calTarget is 'picture':
            if self.pictureTargetFile is None:
                print('ERROR: Clibration target is None, please provide a picture')
                core.quit()
            else:
                self.calibTar = visual.ImageStim(self.display, self.pictureTargetFile, size=self.targetSize)
                
        elif self.calTarget is 'spiral':
            thetas = numpy.arange(0,1440,10)
            N=len(thetas)
            radii = numpy.linspace(0,1.0,N)*self.targetSize
            x, y = pol2cart(theta=thetas, radius=radii)
            xys = numpy.array([x,y]).transpose()
            self.calibTar = visual.ElementArrayStim(self.display, nElements=N, sizes=self.targetSize,
                                                    sfs=3.0, xys=xys, oris=-thetas)
        elif self.calTarget is 'movie':
            if self.movieTargetFile is None:
                print('ERROR: Clibration target is None, please provide a movie clip')
                core.quit()
            else:
                self.calibTar = visual.MovieStim3(self.display, self.movieTargetFile, loop=True, size=self.targetSize)
                
        else: #'use the default 'circle'
            self.calibTar = visual.Circle(self.display, radius=self.targetSize/2, lineColor=self.foregroundColor,
                                          fillColor=self.backgroundColor, lineWidth=self.targetSize/2.0, units='pix')

    def setup_cal_display(self):
        '''Set up the calibration display before entering the calibration/validation routine'''

        self.display.clearBuffer()
        #self.clear_cal_display()

        self.calibInst.autoDraw = True
        self.animatedTarget = False
        self.update_cal_target()

    def clear_cal_display(self):
        '''Clear the calibration display'''
        
        self.calibInst.autoDraw = False
        self.title.autoDraw = False
        self.msgMouseSim.autoDraw = False
        self.camImgRect.autoDraw = False

        self.display.clearBuffer()
        self.display.color = self.backgroundColor
        self.display.flip()
        
    def exit_cal_display(self):
        '''Exit the calibration/validation routine, set the screen units to
        the original one used by the user'''
        
        self.display.setUnits(self.units)
        self.clear_cal_display()
        self.animatedTarget = False

    def record_abort_hide(self):
        '''This function is called if aborted'''
        
        pass

    def erase_cal_target(self):
        '''Erase the calibration/validation & drift-check target'''

        self.clear_cal_display()
        if self.calTarget is 'movie':
            if self.movieTargetFile is not None:
                self.calibTar.pause()

        self.animatedTarget = False
        self.display.flip()

    def draw_cal_target(self, x, y):
        '''Draw the calibration/validation & drift-check  target'''
        
        self.clear_cal_display()
        xVis = (x -  self.w/2)
        yVis = (self.h/2 - y)
        
        # update the target position
        if self.calTarget is 'spiral':
            self.calibTar.fieldPos = (xVis, yVis)
        else:
            self.calibTar.pos = (xVis, yVis)

        # handle the drawing
        if self.calTarget in ['spiral', 'movie']:
            self.animatedTarget = True # hand over drawing to get_input_key
            if self.calTarget in ['movie']:
                if self.movieTargetFile is not None:
                    self.calibTar.play()
        else:
            self.calibTar.draw()
            self.display.flip()

    def play_beep(self, beepid):
        ''' Play a sound during calibration/drift correct.'''

        if self.enableBeep:
            if beepid == pylink.CAL_TARG_BEEP : # or beepid == pylink.DC_TARG_BEEP:
                self.__target_beep__.play()
            if beepid == pylink.CAL_ERR_BEEP : # or beepid == pylink.DC_ERR_BEEP:
                self.__target_beep__error__.play()
            if beepid in [pylink.CAL_GOOD_BEEP] : #, pylink.DC_GOOD_BEEP]:
                self.__target_beep__done__.play()
        else:
            pass

    def getColorFromIndex(self, colorindex):
         '''Return psychopy colors for elements in the camera image'''
         
         if colorindex   ==  pylink.CR_HAIR_COLOR:          return (1, 1, 1)
         elif colorindex ==  pylink.PUPIL_HAIR_COLOR:       return (1, 1, 1)
         elif colorindex ==  pylink.PUPIL_BOX_COLOR:        return (-1, 1, -1)
         elif colorindex ==  pylink.SEARCH_LIMIT_BOX_COLOR: return (1, -1, -1)
         elif colorindex ==  pylink.MOUSE_CURSOR_COLOR:     return (1, -1, -1)
         else:                                              return (0,0,0)

    def draw_line(self, x1, y1, x2, y2, colorindex):
        '''Draw a line. This is used for drawing crosshairs/squares'''
        
        if self.pylinkMinorVer== '1': # the Mac version
            x1 = x1/2; y1=y1/2; x2=x2/2;y2=y2/2;
        y1 = (-y1  + self.size[1]/2)* self.img_scaling_factor 
        x1 = (+x1  - self.size[0]/2)* self.img_scaling_factor 
        y2 = (-y2  + self.size[1]/2)* self.img_scaling_factor 
        x2 = (+x2  - self.size[0]/2)* self.img_scaling_factor 
        color = self.getColorFromIndex(colorindex)
        self.line.start     = (x1, y1)
        self.line.end       = (x2, y2)
        self.line.lineColor = color
        self.line.draw()

    def draw_lozenge(self, x, y, width, height, colorindex):
        ''' draw a lozenge to show the defined search limits
        (x,y) is top-left corner of the bounding box
        '''

        if self.pylinkMinorVer == '1': # Mac version
            x = x/2; y=y/2; width=width/2;height=height/2;
        width = width * self.img_scaling_factor
        height = height* self.img_scaling_factor
        y = (-y + self.size[1]/2)* self.img_scaling_factor 
        x = (+x - self.size[0]/2)* self.img_scaling_factor       
        color = self.getColorFromIndex(colorindex)
        
        if width > height:
            rad = height / 2
            if rad == 0: return #cannot draw the circle with 0 radius
            Xs1 = [rad*cos(t) + x + rad for t in numpy.linspace(pi/2, pi/2+pi, 72)]
            Ys1 = [rad*sin(t) + y - rad for t in numpy.linspace(pi/2, pi/2+pi, 72)]
            Xs2 = [rad*cos(t) + x - rad + width for t in numpy.linspace(pi/2+pi, pi/2+2*pi, 72)]
            Ys2 = [rad*sin(t) + y - rad for t in numpy.linspace(pi/2+pi, pi/2+2*pi, 72)]
        else:
            rad = width / 2
            if rad == 0: return #cannot draw sthe circle with 0 radius
            Xs1 = [rad*cos(t) + x + rad for t in numpy.linspace(0, pi, 72)]
            Ys1 = [rad*sin(t) + y - rad for t in numpy.linspace(0, pi, 72)]
            Xs2 = [rad*cos(t) + x + rad for t in numpy.linspace(pi, 2*pi, 72)]
            Ys2 = [rad*sin(t) + y + rad - height for t in numpy.linspace(pi, 2*pi, 72)]

        lozenge = visual.ShapeStim(self.display, vertices = list(zip(Xs1+Xs2, Ys1+Ys2)),
                                    lineWidth=2.0, lineColor=color, closeShape=True, units='pix')    
        lozenge.draw()

    def get_mouse_state(self):
        '''Get the current mouse position and status'''
        
        X, Y = self.mouse.getPos()
        mX = self.size[0]/2.0*self.img_scaling_factor + X 
        mY = self.size[1]/2.0*self.img_scaling_factor - Y
        if mX <=0: mX =  0
        if mX > self.size[0]*self.img_scaling_factor:
            mX = self.size[0]*self.img_scaling_factor
        if mY < 0: mY =  0
        if mY > self.size[1]*self.img_scaling_factor:
            mY = self.size[1]*self.img_scaling_factor
        state = self.mouse.getPressed()[0] 
        mX = mX/self.img_scaling_factor
        mY = mY/self.img_scaling_factor
        
        if self.pylinkMinorVer == '1':
            mX = mX *2; mY = mY*2
        return ((mX, mY), state)


    def get_input_key(self):
        ''' this function will be constantly pools, update the stimuli here is you need
        dynamic calibration target '''

        # this function is constantly checked by the API, so we could update the gabor here
        if self.animatedTarget:
            if self.calTarget is 'spiral':
                self.calibTar.phases -=0.02
            self.calibTar.draw()
            self.display.flip()

        ky=[]
        for keycode, modifier in event.getKeys(modifiers=True):
            k= pylink.JUNK_KEY
            if keycode   == 'f1': k = pylink.F1_KEY
            elif keycode == 'f2': k = pylink.F2_KEY
            elif keycode == 'f3': k = pylink.F3_KEY
            elif keycode == 'f4': k = pylink.F4_KEY
            elif keycode == 'f5': k = pylink.F5_KEY
            elif keycode == 'f6': k = pylink.F6_KEY
            elif keycode == 'f7': k = pylink.F7_KEY
            elif keycode == 'f8': k = pylink.F8_KEY
            elif keycode == 'f9': k = pylink.F9_KEY
            elif keycode == 'f10': k = pylink.F10_KEY
            elif keycode == 'pageup': k = pylink.PAGE_UP
            elif keycode == 'pagedown': k = pylink.PAGE_DOWN
            elif keycode == 'up': k = pylink.CURS_UP
            elif keycode == 'down': k = pylink.CURS_DOWN
            elif keycode == 'left': k = pylink.CURS_LEFT
            elif keycode == 'right': k = pylink.CURS_RIGHT
            elif keycode == 'backspace': k = ord('\b')
            elif keycode == 'return': 
                k = pylink.ENTER_KEY
                # probe the tracker to see if it's "simulating gaze with mouse"
                # if so, show a warning instead of a blank screen to experimenter
                # do so, only when the tracker is in Camera Setup screen
                if self.tracker.getCurrentMode() is pylink.IN_SETUP_MODE:
                    self.tracker.readRequest('aux_mouse_simulation')
                    pylink.pumpDelay(50)
                    if self.tracker.readReply() is '1':
                        self.msgMouseSim.autoDraw = True
                        self.camImgRect.autoDraw = True
                        self.calibInst.autoDraw = True
                        self.display.flip()
            elif keycode == 'space': k = ord(' ')
            elif keycode == 'escape': k = pylink.ESC_KEY
            elif keycode == 'tab': k = ord('\t')
            elif keycode in string.ascii_letters: k = ord(keycode)
            elif k== pylink.JUNK_KEY: k = 0

            # plus/equal & minux signs for CR adjustment
            if keycode in ['num_add', 'equal']: k = ord('+')
            if keycode in ['num_subtract', 'minus']: k = ord('-')

            if modifier['alt']==True: mod = 256
            else: mod = 0
            
            ky.append(pylink.KeyInput(k, mod))
            #event.clearEvents()
        return ky

    def exit_image_display(self):
        '''Clcear the camera image'''
        
        #self.clear_cal_display()
        self.calibInst.autoDraw=True
        self.title.autoDraw = False
        self.display.flip()

    def alert_printf(self,msg):
        '''Print error messages.'''
        
        print("Error: " + msg)

    def setup_image_display(self, width, height): 
        ''' set up the camera image, for newer APIs, the size is 384 x 320 pixels'''
        
        self.last_mouse_state = -1
        self.size = (width, height)
        self.title.autoDraw = True
        self.msgMouseSim.autoDraw = False
        self.camImgRect.autoDraw = False
        #self.calibInst.autoDraw=True
        
    def image_title(self, text):
        '''Draw title text below the camera image'''
        
        self.title.text = text
        
    def draw_image_line(self, width, line, totlines, buff):
        '''Display image pixel by pixel, line by line'''

        self.size = (width, totlines)

        i =0
        for i in range(width):
            try: self.imagebuffer.append(self.pal[buff[i]])
            except: pass
            
        if line == totlines:
            bufferv = self.imagebuffer.tostring()
            img = Image.frombytes("RGBX", (width, totlines), bufferv) # Pillow
            imgResize = img.resize((width*self.img_scaling_factor, totlines*self.img_scaling_factor))
            imgResizeVisual = visual.ImageStim(self.display, image=imgResize, units='pix')
            imgResizeVisual.draw()
            self.draw_cross_hair()
            self.display.flip()
            self.imagebuffer = array.array(self.imgBuffInitType)
            
            
    def set_image_palette(self, r,g,b):
        '''Given a set of RGB colors, create a list of 24bit numbers representing the pallet.
        I.e., RGB of (1,64,127) would be saved as 82047, or the number 00000001 01000000 011111111'''
        
        self.imagebuffer = array.array(self.imgBuffInitType)
        self.resizeImagebuffer = array.array(self.imgBuffInitType)

        sz = len(r)
        i =0
        self.pal = []
        while i < sz:
            rf = int(b[i])
            gf = int(g[i])
            bf = int(r[i])
            self.pal.append((rf<<16) | (gf<<8) | (bf))
            i = i+1
