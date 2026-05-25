# /// script
# dependencies = [
# "pygame-ce",
# "cffi",
# "pymunk",
# ]
# ///
import pygame
import pymunk
import pymunk.pygame_util
import math
import asyncio

def draw(space, screen, draw_options):
    
    #draw background vvv
    w = SCREEN_WIDTH // 100
    h = SCREEN_HEIGHT // 50
    for i in range(w):
        for j in range(h):
            if (j % 2) == 0:
                pygame.draw.rect(screen, BGWHITE, ((i * 100), (j * 50), 50, 50))
                pygame.draw.rect(screen, BGGREY, ((i * 100 + 50), (j * 50), 50, 50))
            else:
                pygame.draw.rect(screen, BGWHITE, ((i * 100 + 50), (j * 50), 50, 50))
                pygame.draw.rect(screen, BGGREY, ((i * 100), (j * 50), 50, 50))

    #draw lines when drawing box vvv
    if startpos:
        currpos = pygame.mouse.get_pos()
        pygame.draw.line(screen, (0, 0, 0), startpos, (currpos[0], startpos[1]), 2)
        pygame.draw.line(screen, (0, 0, 0), startpos, (startpos[0], currpos[1]), 2)
        pygame.draw.line(screen, (0, 0, 0), currpos, (currpos[0], startpos[1]), 2)
        pygame.draw.line(screen, (0, 0, 0), currpos, (startpos[0], currpos[1]), 2)
        pygame.draw.line(screen, (0, 0, 0), startpos, currpos, 2)
        pygame.draw.line(screen, (0, 0, 0), (startpos[0], currpos[1]), (currpos[0], startpos[1]), 2)

    if box:
        pygame.draw.line(screen, (0, 0, 0), box.position, pygame.mouse.get_pos(), 2)

    space.debug_draw(draw_options)
    pygame.display.update()

def createBounds(space):
    bounds = [
        [(SCREEN_WIDTH / 2, SCREEN_HEIGHT), (SCREEN_WIDTH, 100)],
        [(-50, SCREEN_HEIGHT / 2), (100, SCREEN_HEIGHT)],
        [(SCREEN_WIDTH + 50, SCREEN_HEIGHT / 2), (100, SCREEN_HEIGHT)]
    ]
    for pos, size in bounds:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Poly.create_box(body, size)
        shape.friction = 0.4
        space.add(body, shape)

def createBox(space, size, pos):
    mass = math.prod(size)
    moment = pymunk.moment_for_box(mass, size)
    body = pymunk.Body(mass, moment, pymunk.Body.DYNAMIC)
    body.position = pos
    shape = pymunk.Poly.create_box(body, size, radius=1)
    shape.color = BLACK
    shape.elasticity = 0.4
    shape.friction = 0.4
    space.add(body, shape)
    return (body, shape)


async def main():

    pygame.init()

    global SCREEN_WIDTH
    global SCREEN_HEIGHT
    global screen
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 800
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    #100 pixels (2 background square lengths) = 1 meter
    pygame.display.set_caption("physics")

    global BGWHITE
    global BGGREY
    global BLACK
    BGWHITE = (255, 255, 255)
    BGGREY = (225, 225, 225)
    BLACK = (0, 0, 0, 255)

    space = pymunk.Space()
    space.gravity = (0, 981)

    createBounds(space)

    draw_options = pymunk.pygame_util.DrawOptions(screen)

    global run
    global boxes
    global startpos
    global endpos
    global box

    run = True
    boxes = []
    startpos = None
    endpos = None
    box = None

    while run: #main game loop

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.MOUSEBUTTONUP:
                if startpos:
                    endpos = pygame.mouse.get_pos()
                    x = abs(endpos[0] - startpos[0])
                    y = abs(endpos[1] - startpos[1])
                    if (endpos[0] - startpos[0]) > 0:
                        x2 = startpos[0] + (x // 2)
                    else:
                        x2 = endpos[0] + (x // 2)
                    if (endpos[1] - startpos[1]) > 0:
                        y2 = startpos[1] + (y // 2)
                    else:
                        y2 = endpos[1] + (y // 2)
                    if (x > 0) and (y > 0):
                        boxes.append(createBox(space, (x, y), (x2, y2)))
                    startpos = None
                if box:
                    click = None
                    box = None

            if event.type == pygame.MOUSEBUTTONDOWN:
                click = space.point_query_nearest(pygame.mouse.get_pos(), 0, pymunk.ShapeFilter())
                if click:
                    box = click.shape.body
                else:
                    startpos = pygame.mouse.get_pos()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    for body, shape in boxes:
                        space.remove(body, shape)
                    boxes = []

        if box:
            boxpos = box.position
            mousepos = pygame.mouse.get_pos()
            dist = math.sqrt((mousepos[1] - boxpos[1]) ** 2 + (mousepos[0] - boxpos[0]) ** 2) * (box.mass / 10)
            angle = math.atan2(mousepos[1] - boxpos[1], mousepos[0] - boxpos[0])
            fx = math.cos(angle) * dist
            fy = math.sin(angle) * dist
            box.apply_impulse_at_world_point((fx, fy), boxpos)

        pygame.time.Clock().tick(60)
        
        space.step(1/60)
        draw(space, screen, draw_options)

        await asyncio.sleep(0)
    pygame.quit()


asyncio.run(main())
