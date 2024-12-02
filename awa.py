import math

import tkintertools as tkt
import tkintertools.animation as animation

root = tkt.Tk()
cv = tkt.Canvas(root)
cv.place(width=1280, height=720)

ball = cv.create_oval(640-40, 360-40, 640+40, 360+40, fill="royalblue", outline="")

controller = animation.controller_generator(math.sin, 0, math.tau, map_y=False)

x = animation.MoveItem(cv, ball, 2000, (500, 0), fps=60, repeat=-1, controller=controller)
y = animation.MoveItem(cv, ball, 1000, (0, 300), fps=60, repeat=-1, controller=controller)

x.start()
y.start()

root.mainloop()