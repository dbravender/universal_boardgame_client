# Just a demo for now :-)

import pygame
import rabbyt

class Piece(rabbyt.Sprite):
    def __init__(self, **kargs):
        rabbyt.Sprite.__init__(self, **kargs)
        self.animflag = False
    def animendcallback(self):
        self.animflag = False
    def width(self):
        return self.right - self.left
    def height(self):
        return self.bottom - self.top

size = (1240.0, 780)
ratio = (size[0]/size[1])

pygame.init()
pygame.display.set_mode(size, pygame.OPENGL | pygame.DOUBLEBUF)
rabbyt.set_viewport(size, projection=(0, 0, size[0], size[1]))
rabbyt.set_default_attribs()

pieces = [Piece(xy=attributes[0], texture=attributes[1]) for attributes in
        [((100, 100), 'red_viking.png'),
         ((200, 50),  'green_viking.png'),
         ((300, 150), 'island_tile.png'),
         ((400, 100), 'island_tile.png')]]
grabbed_piece = None

print "Click and drag the pieces. Scrollwheel to rotate pieces."

clock = pygame.time.Clock()
running = True
z = 0
offset_x = 0
offset_y = 0
while running:
    clock.tick(40)

    for event in pygame.event.get():
        if hasattr(event, 'pos'):
            # translate the position from mouse coordinates to viewport coordinates
            x_factor = float(event.pos[0]) / size[0]
            y_factor = float(event.pos[1]) / size[1]
            system_x = x_factor * (size[0] - ratio * z)
            system_y = y_factor * (size[1] - z)
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            grabbed_piece = None
            # sort based on z-order
            collisions = sorted(rabbyt.collisions.collide_single((system_x, system_y), pieces), cmp=lambda x, y: cmp(pieces.index(y), pieces.index(x)))
            
            if collisions:
                grabbed_piece = collisions[0]
            
            if grabbed_piece:
                pieces.remove(grabbed_piece)
                pieces.append(grabbed_piece)
                grabbed_piece.rgb = (.5, .5, .5)
                #grabbed_piece.scale = rabbyt.lerp(1, 1.25, dt=100, extend="reverse")
            
            # Have the scrollwheel zoom in and zoom out when not hovering over a piece
            if not grabbed_piece:
                if event.button == 4:
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        z += 100
                    else:
        	            z += 20
                    rabbyt.set_viewport(size, projection=(0,0,size[0]-ratio*z,size[1]-z))
                elif event.button == 5:
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        z -= 100
                    else:
                        z -= 20
                    rabbyt.set_viewport(size, projection=(0,0,size[0]-ratio*z,size[1]-z))
                
            if event.button == 4 and grabbed_piece and grabbed_piece.animflag == False:
                grabbed_piece.animflag = True
                grabbed_piece.rot = rabbyt.lerp(grabbed_piece.rot, grabbed_piece.rot + 45, dt=100);
                rabbyt.scheduler.add(rabbyt.get_time()+200, grabbed_piece.animendcallback)
            elif event.button == 5 and grabbed_piece and grabbed_piece.animflag == False:
                grabbed_piece.animflag = True
                grabbed_piece.rot = rabbyt.lerp(grabbed_piece.rot, grabbed_piece.rot - 45, dt=100);
                rabbyt.scheduler.add(rabbyt.get_time()+200, grabbed_piece.animendcallback)
            else:
                if grabbed_piece:
                    offset_x = grabbed_piece.x-system_x
                    offset_y = grabbed_piece.y-system_y
        elif event.type == pygame.MOUSEMOTION:
            if grabbed_piece:
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    grabbed_piece.xy = ((system_x + offset_x) - (system_x + offset_x) % grabbed_piece.width(), (system_y + offset_y) - (system_y + offset_y) % grabbed_piece.height())
                else:
                    grabbed_piece.x = system_x + offset_x
                    grabbed_piece.y = system_y + offset_y
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if grabbed_piece:
                grabbed_piece.rgb = (1, 1, 1)
                # this is causing pieces to slide somewhere else when I drop them now...
                #if pygame.key.get_mods() & pygame.KMOD_CTRL:
                #    grabbed_piece.xy = rabbyt.lerp((grabbed_piece.x, grabbed_piece.y), (grabbed_piece.x - grabbed_piece.x % grabbed_piece.width(), grabbed_piece.y - grabbed_piece.y % grabbed_piece.height()), dt=200)     
                #grabbed_piece.scale = rabbyt.lerp(1.25, 1, dt=200)
            grabbed_piece = None

    rabbyt.set_time(pygame.time.get_ticks())
    rabbyt.clear()
    rabbyt.render_unsorted(pieces)
    rabbyt.scheduler.pump()
    pygame.display.flip()
