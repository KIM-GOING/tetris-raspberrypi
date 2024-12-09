import pygame as pg
pg.init()

screen = pg.display.set_mode((400,300))
pg.display.set_caption("Pygame Test")

white = (255,255,255)
blue = (0,0,255)

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    
    screen.fill(white)
    pg.draw.circle(screen, blue, (200,150), 50)
    pg.display.update()

pg.quit()