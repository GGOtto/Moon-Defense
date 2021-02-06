# Name: Moon Defense
# Author: G.G.Otto
# Date: 12/29/2020
# Version 1.2

import pygame, random, math, time
from pygame.locals import *
import os.path as path

class MDMovable:
    '''movable object to inherit from'''

    def __init__(self, surface):
        '''MDObject(surface) -> MDObject
        constructs an object'''
        self.origin = surface
        self.image  = surface
        self.rect   = surface.get_rect()
        self.pos = 0,0
        self.heading = 0

    def get_heading(self):
        '''MDMovable.get_heading() -> int
        returns the heading of the object'''
        return math.degrees(self.heading)

    def set_heading(self, heading):
        '''MDMovable.set_heading(heading) -> None
        sets the heading of the image'''
        self.image = pygame.transform.rotozoom(self.origin, heading, 1)
        self.image.convert()
        self.rect = self.image.get_rect()
        self.heading = math.radians(heading)

    def forward(self, distance):
        '''MDMoveable.forward(distance) -> None
        moves the object forward by distance'''
        self.pos = self.pos[0]+distance*math.cos(self.heading), self.pos[1]-distance*math.sin(self.heading)
        self.rect.center = round(self.pos[0]), round(self.pos[1])
        
class MDPlayer:
    '''represents the player of Moon Defense'''

    def __init__(self, game, xpos=600, ypos=630, hoverDistance=120):
        '''MDPlayer(game) -> MDPlayer
        constructs the player for the game'''
        # set up images
        self.origin = pygame.transform.rotozoom(pygame.image.load("player6.png"), 0, 0.2)
        self.fire = pygame.transform.rotozoom(pygame.image.load("player6_fire.png"), 0, 0.2)
        self.dead = pygame.transform.rotozoom(pygame.image.load("player6_dead.png"), 0, 0.2)
        self.image = self.origin
        
        self.rect = self.image.get_rect()
        self.rect.center = xpos, ypos
        self.ypos = ypos
        self.xpos = xpos
        self.game = game
        self.hoverCount = 0
        self.hoverDistance = hoverDistance
        self.hoverHeight = ypos
        self.hovering = False
        self.expId = None
        self.end = False

    def get_pos(self):
        '''MDPlater.get_pos() -> (x,y)
        returns the position of the player'''
        return self.rect.center

    def explode(self):
        '''MDPlayer.explode() -> None
        explodes the player and removes it from game'''
        self.expId = self.game.explosion((self.rect.center[0]-50, self.rect.center[1]), 100, 5, 5, 5)
        self.image = self.dead
        self.end = True

    def collide(self, pos, rFactor=1.9):
        '''MDPlayer.collide(pos) -> int
        returns the heading a meteor should go after collide
        returns None if meteor does not collide'''
        if (self.rect.center[0]-pos[0])**2+(self.rect.center[1]-pos[1])**2 <= self.rect.width**2/(rFactor**2) \
           and pos[1] < self.rect.center[1]:
            return math.degrees(math.acos(-(self.rect.center[0]-pos[0])*rFactor/self.rect.width))

    def hover(self):
        '''MDPlayer.hover() -> None
        makes the player hover'''
        self.hovering = True

    def move(self, x):
        '''MDPlayer.move(x) -> None
        moves the player on the x-axis'''
        if self.end:
            return
        
        stopped = self.game.get_craters().stopped((self.rect.center[0],x,self.rect.width-50))
        if (stopped[0] and not self.hovering) or not (0 < x < 1200 and 0 < self.rect.center[0] < 1200) :
            return
        
        self.rect.center = x, self.rect.center[1]

    def update_player(self):
        '''MDPlayer.update_player() -> None
        updates the player move'''
        # hover
        if self.hovering and not self.end:
            self.image = self.fire
            if self.hoverCount < self.hoverDistance:
                self.hoverHeight -= 2
            else:
                self.hoverHeight += 2

            # stop hovering
            self.hoverCount += 2
            if self.hoverHeight > self.ypos:
                self.image = self.origin
                self.hoverHeight = self.ypos
                self.hoverCount = 0
                self.hovering = False
            self.rect.center = self.rect.center[0], self.hoverHeight

        # turn into dead
        if self.game.exp_finished(self.expId):
            self.rect.center = self.rect.center[0], self.ypos

        self.game.get_screen().blit(self.image, self.rect)
        
class MDSpaceship(MDMovable):
    '''represents the spaceship for the game'''

    def __init__(self, game):
        '''MDSpaceship(game) -> MDSpaceship
        constructs the spaceship for the game'''
        # image and rectangle
        image = "spaceship.png"
        size = 0.4
        self.origin = pygame.transform.rotozoom(pygame.image.load(image), 0, size)
        self.origin.convert()
        MDMovable.__init__(self, self.origin)

        self.pos = 600, -100
        self.speed = 4
        self.dir = 1
        self.end = False
        self.dontUpdate = False
        self.debris = []

        self.game = game
        self.heading = 0
        self.numHits = 0

    def get_pos(self):
        '''MDSpaceship.get_pos() -> tuple
        returns the position of the spaceship'''
        return self.pos

    def set_end(self, boolean):
        '''MDSpaceship.set_end(boolean) -> None
        sets the end variable to boolean'''
        self.end = boolean

    def drop_off(self):
        '''MDSpaceship.drop_off() -> None
        drops the spaceship off'''
        # turn ship
        self.numHits += 1
        if self.numHits < 12:
            self.set_heading(-self.numHits-1)
        else:
            self.set_heading(-12)

        # flip ship
        self.dir = 1
        willFlip = random.randint(0,1)
        if willFlip:
            self.flip()

        # move
        self.pos = (1199,1)[(self.dir+1)//2], 10

    def hide(self):
        '''MDSpaceship.hide() -> None
        hides the spaceship'''
        self.pos = 600, -200

    def add_debris(self, howMany):
        '''MDSpaceship.add_debris(howMany):
        adds howMany pieces of debris to the ship'''
        for i in range(howMany):
           MDDebris(self.game, (self.pos[0]+random.randint(-80,80), self.pos[1]+random.randint(-30,30)), self.debris)

    def flip(self):
        '''MDSpaceship.flip() -> None
        flips the shaceship'''
        self.heading = math.radians(180-math.degrees(self.heading))
        self.image = pygame.transform.flip(self.image, True, False)
        self.dir = -self.dir

    def update_ship(self):
        '''MDSpaceship.update_ship() -> None
        updates the ship'''
        if self.dontUpdate:
            return
        
        # flip the spaceship
        if not -100 < self.rect.center[0] < 1300:
            self.flip()
            if not self.end:
                self.pos = self.pos[0], self.pos[1]+20

        # descend
        if self.pos[1] > 630 and not self.end:
            self.speed += 1
            self.set_heading((180,0)[(self.dir+1)//2])
            self.end = True
            
        # kill player
        if self.pos[0]-150 <= self.game.get_player().get_pos()[0] <= self.pos[0]+150 \
           and self.pos[1]-60 <= self.game.get_player().get_pos()[1] <= self.pos[1]+60:
            self.game.explosion(self.pos, 150, 5, 4, 5)
            self.game.get_player().explode()
            self.dontUpdate = True
            self.game.end_game()

        # update debris
        for debris in self.debris:
            debris.update()
        
        self.forward(self.speed)
        self.game.get_screen().blit(self.image, self.rect)
        
    def collision(self):
        '''MDSpaceship.collision() -> list
        returns all the meteors hitting shapeship'''        
        output = []
        width, height = 240, 40
        for meteor in self.game.get_meteors():
            pos = meteor.get_rect().center
            
            # meteor is out of screen
            if not -10 < pos[0] < 1210 or pos[1] < -10:
                continue

            # check if meteor has hit
            if 0 < meteor.get_heading() < 180 and \
               ((self.pos[0]-pos[0])**2 + (self.pos[1]-pos[1])**2)**(1/2) < width/2:
                output.append(meteor)
        return output

class MDDebris(MDMovable):
    '''represents debris falling from the ship'''

    def __init__(self, game, pos, debrisList):
        '''MDDebris(game, pos, debrisList) -> MDDebris
        constructs the debris object'''
        # set up surface
        self.surface = pygame.Surface((random.randint(2,4),random.randint(2,4)))
        self.surface.fill((random.randint(0,50),random.randint(0,50),255))
        MDMovable.__init__(self, self.surface)
        self.pos = pos
        self.game = game
        self.debrisList = debrisList
        debrisList.append(self)

        # randomized attributes
        self.set_heading(270+random.randint(-8,8))
        self.collide = random.randint(0,1)
        self.speed = 0.5*random.randint(5,7)
        self.end = 710 #660+random.randint(-30, 30)
                               
    def update(self):
        '''MDDebris.update() -> None
        updates the piece of debris'''
        # turn and move
        if -30 < self.pos[1] < self.end and -30 < self.pos[0] < 1230:
            collide = self.game.get_player().collide(self.pos, 3)
            if collide and self.collide:
                self.set_heading(collide)
            self.forward(self.speed)
        # stop and add to craters
        elif self in self.debrisList:
            self.debrisList.remove(self)
            #self.game.get_craters().add_debris(self)
            
        self.game.get_screen().blit(self.image, self.rect)

class MDMeteor(MDMovable):

    def __init__(self, game, startPos=(500,100)):
        '''MDMeteor(game) -> MDMeteor
        constructor for moon defense meteor'''
        # image and rectangle
        image = "meteor7_1.png"
        size = 0.3
        self.origin = pygame.transform.rotozoom(pygame.image.load(image), 0, size)
        self.origin.convert()
        MDMovable(self.origin)
        
        self.pos = startPos
        self.speed = 9
        
        self.game = game
        self.collided = False
        self.end = False
        self.heading = 0
        self.random_drop()

    def get_rect(self):
        '''MDMeteor.get_rect() -> pygame.Rect
        returns the rectangle of the meteor'''
        return self.rect

    def get_head_pos(self):
        '''MDMeteor.get_head_pos() -> (x,y)
        returns the position of the meteor's head'''
        # get the position of the corner with the head
        factor = 1,1
        if 0 <= self.get_heading() < 90:
            factor = 1,-1
        elif 90 <= self.get_heading() < 180:
            factor = -1,-1
        elif 180 <= self.get_heading() < 270:
            factor = -1,1
            
        return self.rect.center[0]+factor[0]*(self.rect.width/2-11)-40, \
            self.rect.center[1]+factor[1]*(self.rect.height/2-11)-40

    def random_drop(self):
        '''MDMeteor.random_drop() -> None
        drops the meteor from a random position'''
        if self.game.is_over():
            self.pos = (-200, -200)
            self.set_heading(90)
            return
        
        self.pos = random.randint(0,1200), -50
        self.set_heading(random.randint(250,290))
        
    def bounce(self):
        '''MDMeteor.bounce() -> None
        meteor does a bounce if needed'''
        heading = self.game.get_player().collide(self.pos)
        
        if heading != None and not self.collided:
            self.game.explosion(self.get_head_pos(), 80, 5)
            self.set_heading(heading)
        elif self.pos[1] < -50 or not 0 < self.pos[0] < 1200:
            self.random_drop()
        elif self.pos[1] > 660:
            self.game.crater(self.get_head_pos(), 120)
            self.random_drop()
                
        self.collided = heading != None
        
    def update(self):
        '''MDMeteor.move() -> None
        moves the meteor forward by "forward"'''
        # remove meteor when game over
        if self.end:
            return
        elif self.game.is_over():
            self.end = True
            
        self.bounce()
        self.forward(self.speed)
        self.game.get_screen().blit(self.image, self.rect)

class MDExplosion:
    '''represents an explosion in the game'''

    def __init__(self, screen, pos, size, speed, expType=1, frames=3, expId=None):
        '''MDExplosion(screen, pos, size, speed, expType=1, frames=3, expId=None) -> None
        contructs an explosion at pos with size'''
        self.screen = screen
        self.pos = pos[0]-size/2, pos[1]-size/2
        self.size = size
        self.count = 0
        self.speed = speed
        self.frames = frames
        self.expId = expId
        self.imgs = [pygame.image.load(f"explosion{expType}_{i}.png") for i in range(1,frames+1)]

    def get_id(self):
        '''MDExplosion.get_id() -> str
        returns the id of the explosion'''
        return self.expId

    def is_valid(self):
        '''MDExplosion.is_valid() -> bool
        returns if the explosion is still valid or not'''
        return self.count < self.speed*self.frames

    def update(self):
        '''MDExplosion.update() -> None
        updates the explosion'''
        img = pygame.transform.rotozoom(self.imgs[self.count//self.speed], 0, self.size/500)
        self.screen.blit(img, self.pos)
        self.count += 1

class MDCraters:
    '''represents all of the craters in one'''

    def __init__(self, game):
        '''MDCraters(game) -> MDCrater
        constructs the craters for the game'''
        self.craters = []
        self.intervals = []
        self.game = game

    def stopped(self, pos):
        '''MDCraters.stopped(pos) -> bool
        returns if pos is not valid move with craters
        pos is (start,end,width)'''
        for interval in self.intervals:
            if abs(interval[0]-interval[1]) > pos[2] and ((pos[1] > pos[0] and pos[0] <= interval[0] <= pos[1]) \
                or (pos[1] < pos[0] and pos[1] <= interval[1] <= pos[0]) or interval[0] < pos[0] < interval[1]):
                return (True, interval)
        return (False, None)

    def add_debris(self, debris):
        '''MDCraters.add_debris(debris) -> None
        adds a bit of debris to the craters'''
        self.craters.append(debris)

    def add_crater(self, crater):
        '''MDCraters.add_crater(crater) -> None
        adds a crater to the screen
        crater is (x,y,width,height)'''
        self.craters.append(crater)
        self.add_interval(crater)

    def add_interval(self, crater):
        '''MDCraters.add_interval(crater) -> None
        adds an interval that tells where craters are
        crater is (x,y,width,height)'''
        newInts = []
        intervals = self.intervals[:]
        for i in range(len(intervals)):
            left, right = intervals[i][0] <= crater[0] <= intervals[i][1], \
                intervals[i][0] <= crater[0]+crater[2] <= intervals[i][1]

            if left and right:
                return
            if left:
                newInts.append([intervals[i][0], crater[0]+crater[2]])
                self.intervals.remove(intervals[i])
            elif right:
                newInts.append([crater[0], intervals[i][1]])
                self.intervals.remove(intervals[i])

        # not touching other craters
        if len(newInts) == 1:
            self.intervals.append(newInts[0])
            return
        if len(newInts) == 0:
            self.intervals.append([crater[0], crater[0]+crater[2]])
            return

        # remove ints from list and combine
        mn, mx = newInts[0][0], newInts[0][1]
        for interval in newInts:
            if min(interval) < mn:
                mn = min(interval)
            if max(interval) > mx:
                mx = max(interval)

        self.intervals.append([mn, mx])

    def clear(self):
        '''MDCraters.clear() -> None
        clears all craters'''
        self.craters.clear()
        self.intervals.clear()
        
    def update(self):
        '''MDCraters.update() -> None
        updates all craters'''
        for crater in self.craters:
            if isinstance(crater, MDDebris):
                crater.update()
            else:
                pygame.draw.ellipse(self.game.get_screen(), (127,127,127), crater)

class MDEnergy:
    '''represents the energy indicator'''

    def __init__(self, game, fillTime):
        '''MDEnergy(game, fillTime) -> MDEnergy
        constructs the energy indicator. Fill time is in seconds'''
        self.fillTime = fillTime
        self.game = game
        self.image = pygame.transform.rotozoom(pygame.image.load("energy.png"), 0, 0.5)
        self.rect = pygame.Rect(1130, 15+self.image.get_rect().height, self.image.get_rect().width, 87)
        
        self.howFull = 87
        self.emptyTime = time.time()
        self.emptying = False

    def is_full(self):
        '''MDEnergy.is_full() -> bool
        returns if the indicator is full or not'''
        return 86 < self.howFull

    def empty(self):
        '''MDEnergy.empty() -> None
        empties the indicator'''
        if self.game.is_over():
            return
        self.howFull = 0
        self.emptying = True

    def update_how_full(self):
        '''MDEnergy.update_how_full() -> None
        updates how full the indicator is'''
        # empty if needed
        if self.emptying:
            self.rect.height -= 1
            if self.rect.height == 0:
                self.emptying = False
                self.emptyTime = time.time()
        # fill
        elif 86 >= self.howFull and not self.game.is_over():
            self.howFull = (time.time() - self.emptyTime)*88/self.fillTime
            self.rect.height = self.howFull
                     
        self.rect.bottomleft = 1130, 15+self.image.get_rect().height

    def update(self):
        '''MDEnergy.update() -> None
        updates the energy indicator'''
        self.update_how_full()
        pygame.draw.rect(self.game.get_screen(), (0, 255, 0), self.rect)
        self.game.get_screen().blit(self.image, (1130, 15))
        
class MoonDefense:
    '''represents the game objects in one'''

    def __init__(self, dev=False):
        '''MoonDefense(dev) -> MoonDefense
        constructs the game objects'''
        pygame.display.set_caption("Moon Defense")
        pygame.display.set_icon(pygame.image.load("logo.png"))
        pygame.mouse.set_visible(False)
        self.display = pygame.display.set_mode((0,0))
        self.screen = pygame.Surface((1200,700))

        self.width, self.height = pygame.display.get_window_size()
        pygame.draw.rect(self.display, (255,255,255), (self.width/2-600,self.height/2-350,1200,700), 5)
        self.gameOver = False
        
        # meteors
        self.meteors = [MDMeteor(self)]

        # other objects
        self.player = MDPlayer(self)
        self.enemy = MDSpaceship(self)
        self.craters = MDCraters(self)
        self.energy = MDEnergy(self, 5)

        # set up attributes
        self.iterations = 0
        self.enemyDrop = 0
        self.score = 0
        self.highScore = self.get_high_score()
        
        self.explosions = []
        self.explosionCount = 0
        self.finishedExplosions = []
        
        self.dev = dev
        self.font = pygame.font.SysFont(None, 50)
        self.notif = pygame.font.SysFont(None, 30)
        self.enemyWait = 150
        self.endWait = -1

        self.mainloop()

    def get_player(self):
        '''MoonDefense.get_player() -> MDPlayer
        returns the player for the game'''
        return self.player

    def get_screen(self):
        '''MoonDefense.get_screen() -> display
        returns the screen of the game'''
        return self.screen

    def get_craters(self):
        '''MoonDefense.get_craters() -> list
        returns a list of all craters'''
        return self.craters

    def get_meteors(self):
        '''MoonDefense.get_meteors() -> list
        returns all meteors on the board'''
        return self.meteors

    def is_over(self):
        '''MoonDefense.is_over() -> bool
        returns if the game is over or not'''
        return self.gameOver

    def exp_finished(self, expId):
        '''MoonDefense.exp_finised(expId) -> bool
        returns whether explosion with id expId is finished or not'''
        return expId in self.finishedExplosions

    def explosion(self, pos, size=100, speed=3, expType=2, frames=3):
        '''MoonDefense.explosion(pos, size=100, speed=3, expType=2, frames=3) -> str
        makes an explosion at pos and with size and returns the id of the explosion'''
        self.explosionCount += 1
        self.explosions.append(MDExplosion(self.screen, pos, size, speed, expType, frames, f"exp{self.explosionCount}"))
        return f"exp{self.explosionCount}"

    def crater(self, pos, size):
        '''MoonDefense.crater(pos, size) -> None
        makes a crater at pos with size'''           
        self.craters.add_crater((pos[0]-size/2, pos[1]-size/6+random.randint(-5,5), size, size/3))
        self.explosion((pos[0],pos[1]-50), size*1.2, 4, 3, 5)

    def end_game(self):
        '''MoonDefense.end_game() -> None
        ends the game'''
        self.endWait = self.iterations
        self.gameOver = True

    def update_game(self, playing=True):
        '''MoonDefense.update(playing=True) -> None
        updates components of the game such as explosions and score'''
        self.iterations += 1

        # update craters and player and ship
        if self.started:
            self.craters.update()
            self.player.update_player()

        # update explosions
        explosions = self.explosions[:]
        for explosion in explosions:
            if explosion.is_valid():
                explosion.update()
            else:
                self.explosions.remove(explosion)
                self.finishedExplosions.append(explosion.get_id())

        # updateand meteors
        if playing:
            self.enemy.update_ship()
            for meteor in self.meteors:
                meteor.update()
                
        # explosion with meteors
        collision = self.enemy.collision()
        if len(collision):
            self.explosion(self.enemy.get_pos(), 150, 4, 4, 5)
            self.enemyDrop = self.iterations
            self.enemy.add_debris(30)
            self.enemy.hide()
            self.enemy.set_end(False)
            for meteor in collision:
                meteor.random_drop()
            self.score += 1
            self.cleared = False

        # clear craters
        if self.score%10 == 0 and not self.cleared:
            if self.score < 21:
                self.meteors.append(MDMeteor(self))
            self.craters.clear()
            self.cleared = True
            
        # drop off enemy again
        if self.iterations-self.enemyDrop == self.enemyWait:
            self.enemy.drop_off()

        # end game
        if self.endWait > 0 and self.iterations-self.endWait > 170:
            self.endWait = -1
            self.started = False
            self.screen.blit(pygame.image.load("end.png"), (0,0))
            close = self.notif.render("Shift to close", True, 0)
            self.screen.blit(close, (1060, 670))
            
            # save high score
            if self.score > self.highScore:
                self.highScore = self.score
                self.screen.blit(pygame.image.load("highscore.png"), (0,0))
                self.save_high_score(self.score)

            high = self.font.render("High: "+str(self.highScore), True, (255,255,255))
            self.screen.blit(high, (10, 10))

        score = self.font.render(str(self.score), True, (255,255,255))
        self.screen.blit(score, (1155-score.get_rect().width/2, 120))
        self.energy.update()
                         
    def mainloop(self):
        '''MoonDefense.mainloop() -> None
        starts the main loop'''
        self.speed = []
        self.cleared = True
        self.started = True
        background = pygame.image.load("landscape4.png")
        background.convert()

        # title page
        self.screen.blit(background, (0,0))
        self.update_game(False)
        self.screen.blit(pygame.image.load("title.png"), (0,0))

        # text on page
        high = self.font.render("High: "+str(self.highScore), True, (255,255,255))
        self.screen.blit(high, (10, 10))
        close = self.notif.render("Shift to close", True, 0)
        self.screen.blit(close, (1060, 670))
        pygame.display.update()

        # main game loop
        running = True
        self.started = False
        last = time.time()
        while running:
            if self.started:
                self.speed.append(time.time()-last)
                last = time.time()
                self.screen.blit(background, (0,0))
            
            # event loop for game play
            for event in pygame.event.get():
                # close screen
                if event.type == QUIT or (event.type == KEYUP and (event.key == K_RSHIFT or event.key == K_LSHIFT)):
                    running = False
                # make player move
                if event.type == MOUSEMOTION and self.started:
                    self.player.move(event.pos[0]-(self.width/2-600))
                # make player hover or start game
                if (event.type == KEYDOWN and event.key == K_SPACE) or event.type == MOUSEBUTTONDOWN:
                    if self.started and self.energy.is_full():
                        self.energy.empty()
                        self.player.hover()
                    elif not self.started:
                        # restart
                        if self.gameOver:
                            self.restart()
                        self.started = True

            # update game
            self.update_game(self.started)
            self.display.blit(self.screen, (self.width/2-600,self.height/2-350))
            pygame.display.update()
            pygame.time.wait(10)

        if self.dev:
            self.graph()
        else:
            pygame.quit()

    def restart(self):
        '''MoonDefense.restart() -> None
        restarts the game'''
        self.gameOver = False
        self.cleared = True
        self.craters.clear()
        self.score = 0
        
        # reset all objects
        self.enemy.__init__(self)
        self.player.__init__(self)
        self.energy.__init__(self, 5)
        self.meteors = [MDMeteor(self)]
        self.enemyDrop = self.iterations
        
    def graph(self):
        '''MoonDefense.graph() -> None
        graphs the speeds of the meteors'''
        last = (0,self.speed[0])
        graph = pygame.Surface((1200, 800))
        for i in range(0, len(self.speed), math.ceil(len(self.speed)/1200)):
            pygame.draw.line(graph, (255,0,0), (last[0],400-last[1]*5000), (i,400-self.speed[i]*5000), 2)
            last = i,self.speed[i]
        self.screen.blit(graph, (0,0))
        pygame.display.update()

    def get_high_score(self):
        '''MoonDefense.get_high_score() -> int
        returns the high score of the game'''
        if not path.isfile("moondefense_high.txt"):
            return 0
        file = open("moondefense_high.txt")
        score = int(file.read())
        file.close()
        return score

    def save_high_score(self, score):
        '''MoonDefense.save_high_score(score) -> None
        saves the high score of the game'''
        file = open("moondefense_high.txt", "w")
        file.write(str(score))
        file.close()
        
pygame.init()
MoonDefense()
