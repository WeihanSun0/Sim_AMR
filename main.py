import pygame

from environment import * 
from objects import Gmap
from objects import Bot
from objects import Orientation
from time import sleep
import sys



def print_usage():
    print("===Simulation of AMR===")
    print("TARGET: arrive the block with flag without touch any barries")
    print("CONTROL: 1. 'a,w,s,d' to control view orientation 2. arrow to control AMR")
    print("         r: restart, q: quit, o: view the barries")


def save_log(f, player, mode, record):
    f.write(f'{player}, {mode}, {record["move"]}, {record["view"]}, {record["goal"]}, {record["fail"]}\n')

if __name__ == '__main__':
    print_usage()
    # append log
    player = 'unknown'
    if len(sys.argv) == 2:
        player = sys.argv[1]
    log = open('./record.log', 'a+')

    pygame.init()
    screen_g = pygame.display.set_mode((display_height, display_width))
    pygame.display.set_caption('simulation')
    # create map
    global_env = Gmap(screen_g)
    setting = global_env.get_setting() 
    mode = 1 # 0: only tof 1:tof+sona
    bot = Bot(mode)
    done = False
    clock = pygame.time.Clock()
    current_pos = bot.get_current_pos()
    flag_show = 0 # 0: robot view 1: global view 2: failed 3: goal
    is_move = 0 # 0: still 1:move  
    need_save = 0 # 1: need 0: start 2: finished
    record_actions = {'move':0, 'view':0, 'goal': 0, 'fail': 0}
    while not done:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    mode = 0
                    bot.set_mode(mode)
                if event.key == pygame.K_1:
                    mode = 1
                    bot.set_mode(mode)
                if event.key == pygame.K_UP:
                    bot.move(Orientation.UP)
                if event.key == pygame.K_DOWN:
                    bot.move(Orientation.DOWN)
                if event.key == pygame.K_LEFT:
                    bot.move(Orientation.LEFT)
                if event.key == pygame.K_RIGHT:
                    bot.move(Orientation.RIGHT)
                if event.key == pygame.K_a:
                    bot.rotate(Orientation.LEFT)
                if event.key == pygame.K_d:
                    bot.rotate(Orientation.RIGHT)
                if event.key == pygame.K_w:
                    bot.rotate(Orientation.UP)
                if event.key == pygame.K_s:
                    bot.rotate(Orientation.DOWN)
                if event.key == pygame.K_q:
                    done = True 
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_a, pygame.K_w, pygame.K_d, pygame.K_s):
                    is_move = 1
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    record_actions['move'] += 1
                if event.key in (pygame.K_a, pygame.K_w, pygame.K_d, pygame.K_s):
                    record_actions['view'] += 1
                if event.key == pygame.K_h:
                    print_usage()
                if event.key == pygame.K_r:
                    record_actions = {'move':0, 'view':0, 'goal': 0, 'fail': 0}
                    global_env.reset_grids()
                    bot.reset()
                    flag_show = 0
                    need_save = 0
                if event.key == pygame.K_o:
                    flag_show = 1 if flag_show == 0 else 0 
        current_pos = bot.get_current_pos() 
        if is_move:
            bot.update_status()
            bot.detect(global_env.get_setting())
            is_move = 0
        if flag_show == 1: # show gt  
            global_env.show_gt(current_pos)
        elif flag_show == 0: # show bot view
            status = bot.get_status()
            global_env.show_status(current_pos, status)
            sonar_fov = bot.get_sonar_fov()
            tof_fov = bot.get_tof_fov()
            global_env.show_fov(sonar_fov, tof_fov, status)
        elif flag_show == 2: # fail
            global_env.show_fail()
            record_actions['fail'] = 1
            if need_save == 0:
                need_save = 1
        elif flag_show == 3: # goal 
            global_env.show_goal()
            record_actions['goal'] = 1
            if need_save == 0:
                need_save = 1
        if need_save == 1:
            save_log(log, player, mode, record_actions)
            need_save = 2 
        res = global_env.justify(current_pos)

        if res == -1: # bang
            flag_show = 2
        elif res == 1: # goal
            flag_show = 3 
        elif res == 0: # nothing
            pass
        pygame.display.flip()    
    pygame.quit()
    log.close()
