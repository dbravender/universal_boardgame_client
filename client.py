# Just a demo for now :-)
import glob
from pyglet.window import Window
from pyglet import clock
from pyglet import image
import rabbyt

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

class Game(object):
    def __init__(self, window):
        self.window = window
        self.window.push_handlers(self.on_mouse_drag) #key_press, self.on_mouse_press)
        rabbyt.set_viewport((window.width, window.height), projection=(0, 0, window.width, window.height))
        rabbyt.set_default_attribs()
        self.size = (window.width, window.height)
        self.ratio = float(window.width) / window.height
        self.pieces = []
        self.grabbed_piece = None
        self.panning = False
        self.panning_x = 0
        self.panning_y = 0
        self.viewport_x = 0
        self.viewport_y = 0
        self.z = 0
        self.boards = [rabbyt.Sprite(texture='board.png')]
        for card_image in glob.glob('cards/*png'):
            self.pieces.append(Piece(texture=card_image, back='cards/backs/back-red-150-2.png'))

    def update_viewport(self):
        rabbyt.set_viewport(self.size, projection=(self.viewport_x,
                                                   self.viewport_y,
                                                   (self.size[0] - self.ratio * self.z) + self.viewport_x,
                                                   self.size[1] - self.z + self.viewport_y))
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if not self.grabbed_piece:
            #if #TODO: control key is pressed
            #    self.z += scroll_y * 10
            #else:
            if True:
                self.z += scroll_y
            self.update_viewport()
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        #self.viewport_x = self.original_vx - (system_x - self.panning_x)
        #self.viewport_y = self.original_vy - (system_y - self.panning_y)
        self.viewport_x -= dx
        self.viewport_y += dy
        self.update_viewport()
    
    def on_mouse_press(self, x, y, button, modifiers):
        # translate the position from mouse coordinates to viewport coordinates
        x_factor = float(x) / self.size[0]
        y_factor = float(y) / self.size[1]
        system_x = x_factor * (self.size[0] - self.ratio * self.z)
        system_y = y_factor * (self.size[1] - self.z)
        if not self.panning:
            system_x += self.viewport_x
            system_y += self.viewport_y
        elif True:#event.type == pygame.MOUSEBUTTONDOWN:
            grabbed_piece = None
            # sort based on z-order
            location = rabbyt.Sprite(x=system_x, y=system_y)
            collisions = sorted(rabbyt.collisions.aabb_collide_single(location, self.pieces), 
                                cmp=lambda x, y: cmp(self.pieces.index(y), self.pieces.index(x)))
            if collisions:
                self.grabbed_piece = collisions[0]
            
            if self.grabbed_piece and event.button == 3:
                self.grabbed_piece.flip()
            
            if self.grabbed_piece:
               #keep the list in z-order
                self.pieces.remove(self.grabbed_piece)
                self.pieces.append(self.grabbed_piece)
                self.grabbed_piece.rgba = (.5, .5, .5, .75)
                #self.grabbed_piece.scale = rabbyt.lerp(1, 1.25, dt=100, extend="reverse")
            
            # Have the scrollwheel zoom in and zoom out when not hovering over a piece
            
                
            if event.button == 4 and self.grabbed_piece and self.grabbed_piece.animflag == False:
                self.grabbed_piece.animflag = True
                self.grabbed_piece.rot = rabbyt.lerp(self.grabbed_piece.rot, self.grabbed_piece.rot + 45, dt=100);
                rabbyt.scheduler.add(rabbyt.get_time()+200, self.grabbed_piece.animendcallback)
            elif event.button == 5 and self.grabbed_piece and self.grabbed_piece.animflag == False:
                self.grabbed_piece.animflag = True
                self.grabbed_piece.rot = rabbyt.lerp(self.grabbed_piece.rot, self.grabbed_piece.rot - 45, dt=100);
                rabbyt.scheduler.add(rabbyt.get_time()+200, self.grabbed_piece.animendcallback)
            else:
                if self.grabbed_piece:
                    self.offset_x = -(system_x - self.grabbed_piece.x)
                    self.offset_y = -(system_y - self.grabbed_piece.y)
        elif True: #event.type == pygame.MOUSEMOTION:
            if self.panning:
                    self.viewport_x = self.original_vx - (system_x - self.panning_x)
                    self.viewport_y =  self.original_vy - (system_y - self.panning_y)
                    self.update_viewport()
            if self.grabbed_piece:
                if True: #pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.grabbed_piece.xy = ((system_x + self.offset_x) - (system_x + self.offset_x) % self.grabbed_piece.width(), (system_y + self.offset_y) - (system_y + self.offset_y) % self.grabbed_piece.height())
                else:
                    self.grabbed_piece.x = system_x + self.offset_x
                    self.grabbed_piece.y = system_y + self.offset_y
                
        elif True: #event.type == pygame.MOUSEBUTTONUP:
            if self.grabbed_piece:
                self.grabbed_piece.rgba = (1, 1, 1, 1)
                # this is causing pieces to slide somewhere else when I drop them now...
                #if pygame.key.get_mods() & pygame.KMOD_CTRL:
                #    self.grabbed_piece.xy = rabbyt.lerp((self.grabbed_piece.x, self.grabbed_piece.y), (self.grabbed_piece.x - self.grabbed_piece.x % self.grabbed_piece.width(), self.grabbed_piece.y - self.grabbed_piece.y % self.grabbed_piece.height()), dt=200)     
                #self.grabbed_piece.scale = rabbyt.lerp(1.25, 1, dt=200)
            self.grabbed_piece = None
            self.panning = False
              
        # keep running
        return True
    
    def render(self):
        pass

print "Click and drag the pieces. Scrollwheel to rotate pieces."

def run():
    clock.schedule(rabbyt.add_time)
    window = Window(1024, 780)
    game = Game(window)

    while not window.has_exit:
        clock.tick()
        window.dispatch_events()
  
        rabbyt.clear((0,0,0))
        
        rabbyt.render_unsorted(game.boards)
        rabbyt.render_unsorted(game.pieces)
        rabbyt.scheduler.pump()
        
        window.flip()

import cProfile
cProfile.run('run()', 'profile.out')

import pstats
p = pstats.Stats('profile.out')
p.strip_dirs().sort_stats(-1).print_stats()

