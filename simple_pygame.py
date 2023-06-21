# A simple video game using pygame!
# Author: Christina Kampel

# See the companion article Intro to Pygame: LINK HERE
# TODO: Put good link above ^^^ (when notebook is in final repo)
# emoji icons from: https://emojipedia.org/apple/

# -------------------------------------BASICS NEEDED TO RUN THE GAME--------------------------------------------- #
# import libraries
import pygame
from pygame.locals import *

# initialize all imported pygame modules - this will raise exceptions if it fails
pygame.init()

# global variable used with the event listener for quitting the game
running = True

# clock for setting frame rate of game (see end of event loop)
clock = pygame.time.Clock()

# set display window size (width, height) - the window is pygame's built-in GUI
screen = pygame.display.set_mode((700,500))

# -------------------------------------IMAGES, SURFACES & RECTANGLES--------------------------------------------- #
# surfaces - store image info
# convert_alpha() - convert image to pygame-friendly format while keeping transparent pixels
# rectangles - store location info
# get_rect() draws a rectangle around a surface

# bear icon - player's character
bear_surf = pygame.image.load('ai_game_images/brown_bear.png').convert_alpha()
bear_loc = bear_surf.get_rect()

# obstacle - wall
wall = pygame.Rect((200,200),(10,100))

# tree icon - interactive object
tree_surf = pygame.image.load('ai_game_images/tree.png').convert_alpha()
tree_loc = tree_surf.get_rect(center = (400,200))

# key icon - object appears in inventory and can be used on the lock
key_surf_large = pygame.image.load('ai_game_images/key.png').convert_alpha()
# resize image
key_surf = pygame.transform.scale(key_surf_large, (72,72))
key_loc = key_surf.get_rect(center = (595,445))

# lock icon - interactive object
lock_surf_large = pygame.image.load('ai_game_images/lock.png').convert_alpha()
# resize image
lock_surf = pygame.transform.scale(lock_surf_large, (72,72))
lock_loc = key_surf.get_rect(center = (150,300))

# unlocked lock icon - will not appear until key is used on lock
unlocked_surf_large = pygame.image.load('ai_game_images/unlocked_lock.png').convert_alpha()
# resize image
unlocked_surf = pygame.transform.scale(unlocked_surf_large, (72,72))


# -------------------------------------FLAGS FOR INTERACTIVE OBJECTS--------------------------------------------- #

# For Tree:
climb_tree = "None"     # holds player's response for interaction with tree:
                        #   - "None": tree is not interacted with
                        #   - "Yes": player wants to climb tree
                        #   - "No": player does not want to climb tree

tree_climbed = False    # True when the player has climbed the tree
                        # Prevents tree from being interacted with after player climbs tree

# For Lock:
open_lock = "None"      # holds player's response for interaction with lock:
                        #   - "None": lock is not interacted with
                        #   - "Yes": player wants to use key on lock
                        #   - "No": player does not want to use key on lock

lock_state = "Locked"   # current state of lock, either "Locked" or "Unlocked"

# For Key:
key = False             # whether or not the player has the key
                        #   - False: player does not have key
                        #   - True: player has key

key_used = "None"       # whether or not the key has been used
                        #   - "None": player does not have key
                        #   - "Yes": player used key
                        #   - "No": player has key but has not used it

# -------------------------------------TEXT HANDLING--------------------------------------------- #
# Note: General text will be black, player's response text will be blue

# font object - used to render strings into surfaces
font = pygame.font.SysFont("lucidaconsole", 14)

# write lines to screen
def write_lines(lines: list[str], x: int, y: int, colour: str="black"):
    """
    Draws lines of text on the display surface (screen). The top left corner of the first line of text
    begins at position (x,y) and the y-value increases by the increment for each line.
    
    Parameters:
    - lines (list[str]): text to add to screen
    - x (int): x-value of the top left corner of the first line of text
    - y (int): y-value of the top left corner of the first line of text
    - increment (int): number of pixels the y-value will increase by for each consecutive line
    - colour (str): colour of text

    Returns: None
    """
    for line in lines:
        screen.blit(font.render(line, True, colour), (x,y))
        y += 20

# -------------------------------------SET WINDOW TITLE AND ICON--------------------------------------------- #
# set window title
pygame.display.set_caption("My Simple Pygame")
# set window icon
pygame.display.set_icon(bear_surf)

# ---------------------------------------EVENT LOOP-------------------------------------------- #
while running:

    # -----------------------------------EVENT LISTENERS----------------------------------------------- #
    for event in pygame.event.get():

        # user quitting game - when the player clicks the "quit" button, "running" is set to False and application closes
        if event.type == QUIT:
            running = False
        
        # if player collides with tree, accept yes or no responses
        if event.type == KEYDOWN and collide_tree == True:
            if event.key == K_y:
                climb_tree = "Yes"
            elif event.key == K_n:
                climb_tree = "No"
        
        # if player collides with lock, accept yes or no responses
        if event.type == KEYDOWN and collide_lock == True:
            if event.key == K_y:
                open_lock = "Yes"
            elif event.key == K_n:
                open_lock = "No"

    # -----------------------------------MOVEMENTS----------------------------------------------- #
    # get currently pressed keys
    keys = pygame.key.get_pressed()

    # movements for player icon
    if keys[pygame.K_LEFT]:
        # Left movement occurs UNLESS...
        # player is within y-range of wall...........................and player is left of wall.....and player will collide with wall
        if bear_loc.bottom > wall.top and bear_loc.top < wall.bottom and bear_loc.left >= wall.right and bear_loc.left - 10 < wall.right: pass
        # otherwise, move left
        else: bear_loc = bear_loc.move([-10, 0])
    if keys[pygame.K_RIGHT]:
        # Right movement occurs UNLESS...
        # player is within y-range of wall...........................and player is right of wall.....and player will collide with wall
        if bear_loc.bottom > wall.top and bear_loc.top < wall.bottom and bear_loc.right <= wall.left and bear_loc.right + 10 > wall.left: pass
        # otherwise, move right
        else: bear_loc = bear_loc.move([10, 0])
    if keys[pygame.K_UP]:
        # Upward movement occurs UNLESS...
        # player is within x-range of wall...........................and player is below wall........and player will collide with wall
        if bear_loc.right > wall.left and bear_loc.left < wall.right and bear_loc.top >= wall.bottom and bear_loc.top - 10 < wall.bottom: pass
        # otherwise, move up
        else: bear_loc = bear_loc.move([0, -10])
    if keys[pygame.K_DOWN]:
        # Downward movement occurs UNLESS...
        # player is within x-range of wall...........................and player is above wall........and player will collide with wall
        if bear_loc.right > wall.left and bear_loc.left < wall.right and bear_loc.bottom <= wall.top and bear_loc.bottom + 10 > wall.top: pass
        # otherwise, move down
        else: bear_loc = bear_loc.move([0, 10])

    # ----------------------------------DRAWING ITEMS ON SCREEN------------------------------------------------ #
    # draw background
    pygame.draw.rect(screen, (191,180,214), screen.get_rect())

    # add instructions for the player
    instructions = font.render("Use the arrow keys to move.", True, "black")
    # draw instructions in top corner of the window
    screen.blit(instructions, (0,0))

    # draw text box
    pygame.draw.rect(screen, (214,201,240), pygame.Rect(10,400,480,90))
    # add title to text box
    text_box_title = font.render("PLAYER BEAR:", True, "red")

    # draw inventory box
    pygame.draw.rect(screen, (214,201,240), pygame.Rect(500,400,190,90))
    # add title to inventory box
    inventory_box_title = font.render("INVENTORY:", True, "red")

    # draw wall
    pygame.draw.rect(screen, (154, 146, 173), wall)

    # confine the player's icon to the rectangle of the display screen,
    # just below the line of instructions
    bear_loc.clamp_ip(pygame.Rect(0,10,700,390))

    # add bear image to screen
    screen.blit(bear_surf, bear_loc)
    # add tree image to screen
    screen.blit(tree_surf, tree_loc)
    # add text box title to screen
    screen.blit(text_box_title, (10,400))
    # add inventory box title to screen
    screen.blit(inventory_box_title, (500,400))
    
    # add lock image to screen
    screen.blit(lock_surf, lock_loc)

    # ---------------------------------------INTERACTING WITH TREE------------------------------------------- #
    # flag for collision with tree - True if collision is currently occurring
    collide_tree = pygame.Rect.colliderect(bear_loc, tree_loc)

    # if player is colliding with tree and player hasn't climbed tree before, write text to screen
    if collide_tree == True and tree_climbed == False:
        write_lines(["There is a tall tree... with something at the top!", "Climb tree? Yes [y] or No [n]: "], 10, 420)
        
        # event listeners handle player's response, which is stored in climb_tree
        if climb_tree == "Yes":
            write_lines(["[y]: You climb to the top and find a KEY."], 10, 460, "blue")
            # player has key
            # key appears in inventory (see below)
            key = True
            # player has key but has not used it
            key_used = False

        elif climb_tree == "No":
            write_lines(["[n]: It looks too tall to climb anyway."], 10, 460, "blue")
    
    # if player is not colliding with tree
    elif collide_tree == False:
        # if player climbed the tree (has the key)
        if key == True:
            # prevents tree from being interacted with after it has been climbed
            tree_climbed = True

        # climb_tree removes the text from the text box when player is not colliding with tree
        climb_tree = "None"

    # ----------------------------------------KEY APPEARING IN INVENTORY------------------------------------------ #
    # if player has key, key icon appears in inventory
    if key == True:
        screen.blit(key_surf, key_loc)
    
    # ----------------------------------------INTERACTING WITH LOCK------------------------------------------ #
    # flag for collision with lock - True if collision is currently occurring
    collide_lock = pygame.Rect.colliderect(bear_loc, lock_loc)

    # if player is colliding with lock and the lock is locked, write text to screen
    if collide_lock == True and lock_state == "Locked":
        write_lines(["A lock. You use your paws but it won't budge.", "It probably needs a KEY..."], 10, 420)
        
        # if the player has the key but has not used it, give them the option to use it
        if key_used == False:
            write_lines(["Use KEY? Yes [y] or No [n]: "], 10, 460)

            # event listeners handle player's response, which is stored in open_lock
            if open_lock == "Yes":
                write_lines(["[y]: It worked!"], 10, 480, "blue")
                # change lock icon to unlocked version
                lock_surf = unlocked_surf                
                # key disappears from inventory
                key = False

            elif open_lock == "No":
                write_lines(["[n]: Really? Why not?"], 10, 480, "blue")

    # if player is not colliding with lock
    elif collide_lock == False:
        # if player wants to open the lock and the lock is locked...
        if open_lock == "Yes" and lock_state == "Locked":
            # unlock the lock
            lock_state = "Unlocked"
            # key has been used
            key_used = True

        # open_lock removes the text from the text box when player is not colliding with lock
        open_lock = "None"
    
    # ----------------------------------------UPDATE EVENT LOOP------------------------------------------ #
    # update the display surface
    pygame.display.update()

    # set the frame rate to 60 FPS (frames per second) - a constant frame rate helps the game run smoother
    clock.tick(60)

# close the application
pygame.quit()