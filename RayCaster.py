import sys

import pygame

from math import cos, sin, pi

RAY_AMOUNT = 20

wallcolors = {
    '1': pygame.Color('red'),
    '2': pygame.Color('green'),
    '3': pygame.Color('blue'),
    '4': pygame.Color('yellow'),
    '5': pygame.Color('purple')
    }

wallTextures = {
    '1': pygame.image.load('Egipcio_1.png'),
    '2': pygame.image.load('Egipcio_2.png'),
    '3': pygame.image.load('Egipcio_3.png'),
    '4': pygame.image.load('Egipcio_2.png'),
    '5': pygame.image.load('Egipcio_1.png')
    }


class Raycaster(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        self.map = []
        self.blocksize = 50
        self.wallheight = 50

        self.maxdistance = 300

        self.stepSize = 5
        self.turnSize = 5

        self.player = {
           'x' : 100,
           'y' : 175,
           'fov': 60,
           'angle': 180 }


    def load_map(self, filename):
        with open(filename) as file:
            for line in file.readlines():
                self.map.append( list(line.rstrip()) )

    def drawBlock(self, x, y, id):
        tex = wallTextures[id]
        tex = pygame.transform.scale(tex, (self.blocksize, self.blocksize) )
        rect = tex.get_rect()
        rect = rect.move((x,y))
        self.screen.blit(tex, rect)


    def drawPlayerIcon(self, color):
        if self.player['x'] < self.width / 2:
            rect = (self.player['x'] - 2, self.player['y'] - 2, 5,5)
            self.screen.fill(color, rect )

    def castRay(self, angle):
        rads = angle * pi / 180
        dist = 0
        stepSize = 1
        stepX = stepSize * cos(rads)
        stepY = stepSize * sin(rads)

        playerPos = (self.player['x'],self.player['y'] )

        x = playerPos[0]
        y = playerPos[1]

        while True:
            dist += stepSize

            x += stepX
            y += stepY

            i = int(x/self.blocksize)
            j = int(y/self.blocksize)

            if j < len(self.map):
                if i < len(self.map[j]):
                    if self.map[j][i] != ' ':

                        hitX = x - i*self.blocksize
                        hitY = y - j*self.blocksize

                        hit = 0

                        if 1 < hitX < self.blocksize-1:
                            if hitY < 1:
                                hit = self.blocksize - hitX
                            elif hitY >= self.blocksize-1:
                                hit = hitX
                        elif 1 < hitY < self.blocksize-1:
                            if hitX < 1:
                                hit = hitY
                            elif hitX >= self.blocksize-1:
                                hit = self.blocksize - hitY

                        tx = hit / self.blocksize

                        pygame.draw.line(self.screen,pygame.Color('white'), playerPos, (x,y))
                        return dist, self.map[j][i], tx


    def render(self):
        halfWidth = int(self.width / 2)
        halfHeight = int(self.height / 2)

        for x in range(0, halfWidth, self.blocksize):
            for y in range(0, self.height, self.blocksize):

                i = int(x/self.blocksize)
                j = int(y/self.blocksize)

                if j < len(self.map):
                    if i < len(self.map[j]):
                        if self.map[j][i] != ' ':
                            self.drawBlock(x, y, self.map[j][i])

        self.drawPlayerIcon(pygame.Color('black'))

        for column in range(RAY_AMOUNT):
            angle = self.player['angle'] - (self.player['fov'] / 2) + (self.player['fov'] * column / RAY_AMOUNT)
            dist, id, tx = self.castRay(angle)

            rayWidth = int(( 1 / RAY_AMOUNT) * halfWidth)

            startX = halfWidth + int(( (column / RAY_AMOUNT) * halfWidth))

            # perceivedHeight = screenHeight / (distance * cos( rayAngle - viewAngle)) * wallHeight
            h = self.height / (dist * cos( (angle - self.player["angle"]) * pi / 180)) * self.wallheight
            startY = int(halfHeight - h/2)
            endY = int(halfHeight + h/2)

            color_k = (1 - min(1, dist / self.maxdistance)) * 255

            tex = wallTextures[id]
            tex = pygame.transform.scale(tex, (tex.get_width() * rayWidth, int(h)))
            tex.fill((color_k,color_k,color_k), special_flags=pygame.BLEND_MULT)
            tx = int(tx * tex.get_width())
            self.screen.blit(tex, (startX, startY), (tx,0,rayWidth,tex.get_height()))

        # Columna divisora
        for i in range(self.height):
            self.screen.set_at( (halfWidth, i), pygame.Color('black'))
            self.screen.set_at( (halfWidth+1, i), pygame.Color('black'))
            self.screen.set_at( (halfWidth-1, i), pygame.Color('black'))


width = 1000
height = 500

pygame.init()
screen = pygame.display.set_mode((width,height), pygame.DOUBLEBUF | pygame.HWACCEL )
screen.set_alpha(None)

rCaster = Raycaster(screen)
rCaster.load_map("mapa_p.txt")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Calibri", 30)
fondo = pygame.image.load("Fondo.png").convert()

def drawText(text, font, color, surface, x, y):
    textObj = font.render(text,1,color)
    textRect = textObj.get_rect()
    textRect.topleft = (x,y)
    surface.blit(textObj, textRect)

def updateFPS():
    fps = str(int(clock.get_fps()))
    fps = font.render(fps, 1, pygame.Color("white"))
    return fps

click = False
def Main_Menu():

    isRunning = True
    while isRunning:
        screen.blit (fondo, [0, 0])
        drawText ('Menu Principal', font, (255, 255, 255), screen, 50, 50)
        drawText('PyraEscape: The VideoGame',font,(255,255,255),screen,50,20)

        mx,my = pygame.mouse.get_pos()

        button_1 = pygame.Rect (50, 100, 200, 50)
        button_2 = pygame.Rect (50, 200, 200, 50)
        if button_1.collidepoint((mx,my)):
            if click:
                game()
        if button_2.collidepoint((mx,my)):
            if click:
                isRunning = False
        pygame.draw.rect (screen, (255, 0, 0), button_1)
        pygame.draw.rect (screen, (255, 0, 0), button_2)
        drawText ('Jugar', font, (255, 255, 255), screen, 60, 110)
        drawText ('Salir', font, (255, 255, 255), screen, 60, 210)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isRunning = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    pygame.draw.rect (screen, (0, 100, 0), button_1)
                    drawText ('Jugar', font, (255, 255, 255), screen, 60, 110)
                elif event.key == pygame.K_DOWN:
                    pygame.draw.rect (screen, (0, 100, 0), button_2)
                    drawText ('Jugar', font, (255, 255, 255), screen, 60, 110)
                elif event.key == pygame.K_KP_ENTER:
                    click = True
            elif event.type == pygame.MOUSEMOTION:
                if button_1.collidepoint(mx,my):
                    pygame.draw.rect (screen, (0, 100, 0), button_1)
                    drawText ('Jugar', font, (255, 255, 255), screen, 60, 110)
                if button_2.collidepoint(mx,my):
                    pygame.draw.rect (screen, (0, 100, 0), button_2)
                    drawText ('Salir', font, (255, 255, 255), screen, 60, 210)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()
        clock.tick(60)



def game():
    isRunning = True
    while isRunning:

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                isRunning = False

            elif ev.type == pygame.KEYDOWN:
                newX = rCaster.player['x']
                newY = rCaster.player['y']
                forward = rCaster.player['angle'] * pi / 180
                right = (rCaster.player['angle'] + 90) * pi / 180

                if ev.key == pygame.K_ESCAPE:
                    isRunning = False
                elif ev.key == pygame.K_w:
                    newX += cos(forward) * rCaster.stepSize
                    newY += sin(forward) * rCaster.stepSize
                elif ev.key == pygame.K_s:
                    newX -= cos(forward) * rCaster.stepSize
                    newY -= sin(forward) * rCaster.stepSize
                elif ev.key == pygame.K_a:
                    newX -= cos(right) * rCaster.stepSize
                    newY -= sin(right) * rCaster.stepSize
                elif ev.key == pygame.K_d:
                    newX += cos(right) * rCaster.stepSize
                    newY += sin(right) * rCaster.stepSize
                elif ev.key == pygame.K_q:
                    rCaster.player['angle'] -= rCaster.turnSize
                elif ev.key == pygame.K_e:
                    rCaster.player['angle'] += rCaster.turnSize

                i = int(newX/rCaster.blocksize)
                j = int(newY/rCaster.blocksize)

                if rCaster.map[j][i] == ' ':
                    rCaster.player['x'] = newX
                    rCaster.player['y'] = newY


        screen.fill(pygame.Color("gray"))

        # Techo
        screen.fill(pygame.Color("saddlebrown"), (int(width / 2), 0,  int(width / 2), int(height / 2)))

        # Piso
        screen.fill(pygame.Color("dimgray"), (int(width / 2), int(height / 2),  int(width / 2), int(height / 2)))


        rCaster.render()

        #FPS
        screen.fill(pygame.Color("black"), (0,0,30,30) )
        screen.blit(updateFPS(), (0,0))
        clock.tick(60)


        pygame.display.flip()

Main_Menu()

pygame.quit()