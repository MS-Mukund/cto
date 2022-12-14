import random
import sys

#files
import constant as ct
import update as up
import misc 

# command-line arguments
if sys.argv[1].lower() == 'no':
    # print(f"bye alpha = {ct.ALPHA}")
    # exit()
    ct.USE_PYGAME = False
else:
    import pygame as pg

strategy = sys.argv[2] if len(sys.argv) >= 3 else 'naive'
ct.ALPHA = float(sys.argv[3]) if len(sys.argv) >= 4 else 1
# ct.NUM_OBS[-1] = int(sys.argv[3]) if len(sys.argv) >= 4 else ct.NUM_OBS[-1]
ct.NUM_TARGET[-1] = int(sys.argv[4]) if len(sys.argv) >= 5 else ct.NUM_TARGET[-1]
# ct.TARG_SPEED[3] = float(sys.argv[5]) if len(sys.argv) >= 6 else ct.TARG_SPEED[3]
# ct.MODEL = int(sys.argv[5]) if len(sys.argv) >= 6 else ct.MODEL
# ct.TOTAL_TIME = 250

factor = 4
ct.AR_WID *= factor
ct.AR_HEI *= factor
ct.TARG_SPEED *= factor
ct.OBS_SPEED *= factor
ct.SENS_RAN[2] *= factor
ct.TARG_RAD *= factor
ct.OBS_RAD *= factor

if ct.USE_PYGAME == True:
    pg.init()
    window = pg.display.set_mode((ct.AR_WID, ct.AR_HEI)) 
    pg.display.set_caption("Cooperative Target Observation")

# Creating targets
# target_pos = [(random.uniform(0, ct.AR_WID), random.uniform(0, ct.AR_HEI))
            #   for _ in range(ct.NUM_TARGET[-1])]

posi = open('write.txt', 'r')
lines = posi.readlines()

target_pos = []
for i in range(len(lines)):
    if i < ct.NUM_TARGET[-1]:
        a, b = lines[i].strip('\n').split(' ')
        target_pos.append((float(a), float(b)))
target_dest = target_pos.copy()

# print(target_pos)

if ct.USE_PYGAME == True:
    targ = [pg.draw.circle(pg.display.get_surface(), ct.RED, target, ct.TARG_RAD)
        for target in target_pos]

# Creating observers
# obs_pos = [ (random.uniform(0, ct.AR_WID), random.uniform(0, ct.AR_HEI))
        #    for _ in range(ct.NUM_OBS[-1]) ]
obs_pos = []
for i in range(ct.NUM_TARGET[-1], len(lines)):
    if i < ct.NUM_OBS[-1]:
        a, b = lines[i].strip('\n').split(' ')
        obs_pos.append((float(a), float(b)))
obs_dest = obs_pos.copy()
if ct.USE_PYGAME == True:
    obsvr = [pg.draw.circle(pg.display.get_surface(), ct.GREEN, obs, ct.OBS_RAD)
         for obs in obs_pos]

Score = 0
gamma = 0
time_step = 0
pause = False
while time_step < ct.TOTAL_TIME:
    if ct.USE_PYGAME == True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                time_step = ct.TOTAL_TIME    # Break the loop

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_p:
                    pause = True
                    misc.paused(window)

        window.fill((0, 0, 0))
        # Update the position of targets
        up.TargUpdate( target_pos, targ, target_dest, obs_pos, obsvr, time_step )

        # Update the position of observers
        up.ObsUpdate( obs_pos, obsvr, obs_dest, target_pos, targ, time_step, strategy )

        # Check if the target is observed
        Score = up.ScrUpdate( target_pos, obs_pos, Score )
        
        # Display the score
        if pause == False:
            up.DispScr(Score)
            # misc.paused(window)

        # Update the screen
        pg.display.update()

        print(f"time_step: {time_step} Score: {Score}")
        print(f"obs_pos = {[(int(f),int(s)) for f,s in obs_pos]}")
        print(f"target_pos = {[(int(f),int(s)) for f,s in target_pos]}")
        print()
        pg.time.delay(100)

    else:
        up.TargUpdate( target_pos, target_dest, obs_pos, time_step )
        up.ObsUpdate( obs_pos, obs_dest, target_pos, time_step, strategy )

        Score = up.ScrUpdate( target_pos, obs_pos, Score )

    time_step += 1
    # pg.time.delay(10)

Score /= ct.TOTAL_TIME
# fname = 'obs_comp_' + strategy + '.txt'
fname = 'a.txt'
with open(fname, 'a') as f:
    f.write(f"{Score}\n")

if ct.USE_PYGAME == True:
    pg.quit()
