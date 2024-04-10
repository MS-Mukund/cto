from sys import stderr
import constant as ct
import pygame as pg
import random
import math
import pulp

import misc as ms
import helper as hp

# global variables for this file
lstp = [ct.NULL for _ in range(ct.NUM_TARGET[-1])]
MARGIN = 2.5/100  # borders margin percent

# for k-step prediction
kstep_pos = [[ct.NULL for _ in range(ct.GAMMA)]
             for _ in range(ct.NUM_OBS[-1])]
INVALID = -1
nearest_id = [INVALID for _ in range(ct.NUM_OBS[-1])]
uStart = [ct.NULL for _ in range(ct.NUM_OBS[-1])]

# for explore exploit with controlled randomisation
P_alpha_bar = [ 0.1 for _ in range(ct.GAMMA) ]
EPS = 1e-2
targ_info = [ [] for _ in range(ct.NUM_OBS[-1]) ]   # each list is a list containing [ id, uStart, uEnd, end_time ] 
targ_angle = [-1 for _ in range(ct.NUM_TARGET[-1])] 

def ComputeAngle(mean_pos, target):
    angle = 0
    # print(mean_pos, target)
    if (mean_pos[0] - target[0]) == 0:
        if target[1] > mean_pos[1]:
            angle = math.pi/2
        else:
            angle = -math.pi/2
    else:
        angle = math.atan((target[1] - mean_pos[1]) /
                          (target[0] - mean_pos[0]))

    if target[0] - mean_pos[0] < 0:
        angle = angle + math.pi

    # boundary condition
    if ct.AR_WID - target[0] <= ct.AR_WID * MARGIN:     # right edge
        angle = -math.pi
    elif target[0] <= ct.AR_WID*MARGIN:                 # left edge
        angle = 0
    elif ct.AR_HEI - target[1] <= ct.AR_HEI * MARGIN:   # top edge
        angle = -math.pi/2
    elif target[1] <= ct.AR_HEI * MARGIN:               # bottom edge
        angle = math.pi/2

    return angle

def Compute_Reward(obs, k, target_pos):   # Computes reward for each observer at that instant
    mean_pos = [0,0]
    num_targs = len(targ_info[k])
    for targ in targ_info[k]:
        if targ[1] == targ[2]:  # uStart == uEnd (or) target was observed at only one instant
            num_targs -= 1
            continue
        
        angle = ComputeAngle(targ[1], targ[2])
        mean_pos[0] += targ[2][0] + (2 * ct.GAMMA - targ[3]) * ct.TARG_SPEED[3] * math.cos(angle)
        mean_pos[1] += targ[2][1] + (2 * ct.GAMMA - targ[3]) * ct.TARG_SPEED[3] * math.sin(angle)

    reward = [0 for _ in range(10)]
    if num_targs == 0:
        return reward

    mean_pos[0] /= num_targs
    mean_pos[1] /= num_targs
    for j in range(1, 10 + 1):
        alpha = j*0.1
        dest = [ (1-alpha)*obs[0] + alpha*mean_pos[0], (1-alpha)*obs[1] + alpha*mean_pos[1] ]

        for targ in targ_info[k]:
            if (target_pos[targ[0]][0] - dest[0])**2 + (target_pos[targ[0]][1] - dest[1])**2 <= ct.SENS_RAN[2]**2:
                reward[j-1] += 1
    
    return reward

def LP(beta, P_alpha_bar, reward):
    '''
    Problem constraints: beta*P_i <= xi <= 1
                         sum(xi) = 1
                         maximise sum(rixi), ri = reward function
    '''
    prob = pulp.LpProblem('Problem', pulp.LpMaximize )
    P_alpha = [ pulp.LpVariable('P_alpha ' + str(cnt), 0, 1, pulp.LpContinuous) for cnt in range(len(P_alpha_bar)) ]
    
    prob += pulp.lpDot(P_alpha, reward)
    
    prob += pulp.lpSum(P_alpha) == 1, 'Sum_P_alpha'
    for i in range(len(P_alpha)):
        prob += P_alpha[i] >= beta * P_alpha_bar[i], f'P_alpha_bar[{i}] <= beta * P_alpha_bar[{i}]'
    
    prob.solve()
    E = pulp.value(prob.objective)
    P_alpha2 = [ pulp.value(P_alpha[i]) for _ in range(len(P_alpha)) ]

    return P_alpha2, E

def Nullify(i):
    kstep_pos[i] = [ct.NULL for _ in range(ct.GAMMA)]
    uStart[i] = ct.NULL
    nearest_id[i] = INVALID

def BRLP_CTO( obs, k, P_alpha_bar, target_pos ):   
    l = 0
    r = 1
    beta = (l+r)/2

    reward = Compute_Reward( obs, k, target_pos )  # k is the observer's index in targ_info list
    if reward == [0 for _ in range(10)]:        # nothing observed
        return [-1 for _ in range(ct.GAMMA)]    # invalid probabilities

    temp, E_bar = LP(1, P_alpha_bar, reward)     # E_bar is the lower bound on expected reward
    temp, E_star = LP(0, P_alpha_bar, reward)     # E_star is the upper bound on expected reward   

    PERCENT = 0.8
    E_min = E_bar + PERCENT * ( E_star - E_bar )    # E_min is the reward requested by user. 
    # sys.stderr.write(str(E_bar) + " " + str(E_star) + " " + str(E_min) + "\n" )


    P_alpha, E = LP(beta, P_alpha_bar, reward)
    if E_min > E_bar:
        while abs(E - E_min) > EPS:
            if E > E_min:
                l = beta
            else:
                r = beta
            beta = (l+r)/2
            P_alpha, E = LP(beta, P_alpha_bar, reward)
            # sys.stderr.write(str(beta) + " " + str(E) + "\n" )

    return P_alpha

'''
Returns weight for explore in explore-exploit strategy. 
Only one model (0-1) is uncommented. 
'''
def ComputeWt(num_targets):
    # 0-1 model
    if ct.MODEL == 0:
        return (1 if num_targets == 0 else 0)

    # 0-.5-1 model
    elif ct.MODEL == 1:
        if num_targets == 0:
            return 1
        elif num_targets == 1:
            return 0.5
        else:
            return 0

    # 1/(num_targets + 1)**2 model
    return ((1 / (num_targets + 1))**2)

def HandleBoundary(coords, angle, target, wid, ht):
    coords = list(coords)
    if coords[0] < 0:
        coords[1] = target[1] + math.tan(angle) * (0 - target[0])
        coords[1] = max(0, min(coords[1], ht))
        coords[0] = 0

    elif coords[0] > wid:
        coords[1] = target[1] + math.tan(angle) * (wid - target[0])
        coords[1] = max(0, min(coords[1], ht))
        coords[0] = wid

    elif coords[1] < 0:
        coords[0] = target[0] + (0 - target[1]) / math.tan(angle)
        coords[0] = max(0, min(coords[0], wid))
        coords[1] = 0

    elif coords[1] > ht:
        coords[0] = target[0] + (ht - target[1]) / math.tan(angle)
        coords[0] = max(0, min(coords[0], wid))
        coords[1] = ht

    return tuple(coords)

def boundary_check( pos, width, height ):
    if pos[0] < 0:
        pos = (0, pos[1])
    elif pos[0] > width:
        pos = (width, pos[1])
    if pos[1] < 0:
        pos = (pos[0], 0)
    elif pos[1] > height:
        pos = (pos[1], height)
    
    return pos

# def TargUpdate(target_pos, targ, targ_dest, obs_pos, obsvr, time_step):
def TargUpdate(target_pos, targ_dest, obs_pos, time_step):
    randomised = False # randomised movement
    # update target position
    for i, target in enumerate(target_pos):
        if target_pos[i] != targ_dest[i]:
            # prob = 0 # randomised movement
            prob = ct.T_PROB # straight line with randomisation
            # prob = 1 # straight line movement
            angle = hp.ControlledRandomise( prob, target, targ_dest[i], targ_angle[i])

            if (target[0] - targ_dest[i][0])**2 + (target[1] - targ_dest[i][1])**2 <= ct.TARG_SPEED[3]**2:
                target_pos[i] = targ_dest[i]
            else:
                target_pos[i] = (target[0] + ct.TARG_SPEED[3] * math.cos(angle),
                                 target[1] + ct.TARG_SPEED[3] * math.sin(angle))
            
            target_pos[i] = boundary_check( target_pos[i], ct.AR_WID, ct.AR_HEI )

        if ct.USE_PYGAME == True:
            targ[i] = pg.draw.circle( pg.display.get_surface(), ct.RED, target_pos[i], ct.TARG_RAD )

    if time_step % ct.GAMMA == 0:
        for i, target in enumerate(target_pos):
            in_range = []
            for obs in obs_pos:
                if (target[0] - obs[0])**2 + (target[1] - obs[1])**2 <= ct.SENS_RAN[2]**2:
                    in_range.append(obs)

            if len(in_range) == 0:      # sets random destination
                targ_dest[i] = (random.uniform(max(target_pos[i][0] - ct.AR_WID/8, 0), min(target_pos[i][0] + ct.AR_WID/8, ct.AR_WID)),
                                random.uniform(max(target_pos[i][1] - ct.AR_HEI/8, 0), min(target_pos[i][1] + ct.AR_HEI/8, ct.AR_HEI)))
            else:       # sets destination as far away as possible from all observers
                mean_pos = (sum([obs[0] for obs in in_range]) / len(in_range),
                            sum([obs[1] for obs in in_range]) / len(in_range))
                angle = ComputeAngle(mean_pos, target)

                coords = (target[0] + ct.GAMMA * ct.TARG_SPEED[3] * math.cos(angle),
                          target[1] + ct.GAMMA * ct.TARG_SPEED[3] * math.sin(angle))
                # boundary conditions
                targ_dest[i] = HandleBoundary(coords, angle, target, ct.AR_WID, ct.AR_HEI)
                targ_angle[i] = angle

                if randomised == True:
                    targ_angle[i] = random.uniform(0, 2*math.pi)

# def ObsUpdate(obs_pos, obsvr, obs_dest, target_pos, targ, time_step, strategy):
def ObsUpdate(obs_pos, obs_dest, target_pos, time_step, strategy):
    # update observer position
    for i, obs in enumerate(obs_pos):
        if obs_pos[i] != obs_dest[i]:
            angle = ComputeAngle(obs, obs_dest[i])

            if (obs[0] - obs_dest[i][0])**2 + (obs[1] - obs_dest[i][1])**2 <= ct.OBS_SPEED**2:
                obs_pos[i] = obs_dest[i]
            else:
                obs_pos[i] = (obs[0] + ct.OBS_SPEED * math.cos(angle),
                              obs[1] + ct.OBS_SPEED * math.sin(angle))

        if strategy.lower() == 'kstep' and time_step % ct.GAMMA != 0:           # track the nearest target
            if nearest_id[i] != INVALID and (target_pos[nearest_id[i]][0] - obs_pos[i][0])**2 + (target_pos[nearest_id[i]][1] - obs_pos[i][1])**2 <= ct.SENS_RAN[2]**2:
                kstep_pos[i][time_step % ct.GAMMA] = (target_pos[nearest_id[i]][0], target_pos[nearest_id[i]][1])
            else:
                kstep_pos[i][time_step % ct.GAMMA] = ct.NULL

        global targ_info
        if strategy.lower() == 'randomise':      # gathers information at each time step
            for j, target in enumerate(target_pos):
                if (target[0] - obs_pos[i][0])**2 + (target[1] - obs_pos[i][1])**2 <= ct.SENS_RAN[2]**2:
                    ms.HandleInsert(i, targ_info, j, target, time_step % ct.GAMMA )

        if ct.USE_PYGAME == True:
            obsvr[i] = pg.draw.circle( pg.display.get_surface(), ct.GREEN, obs_pos[i], ct.OBS_RAD )
            pg.draw.circle( pg.display.get_surface(), ct.BLUE, obs_pos[i], ct.SENS_RAN[2], 1 )

    if time_step % ct.GAMMA == 0:
        # K-means strategy
        if strategy.lower() == 'kmeans':
            for i, obs in enumerate(obs_pos):
                in_range = []
                for target in target_pos:
                    if (obs[0] - target[0])**2 + (obs[1] - target[1])**2 <= ct.SENS_RAN[2]**2:
                        in_range.append(target)

                if len(in_range) == 0:
                    obs_dest[i] = (random.uniform(max(obs[0] - ct.AR_WID/8, 0), min(obs[0] + ct.AR_WID/8, ct.AR_WID)),
                                   random.uniform(max(obs[1] - ct.AR_HEI/8, 0), min(obs[1] + ct.AR_HEI/8, ct.AR_HEI)))
                else:
                    mean_pos = (sum([target[0] for target in in_range]) / len(in_range),
                                sum([target[1] for target in in_range]) / len(in_range))
                    obs_dest[i] = ((1 - ct.ALPHA) * obs_dest[i][0] + ct.ALPHA * mean_pos[0],
                                   (1 - ct.ALPHA) * obs_dest[i][1] + ct.ALPHA * mean_pos[1])

        # 0-1 explore-exploit model strategy ( can be changed to 0-.5-1 and (1/(targets + 1) )**2 models )
        elif strategy.lower() == 'explexpl':
            for i, obs in enumerate(obs_pos):
                in_range = []
                for target in target_pos:
                    if (obs[0] - target[0])**2 + (obs[1] - target[1])**2 <= ct.SENS_RAN[2]**2:
                        in_range.append(target)

                explore_wt = ComputeWt(len(in_range))
                random_pos = (random.uniform(max(obs[0] - ct.AR_WID/8, 0), min(obs[0] + ct.AR_WID/8, ct.AR_WID)),
                              random.uniform(max(obs[1] - ct.AR_HEI/8, 0), min(obs[1] + ct.AR_HEI/8, ct.AR_HEI)))
                mean_pos = (0, 0)
                if len(in_range) != 0:
                    mean_pos = (sum([target[0] for target in in_range]) / len(in_range),
                                sum([target[1] for target in in_range]) / len(in_range))

                obs_dest[i] = ((1 - ct.ALPHA) * obs_dest[i][0] + ct.ALPHA * (explore_wt * random_pos[0] + (1 - explore_wt) * mean_pos[0]),
                               (1 - ct.ALPHA) * obs_dest[i][1] + ct.ALPHA * (explore_wt * random_pos[1] + (1 - explore_wt) * mean_pos[1]))

        # Memorisation strategy
        elif strategy.lower() == 'memo':
            for i, obs in enumerate(obs_pos):
                in_range = []
                closest = [-1, -1, ct.MAX]
                for target in target_pos:
                    if (obs[0] - target[0])**2 + (obs[1] - target[1])**2 <= ct.SENS_RAN[2]**2:
                        in_range.append(target)
                        if closest[2] > (obs[0] - target[0])**2 + (obs[1] - target[1])**2:
                            closest = [target[0], target[1], (obs[0] - target[0])**2 + (obs[1] - target[1])**2]

                # if no targets in sight, then go to lstp. If lstp is null, random exploret
                if len(in_range) == 0:
                    if lstp[i] == ct.NULL:
                        obs_dest[i] = (random.uniform(max(obs[0] - ct.AR_WID/8, 0), min(obs[0] + ct.AR_WID/8, ct.AR_WID)),
                                       random.uniform(max(obs[1] - ct.AR_HEI/8, 0), min(obs[1] + ct.AR_HEI/8, ct.AR_HEI)))
                    else:
                        obs_dest[i] = lstp[i]
                        lstp[i] = ct.NULL
                # if targets in sight, then exploit. Store position in lstp.
                else:
                    mean_pos = (sum([target[0] for target in in_range]) / len(in_range),
                                sum([target[1] for target in in_range]) / len(in_range))
                    obs_dest[i] = ((1-ct.ALPHA) * obs_dest[i][0] + ct.ALPHA * mean_pos[0],
                                   (1-ct.ALPHA) * obs_dest[i][1] + ct.ALPHA * mean_pos[1])
                    lstp[i] = (closest[0], closest[1])

        # One step prediction strategy
        elif strategy.lower() == 'onestep':
            for i, obs in enumerate(obs_pos):
                in_range = []
                closest = [-1, -1, ct.MAX]
                for target in target_pos:
                    if (obs[0] - target[0])**2 + (obs[1] - target[1])**2 <= ct.SENS_RAN[2]**2:
                        in_range.append(target)
                        if closest[2] > (obs[0] - target[0])**2 + (obs[1] - target[1])**2:
                            closest = [target[0], target[1], (obs[0] - target[0])**2 + (obs[1] - target[1])**2]

                # if no targets in sight, then go to dest predicted from lstp. If lstp is null, random explore
                if len(in_range) == 0:
                    if lstp[i] == ct.NULL:
                        obs_dest[i] = (random.uniform(max(obs[0] - ct.AR_WID/8, 0), min(obs[0] + ct.AR_WID/8, ct.AR_WID)),
                                       random.uniform(max(obs[1] - ct.AR_HEI/8, 0), min(obs[1] + ct.AR_HEI/8, ct.AR_HEI)))
                    else:
                        angle = ComputeAngle(obs, lstp[i])
                        obs_dest[i] = (lstp[i][0] + 2 * ct.GAMMA * ct.TARG_SPEED[3] * math.cos(angle), 
                                        lstp[i][1] + 2 * ct.GAMMA * ct.TARG_SPEED[3] * math.sin(angle))
                        lstp[i] = ct.NULL
                # if targets in sight, then exploit. Store position in lstp.
                else:
                    mean_pos = (sum([target[0] for target in in_range]) / len(in_range),
                                sum([target[1] for target in in_range]) / len(in_range))
                    obs_dest[i] = ((1-ct.ALPHA) * obs_dest[i][0] + ct.ALPHA * mean_pos[0],
                                   (1-ct.ALPHA) * obs_dest[i][1] + ct.ALPHA * mean_pos[1])
                    lstp[i] = (closest[0], closest[1])

        # k-step prediction strategy
        elif strategy.lower() == 'kstep':
            for i, obs in enumerate(obs_pos):
                in_range = []
                closest = [-1, -1, ct.MAX, INVALID]
                for j, target in enumerate(target_pos):
                    if (obs[0] - target[0])**2 + (obs[1] - target[1])**2 <= ct.SENS_RAN[2]**2:
                        in_range.append(target)
                        if closest[2] > (obs[0] - target[0])**2 + (obs[1] - target[1])**2:
                            closest = [ target[0], target[1], (obs[0] - target[0])**2 + (obs[1] - target[1])**2, j ]

                # if no targets in sight, then go to dest predicted from k-observations (kstep_pos). If nearest_id is null, random explore
                if len(in_range) == 0:
                    if nearest_id[i] == INVALID:
                        obs_dest[i] = (random.uniform(max(obs[0] - ct.AR_WID/8, 0), min(obs[0] + ct.AR_WID/8, ct.AR_WID)),
                                       random.uniform(max(obs[1] - ct.AR_HEI/8, 0), min(obs[1] + ct.AR_HEI/8, ct.AR_HEI)))
                    else:
                        cnt = 0
                        for j, pos in enumerate(kstep_pos[i]):
                            if pos == ct.NULL:
                                cnt = j
                                break

                        if cnt == 1:       # uStart and uEnd are the same
                            obs_dest[i] = (random.uniform(max(obs[0] - ct.AR_WID/8, 0), min(obs[0] + ct.AR_WID/8, ct.AR_WID)),
                                           random.uniform(max(obs[1] - ct.AR_HEI/8, 0), min(obs[1] + ct.AR_HEI/8, ct.AR_HEI)))
                        else:
                            angle = ComputeAngle(uStart[i], kstep_pos[i][cnt-1])
                            obs_dest[i] = (kstep_pos[i][cnt-1][0] + (2 * ct.GAMMA - cnt+1) * ct.TARG_SPEED[3] * math.cos(angle), 
                                            kstep_pos[i][cnt-1][1] + (2 * ct.GAMMA - cnt+1) * ct.TARG_SPEED[3] * math.sin(angle))

                    Nullify(i)

                # if targets in sight, then exploit. Store nearest target id.
                else:
                    mean_pos = (sum([target[0] for target in in_range]) / len(in_range),
                                sum([target[1] for target in in_range]) / len(in_range))
                    obs_dest[i] = ((1 - ct.ALPHA) * obs_dest[i][0] + ct.ALPHA * mean_pos[0],
                                   (1 - ct.ALPHA) * obs_dest[i][1] + ct.ALPHA * mean_pos[1])

                    Nullify(i)
                    nearest_id[i] = closest[3]
                    uStart[i] = (target_pos[nearest_id[i]][0], target_pos[nearest_id[i]][1])
                    kstep_pos[i][0] = (uStart[i][0], uStart[i][1])
        
        # explore exploit with controlled randomisation
        elif strategy.lower() == 'randomise':
            for i, obs in enumerate(obs_pos):
                in_range = []
                for target in target_pos:
                    if (obs[0] - target[0])**2 + (obs[1] - target[1])**2 <= ct.SENS_RAN[2]**2:
                        in_range.append(target)

                explore_wt = ComputeWt(len(in_range))
                random_pos = (random.uniform(max(obs[0] - ct.AR_WID/8, 0), min(obs[0] + ct.AR_WID/8, ct.AR_WID)),
                              random.uniform(max(obs[1] - ct.AR_HEI/8, 0), min(obs[1] + ct.AR_HEI/8, ct.AR_HEI)))
                mean_pos = (0, 0)
                if len(in_range) != 0:
                    mean_pos = (sum([target[0] for target in in_range]) / len(in_range),
                                sum([target[1] for target in in_range]) / len(in_range))
                
                P_alpha = BRLP_CTO(obs, i, P_alpha_bar, target_pos)
                if P_alpha == [-1 for _ in range(ct.GAMMA)]:
                    obs_dest[i] = random_pos
                    continue

                alpha = random.uniform(0,1)
                sum2 = 0
                for cnt, probab in enumerate(P_alpha):
                    sum2 += probab
                    if sum2 >= alpha:
                        alpha = (cnt + 1)*0.1
                        break
                
                # print(alpha, file=sys.stderr)
                obs_dest[i] = ((1 - alpha) * obs_dest[i][0] + alpha * (explore_wt * random_pos[0] + (1 - explore_wt) * mean_pos[0]),
                               (1 - alpha) * obs_dest[i][1] + alpha * (explore_wt * random_pos[1] + (1 - explore_wt) * mean_pos[1]))  

            # nullify targ_info
            targ_info = [ [] for _ in range(ct.NUM_OBS[-1]) ]     

        # Move in only Y-direction
        else:
            for i in range(len(obs_pos)):
                obs_pos[i] = (obs_pos[i][0], obs_pos[i][1] + ct.OBS_SPEED)
                if obs_pos[i][1] > ct.AR_HEI:
                    obs_pos[i] = (obs_pos[i][0], 0)

def ScrUpdate(target_pos, obs_pos, Score):
    for t in target_pos:
        for o in obs_pos:
            if (t[0] - o[0])**2 + (t[1] - o[1])**2 <= ct.SENS_RAN[2]**2:
                Score = Score + 1
                break
    return Score

def DispScr(Score):
    font = pg.font.SysFont("comicsansms", 30)
    text = font.render(f"Score: {Score}", True, ct.YELLOW)
    text_rect = text.get_rect()
    text_rect.center = (ct.AR_WID // 2, ct.AR_HEI // 2)
    pg.display.get_surface().blit(text, text_rect)
