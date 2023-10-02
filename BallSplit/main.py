import os
import pygame
# use pip install pygame

################################################################################
# 0. basic initialization (must do)

pygame.init()

# screen size setting
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))

# screen title setting
pygame.display.set_caption("Pang Game")  # name of the game

# FPS
clock = pygame.time.Clock()
################################################################################

# 1. User initialization (background, game image, coordinate, speed, font etc)
current_path = os.path.dirname(__file__) # return directory of current file
image_path = os.path.join(current_path, "images") # return directory of images folder

# background
background = pygame.image.load(os.path.join(image_path, "background.png"))

# stage
stage = pygame.image.load(os.path.join(image_path, "stage.png"))
stage_size = stage.get_rect().size
stage_height = stage_size[1]

# character
character = pygame.image.load(os.path.join(image_path, "character.png"))
character_size = character.get_rect().size
character_width = character_size[0]
character_height = character_size[1]
character_x_pos = screen_width / 2 - character_width / 2
character_y_pos = screen_height - character_height - stage_height

# character direction
character_to_x = 0

# character speed
character_speed = 5

# weapon
weapon = pygame.image.load(os.path.join(image_path, "weapon.png"))
weapon_size = weapon.get_rect().size
weapon_width = weapon_size[0]

# you can launch multiple weapons at a time
# stores multiple coordinates of weapons
weapons = []

# weapon speed
weapon_speed = 10

# calling balls
ball_images = [
    pygame.image.load(os.path.join(image_path, "balloon1.png")),
    pygame.image.load(os.path.join(image_path, "balloon2.png")),
    pygame.image.load(os.path.join(image_path, "balloon3.png")),
    pygame.image.load(os.path.join(image_path, "balloon4.png")),
]

# initial speed depending on ball sizes
ball_speed_y = [-18, -15, -12, -9] # index 0, 1, 2, 3

# balls
balls = []

# add first ball (largest)
balls.append({
    "pos_x" : 50, # x coordinate of the ball
    "pos_y" : 50, # y coordinate of the ball
    "img_idx": 0, # index of ball images (index 0: largest ball)
    "to_x": 3, # x axis direction
    "to_y": -6, # y axis direction
    "init_spd_y": ball_speed_y[0]}) # y axis initial speed

# saving info of ball and weapon that will vanish when collided
weapon_to_remove = -1
ball_to_remove = -1

# TimeOut, Mission Complete (success), Game Over (character hits the ball)
game_font = pygame.font.Font(None, 40)
total_time = 100
start_ticks = pygame.time.get_ticks() # define start time
game_result = "Game Over"

running = True
while running:
    dt = clock.tick(30)

    # 2. event handling (keyboard, mouse etc)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                character_to_x -= character_speed
            elif event.key == pygame.K_RIGHT:
                character_to_x += character_speed
            elif event.key == pygame.K_SPACE:
                weapon_x_pos = character_x_pos + character_width / 2 - weapon_width / 2
                weapon_y_pos = character_y_pos
                weapons.append([weapon_x_pos, weapon_y_pos])

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                character_to_x = 0

    # 3. defining location of game character
    character_x_pos += character_to_x

    if character_x_pos < 0:
        character_x_pos = 0
    elif character_x_pos > screen_width - character_width:
        character_x_pos = screen_width - character_width

    # weapon location control
    weapons = [[w[0], w[1] - weapon_speed] for w in weapons] # move weapon upwards

    # delete weapons that touched the ceiling = leave weapons that did not touch the ceiling
    weapons = [[w[0], w[1]] for w in weapons if w[1] > 0]

    # define ball location
    # enumerate() takes item in the list and get its index number and value
    for ball_idx, ball_val in enumerate(balls):
        ball_pos_x = ball_val["pos_x"]
        ball_pos_y = ball_val["pos_y"]
        ball_img_idx = ball_val["img_idx"]

        ball_size = ball_images[ball_img_idx].get_rect().size
        ball_width = ball_size[0]
        ball_height = ball_size[1]

        # change in direction of the ball when it hit the wall (bouncing effect)
        if ball_pos_x < 0 or ball_pos_x > screen_width - ball_width:
            # if the ball was heading left, it will bounce to right and
            # if the ball was heading right, it will bounce to left
            ball_val["to_x"] = ball_val["to_x"] * -1

        # vertical location
        if ball_pos_y >= screen_height - stage_height - ball_height:
            # ball bouncing from the stage
            ball_val["to_y"] = ball_val["init_spd_y"]
        else:
            # ball falls down to the stage
            ball_val["to_y"] += 0.5

        # movement of ball reflected on its location
        ball_val["pos_x"] += ball_val["to_x"]
        ball_val["pos_y"] += ball_val["to_y"]

    # 4. collision handling

    # update character rect info
    character_rect = character.get_rect()
    character_rect.left = character_x_pos
    character_rect.top = character_y_pos

    for ball_idx, ball_val in enumerate(balls):
        ball_pos_x = ball_val["pos_x"]
        ball_pos_y = ball_val["pos_y"]
        ball_img_idx = ball_val["img_idx"]

        # update ball rect info
        ball_rect = ball_images[ball_img_idx].get_rect()
        ball_rect.left = ball_pos_x
        ball_rect.top = ball_pos_y

        # ball and character collision handling
        if character_rect.colliderect(ball_rect):
            running = False
            break

        # ball and weapons collision handling
        for weapon_idx, weapon_val in enumerate(weapons):
            weapon_pos_x = weapon_val[0]
            weapon_pos_y = weapon_val[1]

            # update weapon rect info
            weapon_rect = weapon.get_rect()
            weapon_rect.left = weapon_pos_x
            weapon_rect.top = weapon_pos_y

            # check collision
            if weapon_rect.colliderect(ball_rect):
                weapon_to_remove = weapon_idx # setting for deleting the weapon
                ball_to_remove = ball_idx # setting for deleting the ball

                # if the ball is not the smallest ball, divide to next smaller balls
                if ball_img_idx < 3:
                    # get size info of current ball
                    ball_width = ball_rect.size[0]
                    ball_height = ball_rect.size[1]

                    # smaller ball info
                    small_ball_rect = ball_images[ball_img_idx+1].get_rect()
                    small_ball_width = small_ball_rect.size[0]
                    small_ball_height = small_ball_rect.size[1]

                    # smaller ball bouncing to left
                    balls.append({
                        "pos_x": ball_pos_x + ball_width/2 - small_ball_width/2,  # x coordinate of the ball
                        "pos_y": ball_pos_y + ball_height/2 - small_ball_height/2,  # y coordinate of the ball
                        "img_idx": ball_img_idx + 1,  # index of ball images (index 0: largest ball)
                        "to_x": -3,  # x axis direction
                        "to_y": -6,  # y axis direction
                        "init_spd_y": ball_speed_y[ball_img_idx+1]})

                    # smaller ball bouncing to right
                    balls.append({
                        "pos_x": ball_pos_x + ball_width/2 - small_ball_width/2,  # x coordinate of the ball
                        "pos_y": ball_pos_y +  ball_height/2 - small_ball_height/2,  # y coordinate of the ball
                        "img_idx": ball_img_idx + 1,  # index of ball images (index 0: largest ball)
                        "to_x": 3,  # x axis direction
                        "to_y": -6,  # y axis direction
                        "init_spd_y": ball_speed_y[ball_img_idx+1]})
                # leads to break in line 228: escape outer for loop
                break
        else: # continue the game
            continue # outer for loop continues
        break # accessed by break in line 225. escape double for loops

    # delete collided ball or weapon
    if ball_to_remove > -1:
        del balls[ball_to_remove]
        ball_to_remove = -1
    if weapon_to_remove > -1:
        del weapons[weapon_to_remove]
        weapon_to_remove = -1

    # end game if all balls are gone (success)
    if len(balls) == 0:
        game_result = "Mission Complete"
        running = False

    # 5. drawing on screen
    screen.blit(background, (0, 0))

    for weapon_x_pos, weapon_y_pos in weapons:
        screen.blit(weapon, (weapon_x_pos, weapon_y_pos))

    for idx, val in enumerate(balls):
        ball_pos_x = val["pos_x"]
        ball_pos_y = val["pos_y"]
        ball_img_idx = val["img_idx"]
        screen.blit(ball_images[ball_img_idx], (ball_pos_x, ball_pos_y))

    # time calculation
    elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
    timer = game_font.render("Time : {}". format(int(total_time - elapsed_time)), True, (255, 255, 255))

    # time ran out
    if total_time - elapsed_time <= 0:
        game_result = "Time Out"
        running = False

    # blit character and stage on top of the weapon
    screen.blit(stage, (0, screen_height - stage_height))
    screen.blit(character, (character_x_pos, character_y_pos))
    screen.blit(timer, (10, 10))

    pygame.display.update()

# game over message
msg = game_font.render(game_result, True, (255, 255, 0))
msg_rect = msg.get_rect(center = (int(screen_width/2), int(screen_height/2)))
screen.blit(msg, msg_rect)

# update screen and delay 2 sec so it doesn't end as soon as the screen is updated
pygame.display.update()
pygame.time.delay(2000)

# end pygame
pygame.quit()