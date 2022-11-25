import pygame
import numpy as np
import random
from environment import *

class BlockType:
    START = -5
    END = -10 
    NOTHING = 0
    BLOCK = 1
    TRANS = 2

class Orientation:
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

class Gmap:
    def __init__(self, screen) -> None:
        self.screen = screen
        self.reset_grids()
        self.init_log()

    def reset_grids(self):
        self.grids = np.array([[0 for x in range(grid_num_y)] for x in range(grid_num_x)])
        indice = np.random.choice(range(1, grid_num_x*grid_num_y-1), size=block_num+trans_num, replace=False)
        block_indice = tuple(indice[:block_num])
        trans_indice = tuple(indice[block_num:])
        for i in block_indice:
            y = i//grid_num_x
            x = i%grid_num_x
            self.grids[x, y] = BlockType.BLOCK
        for i in trans_indice:
            y = i//grid_num_x
            x = i%grid_num_x
            self.grids[x, y] = BlockType.TRANS
        self.grids[start_pos] = BlockType.START
        self.grids[end_pos] = BlockType.END

    def get_setting(self):
        return self.grids

    def init_log(self):
        robot_image = pygame.image.load("./robot_log.png").convert()
        self.robot_log = pygame.transform.scale(robot_image, (grid_width, grid_height))
        trans_image = pygame.image.load("./trans_log.jpg").convert()
        self.trans_log = pygame.transform.scale(trans_image, (grid_width, grid_height))
        block_image = pygame.image.load("./wall_log.png").convert()
        self.block_log = pygame.transform.scale(block_image, (grid_width, grid_height))
        target_image = pygame.image.load("./target_log.png").convert()
        self.target_log = pygame.transform.scale(target_image, (grid_width, grid_height))
        fail_image = pygame.image.load("./fail_log.jpg").convert()
        self.fail_log = pygame.transform.scale(fail_image, (400, 400))
        win_image = pygame.image.load("./goal_log.jpeg").convert()
        self.win_log = pygame.transform.scale(win_image, (400, 400))

    def show_fail(self):
        start_x, start_y = 150, 150 
        self.screen.blit(self.fail_log, (start_x, start_y))

    def show_goal(self):
        start_x, start_y = 150, 150 
        self.screen.blit(self.win_log, (start_x, start_y))

    # * show bot viewer
    def show_status(self, current_pos, grids):
        for j in range(grid_num_y):
            for i in range(grid_num_x):
                drawFloat(self.screen, colors['white'], (i, j), colors['blue'],grids[i, j])
        drawPic(self.screen, self.robot_log, current_pos)
        drawPic(self.screen, self.robot_log, current_pos)

    # * show bot fov 
    def show_fov(self, sonar_fov, tof_fov, grids):
        for j in range(grid_num_y):
            for i in range(grid_num_x):
                if tof_fov[i, j] != 0:
                    drawRect(self.screen, colors['yellow'], (i, j))
                    drawFloat(self.screen, colors['yellow'], (i, j), colors['black'], grids[i, j])
        for j in range(grid_num_y):
            for i in range(grid_num_x):
                if sonar_fov[i, j] != 0:
                    drawRect(self.screen, colors['magenta'], (i, j))
                    drawFloat(self.screen, colors['magenta'], (i, j), colors['black'], grids[i, j])
        drawPic(self.screen, self.target_log, end_pos)

    # * show map
    def show_gt(self, current_pos):
        for j in range(grid_num_y):
            for i in range(grid_num_x):
                drawRect(self.screen, colors['white'], (i, j))
                block_type = self.grids[i, j]
                if block_type == BlockType.BLOCK:
                    drawPic(self.screen, self.block_log, (i, j))
                elif block_type == BlockType.TRANS:
                    drawPic(self.screen, self.trans_log, (i, j))
                elif block_type == BlockType.END:
                    drawPic(self.screen, self.target_log, (i, j))
        drawPic(self.screen, self.robot_log, current_pos)
    
    # * justify
    def justify(self, current_pos):
        x, y = current_pos
        block = self.grids[x,y]
        if block == BlockType.NOTHING:
            return 0 # save
        elif block == BlockType.TRANS or block == BlockType.BLOCK:
            return -1 # fail
        elif block == BlockType.END:
            return 1 # win 


def insideGrids(pos)->bool:
    x, y = pos
    if x >= 0 and x < grid_num_x and y >= 0 and y < grid_num_y:
        return True
    else:
        return False

class Bot:
    def __init__(self, mode) -> None:
        self.set_mode(mode)
        self.reset()

    def set_mode(self, mode):
        self.mode = mode

    def reset(self):
        self.prop = np.array([[0.0 for x in range(grid_num_y)] for x in range(grid_num_x)]) # probability
        self.tof_res = np.array([[0.0 for x in range(grid_num_y)] for x in range(grid_num_x)])
        self.sonar_res = np.array([[0.0 for x in range(grid_num_y)] for x in range(grid_num_x)])
        self.grids = np.array([[0.0 for x in range(grid_num_y)] for x in range(grid_num_x)])
        self.grids[end_pos] = BlockType.END
        self.sonar_fov = np.array([[0.0 for x in range(grid_num_y)] for x in range(grid_num_x)])
        self.tof_fov = np.array([[0.0 for x in range(grid_num_y)] for x in range(grid_num_x)])
        self.orientation = Orientation.LEFT 
        self.cur_pos = [0, 0]

    def update_status(self):
        if self.mode == 1:
            self.update_sonar_fov()
        self.update_tof_fov()

    def update_sonar_fov(self):
        self.sonar_fov = np.array([[0.0 for x in range(grid_num_y)] for x in range(grid_num_x)])
        x, y = self.cur_pos
        if self.orientation == Orientation.RIGHT:
            for i in range(1, 4):
                xv, yv = x+i, y
                if insideGrids((xv, yv)):
                    self.sonar_fov[xv, yv] = 1
                xv, yv = x+2, y+i-2
                if insideGrids((xv, yv)):
                    self.sonar_fov[xv, yv] = 0.33
        elif self.orientation == Orientation.LEFT:
            for i in range(1, 4):
                xv, yv = x-i, y
                if insideGrids((xv, yv)):
                    self.sonar_fov[xv, yv] = 1
                xv, yv = x-2, y+i-2
                if insideGrids((xv, yv)):
                    self.sonar_fov[xv, yv] = 0.33
        elif self.orientation == Orientation.UP:
            for i in range(1, 4):
                xv, yv = x, y-i
                if insideGrids((xv, yv)):
                    self.sonar_fov[xv, yv] = 1
                xv, yv = x+i-2, y-2
                if insideGrids((xv, yv)):
                    self.sonar_fov[xv, yv] = 0.33
        elif self.orientation == Orientation.DOWN:
            for i in range(1, 4):
                xv, yv = x, y+i
                if insideGrids((xv, yv)):
                    self.sonar_fov[xv, yv] = 1
                xv, yv = x+i-2, y+2
                if insideGrids((xv, yv)):
                    self.sonar_fov[xv, yv] = 0.33

    def update_tof_fov(self):
        self.tof_fov = np.array([[0 for x in range(grid_num_y)] for x in range(grid_num_x)])
        x, y = self.cur_pos
        if self.orientation == Orientation.RIGHT:
            for i in range(1, 4):
                for j in range(1, 4):
                    xv, yv = x+i, y+j-2
                    if insideGrids((xv, yv)):
                        self.tof_fov[xv, yv] = 1
        elif self.orientation == Orientation.LEFT:
            for i in range(1, 4):
                for j in range(1, 4):
                    xv, yv = x-i, y+j-2
                    if insideGrids((xv, yv)):
                        self.tof_fov[xv, yv] = 1
        elif self.orientation == Orientation.UP:
            for i in range(1, 4):
                for j in range(1, 4):
                    xv, yv = x+j-2, y-i
                    if insideGrids((xv, yv)):
                        self.tof_fov[xv, yv] = 1
        elif self.orientation == Orientation.DOWN:
            for i in range(1, 4):
                for j in range(1, 4):
                    xv, yv = x+j-2, y+i
                    if insideGrids((xv, yv)):
                        self.tof_fov[xv, yv] = 1
    
    def rotate(self, ori):
        self.orientation = ori
    
    def move(self, ori):
        if ori == Orientation.LEFT:
            self.cur_pos[0] -= 1
        if ori == Orientation.RIGHT:
            self.cur_pos[0] += 1
        if ori == Orientation.UP:
            self.cur_pos[1] -= 1
        if ori == Orientation.DOWN:
            self.cur_pos[1] += 1
        if self.cur_pos[0] < 0:
            self.cur_pos[0] = 0
        if self.cur_pos[0] >= grid_num_x:
            self.cur_pos = grid_num_x - 1
        if self.cur_pos[1] < 0:
            self.cur_pos[1] = 0
        if self.cur_pos[1] >= grid_num_y:
            self.cur_pos[1] = grid_num_y - 1
    
    def get_current_pos(self):
        return self.cur_pos

    def get_sonar_fov(self):
        return self.sonar_fov

    def get_tof_fov(self):
        return self.tof_fov
    
    def get_status(self):
        return self.grids
    
    def detect_by_tof(self, gt_grids):
        pos_weight = 1.0
        neg_weight = -1.0
        visible_blocks = gt_grids == 1
        invisible_blocks = gt_grids != 1
        I_pos = (self.tof_fov & visible_blocks) *  pos_weight
        I_neg = (self.tof_fov & invisible_blocks) *  neg_weight
        I =  I_pos + I_neg
        self.tof_res += I

    def detect_by_sonar(self, gt_grids):
        pos_weight1 = 1.0 * 2
        pos_weight2 = 0.3 * 2
        pos_weight3 = 1.0 * 2
        neg_weight1 = -1.0 * 2
        neg_weight2 = -3.0 * 2
        neg_weight3 = -1.0 * 2
        visible = gt_grids > 0 
        invisible = gt_grids == 0 
        sure_view = self.sonar_fov == 1
        unsure_view = self.sonar_fov == 0.33
        I_pos1 = (sure_view & visible) * pos_weight1 # sure view
        I_neg1 = (sure_view & invisible) * neg_weight1 # nothing detected
        num_invisible = np.count_nonzero(unsure_view & invisible) 
        num_invisible = np.count_nonzero(unsure_view & visible)
        if num_invisible == 3: # nothing detected
            I_pos2 = (unsure_view & invisible) * neg_weight2
        else: # near wall
            I_pos2 = (unsure_view) * pos_weight2
        I = I_pos1 + I_pos2 + I_neg1
        self.sonar_res += I

    def detect(self, gt_grids):
        # tof results
        self.detect_by_tof(gt_grids)
        self.grids += self.tof_res
        # sonar results
        if self.mode == 1:
            self.detect_by_sonar(gt_grids)
            self.grids += self.sonar_res
        # update grids