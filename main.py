import pygame
from sys import exit
import random


pygame.init()
clock = pygame.time.Clock()

#window
win_height = 720
win_width = 551
window = pygame.display.set_mode((win_width, win_height))

# Images
bird_images = [pygame.image.load("assets/bird_down.png"),
               pygame.image.load("assets/bird_mid.png"),
               pygame.image.load("assets/bird_up.png")]
skyline_image = pygame.image.load("assets/background.png")
ground_image = pygame.image.load("assets/ground.png")
top_pipe_image = pygame.image.load("assets/pipe_top.png")
bottom_pipe_image = pygame.image.load("assets/pipe_bottom.png")
game_over_image = pygame.image.load("assets/game_over.png")
start_image = pygame.image.load("assets/start.png")

#game variables
scroll_speed = 1
bird_start_position = (100, 250)
score = 0
font = pygame.font.SysFont('Segoe', 26)
game_is_stopped = True

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = bird_images[0]
        self.rect = self.image.get_rect()
        self.rect.center = bird_start_position
        self.image_index = 0
        self.vel = 0
        self.flap = False
        self.alive = True
        
    #constantly animate, but change velocity if space input is detected
    def update(self, user_input):
        #animate the bird
        if self.alive:
            self.image_index += 1
        if self.image_index >= 30:
            self.image_index = 0
        self.image = bird_images[self.image_index // 10] #floor of dividing by 10

        #regarding the gravity
        self.vel += 0.5
        if self.vel > 7:
            self.vel = 7
        if self.rect.y < 500:
            #applying the gravity
            self.rect.y += int(self.vel)
        if self.vel == 0:
            self.flap = False

        #rotating the bird
        self.image = pygame.transform.rotate(self.image, self.vel * -7)

        #user input
        #input + not flap + below the window
        if user_input[pygame.K_SPACE] and not self.flap and self.rect.y > 0 and self.alive:
            self.flap = True
            self.vel = -7


class Ground(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = ground_image
        self.rect = self.image.get_rect()
        #image was set to be a rectangle
        #assigning its width and height
        self.rect.x, self.rect.y = x, y

    def update(self):
        #moving the ground
        self.rect.x -= scroll_speed
        #kill the ground image that left the screen
        if self.rect.x <= -win_width:
            self.kill()

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, image, pipe_type):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.enter, self.exit, self.passed = False, False, False
        self.pipe_type = pipe_type      #to determine whether it bottom or top

    def update(self):
        #moving the pipe
        self.rect.x -= scroll_speed
        if self.rect.x <= -win_width:
            self.kill()

        #score related
        global score
        if self.pipe_type == "bottom":
            if not self.passed and bird_start_position[0] > self.rect.topleft[0]:
                self.enter = True
            if not self.passed and bird_start_position[0] > self.rect.topright[0]:
                self.exit = True
            if self.enter and self.exit and not self.passed:
                self.passed = True
                score += 1
        
            
def quit_game():
    # Exit Game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

def menu():
    global game_is_stopped

    while game_is_stopped:
        quit_game()
         # drawing the menu
        window.fill((0, 0, 0))
        window.blit(skyline_image, (0, 0))
        window.blit(ground_image, Ground(0, 520))
        window.blit(bird_images[0], (100, 250))
        window.blit(start_image, (win_width // 2 - start_image.get_width() // 2,
                                  win_height // 2 - start_image.get_height() // 2))

        # User Input
        user_input = pygame.key.get_pressed()
        if user_input[pygame.K_SPACE]:
            main()

        pygame.display.update()

def drawning_and_spawning(ground, y_pos_ground, pipes, bird):
    #draw backgorund
        window.blit(skyline_image, (0, 0))

        #spawn more ground objects
        if len(ground) <= 2:
            ground.add(Ground(win_width, y_pos_ground))     #it kind of extends the current number of ground objects so that its always visible on the screen

        #draw the rest - pipes, ground and the bird
        pipes.draw(window)
        ground.draw(window)
        bird.draw(window)

        #showing the score
        score_text = font.render('Score: ' + str(score), True, pygame.Color(255, 255, 255))
        window.blit(score_text, (20, 20))
        
def update(bird, ground, user_input, pipes):
     #update - pipes, ground and the bird
        if bird.sprite.alive:
            pipes.update()
            ground.update()
        bird.update(user_input)


def main():

    global score

    #initiate the bird
    bird = pygame.sprite.GroupSingle()
    bird.add(Bird())

    #initate the pipes
    pipe_timer = 0              #determines when the next pipe should be spawned
    pipes = pygame.sprite.Group()


    #initiate the ground
    x_pos_ground, y_pos_ground = 0, 520
    ground = pygame.sprite.Group()
    ground.add(Ground(x_pos_ground, y_pos_ground))


    while True:
        #Quit
        quit_game()

        #reset frame
        #filling window with color black
        window.fill((0,0,0))

        #user input
        user_input = pygame.key.get_pressed()

        drawning_and_spawning(ground=ground, y_pos_ground=y_pos_ground, pipes=pipes, bird=bird)

        update(bird, ground, user_input, pipes)

        #spawning the pipes (the one at the top and the one at the bottom)
        if pipe_timer <= 0 and bird.sprite.alive:
            x_top, x_bottom = 550, 550
            y_top = random.randint(-600, -480)
            #the top + the gap + the height of the bottom
            y_bottom = y_top + random.randint(110, 150) + bottom_pipe_image.get_height()
            pipes.add(Pipe(x_top, y_top, top_pipe_image, 'top'))
            pipes.add(Pipe(x_bottom, y_bottom, bottom_pipe_image, 'bottom'))
            pipe_timer = random.randint(180, 250)
        pipe_timer -= 1

         # Collision Detection
        collision_with_ground = pygame.sprite.spritecollide(bird.sprites()[0], ground, False)
        if pygame.sprite.spritecollide(bird.sprites()[0], pipes, False) or collision_with_ground:
            bird.sprite.alive = False
            if collision_with_ground:
                window.blit(game_over_image, (win_width // 2 - game_over_image.get_width() // 2, win_height // 2 - game_over_image.get_height() // 2))
                if user_input[pygame.K_r]:
                    score = 0
                    menu()
                    break

        clock.tick(60)
        pygame.display.update()

main()

