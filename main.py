from display import *
from draw import *
from parser import *
from matrix import *
import math
import sys


screen = new_screen()
color = [ 0, 255, 0 ]
edges = []
transform = new_matrix()


if len(sys.argv) == 2:
    file = sys.argv[1]
    parse_file( file, edges, transform, screen, color )
elif len(sys.argv) == 1:
    print("please run a command of the form:\n\npython main.py script\n\nscript can be any name of a script file, including the ones I have provided: pascal and miquel\n")
else:
    print("Too many arguments.")

