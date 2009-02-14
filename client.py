# Just a demo for now :-)
import glob
import pygame
import rabbyt

class Viewport(object):
    def __init__(x, y, ex, ey):
        self.x = x
        self.y = y
        self.ex = ex
        self.ey = ey
        self.set_viewport(self._x, self._y, self._ex, self._ey)
    

class Piece(rabbyt.Sprite):
    def __init__(self, **kargs):
        # back isn't understood by the Sprite class, so pop it out of the dict
        self.back_texture = kargs.pop('back', None)
        self.front_texture = kargs.get('texture', None)
        self.flipped = False
        # this must be a bug in rabbyt... why would textures be backwards by default...
        kargs['tex_shape'] = [0, 0, 1, 1]
        rabbyt.Sprite.__init__(self, **kargs)
        self.animflag = False
    def animendcallback(self):
        self.animflag = False
    def width(self):
        return self.right - self.left
    def height(self):
        return self.bottom - self.top
    def flip(self):
        self.flipped = not self.flipped
        if self.flipped and self.back_texture:
            self.texture = self.back_texture
        else:
            self.texture = self.front_texture

size = (1240.0, 780.0)
ratio = (size[0]/size[1])

pygame.init()
pygame.display.set_mode(size, pygame.OPENGL | pygame.DOUBLEBUF)
rabbyt.set_viewport(size, projection=(0, 0, size[0], size[1]))
rabbyt.set_default_attribs()

pieces = []

for card_image in glob.glob('cards/*png'):
    pieces.append(Piece(texture=card_image, back='cards/backs/back-red-150-2.png'))

grabbed_piece = None

print "Click and drag the pieces. Scrollwheel to rotate pieces."
clock = pygame.time.Clock()
running = True
z = 0
offset_x = 0
offset_y = 0
panning = False
panning_x = 0
panning_y = 0
viewport_x = 0
viewport_y = 0
while running:
    clock.tick(40)

    for event in pygame.event.get():
        if hasattr(event, 'pos'):
            # translate the position from mouse coordinates to viewport coordinates
            x_factor = float(event.pos[0]) / size[0]
            y_factor = float(event.pos[1]) / size[1]
            system_x = x_factor * (size[0] - ratio * z)
            system_y = y_factor * (size[1] - z)
            if not panning:
                system_x += viewport_x
                system_y += viewport_y
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            grabbed_piece = None
            # sort based on z-order
            location = rabbyt.Sprite(x=system_x, y=system_y)
            collisions = sorted(rabbyt.collisions.aabb_collide_single(location, pieces), cmp=lambda x, y: cmp(pieces.index(y), pieces.index(x)))
            if collisions:
                grabbed_piece = collisions[0]
            
            if grabbed_piece and event.button == 3:
                grabbed_piece.flip()
            
            if grabbed_piece:
               #keep the list in z-order
                pieces.remove(grabbed_piece)
                pieces.append(grabbed_piece)
                grabbed_piece.rgb = (.5, .5, .5)
                #grabbed_piece.scale = rabbyt.lerp(1, 1.25, dt=100, extend="reverse")
            
            # Have the scrollwheel zoom in and zoom out when not hovering over a piece
            if not grabbed_piece:
                if event.button == 1:
                    panning = True
                    original_vx = viewport_x
                    original_vy = viewport_y
                    (panning_x, panning_y) = (system_x- viewport_x, system_y - viewport_y)#(event.pos[0], event.pos[1])
                if event.button == 4:
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        z += 100
                    else:
        	            z += 20
                    rabbyt.set_viewport(size, projection=(viewport_x,viewport_y,(size[0]-ratio*z) + viewport_x,size[1]-z + viewport_y))
                elif event.button == 5:
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        z -= 100
                    else:
                        z -= 20
                    rabbyt.set_viewport(size, projection=(viewport_x,viewport_y,(size[0]-ratio*z) + viewport_x,size[1]-z + viewport_y))
                
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
                    offset_x = -(system_x - grabbed_piece.x)
                    offset_y = -(system_y - grabbed_piece.y)
        elif event.type == pygame.MOUSEMOTION:
            if panning:
                    viewport_x = original_vx - (system_x - panning_x)
                    viewport_y =  original_vy - (system_y - panning_y)
                    rabbyt.set_viewport(size, projection=(viewport_x, viewport_y, (size[0]-ratio*z) + viewport_x,size[1]-z+viewport_y))
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
            panning = False  
        
    rabbyt.set_time(pygame.time.get_ticks())
    rabbyt.clear()
    rabbyt.render_unsorted(pieces)
    rabbyt.scheduler.pump()
    pygame.display.flip()
