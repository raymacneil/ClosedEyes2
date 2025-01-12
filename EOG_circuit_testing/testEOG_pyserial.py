import serial

with serial.Serial('COM3', 19200, timeout=1) as ser:
    try:
        while True:
            x=ser.readline().decode('utf-8', errors='replace')
            x = x.strip("\r\n").split(", ")
            dat = [int(v) for v in x]
            print(dat)
    except KeyboardInterrupt:
        pass
