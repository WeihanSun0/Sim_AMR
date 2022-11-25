import pygame

colors = {'black':(0, 0, 0), 'white':(255, 255, 255), 'red':(255, 0, 0), 'green':(0,255,0), 'blue':(0,0,255), 'cyan': (0, 255, 255), 'yellow': (255, 255, 0), 'magenta': (255, 0, 255)}
# map grid
grid_num_x = 9
grid_num_y = 9
grid_width = 80
grid_height = 80
display_width = grid_num_x * grid_width
display_height = grid_num_y * grid_height
# start end position
start_pos = (0, 0)
end_pos = (grid_num_x - 1, grid_num_y - 1)
# num of blocks
block_num = 5 
trans_num = 5 


def drawFloat(screen, bg_color, pos, fg_color, prob):
    ix, iy = pos
    start_x, start_y = grid_width * ix, grid_height * iy
    pygame.draw.rect(screen, bg_color, (start_x, start_y, grid_width, grid_height), 0)
    pygame.draw.rect(screen, colors['black'], (start_x, start_y, grid_width, grid_height), 1)

    # draw prob
    fonts = pygame.font.get_fonts()
    f = pygame.font.SysFont(fonts[0], 20)
    text = f.render(f"%.2f"%prob,True, fg_color, bg_color)
    textRect = text.get_rect()
    textRect.topleft = (start_x+2, start_y+2)
    screen.blit(text, textRect)

def drawRect(screen, color, pos):
    ix, iy = pos
    start_x, start_y = grid_width * ix, grid_height * iy
    pygame.draw.rect(screen, color, (start_x, start_y, grid_width, grid_height), 0)
    pygame.draw.rect(screen, colors['black'], (start_x, start_y, grid_width, grid_height), 1)

def drawPic(screen, image, pos):
    ix, iy = pos
    start_x, start_y = grid_width * ix, grid_height * iy
    screen.blit(image, (start_x, start_y))
    pygame.draw.rect(screen, colors['black'], (start_x, start_y, grid_width, grid_height), 1)
