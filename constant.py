TOTAL_TIME = 1500

NUM_OBS      = [2, 6, 10, 14, 18]
NUM_TARGET   = [3, 9, 15, 21, 27]
TARG_SPEED = [0.2, 0.5, 0.8, 1.0, 1.2, 1.5]
SENS_RAN     = [5, 10, 15, 20, 25]
OBS_SPEED = 1.0

TARG_RAD = 2
OBS_RAD = 2

NUM_RUNS = 30

AR_WID = 150
AR_HEI = 150

#update after every gamma steps
GAMMA = 10
#alpha 
ALPHA = 1.0     # Ki = (1 - ALPHA) * Ki + ALPHA * Mi

#colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (228, 155, 15)

#randomisation probability
T_PROB = 0.7

# null position
NULL = (-1, -1)

#max
MAX = 10 ** 9

# use pygame?
USE_PYGAME = True

MODEL = 0   # 0: 0-1, 1: 0-.5-1, 2: (1/(num_targets+1))**2