# Dragon Eat Dragon (a 2D Katamari Damacy clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random
import sys
import time
import math
import pygame

from pygame.locals import *

FPS = 30                                  # frames per second to update the screen
WINWIDTH = 640                            # width of the program's window, in pixels
WINHEIGHT = 480                           # height in pixels
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

GRASSCOLOR = (163,139,115)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

CAMERASLACK = 90                          # how far from the center the dragon moves before moving the camera
MOVERATE = 9                              # how fast the player moves
BOUNCERATE = 6                            # how fast the player bounces (large is slower)
BOUNCEHEIGHT = 30                         # how high the player bounces
STARTSIZE = 25                            # how big the player starts off
WINSIZE = 300                             # how big the player needs to be to win
INVULNTIME = 2                            # how long the player is invulnerable after being hit in seconds
GAMEOVERTIME = 4                          # how long the "game over" text stays on the screen in seconds
MAXHEALTH = 3                             # how much health the player starts with

NUM_ROCKS = 80                            # number of grass objects in the active area
NUM_DRAGONS = 30                          # number of dragons in the active area
DRAGONMINSPEED = 3                        # slowest dragon speed
DRAGONMAXSPEED = 7                        # fastest dragon speed
DIRCHANGEFREQ = 2                         # % chance of direction change per frame
LEFT = 'left'
RIGHT = 'right'

"""
This program has three data structures to represent the player, enemy dragons, and rock background objects. The data structures are dictionaries with the following keys:

Keys used by all three data structures:
    'x' - the left edge coordinate of the object in the game world (not a pixel coordinate on the screen)
    'y' - the top edge coordinate of the object in the game world (not a pixel coordinate on the screen)
    'rect' - the pygame.Rect object representing where on the screen the object is located.
    
Player data structure keys:
    'surface' - the pygame.Surface object that stores the image of the dragon which will be drawn to the screen.
    'facing' - either set to LEFT or RIGHT, stores which direction the player is facing.
    'size' - the width and height of the player in pixels. (The width & height are always the same.)
    'bounce' - represents at what point in a bounce the player is in. 0 means standing (no bounce), up to BOUNCERATE (the completion of the bounce)
    'health' - an integer showing how many more times the player can be hit by a larger dragon before dying.
    
Enemy Dragon data structure keys:
    'surface' - the pygame.Surface object that stores the image of the dragon which will be drawn to the screen.
    'movex' - how many pixels per frame the dragon moves horizontally. A negative integer is moving to the left, a positive to the right.
    'movey' - how many pixels per frame the dragon moves vertically. A negative integer is moving up, a positive moving down.
    'width' - the width of the dragon's image, in pixels
    'height' - the height of the dragon's image, in pixels
    'bounce' - represents at what point in a bounce the player is in. 0 means standing (no bounce), up to BOUNCERATE (the completion of the bounce)
    'bouncerate' - how quickly the dragon bounces. A lower number means a quicker bounce.
    'bounceheight' - how high (in pixels) the dragon bounces

Grass data structure keys:
    'grassImage' - an integer that refers to the index of the pygame.Surface object in GRASSIMAGES used for this grass object
"""


class BDGame:
    """SCREEN ATTRIBUTES"""
    FPS = 30  # frames per second to update the screen
    WINWIDTH = 640  # width of the program's window, in pixels
    WINHEIGHT = 480  # height in pixels
    HALF_WINWIDTH = int(WINWIDTH / 2)
    HALF_WINHEIGHT = int(WINHEIGHT / 2)

    """COLORS"""
    GRASSCOLOR = (163, 139, 115)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)

    """"""
    CAMERASLACK = 90  # how far from the center the dragon moves before moving the camera
    MOVERATE = 9  # how fast the player moves
    BOUNCERATE = 6  # how fast the player bounces (large is slower)
    BOUNCEHEIGHT = 30  # how high the player bounces
    STARTSIZE = 25  # how big the player starts off
    WINSIZE = 300  # how big the player needs to be to win
    INVULNTIME = 2  # how long the player is invulnerable after being hit in seconds
    GAMEOVERTIME = 4  # how long the "game over" text stays on the screen in seconds
    MAXHEALTH = 3  # how much health the player starts with

    NUM_ROCKS = 80  # number of rock objects in the active area
    NUM_DRAGONS = 30  # number of dragons in the active area
    DRAGONMINSPEED = 3  # slowest dragon speed
    DRAGONMAXSPEED = 7  # fastest dragon speed
    DIRCHANGEFREQ = 2  # % chance of direction change per frame
    LEFT = 'left'
    RIGHT = 'right'

    def __init__(self):
        # set up variables for the start of a new game
        self.invulnerable_mode = False  # if the player is invulnerable
        self.invulnerable_start_time = 0  # time the player became invulnerable
        self.game_over_mode = False  # if the player has lost
        self.game_over_start_time = 0  # time the player lost
        self.win_mode = False  # if the player has won

        # create the surfaces to hold game text
        self.game_over_surf = BASICFONT.render('Game Over', True, WHITE)
        self.game_over_rect = self.game_over_surf.get_rect()
        self.game_over_rect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

        self.win_surf = BASICFONT.render('You have achieved OMEGA DRAGON!', True, WHITE)
        self.win_rect = self.win_surf.get_rect()
        self.win_rect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

        self.win_surf2 = BASICFONT.render('(Press "r" to restart.)', True, WHITE)
        self.win_rect2 = self.win_surf2.get_rect()
        self.win_rect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 30)

        # camera_x and camera_y are the top left of where the camera view is
        self.camera_x = 0
        self.camera_y = 0

        # stores the player object:
        self.player_obj = {
            'surface': pygame.transform.scale(L_DRAGON_IMG, (STARTSIZE, STARTSIZE)),
            'facing': LEFT,
            'size': STARTSIZE,
            'x': HALF_WINWIDTH,
            'y': HALF_WINHEIGHT,
            'bounce': 0,
            'health': MAXHEALTH}

        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False

        self.rock_objs = []  # stores all the grass objects in the game
        self.dragon_objs = []  # stores all the non-player dragon objects

        # start off with some random grass images on the screen
        for i in range(10):
            self.rock_objs.append(self._make_new_rock(self.camera_x, self.camera_y))
            self.rock_objs[i]['x'] = random.randint(0, WINWIDTH)
            self.rock_objs[i]['y'] = random.randint(0, WINHEIGHT)

    def _make_new_dragon(self, camera_x, camera_y):
        dragon = {}

        general_size = random.randint(5, 25)
        multiplier = random.randint(1, 3)

        dragon['width'] = (general_size + random.randint(0, 10)) * multiplier
        dragon['height'] = (general_size + random.randint(0, 10)) * multiplier

        dragon['x'], dragon['y'] = self._get_random_off_camera_pos(camera_x, camera_y, dragon['width'], dragon['height'])

        dragon['movex'] = self._get_random_velocity()
        dragon['movey'] = self._get_random_velocity()

        if dragon['movex'] < 0:  # squirrel is facing left
            dragon['surface'] = pygame.transform.scale(L_DRAGON_IMG, (dragon['width'], dragon['height']))
        else:  # squirrel is facing right
            dragon['surface'] = pygame.transform.scale(R_DRAGON_IMG, (dragon['width'], dragon['height']))

        dragon['bounce'] = 0

        dragon['bouncerate'] = random.randint(10, 18)
        dragon['bounceheight'] = random.randint(10, 50)

        return dragon

    def _make_new_rock(self, camera_x, camera_y):
        gr = dict()

        gr['grassImage'] = random.randint(0, len(GRASSIMAGES) - 1)
        gr['width'] = GRASSIMAGES[0].get_width()
        gr['height'] = GRASSIMAGES[0].get_height()
        gr['x'], gr['y'] = self._get_random_off_camera_pos(camera_x, camera_y, gr['width'], gr['height'])
        gr['rect'] = pygame.Rect((gr['x'], gr['y'], gr['width'], gr['height']))

        return gr

    def _check_invulnerable_mode(self):
        # Check if we should turn off invulnerability
        if self.invulnerable_mode and time.time() - self.invulnerable_start_time > INVULNTIME:
            self.invulnerable_mode = False

    def _move_dragon_objs(self):
        for d_obj in self.dragon_objs:
            # move the dragon, and adjust for their bounce
            d_obj['x'] += d_obj['movex']
            d_obj['y'] += d_obj['movey']
            d_obj['bounce'] += 1

            if d_obj['bounce'] > d_obj['bouncerate']:
                # reset bounce amount
                d_obj['bounce'] = 0

            # random chance they change direction
            if random.randint(0, 99) < DIRCHANGEFREQ:
                d_obj['movex'] = self._get_random_velocity()
                d_obj['movey'] = self._get_random_velocity()

                # faces right
                if d_obj['movex'] > 0:
                    d_obj['surface'] = pygame.transform.scale(R_DRAGON_IMG, (d_obj['width'], d_obj['height']))
                # faces left
                else:
                    d_obj['surface'] = pygame.transform.scale(L_DRAGON_IMG, (d_obj['width'], d_obj['height']))

    @staticmethod
    def _get_random_velocity():
        speed = random.randint(DRAGONMINSPEED, DRAGONMAXSPEED)
        if random.randint(0, 1) == 0:
            return speed
        else:
            return -speed

    @staticmethod
    def _is_outside_active_area(camera_x, camera_y, obj):
        # Return False if camera_x and camera_y are more than
        # a half-window length beyond the edge of the window.
        bounds_left_edge = camera_x - WINWIDTH
        bounds_top_edge = camera_y - WINHEIGHT
        bounds_rect = pygame.Rect(bounds_left_edge, bounds_top_edge, WINWIDTH * 3, WINHEIGHT * 3)
        obj_rect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
        return not bounds_rect.colliderect(obj_rect)

    def _delete_unused_objs(self, obj_list):
        # go through all the objects and see if any need to be deleted.
        for i in range(len(obj_list) - 1, -1, -1):
            if self._is_outside_active_area(self.camera_x, self.camera_y, obj_list[i]):
                del obj_list[i]

    def _add_more_objs(self, obj_list, default_obj_size, obj_creation_func):
        # add more grass & dragons if we don't have enough.
        while len(obj_list) < default_obj_size:
            obj_list.append(obj_creation_func(self.camera_x, self.camera_y))

    def _adjust_player_camera(self):
        player_center_x = self.player_obj['x'] + int(self.player_obj['size'] / 2)
        player_center_y = self.player_obj['y'] + int(self.player_obj['size'] / 2)

        if (self.camera_x + HALF_WINWIDTH) - player_center_x > CAMERASLACK:
            self.camera_x = player_center_x + CAMERASLACK - HALF_WINWIDTH
        elif player_center_x - (self.camera_x + HALF_WINWIDTH) > CAMERASLACK:
            self.camera_x = player_center_x - CAMERASLACK - HALF_WINWIDTH
        if (self.camera_y + HALF_WINHEIGHT) - player_center_y > CAMERASLACK:
            self.camera_y = player_center_y + CAMERASLACK - HALF_WINHEIGHT
        elif player_center_y - (self.camera_y + HALF_WINHEIGHT) > CAMERASLACK:
            self.camera_y = player_center_y - CAMERASLACK - HALF_WINHEIGHT

    def _draw_player_dragon(self):
        # draw the player squirrel
        flash_is_on = round(time.time(), 1) * 10 % 2 == 1

        if not self.game_over_mode and not (self.invulnerable_mode and flash_is_on):
            self.player_obj['rect'] = pygame.Rect((
                self.player_obj['x'] - self.camera_x,
                self.player_obj['y'] - self.camera_y - self._get_bounce_amount(
                    self.player_obj['bounce'],
                    BOUNCERATE,
                    BOUNCEHEIGHT),
                self.player_obj['size'],
                self.player_obj['size']))

            DISPLAYSURF.blit(self.player_obj['surface'], self.player_obj['rect'])

    def _draw_dragons(self):
        # draw the other dragons
        for d_obj in self.dragon_objs:
            d_obj['rect'] = pygame.Rect((
                d_obj['x'] - self.camera_x,
                d_obj['y'] - self.camera_y - self._get_bounce_amount(
                    d_obj['bounce'],
                    d_obj['bouncerate'],
                    d_obj['bounceheight']),
                d_obj['width'],
                d_obj['height']))

            DISPLAYSURF.blit(d_obj['surface'], d_obj['rect'])

    def _draw_rocks(self):
        for r_obj in self.rock_objs:
            r_rect = pygame.Rect((
                r_obj['x'] - self.camera_x,
                r_obj['y'] - self.camera_y,
                r_obj['width'],
                r_obj['height']))

            DISPLAYSURF.blit(GRASSIMAGES[r_obj['grassImage']], r_rect)

    def _draw_health_meter(self):
        # draw red health bars
        for i in range(self.player_obj['health']):
            pygame.draw.rect(DISPLAYSURF, RED, (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10))

        # draw the white outlines
        for i in range(MAXHEALTH):
            pygame.draw.rect(DISPLAYSURF, WHITE, (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)

    def _handle_pygame_events(self):
        # TODO: Handle events in separate class
        # event handling loop
        for event in pygame.event.get():
            if event.type == QUIT:
                self.terminate()

            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    self.move_down = False
                    self.move_up = True

                elif event.key in (K_DOWN, K_s):
                    self.move_up = False
                    self.move_down = True

                elif event.key in (K_LEFT, K_a):
                    self.move_right = False
                    self.move_left = True

                    # change player image
                    if self.player_obj['facing'] != LEFT:
                        self.player_obj['surface'] = pygame.transform.scale(
                            L_DRAGON_IMG,
                            (self.player_obj['size'], self.player_obj['size']))

                    self.player_obj['facing'] = LEFT

                elif event.key in (K_RIGHT, K_d):
                    self.move_left = False
                    self.move_right = True

                    # change player image
                    if self.player_obj['facing'] != RIGHT:
                        self.player_obj['surface'] = pygame.transform.scale(
                            R_DRAGON_IMG,
                            (self.player_obj['size'], self.player_obj['size']))

                    self.player_obj['facing'] = RIGHT

                elif self.win_mode and event.key == K_r:
                    return

            elif event.type == KEYUP:
                # stop moving the player's dragon
                if event.key in (K_LEFT, K_a):
                    self.move_left = False
                elif event.key in (K_RIGHT, K_d):
                    self.move_right = False
                elif event.key in (K_UP, K_w):
                    self.move_up = False
                elif event.key in (K_DOWN, K_s):
                    self.move_down = False

                elif event.key == K_ESCAPE:
                    self.terminate()

    @staticmethod
    def terminate():
        pygame.quit()
        sys.exit()

    def _move_player(self):
        # actually move the player
        if self.move_left:
            self.player_obj['x'] -= MOVERATE
        if self.move_right:
            self.player_obj['x'] += MOVERATE
        if self.move_up:
            self.player_obj['y'] -= MOVERATE
        if self.move_down:
            self.player_obj['y'] += MOVERATE

        if (self.move_left or self.move_right or self.move_up or self.move_down) or self.player_obj['bounce'] != 0:
            self.player_obj['bounce'] += 1

        if self.player_obj['bounce'] > BOUNCERATE:
            # reset bounce amount
            self.player_obj['bounce'] = 0

        # check if the player has collided with any dragons
        for i in range(len(self.dragon_objs) - 1, -1, -1):
            dragon_obj = self.dragon_objs[i]
            if 'rect' in dragon_obj and self.player_obj['rect'].colliderect(dragon_obj['rect']):

                # a player/dragon collision has occurred
                if dragon_obj['width'] * dragon_obj['height'] <= self.player_obj['size'] ** 2:
                    # player is larger and eats the dragon
                    self.player_obj['size'] += int((dragon_obj['width'] * dragon_obj['height']) ** 0.2) + 1
                    del self.dragon_objs[i]

                    # set dragon image to be what direction they are going!
                    facing_image = L_DRAGON_IMG if self.player_obj['facing'] == LEFT else R_DRAGON_IMG
                    self.player_obj['surface'] = pygame.transform.scale(
                        facing_image,
                        (self.player_obj['size'], self.player_obj['size']))

                    if self.player_obj['size'] > WINSIZE:
                        # turn on "win mode"
                        self.win_mode = True

                elif not self.invulnerable_mode:
                    # player is smaller and takes damage
                    self.invulnerable_mode = True
                    self.invulnerable_start_time = time.time()
                    self.player_obj['health'] -= 1
                    if self.player_obj['health'] == 0:
                        self.game_over_mode = True  # turn on "game over mode"
                        self.game_over_start_time = time.time()

    def _show_game_over_text(self):
        # game is over, show "game over" text
        DISPLAYSURF.blit(self.game_over_surf, self.game_over_rect)
        if time.time() - self.game_over_start_time > GAMEOVERTIME:
            # end the current game
            return

    def _show_win_text(self):
        DISPLAYSURF.blit(self.win_surf, self.win_rect)
        DISPLAYSURF.blit(self.win_surf2, self.win_rect2)

    @staticmethod
    def _get_bounce_amount(current_bounce, bounce_rate, bounce_height):
        # Returns the number of pixels to offset based on the bounce.
        # Larger bounce_rate means a slower bounce.
        # Larger bounce_height means a higher bounce.
        # current_bounce will always be less than bounce_rate
        return int(math.sin((math.pi / float(bounce_rate)) * current_bounce) * bounce_height)

    @staticmethod
    def _get_random_off_camera_pos(camera_x, camera_y, obj_width, obj_height):
        # create a Rect of the camera view
        camera_rect = pygame.Rect(camera_x, camera_y, WINWIDTH, WINHEIGHT)
        while True:
            x = random.randint(camera_x - WINWIDTH, camera_x + (2 * WINWIDTH))
            y = random.randint(camera_y - WINHEIGHT, camera_y + (2 * WINHEIGHT))

            # create a Rect object with the random coordinates and use colliderect()
            # to make sure the right edge isn't in the camera view.
            obj_rect = pygame.Rect(x, y, obj_width, obj_height)
            if not obj_rect.colliderect(camera_rect):
                return x, y

    def run_game(self):

        # main game loop
        while True:
            self._check_invulnerable_mode()
            self._move_dragon_objs()

            self._delete_unused_objs(self.rock_objs)
            self._delete_unused_objs(self.dragon_objs)

            # add more rocks and dragons if we dont have enough
            self._add_more_objs(self.rock_objs, NUM_ROCKS, self._make_new_rock)
            self._add_more_objs(self.dragon_objs, NUM_DRAGONS, self._make_new_dragon)

            self._adjust_player_camera()

            # draw the green background
            DISPLAYSURF.fill(GRASSCOLOR)

            self._draw_dragons()
            self._draw_rocks()

            self._draw_player_dragon()

            # draw the health meter
            self._draw_health_meter()

            self._handle_pygame_events()

            if not self.game_over_mode:
                self._move_player()
            else:
                self._show_game_over_text()

            # check if the player has won
            if self.win_mode:
                self._show_win_text()

            pygame.display.update()
            FPSCLOCK.tick(FPS)


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, L_DRAGON_IMG, R_DRAGON_IMG, GRASSIMAGES

    pygame.init()

    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

    pygame.display.set_icon(pygame.image.load('./images/gameicon.png'))
    pygame.display.set_caption('Blueberry Dragon Eat Blueberry Dragon')

    # load the image files
    R_DRAGON_IMG = pygame.image.load('./images/blueberry-dragon.png')
    L_DRAGON_IMG = pygame.transform.flip(R_DRAGON_IMG, True, False)

    GRASSIMAGES = []
    for i in range(1, 4):
        GRASSIMAGES.append(pygame.image.load('./images/rock%s.png' % i))

    game = BDGame()

    while True:
        game.run_game()


if __name__ == '__main__':
    main()
