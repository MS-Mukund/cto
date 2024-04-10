import random
from math import pi

def ControlledRandomise(prob, target, targ_dest, targ_angle, ):
    if random.uniform(0, 1) < prob:   # straight line movement
        return targ_angle if targ_angle != -1 else random.uniform(0, 2*pi)
    elif prob == 0:
        return targ_angle if targ_angle != -1 else random.uniform(0, 2*pi)
    else:                                   # random movement
        return random.uniform(0, 2*pi)
