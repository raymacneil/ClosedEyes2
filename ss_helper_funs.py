## Closed Eyes 2 Helper Functions
import numpy as np

def set_calibration_messages(calMsgID):
    """
    Generate calibration messages based on calibration order ID.
    
    Args:
        calMsgID (str): Once-character string from calibration order ID (e.g., 'H', 'V' or 'O')
        
    Returns:
        dict: Dictionary containing the calibration message strings
    """
    if len(calMsgID) != 1 or not all(c in 'HVO' for c in calMsgID):
        raise ValueError("calMsgID must be a 1-character of either H, V, or O")
    
    CALIBRATION_TYPES = {
    'H': ('horz', 'horizontal'),
    'V': ('vert', 'vertical'),
    'O': ('obli', 'oblique')
    }
    
    # Generate messages for given calibration type

    EV_MSG_CAL, STR_CAL = CALIBRATION_TYPES[calMsgID]
    
    return EV_MSG_CAL, STR_CAL

def split_on_changes(config_array, trial_targ_dir):
    """
    Split a numpy array into a list of arrays based on value changes.
    
    Parameters:
    config_array (numpy.ndarray): Input array containing sequences of identical values
    
    Returns:
    list: List of numpy arrays, where each array contains a sequence of identical values
    """
    # Find indices where values change
    change_indices = np.where(np.diff(trial_targ_dir) != 0)[0] + 1
    
    # Create list of arrays by splitting at change points
    split_config_array = []
    start_idx = 0
    
    # Handle the first sequence
    for idx in change_indices:
        # print(np.arange(start_idx, idx, 1))
        # config_array[start_idx:idx]
        split_config_array.append(config_array[start_idx:idx])
        # print(idx)
        start_idx = idx
    
    # Handle the last sequence
    split_config_array.append(config_array[start_idx:])
    
    return split_config_array


def split_block_array(config_array, trial_targ_dir, trial_block_number):
    """
    Split a block-level variable into a list of arrays based on changes in target direction
    at the trial level.
    
    Parameters:
    config_array (numpy.ndarray): Block-level variable to split (e.g., blockNumbers, blockMarkersOn)
    trial_targ_dir (numpy.ndarray): Trial-level target directions
    trial_block_number (numpy.ndarray): Trial-level block numbers
    
    Returns:
    list: List of numpy arrays containing the split block variable
    """
    # Find unique target directions in order of appearance
    unique_dirs = []
    for dir in trial_targ_dir:
        if dir not in unique_dirs:
            unique_dirs.append(dir)
    
    # Initialize list for results
    split_config_array = []
    
    # For each unique direction
    for direction in unique_dirs:
        # Find blocks associated with this direction
        blocks_mask = trial_block_number[trial_targ_dir == direction]
        unique_blocks = np.unique(blocks_mask)
        
        # Get the block variable values for these blocks
        # Subtract 1 from block numbers because they're 1-indexed
        block_values = config_array[unique_blocks - 1]
        
        # Add to results
        split_config_array.append(block_values)
    
    return split_config_array


