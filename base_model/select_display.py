# -*- coding: utf-8 -*-
"""
@Time ： 2022/12/14 17:06
@Auth ： DingKun
@File ：select_display.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""

import matplotlib.pyplot as plt
import numpy as np

a = np.arange(0,10,1)
b = np.arange(0,20,2)
c = np.arange(0,5,.5)
d = np.arange(-1,9,1)
e = np.arange(0,15,.5)
f = np.arange(-1,19,1)
lined = {}
def onpick(event):
    legl = event.artist
    origl = lined[legl]
    vis = not origl.get_visible()
    origl.set_visible(vis)
    if vis:
        legl.set_alpha(1.0)
    else:
        legl.set_alpha(0.2)
    event.canvas.draw()

for var1, var2 in [(a,b), (c,d)]:
    fig, ax = plt.subplots()
    line1, = ax.plot(var1, label="l1")
    line2, = ax.plot(var2, label="l2")
    leg = fig.legend([line1, line2], ["l1", "l2"])
    legl1, legl2 = leg.get_lines()
    legl1.set_picker(5)
    lined[legl1] = line1
    legl2.set_picker(5)
    lined[legl2] = line2

    fig.canvas.mpl_connect('pick_event', onpick)
plt.show()