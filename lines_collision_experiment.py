import pygame as pg
from player import Player

pg.init()
display = pg.display.set_mode((600, 600))
fps = 60
clock = pg.time.Clock()
done = False

lines = [((250, 400), (350, 400)), ((350, 300), (350, 400)), ((250, 400), (250, 300)), ((250, 300), (350, 300))]
player = Player(pg.Rect(0, 0, 50, 50), pg.Vector2(300, 325))
player2 = Player(pg.Rect(0, 0, 25, 25), pg.Vector2(340, 325))
player_group = pg.sprite.Group(player, player2)


while not done:
    ########################
    # event loop
    ########################
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            done = True

    ########################
    # math before rendering
    ########################
    player_group.update(walls=lines)

    ########################
    # filling screen
    ########################
    display.fill((0, 0, 0))

    ########################
    #  rendering
    ########################
    for line in lines:
        pg.draw.line(display, (255, 255, 255), line[0], line[1])

    player_group.draw(display)

    ########################
    # displaying
    ########################
    pg.display.update()

    ########################
    # math after rendering
    ########################
    # None

    ########################
    # fps cap
    ########################
    clock.tick(fps)
