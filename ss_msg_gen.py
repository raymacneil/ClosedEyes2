# Message generator


# Mapping of calibration types
CALIBRATION_TYPES = {
    'H': ('horz', 'horizontal'),
    'V': ('vert', 'vertical'),
    'O': ('obli', 'oblique')
}

def set_calibration_messages(calOrderID):
    """
    Generate calibration messages based on calibration order ID.
    
    Args:
        calOrderID (str): Two-character string containing calibration order (e.g., 'HV', 'VO', etc.)
        
    Returns:
        dict: Dictionary containing all calibration messages and strings
    """
    if len(calOrderID) != 2 or not all(c in 'HVO' for c in calOrderID):
        raise ValueError("calOrderID must be a 2-character string containing only H, V, or O")
    
    # Get remaining calibration type (the one not in calOrderID)
    all_types = set('HVO')
    remaining_type = list(all_types - set(calOrderID))[0]
    
    # Generate messages for all three calibrations
    results = {}
    
    # First calibration
    msg1, str1 = CALIBRATION_TYPES[calOrderID[0]]
    results['EV_MSG_CAL1'] = msg1
    results['STR_CAL1'] = str1
    
    # Second calibration
    msg2, str2 = CALIBRATION_TYPES[calOrderID[1]]
    results['EV_MSG_CAL2'] = msg2
    results['STR_CAL2'] = str2
    
    # Third calibration
    msg3, str3 = CALIBRATION_TYPES[remaining_type]
    results['EV_MSG_CAL3'] = msg3
    results['STR_CAL3'] = str3
    
    return results

# Example usage:
calOrderID = 'HV'
messages = set_calibration_messages(calOrderID)

# Test cases to verify logic matches original code
test_cases = ['HV', 'HO', 'VH', 'VO', 'OH', 'OV']

for test_case in test_cases:
    result = set_calibration_messages(test_case)
    print(f"\nTest case: {test_case}")
    for key, value in result.items():
        print(f"{key}: {value}")