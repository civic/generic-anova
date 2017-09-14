import sys

def calc(prev, current, target):
    Kp = 20
    Ki = 0.5

    p = (target -current) * Kp
    i = ((target-current) + (target-prev))*10/2*Ki

    print("{:.3f}\tp={:.2f}    i={:.2f}   power={:d}".format(current, p, i, int(p+i)))
    

prev = float(sys.argv[1])
current = float(sys.argv[2])
target = float(sys.argv[3])

calc(prev, current, target)
    
