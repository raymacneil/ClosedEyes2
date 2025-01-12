import time
import sys
import datetime as dt

def consoleTimer(mins, secs) :
    next_secs = (mins * 60) + secs
    start_time = dt.datetime.utcnow() # timer start time
    end_secs = start_time + dt.timedelta(0,next_secs)
    print("e")

    while True:
        current_time = dt.datetime.utcnow()
        time_left = end_secs - current_time
        total_time_elapsed = current_time - start_time

        # Print a time counter (MM:SS) until next message
        remaining_secs = time_left.seconds
        secs_elapsed = total_time_elapsed.seconds + 1
        if remaining_secs > 0 :
            next_secs = remaining_secs
            next_mins, next_secs = divmod(next_secs, 60)
            el_mins, el_secs = divmod(secs_elapsed, 60)
            sys.stdout.write("\r")
            sys.stdout.write('  %02d:%02d remaining. [Total time elapsed: %02d:%02d]' % (next_mins, next_secs, el_mins, el_secs)) 
            sys.stdout.flush()
        else :
            break

    return