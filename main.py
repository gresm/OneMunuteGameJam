import pygame as pg
from game import LevelGenerated


pg.init()
display = pg.display.set_mode((600, 600))
done = False
fps = 60
clock = pg.time.Clock()
progress = 0
timer = 0
timer_running = False

font = pg.font.SysFont("", 30)

while not done:
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            done = True

    display.fill((0, 0, 0))

    pg.display.update()

    clock.tick(fps)
