from builtins import str
from typing import Dict

import pygame as pg

from Math import draw_stick, draw_point
from game import LevelGenerated
from levels import load_json, save_json, load_level

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
option_selecting = 0
mouse_rect = pg.Rect(0, 0, 50, 50)
right = pg.Vector2(1, 0)
down = pg.Vector2(0, 1)

small_font = pg.font.SysFont("", 30)
font = pg.font.SysFont("", 45)

solved_levels = load_json("solved_levels")

if not solved_levels:
    solved_levels = {str(v): False for v in range(9)}
current_level_index = 0

level_selection: Dict[int, pg.Rect] = {}

level_names = {
    1: "level 1: short floating bridge",
    2: "level 2: long bridge",
    3: "level 3: giant bridge",
    4: "level 4: introducing death",
    5: "level 5: maze",
    6: "level 6: falling meteors",
    7: "level 7: tall climb",
    8: "level 8: parkour",
    9: "level 9: last levels"
}

level: LevelGenerated = ...
level_group = pg.sprite.Group()


def get_level(name: str, static_camera: bool = False):
    return LevelGenerated(load_level(name), display, get_difficulty_operation_steps(), static_camera)


def set_level(name: str, static_camera: bool = False):
    global level
    level_group.empty()
    level = get_level(name, static_camera)
    level_group.add(level)


current_difficulty = 0
# 0 - menu
# 1 - easy
# 2 - normal
# 3 - hard
# 4 - impossible


difficulty_info = {
    0: (10, "menu"),
    1: (40, "easy"),
    2: (25, "normal"),
    3: (10, "hard"),
    4: (5, "insane")
}


exception = None


def get_difficulty_operation_steps():
    return difficulty_info[current_difficulty][0]


def get_difficulty_name(diff: int):
    return difficulty_info[diff][1]


def start_level():
    restart_timer()
    level.pool.generate_mesh()
    level.kill.generate_mesh()
    level.building = True


def restart_timer():
    global timer, seconds_timer, timer_running
    timer = 0
    seconds_timer = 0
    timer_running = True


def times_up():
    pass


def killed():
    pass


def next_level():
    global current_level_index, menu, current_menu
    solved_levels[str(current_level_index)] = True
    save_json("solved_levels", solved_levels)
    current_level_index += 1
    if current_level_index >= levels:
        menu = True
        current_menu = 0
    else:
        set_level(f"level_{current_level_index}")


set_level(f"level_{progress}", True)

try:
    while not done:
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                done = True
            elif ev.type == pg.KEYDOWN:
                if ev.unicode == " ":
                    if not menu:
                        level.building = False
                elif ev.unicode == "r":
                    if menu:
                        level.pool.generate_mesh()
                        level.kill.generate_mesh()
                    else:
                        set_level(f"level_{current_level_index}")
                        start_level()
                elif ev.key == pg.K_ESCAPE or ev.unicode == "q":
                    if not menu:
                        menu = True

            elif ev.type == pg.MOUSEBUTTONUP:
                if menu:
                    if current_menu == 0:
                        if option_selecting == 1:
                            menu = False
                            progress = "0"
                            current_difficulty = 1
                            set_level(f"level_{current_level_index}")
                            start_level()
                        elif option_selecting == 2:
                            current_menu = 1
                            progress = "settings_menu"
                            current_difficulty = 1
                            set_level(f"level_{progress}", True)
                        elif option_selecting == 3:
                            done = True
                    elif current_menu == 1:
                        if 0 < option_selecting <= levels:
                            current_level_index = option_selecting - 1
                            set_level(f"level_{current_level_index}")
                            menu = False
                            start_level()
                        elif option_selecting == -1:
                            current_difficulty = current_difficulty % 4
                            current_difficulty += 1
                            level_group.update(setting_steps=True, steps=get_difficulty_operation_steps())
            elif ev.type == pg.MOUSEBUTTONDOWN:
                if not menu and level.building:
                    level.interact(pg.Vector2(ev.pos), ev.button)

        if menu or not level.building:
            level_group.update()

        if menu:
            for _ in range(get_difficulty_operation_steps()):
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

        if menu or not level.building:
            level_group.update()

        display.fill((0, 0, 0))

        if menu:
            mouse_rect.center = pg.mouse.get_pos()

            if current_menu == 0:
                option_selecting = 0
                title_surf = pg.transform.scale2x(small_font.render("LIQUID BRIDGES", False, (255, 255, 255)))
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
                title_surf = pg.transform.scale2x(small_font.render("LIQUID BRIDGES", False, (255, 255, 255)))
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
                        lev_num = small_font.render(str(cnt + 1) if past_solved else "X", False, (255, 255, 255))
                        lev_num_rect = lev_num.get_rect()
                        lev_num_rect.center = rect.center
                        level_selection[cnt] = rect
                        display.blit(lev_num, lev_num_rect)
                        cnt += 1

                        if past_solved and rect.collidepoint(pg.mouse.get_pos()):
                            option_selecting = cnt

                difficulty_surf = small_font.render("DIFFICULTY", False, (255, 255, 255))
                difficulty_rect = difficulty_surf.get_rect()
                difficulty_rect.center = (310, 400)
                display.blit(difficulty_surf, difficulty_rect)

                difficulty_surf = font.render(get_difficulty_name(current_difficulty), False, (255, 255, 255))
                difficulty_rect = difficulty_surf.get_rect()
                difficulty_rect.center = (300, 450)
                pg.draw.rect(display, (255, 255, 255), difficulty_rect, 4)
                display.blit(difficulty_surf, difficulty_rect)
                if difficulty_rect.collidepoint(pg.mouse.get_pos()):
                    option_selecting = -1

            for point in level.pool.points_set:
                if point.anchored:
                    draw_point(display, point)

            for stick in level.pool.sticks_set:
                draw_stick(display, stick)

        else:
            pressed = pg.key.get_pressed()

            if not level.building:
                if pressed[pg.K_LEFT]:
                    level.player.vel -= right * 3
                if pressed[pg.K_RIGHT]:
                    level.player.vel += right * 3
                if pressed[pg.K_UP]:
                    if level.player.on_ground:
                        level.player.vel -= down * 20
            else:
                if pressed[pg.K_UP]:
                    level.camera -= down * 6
                if pressed[pg.K_DOWN]:
                    level.camera += down * 6
                if pressed[pg.K_LEFT]:
                    level.camera -= right * 6
                if pressed[pg.K_RIGHT]:
                    level.camera += right * 6

            if timer > 60:
                set_level(f"level_{current_level_index}")
                start_level()

            level_group.draw(display)

            if timer_running:
                seconds_timer += 1
                if seconds_timer > 60:
                    timer += 1
                    seconds_timer = 0
                timer_surf = small_font.render("time left: " + str(60 - timer), False,
                                               (255, 255, 255) if 60 - timer > 10 or timer % 2 else (255, 0, 0))
                timer_rect = timer_surf.get_rect(topright=(575, 25))
                display.blit(timer_surf, timer_rect)

                points_surf = small_font.render("points left: " + str(level.max_points - level.points_count), False,
                                                (255, 255, 255) if level.max_points - level.points_count > 0 else
                                                (255, 0, 0))
                points_rect = points_surf.get_rect(topleft=(25, 25))
                display.blit(points_surf, points_rect)

                title_surf = font.render(level_names[current_level_index + 1], False, (255, 255, 255))
                title_rect = title_surf.get_rect(center=(300, 100))
                if level.building:
                    display.blit(title_surf, title_rect)

                if level.is_winning():
                    next_level()
                elif level.is_loosing():
                    set_level(f"level_{current_level_index}")
                    start_level()

        pg.display.update()

        clock.tick(fps)
except Exception as e:
    exception = e
finally:
    save_json("solved_levels", solved_levels)
    pg.quit()
    if exception:
        raise exception
    quit()
