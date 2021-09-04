from builtins import str
from typing import Dict

import pygame as pg

from Math import draw_stick, draw_point
from game import LevelGenerated
from levels import load_level, load_json, save_json


pg.init()
display = pg.display.set_mode((600, 600))
done = False
fps = 60
clock = pg.time.Clock()
progress = "main_menu"
current_menu = 0
timer = 0
seconds_timer = 0
levels = 9
menu = True
timer_running = False
building = True
option_selecting = 0
mouse_rect = pg.Rect(0, 0, 50, 50)

small_font = pg.font.SysFont("", 30)
font = pg.font.SysFont("", 45)


solved_levels = load_json("solved_levels")

if not solved_levels:
    solved_levels = {str(v): False for v in range(9)}
current_level_index = 0

level_selection: Dict[int, pg.Rect] = {}


def get_level(name: str):
    return LevelGenerated(load_level(name))


level = get_level(f"level_{progress}")


while not done:
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            done = True
        elif ev.type == pg.MOUSEBUTTONUP:
            if menu:
                if current_menu == 0:
                    if option_selecting == 1:
                        menu = False
                        progress = "0"
                        get_level(f"level_{current_level_index}")
                    elif option_selecting == 2:
                        current_menu = 1
                        progress = "settings_menu"
                        level = get_level(f"level_{progress}")
                    elif option_selecting == 3:
                        done = True
                elif current_menu == 1:
                    if 0 < option_selecting <= levels:
                        current_level_index = option_selecting
                        level = get_level(f"level_{option_selecting}")
                        menu = False

    level.pool.emulate(10)

    for _ in range(10):
        for stick in level.pool.sticks_set:
            clipped = mouse_rect.clipline(stick.stick)
            if not clipped:
                continue
            p1 = pg.Vector2(clipped[0])
            p2 = pg.Vector2(clipped[1])
            c = pg.Vector2(mouse_rect.center)
            dff1 = c - p1
            dff2 = c - p2
            len1 = dff1.length()
            len2 = dff2.length()

            if len1:
                nor1 = dff1 / len1
            else:
                nor1 = pg.Vector2()

            if len2:
                nor2 = dff2 / len2
            else:
                nor2 = pg.Vector2()

            if not stick.point1.anchored:
                stick.point1.pos -= nor1
            if not stick.point2.anchored:
                stick.point2.pos -= nor2

    level.pool.emulate(10)

    display.fill((0, 0, 0))

    if menu:
        mouse_rect.center = pg.mouse.get_pos()

        if current_menu == 0:
            option_selecting = 0
            title_surf = pg.transform.scale2x(small_font.render("WEAK BRIDGES", False, (255, 255, 255)))
            title_rect = title_surf.get_rect()
            title_rect.center = (300, 150)
            display.blit(title_surf, title_rect)

            title_surf = small_font.render("MENU", False, (255, 255, 255))
            title_rect = title_surf.get_rect()
            title_rect.center = (300, 200)
            display.blit(title_surf, title_rect)

            play_surf = font.render("PLAY", False, (255, 255, 255))
            play_rect = play_surf.get_rect()
            play_rect.center = (300, 260)
            display.blit(play_surf, play_rect)

            levels_surf = font.render("LEVELS", False, (255, 255, 255))
            levels_rect = levels_surf.get_rect()
            levels_rect.center = (300, 320)
            display.blit(levels_surf, levels_rect)

            quit_surf = font.render("QUIT", False, (255, 255, 255))
            quit_rect = play_surf.get_rect()
            quit_rect.center = (300, 380)
            display.blit(quit_surf, quit_rect)

            pos = pg.mouse.get_pos()
            if play_rect.collidepoint(pos):
                option_selecting = 1
                pg.draw.rect(display, (255, 255, 255), play_rect, 5)
            elif levels_rect.collidepoint(pos):
                option_selecting = 2
                pg.draw.rect(display, (255, 255, 255), levels_rect, 5)
            elif quit_rect.collidepoint(pos):
                option_selecting = 3
                pg.draw.rect(display, (255, 255, 255), quit_rect, 5)
        elif current_menu == 1:
            option_selecting = 0
            title_surf = pg.transform.scale2x(small_font.render("WEAK BRIDGES", False, (255, 255, 255)))
            title_rect = title_surf.get_rect()
            title_rect.center = (300, 150)
            display.blit(title_surf, title_rect)

            title_surf = small_font.render("SELECT LEVEL", False, (255, 255, 255))
            title_rect = title_surf.get_rect()
            title_rect.center = (300, 200)
            display.blit(title_surf, title_rect)

            cnt = 0
            for x in range(3):
                for y in range(3):
                    rect = pg.Rect(0, 0, 40, 40)
                    rect.center = 250 + x * 50, 250 + y * 50
                    pg.draw.rect(display, (255, 255, 255), rect, 4)
                    past_solved = not (str(cnt - 1) in solved_levels and not solved_levels[str(cnt - 1)])
                    lev_num = small_font.render(str(cnt+1) if past_solved else "X", False, (255, 255, 255))
                    lev_num_rect = lev_num.get_rect()
                    lev_num_rect.center = rect.center
                    level_selection[cnt] = rect
                    display.blit(lev_num, lev_num_rect)
                    cnt += 1

                    if past_solved and rect.collidepoint(pg.mouse.get_pos()):
                        option_selecting = cnt

        for point in level.pool.points_set:
            if point.anchored:
                draw_point(display, point)

        for stick in level.pool.sticks_set:
            draw_stick(display, stick)

    else:
        pass

    if timer_running:
        seconds_timer += 1
        if seconds_timer > 60:
            timer += 1
            seconds_timer = 0
        timer_surf = small_font.render("time left: " + str(60-timer), False,
                                       (255, 255, 255) if 60-timer > 10 or timer % 2 else (255, 0, 0))
        timer_rect = timer_surf.get_rect(topright=(550, 50))
        display.blit(timer_surf, timer_rect)

    pg.display.update()

    clock.tick(fps)

save_json("solved_levels", solved_levels)
pg.quit()
quit()
