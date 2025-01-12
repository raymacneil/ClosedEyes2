from random import randrange
import pylink
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
from psychopy import visual, core, event, sound, tools
from pylsl import StreamInfo, StreamOutlet
from eyelink_commands import *
import numpy as np
import time
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 51000

vert_shift_cm = -3.0
VERT_MD = 2.625
EYE_TO_SCREEN_CM = 50.00 # 96.5 (old setup) 

# comment to ensure update
# Used to screen trial lists for no more than n consecutive targets
def has_consecutive_runs(a, n):
    da = np.diff(a) # finds runs of zeros of >= n in differentiated vector
    iszero = np.concatenate(([0], np.equal(da, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    runs = filter(lambda x: (x[1] - x[0]) > (n-1), ranges)
    has_runs = len(list(runs)) > 0
    return has_runs

# def get_spacebar_press() :
#     return 'space' in msvcrt.getch() if msvcrt.kbhit() else 0

# def inRect(gaze, cent, x_dist, y_dist) :
#     return (gaze[0] - cent[0]) < x_dist and (gaze[1] - cent[1]) < y_dist

def get_calib_pix_from_pos(mywin, w_cent_x, w_cent_y) :
    return [w_cent_x, w_cent_y - int(round(tools.monitorunittools.convertToPix(vertices=0.0, pos=vert_shift_cm, units="cm", win=mywin)))]

def createMessage(mywin, FG_COLOUR, msg) :
    return visual.TextStim(mywin, 
                            text=msg,
                            height=1.8,
                            color=FG_COLOUR, 
                            pos=(0.0,vert_shift_cm), 
                            antialias=False,
                            wrapWidth = 55,
                            units='cm'
                            )


def drawFixation(mywin, fixOuter, fixInner, position=(0,0)) :
    fixOuter.setPos(position)
    fixInner.setPos(position)
    fixOuter.draw()
    fixInner.draw()


def drawLetter(mywin, calLetter, position=(0,0), embolden=False) :
    if embolden :
        calLetter.setColor((1,1,0))
        calLetter.setPos(position)
        calLetter.setHeight(5)
        calLetter.draw()
        calLetter.setColor((-1,-1,-1))
        calLetter.setHeight(2.5)
    else :
        calLetter.setPos(position)
        calLetter.draw()


def drawCentStimOnly(mywin, fixOuter, fixInner, fix_shift):
    drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,vert_shift_cm))


def drawFixStimsHorz(mywin, fixOuter, fixInner, single_tgt_idx, TOFFSETX_HORZ, fix_shift) :
    drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,vert_shift_cm))
    if single_tgt_idx is None or single_tgt_idx < 0:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][0]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][1]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][2]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][3]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][4]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][0]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][1]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][2]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][3]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][4]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 0:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][0]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 1:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][1]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 2:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][2]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 3:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][3]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 4:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][4]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 5:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][0]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 6:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][1]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 7:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][2]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 8:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][3]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 9:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][4]+fix_shift,vert_shift_cm))


def drawFixStimsVert(mywin, fixOuter, fixInner, single_tgt_idx, TOFFSETY_VERT, fix_shift) :
    drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,vert_shift_cm))
    if single_tgt_idx is None or single_tgt_idx < 0:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_VERT[0][0]+VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_VERT[0][1]+VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_VERT[0][2]+VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_VERT[0][3]+VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_VERT[0][4]+VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_VERT[1][0]-VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_VERT[1][1]-VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift, (TOFFSETY_VERT[1][2]-VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift, (TOFFSETY_VERT[1][3]-VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift, (TOFFSETY_VERT[1][4]-VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 0:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_VERT[0][0]+VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 1:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_VERT[0][1]+VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 2:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_VERT[0][2]+VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 3:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_VERT[0][3]+VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 4:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_VERT[0][4]+VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 5:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_VERT[1][0]-VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 6:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift, (TOFFSETY_VERT[1][1]-VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 7:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift, (TOFFSETY_VERT[1][2]-VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 8:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift, (TOFFSETY_VERT[1][3]-VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 9:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift, (TOFFSETY_VERT[1][4]-VERT_MD) + vert_shift_cm))

def drawFixStimsOblique(mywin, fixOuter, fixInner, single_tgt_idx, TOFFSETX_HORZ, TOFFSETY_VERT, fix_shift):
    drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,vert_shift_cm))
    if single_tgt_idx is None or single_tgt_idx < 0:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][0]+fix_shift,((TOFFSETY_VERT[0][0]+VERT_MD) + vert_shift_cm)))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][1]+fix_shift,((TOFFSETY_VERT[0][1]+VERT_MD) + vert_shift_cm)))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][2]+fix_shift,((TOFFSETY_VERT[0][2]+VERT_MD) + vert_shift_cm)))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][3]+fix_shift,((TOFFSETY_VERT[0][3]+VERT_MD) + vert_shift_cm)))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][4]+fix_shift,((TOFFSETY_VERT[0][4]+VERT_MD) + vert_shift_cm)))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][0]+fix_shift,((TOFFSETY_VERT[1][0]-VERT_MD) + vert_shift_cm)))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][1]+fix_shift,((TOFFSETY_VERT[1][1]-VERT_MD) + vert_shift_cm)))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][2]+fix_shift,((TOFFSETY_VERT[1][2]-VERT_MD) + vert_shift_cm)))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][3]+fix_shift,((TOFFSETY_VERT[1][3]-VERT_MD) + vert_shift_cm)))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][4]+fix_shift,((TOFFSETY_VERT[1][4]-VERT_MD) + vert_shift_cm)))
    if single_tgt_idx == 0:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][0]+fix_shift,((TOFFSETY_VERT[0][0]+VERT_MD) + vert_shift_cm)))
    if single_tgt_idx == 1:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][1]+fix_shift,((TOFFSETY_VERT[0][1]+VERT_MD) + vert_shift_cm)))
    if single_tgt_idx == 2:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][2]+fix_shift,((TOFFSETY_VERT[0][2]+VERT_MD) + vert_shift_cm)))
    if single_tgt_idx == 3:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][3]+fix_shift,((TOFFSETY_VERT[0][3]+VERT_MD) + vert_shift_cm)))
    if single_tgt_idx == 4:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[0][4]+fix_shift,((TOFFSETY_VERT[0][4]+VERT_MD) + vert_shift_cm)))
    if single_tgt_idx == 5:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][0]+fix_shift,((TOFFSETY_VERT[1][0]-VERT_MD) + vert_shift_cm)))
    if single_tgt_idx == 6:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][1]+fix_shift,((TOFFSETY_VERT[1][1]-VERT_MD) + vert_shift_cm)))
    if single_tgt_idx == 7:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][2]+fix_shift,((TOFFSETY_VERT[1][2]-VERT_MD) + vert_shift_cm)))
    if single_tgt_idx == 8:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][3]+fix_shift,((TOFFSETY_VERT[1][3]-VERT_MD) + vert_shift_cm)))
    if single_tgt_idx == 9:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_HORZ[1][4]+fix_shift,((TOFFSETY_VERT[1][4]-VERT_MD) + vert_shift_cm)))        

def drawCalibStimsOblique(mywin, fixOuter, fixInner, single_tgt_idx,TOFFSETX_CAL_HORZ, TOFFSETY_CAL_VERT, fix_shift) :
    drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,vert_shift_cm))
    if single_tgt_idx is None or single_tgt_idx < 0:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][0]+fix_shift,(TOFFSETY_CAL_VERT[0][0]+VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][1]+fix_shift,(TOFFSETY_CAL_VERT[0][1]+VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][2]+fix_shift,(TOFFSETY_CAL_VERT[0][2]+VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][3]+fix_shift,(TOFFSETY_CAL_VERT[0][3]+VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][4]+fix_shift,(TOFFSETY_CAL_VERT[0][4]+VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][0]+fix_shift,(TOFFSETY_CAL_VERT[1][0]-VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][1]+fix_shift,(TOFFSETY_CAL_VERT[1][1]-VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][2]+fix_shift,(TOFFSETY_CAL_VERT[1][2]-VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][3]+fix_shift,(TOFFSETY_CAL_VERT[1][3]-VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][4]+fix_shift,(TOFFSETY_CAL_VERT[1][4]-VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 0:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][0]+fix_shift,(TOFFSETY_CAL_VERT[0][0]+VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 1:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][1]+fix_shift,(TOFFSETY_CAL_VERT[0][1]+VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 2:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][2]+fix_shift,(TOFFSETY_CAL_VERT[0][2]+VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 3:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][3]+fix_shift,(TOFFSETY_CAL_VERT[0][3]+VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 4:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][4]+fix_shift,(TOFFSETY_CAL_VERT[0][4]+VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 5:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][0]+fix_shift,(TOFFSETY_CAL_VERT[1][0]-VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 6:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][1]+fix_shift,(TOFFSETY_CAL_VERT[1][1]-VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 7:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][2]+fix_shift,(TOFFSETY_CAL_VERT[1][2]-VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 8:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][3]+fix_shift,(TOFFSETY_CAL_VERT[1][3]-VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 9:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][4]+fix_shift,(TOFFSETY_CAL_VERT[1][4]-VERT_MD) + vert_shift_cm))

def drawCalibLettersOblique(mywin, num1, num2, num3, num4, num5, num6, num7, num8, num9, num10, emb_idx, TOFFSETX_CAL_HORZ, TOFFSETY_CAL_VERT, fix_shift) :
    is_emboldened = [False,False,False,False, False, False,False,False,False,False]
    if emb_idx >= 0 and emb_idx <= 3 :
        is_emboldened[emb_idx] = True
    drawLetter(mywin, num1, position=(TOFFSETX_CAL_HORZ[0][0]+fix_shift,(TOFFSETY_CAL_VERT[0][0]+VERT_MD)+vert_shift_cm), embolden=is_emboldened[0])
    drawLetter(mywin, num2, position=(TOFFSETX_CAL_HORZ[0][1]+fix_shift,(TOFFSETY_CAL_VERT[0][1]+VERT_MD)+vert_shift_cm), embolden=is_emboldened[1])
    drawLetter(mywin, num3, position=(TOFFSETX_CAL_HORZ[0][2]+fix_shift,(TOFFSETY_CAL_VERT[0][2]+VERT_MD)+vert_shift_cm), embolden=is_emboldened[2])
    drawLetter(mywin, num4, position=(TOFFSETX_CAL_HORZ[0][3]+fix_shift,(TOFFSETY_CAL_VERT[0][3]+VERT_MD)+vert_shift_cm), embolden=is_emboldened[3])
    drawLetter(mywin, num5, position=(TOFFSETX_CAL_HORZ[0][4]+fix_shift,(TOFFSETY_CAL_VERT[0][4]+VERT_MD)+vert_shift_cm), embolden=is_emboldened[4])
    drawLetter(mywin, num6, position=(TOFFSETX_CAL_HORZ[1][0]+fix_shift,(TOFFSETY_CAL_VERT[1][0]-VERT_MD)+vert_shift_cm), embolden=is_emboldened[5])
    drawLetter(mywin, num7, position=(TOFFSETX_CAL_HORZ[1][1]+fix_shift,(TOFFSETY_CAL_VERT[1][1]-VERT_MD)+vert_shift_cm), embolden=is_emboldened[6])
    drawLetter(mywin, num8, position=(TOFFSETX_CAL_HORZ[1][2]+fix_shift,(TOFFSETY_CAL_VERT[1][2]-VERT_MD)+vert_shift_cm), embolden=is_emboldened[7])
    drawLetter(mywin, num9, position=(TOFFSETX_CAL_HORZ[1][3]+fix_shift,(TOFFSETY_CAL_VERT[1][3]-VERT_MD)+vert_shift_cm), embolden=is_emboldened[8])
    drawLetter(mywin, num10, position=(TOFFSETX_CAL_HORZ[1][4]+fix_shift,(TOFFSETY_CAL_VERT[1][4]-VERT_MD)+vert_shift_cm), embolden=is_emboldened[9])


def drawCalibStimsHorz(mywin, fixOuter, fixInner, single_tgt_idx, TOFFSETX_CAL_HORZ, fix_shift) :
    drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,vert_shift_cm))
    if single_tgt_idx is None or single_tgt_idx < 0:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][0]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][1]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][2]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][3]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][4]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][0]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][1]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][2]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][3]+fix_shift,vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][4]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 0:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][0]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 1:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][1]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 2:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][2]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 3:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][3]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 4:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[0][4]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 5:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][0]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 6:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][1]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 7:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][2]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 8:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][3]+fix_shift,vert_shift_cm))
    if single_tgt_idx == 9:
        drawFixation(mywin, fixOuter, fixInner, position=(TOFFSETX_CAL_HORZ[1][4]+fix_shift,vert_shift_cm))

def drawCalibLettersHorz(mywin, num1, num2, num3, num4, num5, num6, num7, num8, num9, num10, emb_idx, TOFFSETX_CAL_HORZ, fix_shift) :
    is_emboldened = [False,False,False,False,False,False,False,False,False,False]
    if emb_idx >= 0 and emb_idx <= 7 :
        is_emboldened[emb_idx] = True
    drawLetter(mywin, num1, position=(TOFFSETX_CAL_HORZ[0][0]+fix_shift,vert_shift_cm), embolden=is_emboldened[0])
    drawLetter(mywin, num2, position=(TOFFSETX_CAL_HORZ[0][1]+fix_shift,vert_shift_cm), embolden=is_emboldened[1])
    drawLetter(mywin, num3, position=(TOFFSETX_CAL_HORZ[0][2]+fix_shift,vert_shift_cm), embolden=is_emboldened[2])
    drawLetter(mywin, num4, position=(TOFFSETX_CAL_HORZ[0][3]+fix_shift,vert_shift_cm), embolden=is_emboldened[3])
    drawLetter(mywin, num5, position=(TOFFSETX_CAL_HORZ[0][4]+fix_shift,vert_shift_cm), embolden=is_emboldened[4])
    drawLetter(mywin, num6, position=(TOFFSETX_CAL_HORZ[1][0]+fix_shift,vert_shift_cm), embolden=is_emboldened[5])
    drawLetter(mywin, num7, position=(TOFFSETX_CAL_HORZ[1][1]+fix_shift,vert_shift_cm), embolden=is_emboldened[6])
    drawLetter(mywin, num8, position=(TOFFSETX_CAL_HORZ[1][2]+fix_shift,vert_shift_cm), embolden=is_emboldened[7])
    drawLetter(mywin, num9, position=(TOFFSETX_CAL_HORZ[1][3]+fix_shift,vert_shift_cm), embolden=is_emboldened[8])
    drawLetter(mywin, num10, position=(TOFFSETX_CAL_HORZ[1][4]+fix_shift,vert_shift_cm), embolden=is_emboldened[9])

def drawCalibStimsVert(mywin, fixOuter, fixInner, single_tgt_idx, TOFFSETY_CAL_VERT, fix_shift) :
    drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,vert_shift_cm))
    if single_tgt_idx is None or single_tgt_idx < 0:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_CAL_VERT[0][0]+VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_CAL_VERT[0][1]+VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_CAL_VERT[0][2]+VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_CAL_VERT[0][3]+VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_CAL_VERT[0][4]+VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_CAL_VERT[1][0]-VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_CAL_VERT[1][1]-VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_CAL_VERT[1][2]-VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_CAL_VERT[1][3]-VERT_MD) + vert_shift_cm))
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_CAL_VERT[1][4]-VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 0:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_CAL_VERT[0][0]+VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 1:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_CAL_VERT[0][1]+VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 2:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_CAL_VERT[0][2]+VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 3:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_CAL_VERT[0][3]+VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 4:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_CAL_VERT[0][4]+VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 5:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift,(TOFFSETY_CAL_VERT[1][0]-VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 6:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift, (TOFFSETY_CAL_VERT[1][1]-VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 7:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift, (TOFFSETY_CAL_VERT[1][2]-VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 8:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift, (TOFFSETY_CAL_VERT[1][3]-VERT_MD) + vert_shift_cm))
    if single_tgt_idx == 9:
        drawFixation(mywin, fixOuter, fixInner, position=(fix_shift, (TOFFSETY_CAL_VERT[1][4]-VERT_MD) + vert_shift_cm))

def drawCalibLettersVert(mywin, num1, num2, num3, num4, num5, num6, num7, num8, num9, num10, emb_idx, TOFFSETY_CAL_VERT, fix_shift) :
    is_emboldened = [False,False,False,False, False, False, False, False, False, False]
    if emb_idx >= 0 and emb_idx <= 3 :
        is_emboldened[emb_idx] = True
    drawLetter(mywin, num1, position=(fix_shift,(TOFFSETY_CAL_VERT[0][0]+VERT_MD)+vert_shift_cm), embolden=is_emboldened[0])
    drawLetter(mywin, num2, position=(fix_shift,(TOFFSETY_CAL_VERT[0][1]+VERT_MD)+vert_shift_cm), embolden=is_emboldened[1])
    drawLetter(mywin, num3, position=(fix_shift,(TOFFSETY_CAL_VERT[0][2]+VERT_MD)+vert_shift_cm), embolden=is_emboldened[2])
    drawLetter(mywin, num4, position=(fix_shift,(TOFFSETY_CAL_VERT[0][3]+VERT_MD)+vert_shift_cm), embolden=is_emboldened[3])
    drawLetter(mywin, num5, position=(fix_shift,(TOFFSETY_CAL_VERT[0][4]+VERT_MD)+vert_shift_cm), embolden=is_emboldened[4])
    drawLetter(mywin, num6, position=(fix_shift,(TOFFSETY_CAL_VERT[1][0]-VERT_MD)+vert_shift_cm), embolden=is_emboldened[5])
    drawLetter(mywin, num7, position=(fix_shift,(TOFFSETY_CAL_VERT[1][1]-VERT_MD)+vert_shift_cm), embolden=is_emboldened[6])
    drawLetter(mywin, num8, position=(fix_shift,(TOFFSETY_CAL_VERT[1][2]-VERT_MD)+vert_shift_cm), embolden=is_emboldened[7])
    drawLetter(mywin, num9, position=(fix_shift,(TOFFSETY_CAL_VERT[1][3]-VERT_MD)+vert_shift_cm), embolden=is_emboldened[8])
    drawLetter(mywin, num10, position=(fix_shift,(TOFFSETY_CAL_VERT[1][4]-VERT_MD)+vert_shift_cm), embolden=is_emboldened[9])    
 

def ss_runcalibs(w, calDr, FG_COLOUR, BG_COLOUR, RED, GRN, PPCM, st_msg, end_msg, trialLetterOrder, numLetters, numTrialsPerLetter, isi, angles_horz, angles_vert, fix_shift, ev_outlet, udp_socket, el_outlet, elTk, EYE_TO_SCREEN_CM) :
    ### Define where the calibration targets will be
    # L1-L5 indicate the five distinct horizontal positions to the left of center 
    # R1-R5 indicate the five distinct horizontal positions to the right of center
    # U1-U5 indicate the five distinct vertical positions above center
    # D1-D5 indicate the five distincr vertical positions below center

    TOFFSETX_CAL_HORZ_L1 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[4])))
    TOFFSETX_CAL_HORZ_L2 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[3])))
    TOFFSETX_CAL_HORZ_L3 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[2])))
    TOFFSETX_CAL_HORZ_L4 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[1])))
    TOFFSETX_CAL_HORZ_L5 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[0])))
    
    TOFFSETX_CAL_HORZ_R1 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[0])))
    TOFFSETX_CAL_HORZ_R2 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[1])))
    TOFFSETX_CAL_HORZ_R3 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[2])))
    TOFFSETX_CAL_HORZ_R4 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[3])))
    TOFFSETX_CAL_HORZ_R5 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[4])))

    TOFFSETX_CAL_HORZ = np.array([[TOFFSETX_CAL_HORZ_L1,TOFFSETX_CAL_HORZ_L2,TOFFSETX_CAL_HORZ_L3,TOFFSETX_CAL_HORZ_L4,TOFFSETX_CAL_HORZ_L5], [TOFFSETX_CAL_HORZ_R1,TOFFSETX_CAL_HORZ_R2,TOFFSETX_CAL_HORZ_R3,TOFFSETX_CAL_HORZ_R4,TOFFSETX_CAL_HORZ_R5]])

    TOFFSETY_CAL_VERT_U1 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[4])))
    TOFFSETY_CAL_VERT_U2 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[3])))
    TOFFSETY_CAL_VERT_U3 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[2])))
    TOFFSETY_CAL_VERT_U4 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[1])))
    TOFFSETY_CAL_VERT_U5 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[0])))

    TOFFSETY_CAL_VERT_D1 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[0])))
    TOFFSETY_CAL_VERT_D2 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[1])))
    TOFFSETY_CAL_VERT_D3 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[2])))
    TOFFSETY_CAL_VERT_D4 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[3])))
    TOFFSETY_CAL_VERT_D5 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[4])))

    TOFFSETY_CAL_VERT = np.array([[TOFFSETY_CAL_VERT_U1,TOFFSETY_CAL_VERT_U2,TOFFSETY_CAL_VERT_U3,TOFFSETY_CAL_VERT_U4,TOFFSETY_CAL_VERT_U5], [TOFFSETY_CAL_VERT_D1,TOFFSETY_CAL_VERT_D2,TOFFSETY_CAL_VERT_D3,TOFFSETY_CAL_VERT_D4,TOFFSETY_CAL_VERT_D5]])


    ### Create visual stimuli
    fixOuter = visual.Circle(win=w, radius=0.50, units="cm", pos=(0,0), lineWidth=0.0, interpolate=True, fillColor=FG_COLOUR)
    fixInner = visual.Circle(win=w, radius=0.125, units="cm", pos=(0,0), lineWidth=0.0, interpolate=True, fillColor=BG_COLOUR)
    fixOuterWarning = visual.Circle(win=w, radius=0.50, units="cm", pos=(0,0), lineWidth=0.0, interpolate=True, fillColor=RED)
    fixOuterDrift = visual.Circle(win=w, radius=0.50, units="cm", pos=(0,0), lineWidth=0.0, interpolate=True, fillColor=GRN)

    exp_abort_prompt = createMessage(w, FG_COLOUR, 'Really abort experiment? [y] or [n]')

    pretrial_warning_msg = createMessage(w, FG_COLOUR, 'Warning: Eye movement detected before the auditory cue!\nPress any key to continue.')
    
    drift_correct_fail_msg = createMessage(w, FG_COLOUR, 'Drift correct failed, perform a calibration? [y] or [n]')

    el_calib_msg = createMessage(w, FG_COLOUR, "Press the spacebar to begin eye tracker calibration.\nOr press 'k' to skip calibration.")

 
    num1 = visual.TextStim(win=w, text='1', bold=True, units='cm', antialias=False, height=2.5, color=FG_COLOUR)
    num2 = visual.TextStim(win=w, text='2', bold=True, units='cm', antialias=False, height=2.5, color=FG_COLOUR)
    num3 = visual.TextStim(win=w, text='3', bold=True, units='cm', antialias=False, height=2.5, color=FG_COLOUR)
    num4 = visual.TextStim(win=w, text='4', bold=True, units='cm', antialias=False, height=2.5, color=FG_COLOUR)
    num5 = visual.TextStim(win=w, text='5', bold=True, units='cm', antialias=False, height=2.5, color=FG_COLOUR)
    num6 = visual.TextStim(win=w, text='6', bold=True, units='cm', antialias=False, height=2.5, color=FG_COLOUR)
    num7 = visual.TextStim(win=w, text='7', bold=True, units='cm', antialias=False, height=2.5, color=FG_COLOUR)
    num8 = visual.TextStim(win=w, text='8', bold=True, units='cm', antialias=False, height=2.5, color=FG_COLOUR)
    num9 = visual.TextStim(win=w, text='9', bold=True, units='cm', antialias=False, height=2.5, color=FG_COLOUR)
    num10 = visual.TextStim(win=w, text='10', bold=True, units='cm', antialias=False, height=2.5, color=FG_COLOUR)
     
    
    trialNums = ['1','2','3','4','5','6','7','8','9','10']


    ### Load sound stimuli
    sound_path = "Sound_Files\\"
    sound_format = ".wav"
    snd_names = ["1_snd", "2_snd", "3_snd", "4_snd", "5_snd", "6_snd", "7_snd", "8_snd", "9_snd", "10_snd"] 
    
    sounds = []
    for snd in snd_names :
        snd_fname = sound_path + snd + sound_format
        sounds.append(sound.Sound(snd_fname))

    exp_end_sound = sound.Sound(sound_path + "exp_end" + sound_format)
    ping_sound = sound.Sound(sound_path + "ping" + sound_format)
    gaze_warning_sound = sound.Sound(sound_path + "gaze_warn" + sound_format)
    gaze_warning_snd_dur = gaze_warning_sound.getDuration()

    w_dim = w.size
    w_cent_x = w_dim[0] / 2
    w_cent_y = w_dim[1] / 2
    gaze_warning_dist_cm = 10. # in CM
    gaze_warning_dist = gaze_warning_dist_cm * PPCM

    w.flip()

    use_eyelink = el_outlet is not None 
    if use_eyelink :
        el_calib_msg.draw()
        w.flip()
        init_cal_resp = False
        init_calibrate = False

        ## Refresh PsychoPy event listener (for KB press)
        event.clearEvents()

        while not init_cal_resp :
            keys = event.getKeys()
            if keys :
                if 'k' in keys :
                    init_cal_resp = True
                    init_calibrate = False
                else :
                    init_cal_resp = True
                    init_calibrate = True
        
        w.flip()

        if init_calibrate :
            CalibrateEyelink(elTk)

    w.flip()

    # Display trial end message and wait for keypress
    # end_message.setAutoDraw(True)  # automatically draw every frame
    exp_quit = False
    while not exp_quit :
        st_msg.draw()  # automatically draw every frame
        w.flip()
        keys = event.getKeys()  # get keys from event buffer
        if keys:
            exp_quit = True
    w.flip()

    emboldened_trials = [0] * numLetters

    exp_abort = False
    first_trial = True
    trial_drift_correct = False
    last_sample_time = 0

    # Before beginning calibration trials, display all letters
    if calDr == 'H':
        drawCalibLettersHorz(w, num1, num2, num3, num4, num5, num6, num7, num8, num9, num10, -1, TOFFSETX_CAL_HORZ,fix_shift)
    elif calDr == 'V':
        drawCalibLettersVert(w, num1, num2, num3, num4, num5, num6, num7, num8, num9, num10, -1, TOFFSETY_CAL_VERT, fix_shift)
    elif calDr == 'O':
        drawCalibLettersOblique(w, num1, num2, num3, num4, num5, num6, num7, num8, num9, num10, -1, TOFFSETX_CAL_HORZ, TOFFSETY_CAL_VERT, fix_shift)
         
    w.flip()

    event.clearEvents()
    
    init_show_letters_resp = False
    while not init_show_letters_resp :
        keys = event.getKeys()
        if keys :
            init_show_letters_resp = True
    
    w.flip()


    ### Loop through all trials 
    # for tn in range(np.size(trialLetterOrder)) :
    tn = 0
    while tn < np.size(trialLetterOrder) :
        #print("Trial Index: " + str(tn) )

        ## Refresh PsychoPy event listener (for KB press)
        event.clearEvents()

        # If experiment was aborted, display Y/N message, if Y then quit
        if exp_abort :
            exp_abort_prompt.draw()
            w.flip()
            abort_resp = False

            while not abort_resp :
                keys = event.getKeys()
                if 'y' in keys :
                    abort_resp = True
                if 'n' in keys :
                    abort_resp = True
                    exp_abort = False
                    first_trial = True # spacebar pause before resuming trials
                    
            pylink.msecDelay(500)

            if exp_abort :
                break
        
        # # Drift correct 
        if first_trial :
            trial_drift_correct = False # !! to control TRIAL-BY-TRIAL drift correct change this
        else : 
            trial_drift_correct = True # !! to control TRIAL-BY-TRIAL drift correct change this

        if trial_drift_correct :
            pylink.msecDelay(500)
            drawCentStimOnly(w, fixOuterDrift, fixInner, fix_shift) 
            w.flip()
            drift_error = manual_drift_correction(get_calib_pix_from_pos(w, w_cent_x, w_cent_y), elTk)
            recalibrate = False
            if drift_error != 0 :
                drift_correct_fail_msg.draw()
                w.flip()
                drift_resp = False

                ## Refresh PsychoPy event listener (for KB press)
                event.clearEvents()

                while not drift_resp :
                    keys = event.getKeys()
                    if 'y' in keys :
                        drift_resp = True
                        recalibrate = True
                    if 'n' in keys :
                        drift_resp = True
                    if 'escape' in keys :
                        drift_resp = True
                        exp_abort = True

            if recalibrate :
                recalibrate = False
                trial_drift_correct = False
                ## Refresh PsychoPy event listener (for KB press)
                event.clearEvents()
                w.flip()
                CalibrateEyelink(elTk)
                post_calib_pause = True
            else :
                post_calib_pause = False

            ## Refresh PsychoPy event listener (for KB press)
            event.clearEvents()
            w.flip()

            # If experiment was aborted during drift check, display Y/N message, if Y then quit
            if exp_abort :
                exp_abort_prompt.draw()
                w.flip()
                abort_resp = False

                while not abort_resp :
                    keys = event.getKeys()
                    if 'y' in keys :
                        abort_resp = True
                    if 'n' in keys :
                        abort_resp = True
                        exp_abort = False
                        first_trial = True # spacebar pause before resuming trials

                pylink.msecDelay(500)

                if exp_abort :
                    break

        w.flip()

        # stim_disp = True
        trialLetter = trialLetterOrder[tn]-1
        #print("Trial Number: " + str(trialLetter+1))
        
            
        ### Display stims
        if calDr == 'H':
            drawCalibStimsHorz(w, fixOuter, fixInner, trialLetter, TOFFSETX_CAL_HORZ, fix_shift)
        elif calDr == 'V':
            drawCalibStimsVert(w, fixOuter, fixInner, trialLetter, TOFFSETY_CAL_VERT, fix_shift)
        elif calDr == 'O':
            drawCalibStimsOblique(w, fixOuter, fixInner, trialLetter, TOFFSETX_CAL_HORZ, TOFFSETY_CAL_VERT, fix_shift)
        # drawCalibLetters(w, ltrA, ltrB, ltrC, ltrD, -1, TOFFSETX_SM, TOFFSETX_LG, fix_shift)

        w.flip()

        ## Refresh PsychoPy event listener (for KB press)
        event.clearEvents()

        # Make messages for EDF and XDF
        iti_st_msg  = ["ITI_CALIB" + calDr + "_T" + '{0:02d}'.format(tn+1) + "_START"]
        iti_end_msg = ["ITI_CALIB" + calDr + "_T" + '{0:02d}'.format(tn+1) + "_END"]

        trial_st_msg   = ["CALIB" + calDr + "_T" + '{0:02d}'.format(tn+1) + "_N" +  trialNums[trialLetter] + "_START"]
        trial_stim_msg = ["CALIB" + calDr + "_T" + '{0:02d}'.format(tn+1) + "_N" +  trialNums[trialLetter] + "_STIM"]
        trial_ping_msg = ["CALIB" + calDr + "_T" + '{0:02d}'.format(tn+1) + "_N" +  trialNums[trialLetter] + "_PING"]
        trial_end_msg  = ["CALIB" + calDr + "_T" + '{0:02d}'.format(tn+1) + "_N" +  trialNums[trialLetter] + "_END"]
        trial_warn_msg = ["CALIB" + calDr + "_T" + '{0:02d}'.format(tn+1) + "_N" +  trialNums[trialLetter] + "_WARN"]

        if first_trial :
            # Wait for spacebar to begin, unless we just successfully drift corrected
            if not trial_drift_correct :
                trials_start = False
                while not trials_start :
                    keys = event.getKeys()
                    if keys:
                        if 'escape' in keys :
                            trials_start = True
                            exp_abort = True
                        if 'space' in keys :
                            trials_start = True
                if exp_abort :
                    continue
            first_trial = False
            pylink.msecDelay(1000)
        else:
            ## Refresh PsychoPy event listener (for KB press)
            event.clearEvents()

            while post_calib_pause :
                keys = event.getKeys()
                if keys :
                    if 'space' in keys :
                        post_calib_pause = False
                    if 'escape' in keys :
                        post_calib_pause = False
                        exp_abort = True
                        break

            if exp_abort :
                continue

        ## Refresh PsychoPy event listener (for KB press)
        event.clearEvents()

        if udp_socket is not None :
            udp_socket.send(b"b")
        # udp_socket.sendto("b", (UDP_IP, UDP_PORT))
        
        ev_outlet.push_sample(trial_st_msg)

        if use_eyelink :
            elTk.sendMessage(trial_st_msg)
            elTk.startRecording(1, 1, 1, 1)

        no_fix_pre_target = True
        trial_end = False
        pinged = False
        pretarget_pause_time = 1.
        gaze_warning_activated = False
        gaze_warning_trial_break = False

        # Pause briefly to verify fixation after letter is announced
        pause_start = time.clock()
        while no_fix_pre_target :
            if not exp_abort :
                curr_time = time.clock()

                # Get Eyelink sample
                if use_eyelink :
                    els = None
                    els = CollectEyelinkSample(el_outlet, elTk, last_sample_time)
                    if els is not None:
                        smp = els[0]
                        last_sample_time = els[1]
                        if smp is not None:
                            gaze = smp[0:2]
                        else:
                            print("Eyelink error in trial - empty data point:" + ''.join(trial_warn_msg))

                if (curr_time - pause_start) > pretarget_pause_time :
                    no_fix_pre_target = False
                    break

                if use_eyelink :
                    # Gets saccade angular distance upon any EndSaccade event
                    elsc = None
                    elsc = CollectEyelinkSaccades(el_outlet, elTk, last_sample_time)
                    if elsc is not None:
                        dist = elsc[0]
                        last_sample_time = elsc[1]
                        if dist > 3. :
                            if not gaze_warning_activated :
                                gaze_warning_activated = True
                                no_fix_pre_target = False
                                break

                keys = event.getKeys()
                if keys:
                    if 'escape' in keys :
                        exp_abort = True
                        no_fix_pre_target = False
                        break

        # Send letter announcement message
        if not gaze_warning_activated :
            ev_outlet.push_sample(trial_stim_msg)
            if use_eyelink :
                elTk.sendMessage(trial_stim_msg)
            # Play stimulus sound
            sounds[trialLetter].play()
            #print("Sound Playing: " + str(trialLetter))
            start_time = time.clock()
        else :
            start_time = 0

        ## Refresh PsychoPy event listener (for KB press)
        event.clearEvents()

        # Pause briefly to get fixation after letter is announced
        no_fix_post_target = True
        posttarget_pause_time = 0.3
        if not gaze_warning_activated :
            pause_start = time.clock()
            while no_fix_post_target :
                if not exp_abort :
                    curr_time = time.clock()
                    if (curr_time - pause_start) > posttarget_pause_time :
                        no_fix_post_target = False
                        break

                    if use_eyelink :
                        # Gets saccade angular distance upon any EndSaccade event
                        elsc = None
                        elsc = CollectEyelinkSaccades(el_outlet, elTk, last_sample_time)
                        if elsc is not None:
                            dist = elsc[0]
                            last_sample_time = elsc[1]
                            if dist > 3. :
                                print("WARN")
                                if not gaze_warning_activated :
                                    gaze_warning_activated = True
                                    no_fix_post_target = False
                                    break

                    keys = event.getKeys()
                    if keys:
                        if 'escape' in keys :
                            exp_abort = True
                            no_fix_post_target = False
                            break

        ## Refresh PsychoPy event listener (for KB press)
        event.clearEvents()

        # print("Pre Gaze Warning!")
        # Display gaze warning message and wait for keypress
        if gaze_warning_activated:
            ev_outlet.push_sample(trial_warn_msg)
            if use_eyelink :
                elTk.sendMessage(trial_warn_msg)
            
            # warn_pause_start = time.clock()
            warn_wait = True
            while warn_wait :
                now = time.clock()
                if (now - start_time) > .75 :
                    warn_wait = False

            # print("Gaze Warning!")
            gaze_warning_sound.play()
            warning_quit = False
            gaze_warning_trial_break = True
            warn_flash_start = time.clock()
            warn_flash_time = 0.75
            while not warning_quit :
                # pretrial_warning_msg.draw()  # automatically draw every frame
                # w.flip()
                now = time.clock()
                if calDr == 'H' :
                    if (now - warn_flash_start) < warn_flash_time :
                        ### Display red warning stims
                        drawCalibStimsHorz(w, fixOuterWarning, fixInner, trialLetter, TOFFSETX_CAL_HORZ, fix_shift)
                    else :
                        ### Back to regular black stims
                        drawCalibStimsHorz(w, fixOuter, fixInner, trialLetter, TOFFSETX_CAL_HORZ,fix_shift)
                elif calDr == 'V' : 
                    if (now - warn_flash_start) < warn_flash_time :
                        ### Display red warning stims
                        drawCalibStimsVert(w, fixOuter, fixInner, trialLetter, TOFFSETY_CAL_VERT, fix_shift)
                    else :
                        ### Back to regular black stims
                        drawCalibStimsVert(w, fixOuter, fixInner, trialLetter, TOFFSETY_CAL_VERT, fix_shift)
                elif calDr == 'O' : 
                    if (now - warn_flash_start) < warn_flash_time :
                        ### Display red warning stims
                        drawCalibStimsOblique(w, fixOuter, fixInner, trialLetter, TOFFSETX_CAL_HORZ, TOFFSETY_CAL_VERT, fix_shift)
                    else :
                        ### Back to regular black stims
                        drawCalibStimsOblique(w, fixOuter, fixInner, trialLetter, TOFFSETX_CAL_HORZ, TOFFSETY_CAL_VERT, fix_shift)
                    
                
                w.flip()
                keys = event.getKeys()  # get keys from event buffer
                if keys:
                    warning_quit = True
                    if 'escape' in keys :
                        trial_end = True
                        exp_abort = True
                        break

        ## Refresh PsychoPy event listener (for KB press)
        event.clearEvents()

        # Recycle trial if gaze warning occured
        if gaze_warning_trial_break :
            # Pause to avoid warning sound stuttering error
            # warn_pause_start = time.clock()
            warn_snd_wait = True
            while warn_snd_wait :
                now = time.clock()
                if (now - warn_flash_start) > 1. :
                    warn_snd_wait = False
            pylink.msecDelay(500) # pause for 500ms to reduce immediate warning on next trial
            continue # don't iterate trial number, so that we continue from same tn value

        # TRIAL LOOP
        while not trial_end :
            frame_start = time.clock()

            # Get Eyelink sample
            if use_eyelink :
                els = None
                els = CollectEyelinkSample(el_outlet, elTk, last_sample_time)
                if els is not None:
                    smp = els[0]
                    last_sample_time = els[1]
                    if smp is not None:
                        gaze = smp[0:2]
                    else:
                        print("Eyelink error in trial - empty data point:" + ''.join(trial_warn_msg))

            # If 2 seconds has elapsed, play the ping sound, send to EDF/XDF
            if not pinged : 
                if (frame_start - start_time) > 2.0 :
                    ev_outlet.push_sample(trial_ping_msg)
                    if use_eyelink :
                        elTk.sendMessage(trial_ping_msg)
                    ping_sound.play()
                    pinged = True

            # After the ping, wait 1000ms (3s since trial st) then end trial
            if pinged :
                #if 'space' in keys :
                if (frame_start - start_time) > 3.0 :
                    # Push LSL event marker for trial end
                    ev_outlet.push_sample(trial_end_msg)

                    if use_eyelink :
                        elTk.stopRecording()
                        elTk.sendMessage(trial_end_msg)

                    if udp_socket is not None :
                        udp_socket.send(b"e")
                    # udp_socket.sendto("e", (UDP_IP, UDP_PORT))
                    trial_end = True
                    break
                
            # If ESC is pressed at any point, end trial
            keys = event.getKeys()
            if keys :
                if 'escape' in keys :
                    trial_end = True
                    exp_abort = True
                    break

            ## Sleep for remainder of inter-sample period
            frame_end = time.clock()
            sleep_time = int(np.round(np.maximum(0., frame_start - frame_end + isi)*1000.))
            pylink.msecDelay(sleep_time)
            
        # END TRIAL LOOP

        ## Refresh PsychoPy event listener (for KB press)
        event.clearEvents()

        # ITI - Pause briefly between trials
        intr_pause_min_time = 1.0
        pause_start = time.clock()
        intr_pause = True
        intr_spacebar_press = False
        # Push LSL event marker for ITI start
        ev_outlet.push_sample(iti_st_msg)
        if use_eyelink :
            elTk.sendMessage(iti_st_msg)
        if not exp_abort :
            while intr_pause :
                curr_time = time.clock()
                if curr_time - pause_start > intr_pause_min_time :
                    if intr_spacebar_press :
                        intr_pause = False
                keys = event.getKeys()
                if keys :
                    if 'space' in keys :
                        intr_spacebar_press = True
                    if 'escape' in keys :
                        intr_pause = False
                        exp_abort = True
                        break
        
        # Push LSL event marker for ITI end
        ev_outlet.push_sample(iti_end_msg)
        if use_eyelink :
            elTk.sendMessage(iti_end_msg)

        tn = tn + 1

        w.flip()


    if not exp_abort :
        # Display trial end message and wait for keypress
        # end_message.setAutoDraw(True)  # automatically draw every frame
        exp_quit = False
        while not exp_quit :
            end_msg.draw()  # automatically draw every frame
            w.flip()
            keys = event.getKeys()  # get keys from event buffer
            if keys:
                exp_quit = True
        w.flip()

    return exp_abort



def ss_runtrials(w, FG_COLOUR, BG_COLOUR, RED, GRN, PPCM, st_msg, end_msg, trialTargetOrder, trialBlockNumber, blockNumbers, blockMarkersOn, blockTargVert, isi, angles_horz, angles_vert, fix_shift, ev_outlet, udp_socket, el_outlet, elTk, EYE_TO_SCREEN_CM) :   # MkrDir was removed from the function

    ### Create visual stimuli
    fixOuter = visual.Circle(win=w, radius=0.50, units="cm", pos=(0,0), lineWidth=0.0, interpolate=True, fillColor=FG_COLOUR)
    fixInner = visual.Circle(win=w, radius=0.125, units="cm", pos=(0,0), lineWidth=0.0, interpolate=True, fillColor=BG_COLOUR)
    fixOuterWarning = visual.Circle(win=w, radius=0.50, units="cm", pos=(0,0), lineWidth=0.0, interpolate=True, fillColor=RED)
    fixOuterDrift = visual.Circle(win=w, radius=0.50, units="cm", pos=(0,0), lineWidth=0.0, interpolate=True, fillColor=GRN)

    exp_abort_prompt = createMessage(w, FG_COLOUR, 'Really abort experiment? [y] or [n]')
    # prac_marker_msg_st  = createMessage(w, 'You will now complete some practice trials with visual markers. Press any key to continue.')
    # prac_marker_msg_end = createMessage(w, 'Practice trials complete. Turn off screen now. Press any key to continue.')

    # block_markers_on_msg  = createMessage(w, 'The next block will be visually guided (markers on).\n Press any key to continue.')
    # block_markers_off_msg = createMessage(w, 'The next block will be memory guided (markers off).\n  Press any key to continue.')

    pretrial_warning_msg = createMessage(w, FG_COLOUR, 'Warning: Eye movement detected before the auditory cue!\nPress any key to continue.')
    # iti_prompt_msg = createMessage(w, 'Please initiate the next trial by pressing the space key.')
    drift_correct_fail_msg = createMessage(w, FG_COLOUR, 'Drift correct failed, perform a calibration? [y] or [n]')

    el_calib_msg = createMessage(w, FG_COLOUR, "Press the spacebar to begin eye tracker calibration.\nOr press 'k' to skip calibration.")

    trialTargets = ['1','2','3','4','5','6','7','8','9','10']

    TOFFSETX_HORZ_L1 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[4])))
    TOFFSETX_HORZ_L2 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[3])))
    TOFFSETX_HORZ_L3 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[2])))
    TOFFSETX_HORZ_L4 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[1])))
    TOFFSETX_HORZ_L5 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[0])))
    
    TOFFSETX_HORZ_R1 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[0])))
    TOFFSETX_HORZ_R2 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[1])))
    TOFFSETX_HORZ_R3 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[2])))
    TOFFSETX_HORZ_R4 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[3])))
    TOFFSETX_HORZ_R5 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_horz[4])))

    TOFFSETX_HORZ = np.array([[TOFFSETX_HORZ_L1,TOFFSETX_HORZ_L2,TOFFSETX_HORZ_L3,TOFFSETX_HORZ_L4,TOFFSETX_HORZ_L5], [TOFFSETX_HORZ_R1,TOFFSETX_HORZ_R2,TOFFSETX_HORZ_R3,TOFFSETX_HORZ_R4,TOFFSETX_HORZ_R5]])

    TOFFSETY_VERT_U1 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[4])))
    TOFFSETY_VERT_U2 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[3])))
    TOFFSETY_VERT_U3 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[2])))
    TOFFSETY_VERT_U4 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[1])))
    TOFFSETY_VERT_U5 = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[0])))

    TOFFSETY_VERT_D1 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[0])))
    TOFFSETY_VERT_D2 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[1])))
    TOFFSETY_VERT_D3 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[2])))
    TOFFSETY_VERT_D4 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[3])))
    TOFFSETY_VERT_D5 = -1*(EYE_TO_SCREEN_CM * np.tan(np.deg2rad(angles_vert[4])))

    TOFFSETY_VERT = np.array([[TOFFSETY_VERT_U1,TOFFSETY_VERT_U2,TOFFSETY_VERT_U3,TOFFSETY_VERT_U4,TOFFSETY_VERT_U5], [TOFFSETY_VERT_D1,TOFFSETY_VERT_D2,TOFFSETY_VERT_D3,TOFFSETY_VERT_D4,TOFFSETY_VERT_D5]])



    ### Load sound stimuli
    sound_path = "Sound_Files\\"
    sound_format = ".wav"
    snd_names = ["1_snd", "2_snd", "3_snd", "4_snd", "5_snd", "6_snd","7_snd","8_snd","9_snd","10_snd"] 
    sounds = []
    for snd in snd_names :
        snd_fname = sound_path + snd + sound_format
        sounds.append(sound.Sound(snd_fname))        
    
    exp_end_sound = sound.Sound(sound_path + "exp_end" + sound_format)
    ping_sound = sound.Sound(sound_path + "ping" + sound_format)
    gaze_warning_sound = sound.Sound(sound_path + "gaze_warn" + sound_format)
    eyes_open_sound = sound.Sound(sound_path + "eyes_open" + sound_format)
    eyes_closed_sound = sound.Sound(sound_path + "eyes_closed" + sound_format)
    gaze_warning_snd_dur = gaze_warning_sound.getDuration()

    w_dim = w.size
    w_cent_x = w_dim[0] / 2
    w_cent_y = w_dim[1] / 2
    gaze_warning_dist_cm = 10. # in CM
    gaze_warning_dist = gaze_warning_dist_cm * PPCM
 
    w.flip()


    use_eyelink = el_outlet is not None
    
    if use_eyelink :
        el_calib_msg.draw()
        w.flip()
        init_cal_resp = False
        init_calibrate = False

        ## Refresh PsychoPy event listener (for KB press)
        event.clearEvents()

        while not init_cal_resp :
            keys = event.getKeys()
            if keys :
                if 'k' in keys :
                    init_cal_resp = True
                    init_calibrate = False
                else :
                    init_cal_resp = True
                    init_calibrate = True
        
        w.flip()

        if init_calibrate :
            CalibrateEyelink(elTk)

    w.flip()

    # Display trial end message and wait for keypress
    # end_message.setAutoDraw(True)  # automatically draw every frame
    exp_quit = False
    while not exp_quit :
        st_msg.draw()  # automatically draw every frame
        w.flip()
        keys = event.getKeys()  # get keys from event buffer
        if keys:
            exp_quit = True
    w.flip()

    exp_abort = False
    first_trial = True
    last_sample_time = 0

#    show_prac_msg = True
#    show_prac_end = True

    # saves current block number 
    # (this is only used for cond 1 where we alternate markers on and off)
    bn = 0
    
    bMarkerStr = "MARK"

    ### Loop through all trials
    for bn in range(np.size(blockNumbers)) :
        if exp_abort :
            break

        # end old block if needed
        if (blockNumbers[bn] != 1) and (bn > 0) :
            block_end_msg  = ["BLOCK" + bMarkerStr + "_B" + '{0:02d}'.format(blockNumbers[bn-1]) + "_END"]
            if use_eyelink :
                elTk.sendMessage(block_end_msg)
            ev_outlet.push_sample(block_end_msg)         
           
        # Get current block number    
        current_block = blockNumbers[bn]

        # Determine if current block is markers on or off
        block_markers_on = blockMarkersOn[bn]
        if block_markers_on == 0:
            block_start_msg = createMessage(w, FG_COLOUR, 'Block ' + str(current_block) + ': Markers.\nWait for experimenter to intiate next sequence \nof trials.')
            bMarkerStr = "MARK"
            markers_on = True
            eyes_open = True
            skip_first_trial_check = False
            
            if current_block != 1:
                eyes_open_sound.play()
                sound_wait = True
                sound_start = time.clock()
                while sound_wait :
                    now = time.clock()
                    if (now - sound_start) > 2.00:
                        sound_wait = False

        elif block_markers_on == 1:
            block_start_msg = createMessage(w, FG_COLOUR, 'Block ' + str(current_block) + ': Eyes Open / Dark.\nWait for experimenter to intiate next sequence \nof trials.')
            bMarkerStr = "DARK"
            markers_on = False
            eyes_open = True
            skip_first_trial_check = True
            eyes_open_sound.play()
            sound_wait = True
            sound_start = time.clock()
            while sound_wait :
                now = time.clock()
                if (now - sound_start) > 2.00:
                    sound_wait = False

        elif block_markers_on == 2:
            block_start_msg = createMessage(w, FG_COLOUR, 'Block ' + str(current_block) + ': Eyes Closed / Dark.\nWait for experimenter to intiate next sequence \nof trials.')
            bMarkerStr = "CLOSED"
            markers_on = False
            eyes_closed_sound.play()
            skip_first_trial_check = True
            eyes_open = False
            sound_wait = True
            sound_start = time.clock()
            while sound_wait :
                    now = time.clock()
                    if (now - sound_start) > 2.00:
                        sound_wait = False   
        show_block_msg = True
        
        while show_block_msg :
            block_start_msg.draw()  # automatically draw every frame
            w.flip()
            keys = event.getKeys(['s', 'escape'])  # get keys from event buffer
            if 's' in keys: # experimenter must press ctl + s
                show_block_msg = False
            elif 'escape' in keys :
                exp_abort = True
                show_block_msg = False
           
        block_st_msg   = ["BLOCK_" + bMarkerStr + "_B" + '{0:02d}'.format(current_block) + "_START"]
        block_end_msg  = ["BLOCK_" + bMarkerStr + "_B" + '{0:02d}'.format(current_block) + "_END"]
        ev_outlet.push_sample(block_st_msg)

        if use_eyelink :
            elTk.sendMessage(block_st_msg)
        w.flip()
        
        block_trials = trialTargetOrder[trialBlockNumber == current_block]
        tn = 0

        # i = randrange(0,4)
        # SM = angles_horz[i][0]
        # MD = angles_horz[i][1]
        # LG = angles_horz[i][2]
        # TOFFSETX_SM = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(SM)))
        # TOFFSETX_MD = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(MD)))
        # TOFFSETX_LG = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(LG)))
        
        # SM_Y = angles_vert[i][0]
        # MD_Y = angles_vert[i][1]
        # LG_Y = angles_vert[i][2]
        # TOFFSETY_SM = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(SM_Y)))
        # TOFFSETY_MD = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(MD_Y)))
        # TOFFSETY_LG = (EYE_TO_SCREEN_CM * np.tan(np.deg2rad(LG_Y)))

        while tn < np.size(block_trials) :
        
            ## Refresh PsychoPy event listener (for KB press)
            event.clearEvents()

            # If experiment was aborted, display Y/N message, if Y then quit
            if exp_abort :
                exp_abort_prompt.draw()
                w.flip()
                abort_resp = False

                while not abort_resp :
                    keys = event.getKeys()
                    if 'y' in keys :
                        abort_resp = True
                    if 'n' in keys :
                        abort_resp = True
                        exp_abort = False
                        first_trial = True # spacebar pause before resuming trials
                        
                pylink.msecDelay(500)

                if exp_abort :
                    break
            
            # # Drift correct 
            if first_trial :
                trial_drift_correct = False # !! to control TRIAL-BY-TRIAL drift correct change this
            else : 
                trial_drift_correct = True # !! to control TRIAL-BY-TRIAL drift correct change this

            if trial_drift_correct and markers_on:
                pylink.msecDelay(500)
                drawCentStimOnly(w, fixOuterDrift, fixInner, fix_shift) 
                w.flip()
                drift_error = manual_drift_correction(get_calib_pix_from_pos(w, w_cent_x, w_cent_y), elTk)
                recalibrate = False
                if drift_error != 0 :
                    drift_correct_fail_msg.draw()
                    w.flip()
                    drift_resp = False
                    
                    ## Refresh PsychoPy event listener (for KB press)
                    event.clearEvents()

                    while not drift_resp :
                        keys = event.getKeys()
                        if 'y' in keys :
                            drift_resp = True
                            recalibrate = True
                        if 'n' in keys :
                            drift_resp = True
                        if 'escape' in keys :
                            drift_resp = True
                            exp_abort = True

               
                if recalibrate :
                    recalibrate = False
                    trial_drift_correct = False
                    ## Refresh PsychoPy event listener (for KB press)
                    event.clearEvents()
                    w.flip()
                    CalibrateEyelink(elTk)
                    post_calib_pause = True
                else :
                    post_calib_pause = False

                ## Refresh PsychoPy event listener (for KB press)
                event.clearEvents()
                w.flip()

                # If experiment was aborted during drift check, display Y/N message, if Y then quit
                if exp_abort :
                    exp_abort_prompt.draw()
                    w.flip()
                    abort_resp = False

                    while not abort_resp :
                        keys = event.getKeys()
                        if 'y' in keys :
                            abort_resp = True
                        if 'n' in keys :
                            abort_resp = True
                            exp_abort = False
                            first_trial = True # spacebar pause before resuming trials
                            
                    pylink.msecDelay(500)

                    if exp_abort :
                        break

            w.flip()

            # print("tn=" + str(tn) + ", tgt=" + str(block_trials[tn]))

            # stim_disp = True
            trialTarget = block_trials[tn]-1
            targDrawVert = blockTargVert[bn] 
            
            # Make messages for EDF and XDF
            iti_st_msg  = ["ITI_" + bMarkerStr + "_B" + '{0:02d}'.format(current_block) + "_T" + '{0:02d}'.format(tn+1) + "_START"]
            iti_end_msg = ["ITI_" + bMarkerStr + "_B" + '{0:02d}'.format(current_block) + "_T" + '{0:02d}'.format(tn+1) + "_END"]
    
            trial_st_msg   = ["TRIAL_" + bMarkerStr + "_B" + '{0:02d}'.format(current_block) + "_T" + '{0:02d}'.format(tn+1) + "_N" +  trialTargets[trialTarget] + "_START"]
            trial_stim_msg = ["TRIAL_" + bMarkerStr + "_B" + '{0:02d}'.format(current_block) + "_T" + '{0:02d}'.format(tn+1) + "_N" +  trialTargets[trialTarget] + "_STIM"]
            trial_ping_msg = ["TRIAL_" + bMarkerStr + "_B" + '{0:02d}'.format(current_block) + "_T" + '{0:02d}'.format(tn+1) + "_N" +  trialTargets[trialTarget] + "_PING"]
            trial_end_msg  = ["TRIAL_" + bMarkerStr + "_B" + '{0:02d}'.format(current_block) + "_T" + '{0:02d}'.format(tn+1) + "_N" +  trialTargets[trialTarget] + "_END"]
            trial_warn_msg = ["TRIAL_" + bMarkerStr + "_B" + '{0:02d}'.format(current_block) + "_T" + '{0:02d}'.format(tn+1) + "_N" +  trialTargets[trialTarget] + "_WARN"]

            ## Refresh PsychoPy event listener (for KB press)
            event.clearEvents()
    
            ### Display stims
            if markers_on :
                if targDrawVert == 1:
                    drawFixStimsVert(w, fixOuter, fixInner, trialTarget, TOFFSETY_VERT, fix_shift) 
                elif targDrawVert == 0:
                    drawFixStimsHorz(w, fixOuter, fixInner, trialTarget, TOFFSETX_HORZ, fix_shift)
                elif targDrawVert == 2:
                    drawFixStimsOblique(w, fixOuter, fixInner, trialTarget, TOFFSETX_HORZ, TOFFSETY_VERT, fix_shift)
            else :
                drawCentStimOnly(w, fixOuter, fixInner, fix_shift) 
            w.flip()
            
            if first_trial :
                # Wait for spacebar to begin, unless we just successfully drift corrected
                if not trial_drift_correct and not skip_first_trial_check:
                    if not markers_on :
                        if targDrawVert == 1:
                            drawFixStimsVert(w, fixOuter, fixInner, trialTarget, TOFFSETY_VERT, fix_shift) 
                        elif targDrawVert == 0:
                            drawFixStimsHorz(w, fixOuter, fixInner, trialTarget, TOFFSETX_HORZ, fix_shift)
                        elif targDrawVert == 2:
                            drawFixStimsOblique(w, fixOuter, fixInner, trialTarget, TOFFSETX_HORZ, TOFFSETY_VERT, fix_shift)
                        w.flip()
                    trials_start = False
                    while not trials_start :
                        keys = event.getKeys()
                        if keys:
                            if 'escape' in keys :
                                trials_start = True
                                exp_abort = True
                            if 'space' in keys :
                                trials_start = True
                    if exp_abort :
                        continue
                first_trial = False
                ### Display stims
                if markers_on :
                    if targDrawVert == 1:
                        drawFixStimsVert(w, fixOuter, fixInner, trialTarget, TOFFSETY_VERT, fix_shift) 
                    elif targDrawVert == 0:
                        drawFixStimsHorz(w, fixOuter, fixInner, trialTarget, TOFFSETX_HORZ, fix_shift)
                    elif targDrawVert == 2:
                        drawFixStimsOblique(w, fixOuter, fixInner, trialTarget, TOFFSETX_HORZ, TOFFSETY_VERT, fix_shift)
                else :
                    drawCentStimOnly(w, fixOuter, fixInner, fix_shift) 
                w.flip()
                pylink.msecDelay(1000)
            else:
                ## Refresh PsychoPy event listener (for KB press)
                event.clearEvents()

                

                while post_calib_pause :
                    keys = event.getKeys()
                    if keys :
                        if 'space' in keys :
                            post_calib_pause = False
                        if 'escape' in keys :
                            post_calib_pause = False
                            exp_abort = True
                            break

                if exp_abort :
                    continue

            ## Refresh PsychoPy event listener (for KB press)
            event.clearEvents()

            if udp_socket is not None :
                udp_socket.send(b"b")
            # udp_socket.sendto("b", (UDP_IP, UDP_PORT))
    
            # Send trial start message
            ev_outlet.push_sample(trial_st_msg)
            if use_eyelink :
                elTk.sendMessage(trial_st_msg)
                elTk.startRecording(1, 1, 1, 1)
    
            no_fix_pre_target = True
            trial_end = False
            pinged = False
            pretarget_pause_time = 1.
            gaze_warning_activated = False
            gaze_warning_trial_break = False

            # Pause briefly to verify fixation after letter is announced
            pause_start = time.clock()
           
            while no_fix_pre_target :
                if not exp_abort :
                    curr_time = time.clock()

                    # Get Eyelink sample
                    if eyes_open :
                        if use_eyelink :
                            els = None
                            els = CollectEyelinkSample(el_outlet, elTk, last_sample_time)
                            if els is not None:
                                smp = els[0]
                                last_sample_time = els[1]
                                if smp is not None:
                                    gaze = smp[0:2]
                                else:
                                    print("Eyelink error in trial - empty data point:" + ''.join(trial_warn_msg))

                    if (curr_time - pause_start) > pretarget_pause_time :
                        no_fix_pre_target = False
                        break

                    if eyes_open :     
                        if use_eyelink :
                            # Gets saccade angular distance upon any EndSaccade event
                            elsc = None
                            elsc = CollectEyelinkSaccades(el_outlet, elTk, last_sample_time)
                            if elsc is not None:
                                dist = elsc[0]
                                last_sample_time = elsc[1]
                                if dist > 4. :
                                    if not gaze_warning_activated :
                                        gaze_warning_activated = True
                                        no_fix_pre_target = False
                                        break

                    keys = event.getKeys()
                    if keys:
                        if 'escape' in keys :
                            exp_abort = True
                            no_fix_pre_target = False
                            break

            # Send letter announcement message
            if not gaze_warning_activated :
                ev_outlet.push_sample(trial_stim_msg)
                if use_eyelink :
                    elTk.sendMessage(trial_stim_msg)
                    # Play stimulus sound
                sounds[trialTarget].play()
                start_time = time.clock()
            else :
                start_time = 0

            ## Refresh PsychoPy event listener (for KB press)
            event.clearEvents()

            # Pause briefly to get fixation after letter is announced
            no_fix_post_target = True
            posttarget_pause_time = 0.35
            if not gaze_warning_activated :
                pause_start = time.clock()
                while no_fix_post_target :
                    if not exp_abort :
                        curr_time = time.clock()
                        if (curr_time - pause_start) > posttarget_pause_time :
                            no_fix_post_target = False
                            break
                        if eyes_open :
                            if use_eyelink :
                                # Gets saccade angular distance upon any EndSaccade event
                                elsc = None
                                elsc = CollectEyelinkSaccades(el_outlet, elTk, last_sample_time)
                                if elsc is not None:
                                    dist = elsc[0]
                                    last_sample_time = elsc[1]
                                    if dist > 3. :
                                        print("WARN")
                                        if not gaze_warning_activated :
                                            gaze_warning_activated = True
                                            no_fix_post_target = False
                                            break

                        keys = event.getKeys()
                        if keys:
                            if 'escape' in keys :
                                exp_abort = True
                                no_fix_post_target = False
                                break

            ## Refresh PsychoPy event listener (for KB press)
            event.clearEvents()

            # print("Pre Gaze Warning!")
            # Display gaze warning message and wait for keypress
            if gaze_warning_activated:
                ev_outlet.push_sample(trial_warn_msg)
                if eyes_open :
                    if use_eyelink :
                        elTk.sendMessage(trial_warn_msg)
                
                # warn_pause_start = time.clock()
                warn_wait = True
                while warn_wait :
                    now = time.clock()
                    if (now - start_time) > 0.75 :
                        warn_wait = False

                # print("Gaze Warning!")
                gaze_warning_sound.play()
                warning_quit = False
                gaze_warning_trial_break = True
                warn_flash_start = time.clock()
                warn_flash_time = 0.75
                while not warning_quit :
                    # pretrial_warning_msg.draw()  # automatically draw every frame
                    # w.flip()
                    now = time.clock()
                    if (now - warn_flash_start) < warn_flash_time :
                        ### Display red warning stims
                        if markers_on :
                            if targDrawVert == 1:
                                drawFixStimsVert(w, fixOuter, fixInner, trialTarget, TOFFSETY_VERT, fix_shift) 
                            elif targDrawVert == 0:
                                drawFixStimsHorz(w, fixOuterWarning, fixInner, trialTarget, TOFFSETX_HORZ, fix_shift)
                            elif targDrawVert == 2:
                                drawFixStimsOblique(w, fixOuter, fixInner, trialTarget, TOFFSETX_HORZ, TOFFSETY_VERT, fix_shift)
                        else :
                            drawCentStimOnly(w, fixOuterWarning, fixInner, fix_shift) 
                    else :
                        ### Back to regular black stims
                        if markers_on :
                            if targDrawVert == 1:
                                drawFixStimsVert(w, fixOuter, fixInner, trialTarget, TOFFSETY_VERT, fix_shift) 
                            elif targDrawVert == 0:
                                drawFixStimsHorz(w, fixOuter, fixInner, trialTarget, TOFFSETX_HORZ, fix_shift)
                            elif targDrawVert == 2:
                                drawFixStimsOblique(w, fixOuter, fixInner, trialTarget, TOFFSETX_HORZ, TOFFSETY_VERT, fix_shift)
                        else :
                            drawCentStimOnly(w, fixOuter, fixInner, fix_shift) 
                    w.flip()
                    keys = event.getKeys()  # get keys from event buffer
                    if keys:
                        warning_quit = True
                        if 'escape' in keys :
                            trial_end = True
                            exp_abort = True
                            break
            
            ## Refresh PsychoPy event listener (for KB press)
            event.clearEvents()

            # Recycle trial if gaze warning occured
            if gaze_warning_trial_break :
                
                # Pause to avoid warning sound stuttering error
                # warn_pause_start = time.clock()
                warn_snd_wait = True
                while warn_snd_wait :
                    now = time.clock()
                    if (now - warn_flash_start) > 1. :
                        warn_snd_wait = False

                # Append current trial to end of remaining trials list
                block_trials_remaining = np.concatenate((block_trials[tn+1:], [block_trials[tn]]), axis=None)
                # Shuffle if possible, to incorporate warned trial at a random point later in block
                if len(block_trials_remaining) > 2 :
                    while has_consecutive_runs(block_trials_remaining, 4) : # no >3 consecutives 
                        np.random.shuffle(block_trials_remaining)
                # Add new shuffled remaining block trials list to old list
                block_trials = np.concatenate((block_trials[:tn], block_trials_remaining), axis=None)
                pylink.msecDelay(500) # pause for 500ms to reduce immediate warning on next trial
                continue # don't iterate trial number, so that we continue from same tn value

            if markers_on :
                if targDrawVert == 1:
                    drawFixStimsVert(w, fixOuter, fixInner, trialTarget, TOFFSETY_VERT, fix_shift) 
                elif targDrawVert == 0:
                    drawFixStimsHorz(w, fixOuter, fixInner, trialTarget, TOFFSETX_HORZ, fix_shift)
                elif targDrawVert == 2:
                    drawFixStimsOblique(w, fixOuter, fixInner, trialTarget, TOFFSETX_HORZ, TOFFSETY_VERT, fix_shift)
            else :
                drawCentStimOnly(w, fixOuter, fixInner, fix_shift)
            w.flip()
    
            ## Refresh PsychoPy event listener (for KB press)
            event.clearEvents()

            # TRIAL LOOP
            while not trial_end :
                frame_start = time.clock()
    
                # Get Eyelink sample
                if eyes_open :
                    if use_eyelink :
                        els = None
                        els = CollectEyelinkSample(el_outlet, elTk, last_sample_time)
                        if els is not None:
                            smp = els[0]
                            last_sample_time = els[1]
                            if smp is not None:
                                gaze = smp[0:2]
                            else:
                                print("Eyelink error in trial - empty data point:" + ''.join(trial_warn_msg))
    
                # If 2 seconds has elapsed, play the ping sound, send to EDF/XDF
                if not pinged : 
                    if (frame_start - start_time) > 2.0 :
                        ev_outlet.push_sample(trial_ping_msg)
                        if use_eyelink :
                            elTk.sendMessage(trial_ping_msg)
                        ping_sound.play()
                        pinged = True
                
                # After the ping, wait 1000ms (3s since trial st) then end trial
                if pinged :
                    #if 'space' in keys :
                    if (frame_start - start_time) > 3.0 :
                        # Push LSL event marker for trial end
                        ev_outlet.push_sample(trial_end_msg)
                        # udp_socket.sendto("e", (UDP_IP, UDP_PORT)
                        if use_eyelink :
                            elTk.stopRecording()
                            elTk.sendMessage(trial_end_msg)
                        if udp_socket is not None :
                            udp_socket.send(b"e")
                        trial_end = True
                        break
                    
                # If ESC is pressed at any point, end trial
                keys = event.getKeys()
                if keys :
                    if 'escape' in keys :
                        trial_end = True
                        exp_abort = True
                        break
    
                ## Sleep for remainder of inter-sample period
                frame_end = time.clock()
                sleep_time = int(np.round(np.maximum(0., frame_start - frame_end + isi)*1000.))
                pylink.msecDelay(sleep_time)
                
            # END TRIAL LOOP

            ## Refresh PsychoPy event listener (for KB press)
            event.clearEvents()

            # ITI - Pause briefly between trials
            intr_pause_min_time = 1.0
            pause_start = time.clock()
            intr_pause = True
            intr_spacebar_press = False
            # Push LSL event marker for ITI start
            ev_outlet.push_sample(iti_st_msg)
            if use_eyelink :
                elTk.sendMessage(iti_st_msg)
            if not exp_abort :
                while intr_pause :
                    curr_time = time.clock()
                    if curr_time - pause_start > intr_pause_min_time :
                        if intr_spacebar_press :
                            intr_pause = False
                    keys = event.getKeys()
                    if keys :
                        if 'space' in keys :
                            intr_spacebar_press = True
                        if 'escape' in keys :
                            intr_pause = False
                            exp_abort = True
                            break
            
            # Push LSL event marker for ITI end
            ev_outlet.push_sample(iti_end_msg)
            if use_eyelink :
                elTk.sendMessage(iti_end_msg)

            tn = tn + 1

    w.flip()

    ## Refresh PsychoPy event listener (for KB press)
    event.clearEvents()

    # End final block
    block_end_msg  = ["b" + str(bn) + "_end"]
    if use_eyelink :
        elTk.sendMessage(block_end_msg)
    ev_outlet.push_sample(block_end_msg)

    # Display trial end message and wait for keypress
    # end_message.setAutoDraw(True)  # automatically draw every frame
    if not exp_abort :
        exp_end_sound.play()

    exp_quit = False
    while not exp_quit :
        end_msg.draw()  # automatically draw every frame
        w.flip()
        keys = event.getKeys()  # get keys from event buffer
        if keys:
            exp_quit = True
            
    pylink.msecDelay(1000)
    w.flip()