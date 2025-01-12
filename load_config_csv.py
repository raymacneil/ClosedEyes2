from pickle import TRUE
import Tkinter, tkFileDialog
import csv
import os
import numpy as np


def load_cond1_config_file() :
    
    # Init output vars (to pass to ss_trial)
    trialTargetOrder = np.array([], dtype=int)
    blockMarkersByTrial = np.array([], dtype=int)
    blockMarkersOn = np.array([], dtype=int)
    trialBlockNumber = np.array([], dtype=int)
    trialTargDir = np.array([], dtype=int)
    blockTargDir = np.array([], dtype=int)
    calOrderID = np.array([], dtype=int)

    # Open system dialog to choose config file
    root = Tkinter.Tk()
    root.withdraw()
    file_path = tkFileDialog.askopenfilename(initialdir = "Config_Files/",title = "Select file",filetypes = (("CSV files","*.csv"),("all files","*.*")))

    # Parse CSV file and store output vars
    if not file_path:
        print("error: no file selected!")
    else:
        try :
            with open(file_path, mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        line_count += 1
                    trialTargetOrder = np.append(trialTargetOrder, int(row["TrialTargetNum"]))
                    blockMarkersByTrial = np.append(blockMarkersByTrial, int(row["BlockMarkersOn"]))
                    trialBlockNumber = np.append(trialBlockNumber, int(row["BlockNum"]))
                    trialTargDir = np.append(trialTargDir, int(row["TargDirID"]))
                    calOrderID = np.append(calOrderID, int(row["TargDirID"]))
                    line_count += 1
                print('Got ' + os.path.basename(file_path) + ', processed ' + str(line_count-1) + ' trials total.')
                
                blockNumbers = np.unique(trialBlockNumber)
                num_blocks = np.size(blockNumbers,0)

                for bn in range(num_blocks):
                    current_block = blockNumbers[bn]
                    block_markers = blockMarkersByTrial[trialBlockNumber == current_block]
                    if np.all(block_markers == 0):
                        blockMarkersOn = np.append(blockMarkersOn, 0)
                    elif np.all(block_markers == 1):
                        blockMarkersOn = np.append(blockMarkersOn, 1)
                    elif np.all(block_markers == 2):
                        blockMarkersOn = np.append(blockMarkersOn, 2)

                for bn in range(num_blocks):
                    current_block = blockNumbers[bn]
                    targ_dir = trialTargDir[trialBlockNumber == current_block]
                    if np.all(targ_dir == 0):
                        blockTargDir = np.append(blockTargDir, 0)
                    elif np.all(targ_dir == 1):
                        blockTargDir = np.append(blockTargDir, 1)
                    elif np.all(targ_dir == 2):
                        blockTargDir = np.append(blockTargDir, 2)

                calOrderID_INDEX = np.unique(calOrderID, return_index=TRUE)[1]
                calOrderID_INDEX = calOrderID[np.unique(calOrderID_INDEX)] 
                numDirections =  np.size(calOrderID_INDEX)
            
            calOrderID = [0]*numDirections 

            for ii in range(numDirections):
                
                if calOrderID_INDEX[ii] == 0:
                    calOrderID[ii] = 'H'
                elif calOrderID_INDEX[ii] == 1:
                    calOrderID[ii] = 'V'
                elif calOrderID_INDEX[ii] == 2:
                    calOrderID[ii] = 'O'

            # if calOrderID_INDEX[1] == 0:
            #     calOrderID[1] = 'H'
            # elif calOrderID_INDEX[1] == 1:
            #     calOrderID[1] = 'V'
            # elif calOrderID_INDEX[1] == 2:
            #     calOrderID[1] = 'O'

            # if calOrderID_INDEX[2] == 0:
            #     calOrderID[2] = 'H'
            # elif calOrderID_INDEX[2] == 1:
            #     calOrderID[2] = 'V'
            # elif calOrderID_INDEX[2] == 2:
            #     calOrderID[2] = 'O'                    


        except:
            print("error: could not load file!")

    return trialTargetOrder, trialBlockNumber, trialTargDir, blockNumbers, blockMarkersOn, blockTargDir, calOrderID    



def load_cond2_config_file() :
    
    # Init output vars (to pass to ss_trial)
    trialTargetOrder = np.array([], dtype=int)
    blockEyesByTrial = np.array([], dtype=int)
    blockEyesOpen = np.array([], dtype=int)
    trialBlockNumber = np.array([], dtype=int)

    # Open system dialog to choose config file
    root = Tkinter.Tk()
    root.withdraw()
    file_path = tkFileDialog.askopenfilename(initialdir = "Config_Files/",title = "Select file",filetypes = (("CSV files","*.csv"),("all files","*.*")))

    # Parse CSV file and store output vars
    if not file_path:
        print("error: no file selected!")
    else:
        try :
            with open(file_path, mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        line_count += 1
                    trialTargetOrder = np.append(trialTargetOrder, int(row["TrialTargetNum"]))
                    blockEyesByTrial = np.append(blockEyesByTrial, int(row["BlockEyesOpen"]))
                    trialBlockNumber = np.append(trialBlockNumber, int(row["BlockNum"]))
                    line_count += 1
                print('Got ' + os.path.basename(file_path) + ', processed ' + str(line_count-1) + ' trials total.')
                
                blockNumbers = np.unique(trialBlockNumber)
                num_blocks = np.size(blockNumbers,0)
                for bn in range(num_blocks):
                    current_block = blockNumbers[bn]
                    block_markers = blockEyesByTrial[trialBlockNumber == current_block]
                    if np.all(block_markers == 0):
                        blockEyesOpen = np.append(blockEyesOpen, 0)
                    elif np.all(block_markers == 1):
                        blockEyesOpen = np.append(blockEyesOpen, 1)
        except:
            print("error: could not load file!")

    return trialTargetOrder, trialBlockNumber, blockNumbers, blockEyesOpen