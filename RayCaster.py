import sys

import pygame

from math import cos, sin, pi, atan2

RAY_AMOUNT = 200
SPRITE_BACKGROUND = (152,0,136,255)

enemies = [{"x" : 100,
            "y" : 200,
            "sprite" : pygame.image.load('momia.png')},

           {"x" : 400,
            "y" : 150,
            "sprite" : pygame.image.load('momia2.png')},

            {"x" : 350,
             "y" : 300,
             "sprite" : pygame.image.load('momia3.png')}
    ]


class Raycaster(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        self.map = []
        self.zbuffer = [float('inf') for z in range(self.width)]

        self.blocksize = 50
        self.wallheight = 50

        self.maxdistance = 300

        self.stepSize = 5
        self.turnSize = 5

        self.player = {
           'x' : 100,
           'y' : 100,
           'fov': 60,
           'angle': 0 }

        self.hitEnemy = False


    def load_map(self, filename):
        with open(filename) as file:
            for line in file.readlines():
                self.map.append( list(line.rstrip()) )

    def drawMinimap(self):
        minimapWidth = 100
        minimapHeight = 100

        minimapSurface = pygame.Surface ((500, 500))
        minimapSurface.fill (pygame.Color ("gray"))

        for x in range (0, 500, self.blocksize):
            for y in range (0, 500, self.blocksize):

                i = int (x / self.blocksize)
                j = int (y / self.blocksize)

                if j < len (self.map):
                    if i < len (self.map [j]):
                        if self.map [j] [i] != ' ':
                            tex = wallTextures [self.map [j] [i]]
                            tex = pygame.transform.scale (tex, (self.blocksize, self.blocksize))
                            rect = tex.get_rect ()
                            rect = rect.move ((x, y))
                            minimapSurface.blit (tex, rect)

        rect = (int (self.player ['x'] - 4), int (self.player ['y']) - 4, 10, 10)
        minimapSurface.fill (pygame.Color ('black'), rect)

        for enemy in enemies:
            rect = (enemy ['x'] - 4, enemy ['y'] - 4, 10, 10)
            minimapSurface.fill (pygame.Color ('red'), rect)

        minimapSurface = pygame.transform.scale (minimapSurface, (minimapWidth, minimapHeight))
        self.screen.blit (minimapSurface, (self.width - minimapWidth, self.height - minimapHeight))

    def drawSprite(self, obj, size):
        # Pitagoras
        spriteDist = ((self.player ['x'] - obj ['x']) ** 2 + (self.player ['y'] - obj ['y']) ** 2) ** 0.5

        # Angulo
        spriteAngle = atan2 (obj ['y'] - self.player ['y'], obj ['x'] - self.player ['x']) * 180 / pi

        # Tamaño del sprite
        aspectRatio = obj ['sprite'].get_width () / obj ['sprite'].get_height ()
        spriteHeight = (self.height / spriteDist) * size
        spriteWidth = spriteHeight * aspectRatio

        # Buscar el punto inicial para dibujar el sprite
        angleDif = (spriteAngle - self.player ['angle']) % 360
        angleDif = (angleDif - 360) if angleDif > 180 else angleDif
        startX = angleDif * self.width / self.player ['fov']
        startX += (self.width / 2) - (spriteWidth / 2)
        startY = (self.height / 2) - (spriteHeight / 2)
        startX = int (startX)
        startY = int (startY)

        for x in range (startX, startX + int (spriteWidth)):
            if (0 < x < self.width) and self.zbuffer [x] >= spriteDist:
                for y in range (startY, startY + int (spriteHeight)):
                    tx = int ((x - startX) * obj ['sprite'].get_width () / spriteWidth)
                    ty = int ((y - startY) * obj ['sprite'].get_height () / spriteHeight)
                    texColor = obj ['sprite'].get_at ((tx, ty))
                    if texColor != SPRITE_BACKGROUND and texColor [3] > 128:
                        self.screen.set_at ((x, y), texColor)

                        if y == self.height / 2:
                            self.zbuffer [x] = spriteDist
                            if x == self.width / 2:
                                self.hitEnemy = True

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

                        return dist, self.map[j][i], tx


    def render(self):
        halfHeight = int(self.height / 2)

        for column in range (RAY_AMOUNT):
            angle = self.player ['angle'] - (self.player ['fov'] / 2) + (self.player ['fov'] * column / RAY_AMOUNT)
            dist, id, tx = self.castRay (angle)

            rayWidth = int ((1 / RAY_AMOUNT) * self.width)

            for i in range (rayWidth):
                self.zbuffer [column * rayWidth + i] = dist

            startX = int (((column / RAY_AMOUNT) * self.width))

            # perceivedHeight = screenHeight / (distance * cos( rayAngle - viewAngle)) * wallHeight
            h = self.height / (dist * cos ((angle - self.player ["angle"]) * pi / 180)) * self.wallheight
            startY = int (halfHeight - h / 2)
            endY = int (halfHeight + h / 2)

            color_k = (1 - min (1, dist / self.maxdistance)) * 255

            tex = wallTextures [id]
            tex = pygame.transform.scale (tex, (tex.get_width () * rayWidth, int (h)))
            tx = int (tx * tex.get_width ())
            self.screen.blit (tex, (startX, startY), (tx, 0, rayWidth, tex.get_height ()))

        self.hitEnemy = False
        for enemy in enemies:
            self.drawSprite (enemy, 50)

        sightRect = (int (self.width / 2 - 2), int (self.height / 2 - 2), 5, 5)
        self.screen.fill (pygame.Color ('red') if self.hitEnemy else pygame.Color ('white'), sightRect)

        self.drawMinimap ()


width = 1000
height = 500

pygame.init()
screen = pygame.display.set_mode((width,height), pygame.DOUBLEBUF | pygame.HWACCEL | pygame.HWSURFACE )
screen.set_alpha(None)

rCaster = Raycaster(screen)
rCaster.load_map("mapa_p.txt")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Calibri", 30)
fondo = pygame.image.load("Texturas/Fondo.png").convert()
sonido = pygame.mixer.Sound('EgipMusic.wav')

wallTextures = {
    '1': pygame.image.load('Texturas/Egipcio_1.png').convert(),
    '2': pygame.image.load('Texturas/Egipcio_2.png').convert(),
    '3': pygame.image.load('Texturas/Egipcio_3.png').convert(),
    '4': pygame.image.load('Texturas/Egipcio_2.png').convert(),
    '5': pygame.image.load('Texturas/Egipcio_1.png').convert()
    }

def drawText(text, font, color, surface, x, y):
    textObj = font.render(text,1,color)
    textRect = textObj.get_rect()
    textRect.topleft = (x,y)
    surface.blit(textObj, textRect)

def updateFPS():
    fps = str(int(clock.get_fps()))
    fps = font.render(fps, 1, pygame.Color("white"))
    return fps


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
                pygame.quit()
                quit()
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
        pygame.mixer.Sound.play(sonido,-1)


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
                    pausa()
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
        screen.fill(pygame.Color("saddlebrown"),(0, 0, width, int(height / 2)))

        # Piso
        screen.fill(pygame.Color("dimgray"),(0, int(height / 2),  width, int(height / 2)))


        rCaster.render()

        #FPS
        screen.fill(pygame.Color("black"), (0,0,30,30) )
        screen.blit(updateFPS(), (0,0))
        clock.tick(60)

        pygame.display.flip()

def pausa():

    paused = True
    click = False
    while paused:

        screen.fill (pygame.Color ("White"))
        drawText ("Paused", font, (0, 0, 0), screen, 350, 10)

        mx, my = pygame.mouse.get_pos()

        button_3 = pygame.Rect (350, 100, 200, 50)
        button_4 = pygame.Rect (350, 200, 200, 50)
        if button_3.collidepoint((mx,my)):
            if click:
                paused = False
        if button_4.collidepoint((mx,my)):
            if click:
                Main_Menu()
        pygame.draw.rect (screen, (255, 0, 0), button_3)
        pygame.draw.rect (screen, (255, 0, 0), button_4)
        drawText ('Continuar', font, (255, 255, 255), screen, 350, 110)
        drawText ('Salir al menu', font, (255, 255, 255), screen, 350, 210)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()
        clock.tick(60)


Main_Menu()

pygame.quit()