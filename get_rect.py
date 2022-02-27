import sys
import pygame as pg

BG_COLOR = pg.Color(80, 60, 70)
PLAYER_COLOR = pg.Color(90, 140, 190)

def main():
    screen = pg.display.set_mode((640, 480))
    clock = pg.time.Clock()

    player_img = pg.Surface((40, 60))
    player_img.fill(PLAYER_COLOR)
    # Create a rect with the size of the image/pygame.Surface
    # and immediately set it's topleft coords to (100, 300).
    player_rect = player_img.get_rect(topleft=(100, 300))

    done = False

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_d:
                    # Set the center to these new coords.
                    player_rect.center = (400, 200)
                if event.key == pg.K_a:
                    # Set the x coord to 300.
                    player_rect.x = 300

        screen.fill(BG_COLOR)
        screen.blit(player_img, player_rect)
        pg.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    pg.init()
    main()
    pg.quit()
    sys.exit()