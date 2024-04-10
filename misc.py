import pygame as pg
# from bisect import bisect_left
 
def HandleInsert( k, targ_info, j, pos, end_t ):
    for i in range(len(targ_info[k])):      # if the target is already in the list
        if targ_info[k][i][0] == j:
            targ_info[k][i][2] = pos
            targ_info[k][i][3] = end_t
            return

    # if the target is not in the list
    targ_info[k].append( [j, pos, pos, end_t] )   

# pause functionality
def paused(surface):   
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_p:
                    return

        pg.display.update()
