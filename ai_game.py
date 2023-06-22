# A video game using pygame and AI!
# Interact with non-player characters (NPCs) that use natural language processing models to chat with the user!
# Author: Christina Kampel

# See the companion article "Pygame with AI": https://de-fellows.github.io/RexCoding/python/pygame/huggingface/transformers/pipelines/natural%20language%20processing/nlp/machine%20learning/ml/artificial%20intelligence/ai/conversational%20models/question-answering%20models/fill-mask/text-generation/2023/06/21/Pygame-with-AI.html

# emoji icons from: https://emojipedia.org/apple/

# -------------------------------------BASICS NEEDED TO RUN THE GAME--------------------------------------------- #
# import libraries
import pygame
from pygame.locals import *
import random

# import NLP models
import chat_models
from chat_models import *

from transformers import Conversation, set_seed

# initialize all imported pygame modules - this will raise exceptions if it fails
pygame.init()

# global variable used with the event listener for quitting the game
running = True

# clock for setting frame rate of game (see end of event loop)
clock = pygame.time.Clock()

# set display window size (width, height) - the window is pygame's built-in GUI
screen = pygame.display.set_mode((1000,700))

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
key_loc = key_surf.get_rect(center = (850,615))

# lock icon - interactive object
lock_surf_large = pygame.image.load('ai_game_images/lock.png').convert_alpha()
# resize image
lock_surf = pygame.transform.scale(lock_surf_large, (72,72))
lock_loc = key_surf.get_rect(center = (150,300))

# unlocked lock icon - will not appear until key is used on lock
unlocked_surf_large = pygame.image.load('ai_game_images/unlocked_lock.png').convert_alpha()
# resize image
unlocked_surf = pygame.transform.scale(unlocked_surf_large, (72,72))

# polar bear icon - conversational chatbot NPC
polar_surf = pygame.image.load('ai_game_images/polar_bear.png').convert_alpha()
polar_loc = polar_surf.get_rect(center = (600,100))

# robot icon - question-answering NPC
robot_surf_large = pygame.image.load('ai_game_images/robot.png').convert_alpha()
# resize image
robot_surf = pygame.transform.scale(robot_surf_large, (72,72))
robot_loc = robot_surf.get_rect(center = (800,300))

# fox icon - fill-mask NPC
fox_surf_large = pygame.image.load('ai_game_images/fox.png').convert_alpha()
# resize image
fox_surf = pygame.transform.scale(fox_surf_large, (72,72))
fox_loc = fox_surf.get_rect(center = (900,450))

# moose icon - text generation NPC
moose_surf_large = pygame.image.load('ai_game_images/moose.png').convert_alpha()
# resize image
moose_surf = pygame.transform.scale(moose_surf_large, (72,72))
moose_loc = moose_surf.get_rect(center = (500,450))

# -------------------------------------FLAGS FOR INTERACTIVE OBJECTS--------------------------------------------- #

# For Text Box:
current_title = "PLAYER BEAR:"      # title changes to the name of the object/NPC being interacted with when
                                    # update_text_box_title is called at end of event loop

# For Chatbot NPCs:
input_text = ""                     # holds user input during interaction with NPC

new_user_input = False              # flag for new user input when talking to chatbot
                                    # True if user hits RETURN or ENTER key when interacting with chatbot
                                    # False otherwise

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

# For Conversational NPC (Polar Bear):
polar_convo = Conversation(conversation_id="100")
polar_convo.append_response("Hey! I'm a conversational model. Wanna chat?")

# For Question-Answering NPC (Robot):
robot_convo = {"past_user_inputs": [], "generated_responses": []}
robot_convo["generated_responses"].append("I am a question-answering chatbot. Ask me anything about this game.")

# For Fill-Mask NPC (Fox):
fox_convo = {"past_user_inputs": [], "generated_responses": []}
fox_convo["generated_responses"].append("I am a fill-mask chatbot. Give me a sentence and I will fill in the blanks wherever you write '<mask>'.")

# For Text-Generation NPC (Moose):
moose_story = "Once upon a time,"
# create a list of random numbers to be used as seeds for the text-generating model
seed_list = []
for i in range(100):
    seed_list.append(random.randint(0,500))
# use the first entry as the current seed
current_seed = seed_list[0]

# write lines to screen
def write_lines(lines: list[str], x: int, y: int, colour: str="black"):
    """
    Draws lines of text on the display surface (screen). The top left corner of the first line of text
    begins at position (x,y) and the y-value increases by 20 pixels for each line. If a line of text is
    longer than the width of the text box (690 pixels), the text is wrapped down to the next line.
    
    Parameters:
    - lines (list[str]): text to add to screen
    - x (int): x-value of the top left corner of the first line of text
    - y (int): y-value of the top left corner of the first line of text
    - colour (str): colour of text

    Returns:
    - y (int): y-value of the next possible line
    """
    for line in lines:
        # line of text that will appear on the screen - must fit text box width of 690 pixels
        line_to_render = ""
        # temporary string to test if a line will fit within the width of the text box
        line_to_test = ""

        # if the line will fit within the width of the text box, print the line to the screen
        if font.render(line, True, colour).get_width() <= 690:
            screen.blit(font.render(line, True, colour), (x,y))
        
        # if the line is longer than the text box...
        else:
            # create a list of all words in the line
            words = line.split()

            # Iterate over the list of words.
            # Here, we add words to line_to_test until it is too long to fit in the test box.
            # Note: when we split the line into words, we lost the spaces, so we need to add the spaces back in-between words,
            # unless we have reached the last word

            i = 0
            while i < len(words):

                # if the last word has been reached, add the word to line_to_test but don't add a space
                if i == len(words) - 1:
                    line_to_test = line_to_test + words[i]

                # otherwise, add the word to line_to_test with a space after it
                else:
                    line_to_test = line_to_test + words[i] + " "
                
                # check the length of line_to_test - if line_to_test is 690 pixels or less in width when it is rendered,
                # then add it to the line_to_render
                if font.render(line_to_test, True, colour).get_width() <= 690:
                    line_to_render = line_to_test
                
                # if the line would be too long with another added word...
                else:
                    # print the current line_to_render
                    screen.blit(font.render(line_to_render, True, colour), (x,y))
                    # clear the line_to_render (starts the next line with a blank string)
                    line_to_render = ""

                    # if the last word in words has been reached
                    if i == len(words) - 1:
                        # add the word to the line_to_test with no space after it
                        line_to_test = words[i]
                        # if we have reached the last word, we need to print it to the screen
                        line_to_render = line_to_test

                    # otherwise, add a space in-between the words
                    else:
                        # add the word to the line_to_test plus a space
                        line_to_test = words[i] + " "

                    # move the next line down on the screen
                    y += 20
                
                # move on to the next word
                i += 1
            
            # if the line_to_render is not empty, print it to the screen
            if not line_to_render == "":
                screen.blit(font.render(line_to_render, True, colour), (x,y))

        # move down a line
        y += 20
    
    return y

# update title of text box
def update_text_box_title():
    """
    Updates the title of the text box to the name of the object or NPC the player is colliding with.
    If none of these collisions are occurring, the default title "PLAYER BEAR: " is used.

    Parameters: None

    Returns: None
    """

    # make the current_title variable and all collision flags global so they do not need to be passed to the function
    global current_title
    global collide_tree
    global collide_lock
    global lock_state
    global collide_robot
    global collide_fox
    global collide_moose

    # collision with tree
    if collide_tree == True:
        current_title = "TREE: "
    
    # collision with lock
    elif collide_lock == True:
        if lock_state == "Locked":
            current_title = "LOCK: "
        elif lock_state == "Unlocked":
            current_title = "OPEN LOCK: "
    
    # coliision with polar bear
    elif collide_polar == True:
        current_title = "POLAR BEAR: CONVERSATIONAL MODEL"

    # collision with robot
    elif collide_robot == True:
        current_title = "ROBOT: QUESTION-ANSWERING MODEL"
    
    # collision with fox
    elif collide_fox == True:
        current_title = "FOX: FILL-MASK MODEL"

    # collision with moose
    elif collide_moose == True:
        current_title = "MOOSE: TEXT-GENERATING MODEL"
    
    # no collisions
    else:
        current_title = "PLAYER BEAR: "

# reset the story for the text-generating NPC
def reset_story():
    """
    Reset's the text-generating NPC's story to 'Once upon a time,'.
    Is activated when the player is interacting with the NPC and presses the BACKSPACE key.
    """

    # set global variables so they do not need to be passed to the function
    global moose_story
    global current_seed

    # reset the story variable
    moose_story = "Once upon a time,"

    # select a random new number from the seed_list to be the new seed
    current_seed = random.choice(seed_list)

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

        # if player collides with an NPC, accept the user's text input
        if event.type == KEYDOWN:
            if collide_polar == True or collide_robot == True or collide_fox == True or collide_moose == True:
                if event.key == pygame.K_RETURN:
                    new_user_input = True
                    
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                    if collide_moose == True:
                        reset_story()
                else:
                    input_text += event.unicode


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
    instructions = font.render("Use the arrow keys to move. When prompted, enter text and hit RETURN or ENTER.", True, "black")
    # draw instructions in top corner of the window
    screen.blit(instructions, (0,0))

    # draw text box
    pygame.draw.rect(screen, (214,201,240), pygame.Rect(10,540,690,150))
    # add title to text box - title changes to the object or NPC the player is interacting with
    # current_title = "PLAYER BEAR:"
    text_box_title = font.render(current_title, True, "red")

    # draw inventory box
    pygame.draw.rect(screen, (214,201,240), pygame.Rect(710,540,280,150))
    # add title to inventory box
    inventory_box_title = font.render("INVENTORY:", True, "red")

    # draw wall
    pygame.draw.rect(screen, (154, 146, 173), wall)

    # confine the player's icon to the rectangle of the display screen,
    # just below the line of instructions
    bear_loc.clamp_ip(pygame.Rect(0,10,1000,530))

    # add bear image to screen
    screen.blit(bear_surf, bear_loc)
    # add tree image to screen
    screen.blit(tree_surf, tree_loc)
    # add text box title to screen
    screen.blit(text_box_title, (10,540))
    # add inventory box title to screen
    screen.blit(inventory_box_title, (710,540))
    # add lock image to screen
    screen.blit(lock_surf, lock_loc)
    # add polar bear NPC to screen
    screen.blit(polar_surf, polar_loc)
    # add robot NPC to screen
    screen.blit(robot_surf, robot_loc)
    # add fox NPC to screen
    screen.blit(fox_surf, fox_loc)
    # add moose NPC to screen
    screen.blit(moose_surf, moose_loc)

    # ---------------------------------------INTERACTING WITH TREE------------------------------------------- #
    # flag for collision with tree - True if collision is currently occurring
    collide_tree = pygame.Rect.colliderect(bear_loc, tree_loc)

    # if player is colliding with tree and player hasn't climbed tree before, write text to screen
    if collide_tree == True and tree_climbed == False:
        write_lines(["There is a tall tree... with something at the top!", "Climb tree? Yes [y] or No [n]: "], 10, 560)
        
        # event listeners handle player's response, which is stored in climb_tree
        if climb_tree == "Yes":
            write_lines(["[y]: You climb to the top and find a KEY."], 10, 600, "blue")
            # player has key
            # key appears in inventory (see below)
            key = True
            # player has key but has not used it
            key_used = False

        elif climb_tree == "No":
            write_lines(["[n]: It looks too tall to climb anyway."], 10, 600, "blue")
    
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
        write_lines(["A lock. You use your paws but it won't budge.", "It probably needs a KEY..."], 10, 560)
        
        # if the player has the key but has not used it, give them the option to use it
        if key_used == False:
            write_lines(["Use KEY? Yes [y] or No [n]: "], 10, 600)

            # event listeners handle player's response, which is stored in open_lock
            if open_lock == "Yes":
                write_lines(["[y]: It worked!"], 10, 620, "blue")
                # change lock icon to unlocked version
                lock_surf = unlocked_surf                
                # key disappears from inventory
                key = False

            elif open_lock == "No":
                write_lines(["[n]: Really? Why not?"], 10, 620, "blue")

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


    # ----------------------------------------INTERACTING WITH POLAR BEAR (CONVERSATIONAL NPC)------------------------------------------ #
    # Model: facebook/blenderbot-400M-distill (https://huggingface.co/facebook/blenderbot-400M-distill?text=Hey+my+name+is+Julien%21+How+are+you%3F)
    
    # flag for collision with polar bear - True if collision is currently occurring
    collide_polar = pygame.Rect.colliderect(bear_loc, polar_loc)
    
    if collide_polar == True:

        # if the player has not spoken to the chatbot yet
        if len(polar_convo.past_user_inputs) == 0:
            # show the most recent bot response and get the y-coordinate for the next line
            y = write_lines(["P. Bear: " + polar_convo.generated_responses[-1]], 10, 560, "blue")
            # on the next line, show the user's input on screen as they type it out
            write_lines([f"You: {input_text}"], 10, y, "black")

        else:
            # show the most recent user input and get the y-coordinate for the next line
            y = write_lines(["You: " + polar_convo.past_user_inputs[-1]], 10, 560, "black")
            # on the next line, show the most recent bot response and get the y-coordinate for the next line
            y2 = write_lines(["P. Bear: " + polar_convo.generated_responses[-1]], 10, y, "blue")
            # on the next line, show the user's input on screen as they type it out
            write_lines([f"You: {input_text}"], 10, y2, "black")

        # if the player hits the RETURN or ENTER key
        if new_user_input == True:
            # remove the oldest bot response from the conversation
            polar_convo.generated_responses.pop(0)
            # if there are older lines of user input in the conversation, remove the oldest line
            # (this does not occur the first time the user enters a new line)
            if len(polar_convo.past_user_inputs) > 0:
                polar_convo.past_user_inputs.pop(0)
            # add the user's input to the conversation object
            polar_convo.add_user_input(input_text)
            # have the chatbot respond to the conversation object - automatically adds bot's response to the object
            blenderbot(polar_convo)
            
            new_user_input = False
            input_text = ""

    # ----------------------------------------INTERACTING WITH ROBOT (QUESTION-ANSWERING NPC)------------------------------------------ #
    # Model: distilbert-base-cased-distilled-squad (https://huggingface.co/distilbert-base-cased-distilled-squad)
    
    # Note: the logic below is the same as the logic for the conversational model

    # flag for collision with robot - True if collision is currently occurring
    collide_robot = pygame.Rect.colliderect(bear_loc, robot_loc)
    
    if collide_robot == True:

        # if the player has not spoken to the chatbot yet
        if len(robot_convo["past_user_inputs"]) == 0:
            # show the most recent bot response and get the y-coordinate for the next line
            y = write_lines(["Robot: " + robot_convo["generated_responses"][-1]], 10, 560, "blue")
            # on the next line, show the user's input on screen as they type it out
            write_lines([f"You: {input_text}"], 10, y, "black")

        else:
            # show the most recent user input and get the y-coordinate for the next line
            y = write_lines(["You: " + robot_convo["past_user_inputs"][-1]], 10, 560, "black")
            # on the next line, show the most recent bot response and get the y-coordinate for the next line
            y2 = write_lines(["Robot: " + robot_convo["generated_responses"][-1]], 10, y, "blue")
            # on the next line, show the user's input on screen as they type it out
            write_lines([f"You: {input_text}"], 10, y2, "black")

        # if the player hits the RETURN or ENTER key
        if new_user_input == True:
            # remove the oldest bot response from the conversation
            robot_convo["generated_responses"].pop(0)
            # if there are older lines of user input in the conversation, remove the oldest line
            # (this does not occur the first time the user enters a new line)
            if len(robot_convo["past_user_inputs"]) > 0:
                robot_convo["past_user_inputs"].pop(0)
            # add the user's input to the conversation
            robot_convo["past_user_inputs"].append(input_text)
            # get the chatbot's response to the conversation - we only want the answer, not the other information it returns (score, etc.)
            response = qa_chatbot(robot_convo["past_user_inputs"][-1], context)["answer"]
            # format the response so the text looks normal
            response = response.capitalize() + "."
            # add the bot's response to the conversation history
            robot_convo["generated_responses"].append(response)

            new_user_input = False
            input_text = ""

    # ----------------------------------------INTERACTING WITH FOX (FILL-MASK NPC)------------------------------------------ #
    # Model: distilroberta-base (https://huggingface.co/distilroberta-base)
    
    # Note: the logic below is the same as the logic for the conversational model

    # flag for collision with fox - True if collision is currently occurring
    collide_fox = pygame.Rect.colliderect(bear_loc, fox_loc)

    if collide_fox == True:

        # if the player has not spoken to the chatbot yet
        if len(fox_convo["past_user_inputs"]) == 0:
            # show the most recent bot response and get the y-coordinate for the next line
            y = write_lines(["Fox: " + fox_convo["generated_responses"][-1]], 10, 560, "blue")
            # on the next line, show the user's input on screen as they type it out
            write_lines([f"You: {input_text}"], 10, y, "black")

        else:
            # show the most recent user input and get the y-coordinate for the next line
            y = write_lines(["You: " + fox_convo["past_user_inputs"][-1]], 10, 560, "black")
            # on the next line, show the most recent bot response and get the y-coordinate for the next line
            y2 = write_lines(["Fox: " + fox_convo["generated_responses"][-1]], 10, y, "blue")
            # on the next line, show the user's input on screen as they type it out
            write_lines([f"You: {input_text}"], 10, y2, "black")

        # if the player hits the RETURN or ENTER key
        if new_user_input == True:

            # remove the oldest bot response from the conversation
            fox_convo["generated_responses"].pop(0)
            # if there are older lines of user input in the conversation, remove the oldest line
            # (this does not occur the first time the user enters a new line)
            if len(fox_convo["past_user_inputs"]) > 0:
                fox_convo["past_user_inputs"].pop(0)
            # add the user's input to the conversation
            fox_convo["past_user_inputs"].append(input_text)

            # if the input text contains '<mask>', get the chatbot's response
            if '<mask>' in input_text:

                # get the chatbot's response to the conversation
                response = fm_chatbot(fox_convo["past_user_inputs"][-1])

                # get the most likely <mask> tokens and store them in a string
                response_tokens = ""
                i = 0
                while i < len(response):
                    # if we have reached the last token, insert a period
                    if i == len(response) - 1:
                        response_tokens += response[i]['token_str'] + "."
                    # otherwise, insert a comma
                    else:
                        response_tokens += response[i]['token_str'] + ","
                    i += 1

                # add the bot's response to the conversation history - The sentence with the filled-in blank, and the most likely words
                fox_convo["generated_responses"].append(f"{response[0]['sequence']} The most likely words are:{response_tokens}")

            # if the input does not contain '<mask>', print an error message
            else:
                fox_convo["generated_responses"].append("I don't understand. Make sure your input contains the word <mask>.")

            new_user_input = False
            input_text = ""

    # ----------------------------------------INTERACTING WITH MOOSE (TEXT-GENERATING NPC)------------------------------------------ #
    # Model: gpt2 (https://huggingface.co/gpt2?text=Once+upon+a+time%2C)

    # flag for collision with moose - True if collision is currently occurring
    collide_moose = pygame.Rect.colliderect(bear_loc, moose_loc)

    if collide_moose == True:

        # show the story
        write_lines(["Moose: " + moose_story], 10, 560, "blue")

        # show instructions for player
        write_lines(["TIP - Hit RETURN or ENTER to continue the story, or BACKSPACE to reset it."], 10, 670, "black")
 
        # if the player hits the RETURN or ENTER key, continue the story
        if new_user_input == True:
            
            # set the seed
            set_seed(current_seed)
            
            # get the model's response - the continued story
            moose_story = tg_chatbot(moose_story, max_new_tokens=35)[0]['generated_text']

            new_user_input = False
            input_text = ""
        
        # Note: if the player hits the BACKSPACE key, the story is reset to "Once upon a time," and the seed is changed.
        # This occurs when an event listener (see EVENT LISTENERS section) calls the reset_story() function.


    # ----------------------------------------UPDATE EVENT LOOP------------------------------------------ #
    # update text box title
    update_text_box_title()
    
    # update the display surface
    pygame.display.update()

    # set the frame rate to 60 FPS (frames per second) - a constant frame rate helps the game run smoother
    clock.tick(60)

# close the application
pygame.quit()