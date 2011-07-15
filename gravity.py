import pyglet
import math
import Queue
from collections import namedtuple, deque

fps_display = pyglet.clock.ClockDisplay()

window = pyglet.window.Window()

TwoVector_ = namedtuple('TwoVector', ['x','y'])
class TwoVector(TwoVector_):
    def __add__(self, other):
        """ Add together two vectors component-wise."""
        return TwoVector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        """ Subtract two vectors component-wise."""
        return TwoVector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other):
        """ If other is a vector, then return the dot product of two vectors. Otherwise, scalar multiplication. """
        if isinstance(other, TwoVector):
            return self.x*other.x + self.y*other.y
        else:
            return TwoVector( self.x*other, self.y*other)
    
    def __div__(self, other):
        """ Scalar division. """
        return TwoVector(self.x/other, self.y/other)

    def __pow__(self, other):
        """ Component-wise exponentiation. """
        return TwoVector(self.x**other,  self.y**other)
    
    def __abs__(self):
        """ Returns the magnitude of the vector. """
        return math.sqrt(self.x*self.x + self.y*self.y)

    def __neg__(self):
        """ Returns the inverse of the vector. """
        return TwoVector(-self.x, -self.y)

    def __rshift__(self, other):
        """ Returns a unit vector pointing from this vector to the other vector. """
        temp = other-self
        return temp/abs(temp)

G = 6.674e-11
G = 20

def f_gravity(pos1, mass1, pos2, mass2):
    """ Returns the force of gravity exerted by object 2 on object 1, as a vector. """
    return (pos1>>pos2)*G*mass1*mass2/abs(pos1-pos2)

class Body():
    def __init__(self, pos, mass, radius):
        self.pos = pos
        self.mass = mass
        self.radius = radius

class Ship():
    tick_size = 1/100.0
    tick = 0
    remainder = 0.0

    def __init__(self, pos, vel, mass, radius):
        #Always contains position at self.tick
        self.pos = pos

        #Always contains velocity at self.tick
        self.vel = vel

        self.mass = mass
        self.radius = radius

        self.buffer = deque()

    def step(self, dt):
        """
            Step the simulation forward by dt.  Keep track of remainder, if dt doesn't lie on a tick.
        """
        ticks, self.remainder = divmod(self.remainder + dt, self.tick_size)

        while( ticks > 0 ):
            self.predict( 10 -len(self.buffer) )
                
            self.pos, self.vel  = self.buffer.popleft()
            self.tick += 1
            
            ticks -= 1
        

    def predict(self, ticks):
        """
            Predict for some number of ticks, place in buffer.
        """

        while ticks > 0:
            if len(self.buffer) > 0:
                last_pos, last_vel = self.buffer[-1]
            else:
                last_pos = self.pos
                last_vel = self.vel
        
            #Gravity force vector
            f_g = TwoVector(0,0)
        
            #For each body, add gravity force vector
            for b in bodies:
                f_g += f_gravity(last_pos, self.mass, b.pos, b.mass)
        
            #pos = p_old + v*dt + f_g/m*dt^2
            new_pos = last_pos + (last_vel * self.tick_size) + f_g / self.mass * self.tick_size * self.tick_size
            #vel = v_old + f_g/m*dt
            new_vel = last_vel + (f_g / self.mass * self.tick_size)

            self.buffer.append( (new_pos, new_vel) )

            ticks -=1

bodies = set( [ Body( TwoVector(200,100), 100, 20),
                Body( TwoVector(250,300), 50, 10),
                Body( TwoVector(275,200), 50, 10) ] )

ship = Ship( TwoVector(0,0), TwoVector(0,0), 2, 5 )

def draw_body(b):
    x = b.pos.x
    y = b.pos.y
    r = b.radius
   
    pyglet.graphics.draw_indexed(4, pyglet.gl.GL_TRIANGLES,
        [0, 1, 2, 0, 2, 3],
        ('v2f', (x-r/2, y-r/2, x+r/2, y-r/2, x+r/2, y+r/2, x-r/2, y+r/2))
    )

def draw_arrow(x, y, dx, dy):
    line_angle = math.atan2(dy, dx)
    endx = x+dx
    endy = y+dy 
    sweep = math.pi * 5 / 6
    length = 7
    #Draw arrow line
    pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (x, y, endx, endy)))

    #Draw arrow part
    pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (endx, endy, endx+length*math.cos(line_angle+sweep) , endy+length*math.sin(line_angle + sweep))))
    
    pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (endx, endy, endx+length*math.cos(line_angle-sweep) , endy+length*math.sin(line_angle - sweep))))



def draw_buffer(ship):
    points = []
    for b in ship.buffer:
        points.append(b[0].x)
        points.append(b[0].y)

    pyglet.graphics.draw( len(points) / 2, pyglet.gl.GL_LINE_STRIP, ('v2f', points))
    
@window.event
def on_draw():
    window.clear()
    
    for b in bodies:
        draw_body(b)

    draw_body(ship)
    #draw_buffer(ship)
    draw_arrow(ship.pos.x, ship.pos.y, ship.vel.x, ship.vel.y)
    fps_display.draw()


def update(dt):
    ship.step(dt)
    

pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()

