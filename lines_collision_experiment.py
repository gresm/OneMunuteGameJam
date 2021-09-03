import pygame as pg
from player import Player
from Math import GravityPool, PoolStickIterator

pg.init()
display = pg.display.set_mode((600, 600))
fps = 60
clock = pg.time.Clock()
done = False

pool = GravityPool.deserialize(({(125.0, 400.0): True, (175.0, 400.0): False, (225.0, 400.0): False,
                                 (275.0, 400.0): False, (350.0, 400.0): False, (400.0, 400.0): False,
                                 (450.0, 400.0): False, (500.0, 400.0): True},
                                {(125.0, 400.0): {(175.0, 400.0)},
                                 (175.0, 400.0): {(125.0, 400.0), (225.0, 400.0)},
                                 (225.0, 400.0): {(275.0, 400.0), (175.0, 400.0)},
                                 (275.0, 400.0): {(350.0, 400.0), (225.0, 400.0)},
                                 (350.0, 400.0): {(275.0, 400.0), (400.0, 400.0)},
                                 (400.0, 400.0): {(450.0, 400.0), (350.0, 400.0)},
                                 (450.0, 400.0): {(500.0, 400.0), (400.0, 400.0)}, (500.0, 400.0): {(450.0, 400.0)}},
                                {((125.0, 400.0), (175.0, 400.0)): 50.0, ((175.0, 400.0), (225.0, 400.0)): 50.0,
                                 ((225.0, 400.0), (275.0, 400.0)): 50.0, ((275.0, 400.0), (350.0, 400.0)): 75.0,
                                 ((350.0, 400.0), (400.0, 400.0)): 50.0, ((400.0, 400.0), (450.0, 400.0)): 50.0,
                                 ((450.0, 400.0), (500.0, 400.0)): 50.0}))
pool.generate_mesh()
lines = PoolStickIterator(pool)
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
    pool.emulate(50)

    ########################
    # fps cap
    ########################
    clock.tick(fps)
