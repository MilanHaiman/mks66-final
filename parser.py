from display import *
from matrix import *
from draw import *

import math
import os

ARG_COMMANDS = [ 'frames', 'vary', 'point', 'intersection', 'circle', 'circumcircle', 'bezier', 'hermite', 'segment', 'line', 'scale', 'move', 'rotate', 'save' ]

def make_animation( name ):
    name_arg = 'anim/' + name + '*'
    name = name + '.gif'
    print 'Saving animation as ' + name
    f = os.fork()
    if f == 0:
        os.execlp('convert', 'convert', '-delay', '3.4', name_arg, name)

def parse_file( fname, edges, transform, screen, color ):

    Objects = [] 
    #will store a list of dictionaries, which contains info about each object:
    # name
    # type (point, circle, line)
    # dependence (constant or dependent)
    # location info (if constant)
    # construction info (if dependent)
    # color

    variations = []

    f = open(fname)
    lines = f.readlines()

    numframes = 1

    # step = 0.01

    c = 0
    while c < len(lines):
        line = lines[c].strip()

        if line in ARG_COMMANDS:
            c+= 1
            args = lines[c].strip().split(' ')

        if line == 'frames':
            numframes = int(args[0])

        elif line == 'vary':
            var = [0]*5
            var[0] = args[0]        # name
            var[1] = float(args[1]) # start loc
            var[2] = float(args[2]) # end   loc
            var[3] = int(args[3])   # start frame
            var[4] = int(args[4])   # end   frame
            variations.append(var)

        elif line == 'point':
            if args[0] == 'on':
              dictionary = {}
              dictionary['name'] = args[3]
              dictionary['type'] = 'point'
              dictionary['dependence'] = 'on'
              dictionary['on'] = args[1]
              dictionary['location'] = float(args[2])
              dictionary['color'] = [int(args[4]),int(args[5]),int(args[6])]
            else:
              dictionary = {}
              dictionary['name'] = args[3]
              dictionary['type'] = 'point'
              dictionary['dependence'] = 'constant'
              dictionary['x'], dictionary['y'], dictionary['z'] = float(args[0]), float(args[1]), float(args[2])
              dictionary['color'] = [int(args[4]),int(args[5]),int(args[6])]
            Objects.append(dictionary)

        elif line == 'intersection':
            dictionary = {}
            dictionary['name'] = args[2]
            dictionary['type'] = 'point'
            dictionary['dependence'] = 'intersection'
            dictionary['lines'] = [args[0],args[1]]
            dictionary['color'] = [int(args[3]),int(args[4]),int(args[5])]
            Objects.append(dictionary)

        elif line == 'circle':
            dictionary = {}
            dictionary['name'] = args[4]
            dictionary['type'] = 'circle'
            dictionary['dependence'] = 'constant'
            dictionary['x'], dictionary['y'], dictionary['z'], dictionary['r'] = float(args[0]), float(args[1]), float(args[2]), float(args[3])
            dictionary['color'] = [int(args[5]),int(args[6]),int(args[7])]
            Objects.append(dictionary)

        elif line == 'circumcircle':
            dictionary = {}
            dictionary['name'] = args[3]
            dictionary['type'] = 'circle'
            dictionary['dependence'] = 'circumcircle'
            dictionary['points'] = [args[0],args[1],args[2]]
            dictionary['color'] = [int(args[4]),int(args[5]),int(args[6])]
            Objects.append(dictionary)
            
        elif line == 'line' or line == 'segment':
            if args[0] == 'through':
              dictionary = {}
              dictionary['name'] = args[3]
              dictionary['type'] = line
              dictionary['dependence'] = 'through'
              dictionary['points'] = [args[1],args[2]]
              dictionary['color'] = [int(args[4]),int(args[5]),int(args[6])]
            else:
              dictionary = {}
              dictionary['name'] = args[4]
              dictionary['type'] = line
              dictionary['dependence'] = 'constant'
              dictionary['x1'], dictionary['y1'], dictionary['x2'], dictionary['y2'] = float(args[0]), float(args[1]), float(args[2]), float(args[3])
              dictionary['color'] = [int(args[5]),int(args[6]),int(args[7])]
            
            Objects.append(dictionary)
            
        c+= 1

    for f in range(numframes):
      for var in variations:
        if var[3]<=f<=var[4]:
          point = Objects[findobjectindex(var[0], Objects)]
          point['location'] = ((var[4] - f) * var[1] + (f - var[3]) * var[2])/(1.*(var[4]-var[3]))
      ## actually make the image now
      clear_screen(screen)
      for object in Objects:
        if object['type'] == 'segment':
          x1,y1,x2,y2 = getxyxy(object['name'], Objects)
          draw_line(x1,y1,x2,y2, screen, object['color'])
        if object['type'] == 'line':
          x1,y1,x2,y2 = getxyxy(object['name'], Objects)
          slope = (y2-y1)/(x2-x1)
          if abs(slope)>1:
            x2_ = x1 + (500-y1)/slope
            x1_ = x2 + (0-y2)/slope    
            draw_line(x1_,0,x2_,500, screen, object['color'])
          else:
            y2_ = y1 + (500-x1)*slope
            y1_ = y2 + (0-x2)*slope
            draw_line(0,y1_,500,y2_, screen, object['color'])
        if object['type'] == 'point':
          x,y = getxy(object['name'], Objects)
          draw_point(x,y, screen, object['color'])
        if object['type'] == 'circle':
          x,y,z,r = getxyzr(object['name'], Objects)
          draw_circle(x,y,z,r, screen, object['color'])
      save_extension(screen, "./anim/" + fname.split('.')[0] + ("0000" + str(f))[-4:] + ".png")
      print(str(f+1) + "/" + str(numframes))
    make_animation(fname.split('.')[0])

def findobjectindex(name, Objects):
  for i in range(len(Objects)):
    if Objects[i]['name'] == name:
      return i
  return -1

def getxy(pointname, Objects):
  point = Objects[findobjectindex(pointname, Objects)]
  if point['dependence'] == 'constant':
    return point['x'],point['y']
  if point['dependence'] == 'intersection':
    line1, line2 = point['lines'][0], point['lines'][1]
    x1,y1,x2,y2 = getxyxy(line1, Objects)
    x3,y3,x4,y4 = getxyxy(line2, Objects)
    x = -((-(x3 - x4) *(x2 *y1 - x1 *y2) + (x1 - x2) *(x4 *y3 - x3 *y4))/(-(x3 - x4) *(-y1 + y2) + (x1 - x2) *(-y3 + y4)))
    y = -((x2 *y1 *y3 - x4 *y1 *y3 - x1 *y2 *y3 + x4 *y2 *y3 - x2 *y1 *y4 + x3 *y1 *y4 + x1 *y2 *y4 - x3 *y2 *y4)/(-x3 *y1 + x4 *y1 + x3 *y2 - x4 *y2 + x1 *y3 - x2 *y3 - x1 *y4 + x2 *y4))
    return x,y
  if point['dependence'] == 'on':
    objname = point['on']
    obj = Objects[findobjectindex(objname, Objects)]
    loc = point['location']
    if obj['type'] == 'line' or obj['type'] == 'segment':
      x1,y1,x2,y2 = getxyxy(objname, Objects)
      x = loc * x2 + (1-loc) * x1
      y = loc * y2 + (1-loc) * y1
      return x,y
    if obj['type'] == 'circle':
      x,y,z,r = getxyzr(objname, Objects)
      x0 = x + r * math.cos(loc * 2 * math.pi)
      y0 = y + r * math.sin(loc * 2 * math.pi)
      return x0,y0

def getxyxy(linename, Objects):
  line = Objects[findobjectindex(linename, Objects)]
  if line['dependence'] == 'constant':
    return line['x1'],line['y1'],line['x2'],line['y2']
  if line['dependence'] == 'through':
    point1, point2 = line['points'][0], line['points'][1]
    x1,y1 = getxy(point1, Objects)
    x2,y2 = getxy(point2, Objects)
    return x1,y1,x2,y2

def getxyzr(circlename, Objects):
  circle = Objects[findobjectindex(circlename, Objects)]
  if circle['dependence'] == 'constant':
    return circle['x'],circle['y'],circle['z'],circle['r']
  if circle['dependence'] == 'circumcircle':
    point1, point2, point3 = circle['points'][0], circle['points'][1], circle['points'][2]
    x1,y1 = getxy(point1, Objects)
    x2,y2 = getxy(point2, Objects)
    x3,y3 = getxy(point3, Objects)
    x = -((-(-x1**2 + x2**2 - y1**2 + y2**2) *(2 *y1 - 2 *y3) + (2 *y1 - 2 *y2) *(-x1**2 + x3**2 - y1**2 + y3**2))/(4 *x2 *y1 - 4 *x3 *y1 - 4 *x1 *y2 + 4 *x3 *y2 + 4 *x1 *y3 - 4 *x2 *y3))
    y = (-x1**2 *x2 + x1 *x2**2 + x1**2 *x3 - x2**2 *x3 - x1 *x3**2 +x2 *x3**2 - x2 *y1**2 + x3 *y1**2 + x1 *y2**2 - x3 *y2**2 - x1 *y3**2 + x2 *y3**2)/(2 *(-x2 *y1 + x3 *y1 + x1 *y2 - x3* y2 - x1 *y3 + x2* y3))
    r = math.sqrt((x-x1)*(x-x1)+(y-y1)*(y-y1))
    z=0
    return x,y,z,r

