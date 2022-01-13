# from threading import Thread
import numpy as np
import math

from ROB.HexaplotReceiver import HexaplotReceiver
import ROB.config as cn

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.patches import Polygon
import mpl_toolkits.mplot3d.art3d as art3d


class Hexaplot:

    def __init__(self, height,hex_coord, ax_limits=None, plt_pause_value=0.05, dot_color='white', line_color='black', show_lines=False):
        self.hex_coord = hex_coord
        self.height = height

        if ax_limits is None:
            ax_limits = [10, 10, 2]
        self.hr = HexaplotReceiver()
        self.ax_limits = ax_limits
        self.fig = plt.figure()

        self.fig.canvas.manager.window.attributes('-topmost', 0)
        self.ax = self.fig.add_subplot(111, projection='3d')
        #self.ax2 = self.fig.add_subplot(122)


        # Setting the axes properties
        self.ax.set_xlim3d([-self.ax_limits[0], self.ax_limits[0]])
        #self.ax.set_xlabel('X')
        self.ax.set_ylim3d([-self.ax_limits[1], self.ax_limits[1]])
        #self.ax.set_ylabel('Y')
        self.ax.set_zlim3d([-self.ax_limits[2], self.ax_limits[2]])
        #self.ax.set_zlabel('Z')
        self.ax.grid(False)


        # Get rid of the ticks
        self.ax.axes.get_xaxis().set_ticks([])
        self.ax.axes.get_yaxis().set_ticks([])
        self.ax.axes.get_zaxis().set_ticks([])

        # Get rid of the panes
        self.ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        self.ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        self.ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))

        # Get rid of the spines
        self.ax.w_xaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
        self.ax.w_yaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
        self.ax.w_zaxis.line.set_color((1.0, 1.0, 1.0, 0.0))


        self.center_x_offset = 0
        self.center_y_offset = 0
        self.center_z_offset = 0

        self.ax.set_title('Hexapod Simulation')
        self.plt_pause_value = plt_pause_value
        self.show_lines = show_lines

        self.dot_color = dot_color
        self.line_color = line_color

        self.last_scatter_list = []
        self.last_scatter_list2 = []
        self.last_line_list = []
        self.current_points = []
        self.current_lines = []
        self.first = True


    def update_points(self, points=None, tPoints=None): # VL, ML, HL, VR, MR, HR

        if tPoints is None:
            tPoints = [0, 0]

        if points:
            if self.last_scatter_list:
                for ls in self.last_scatter_list:
                    ls.remove()
                self.last_scatter_list = []

            if self.show_lines:
                self.plot_lines(points)
            if len(self.last_scatter_list2) == 1:
                self.last_scatter_list2[0].remove()
                self.last_scatter_list2 = []
            last_scatter =self.ax2.scatter(tPoints[0],tPoints[1], c="Red", linewidths=2)
            self.last_scatter_list2.append(last_scatter)

            for p in points:
                x1 = p[0]+self.center_x_offset
                y1 = p[1]+self.center_y_offset
                z1 = p[2]+self.center_z_offset
                last_scatter = self.ax.scatter(x1, y1, z1, c=self.dot_color)
                self.last_scatter_list.append(last_scatter)

    def show_plot(self):
        while True:
            data = self.hr.getData()
            if data != None:
                formatted_data = []
                for line in data:
                    formatted_data.append([[line[0][0] * 100, line[0][1] * 100, line[0][2] * 100], [line[1][0] * 100, line[1][1] * 100, line[1][2] * 100]])
                data = formatted_data
                self.plot_lines(data)
            #self.update_points(data[0], data[2])
            plt.pause(self.plt_pause_value)



    def plot_lines(self, lines):   #[[[0,0,0],[0,0,0]],[[0,0,0],[0,0,0]]]
        if lines != None:
            self.ax.lines.clear()
            if self.last_scatter_list:
                for ls in self.last_scatter_list:
                    ls.remove()
                self.last_scatter_list = []
            for line in lines:
                x = [line[0][0], line[1][0]]
                y = [line[0][1], line[1][1]]
                z = [line[0][2], line[1][2]]
                self.last_line_list.append(self.ax.plot(x, y, z, c=self.line_color , linewidth=4))
                self.last_scatter_list.append(self.ax.scatter(x[0], y[0], z[0], c=self.dot_color))
                self.last_scatter_list.append(self.ax.scatter(x[1], y[1], z[1], c=self.dot_color))

def calcDiagonal(polgyon1, polygon2, steps):
    if len(polgyon1) != len(polygon2):
        print("ERROR Länge von beiden Listen muss übereinstimmen")
        return

    diag = []
    for index in range(0,len(polgyon1)):
        diag.append(np.subtract(polgyon1[index],polygon2[index]).tolist())

    list = []
    for i in range(1,steps):
        temp = []
        for index in range(0,len(polgyon1)):
            temp.append(np.add(polygon2[index],(np.array(diag[index])*(1/steps*i)).tolist()).tolist())
        list.append(temp)

    return list


def plotStart(height_top, height_bot,step):
    height_bot *= 100
    height = height_top * 100
    hex_coord = [[0.160,0.087],[0.160, -0.087],[0, -0.1615],[-0.160,-0.087],[-0.160, 0.087],[0, 0.1615]]
    hex_off_coord = [[0.033, 0.032],[0.033, -0.032],[0, -0.0445],[-0.033, -0.032],[-0.033, 0.032],[0, 0.0445]]
    hex_str_coord = [[0.075, 0.032], [0.075, -0.032], [0, -0.0765], [-0.075, -0.032], [-0.075, 0.032], [0, 0.0765]]

    for lists in [hex_coord,hex_off_coord,hex_str_coord]:
        for coord in lists:
            coord[0] *= 100
            coord[1] *= 100
    hp = Hexaplot(height,hex_coord, ax_limits=[20,20,15], dot_color='red', line_color='black', show_lines=True)

    # [[3,1.5],[1,5],[3,8.5],[7,1.5],[9,5],[7,8.5]]

    # Draw a circle on the x=0 'wall'
    l1 = Circle(hex_coord[0],  cn.robot['radius']*100, alpha=0.3)
    l2 = Circle(hex_coord[1],  cn.robot['radius']*100, alpha=0.3)
    l3 = Circle(hex_coord[2],  cn.robot['radius']*100, alpha=0.3)
    l4 = Circle(hex_coord[3],  cn.robot['radius']*100, alpha=0.3)
    l5 = Circle(hex_coord[4],  cn.robot['radius']*100, alpha=0.3)
    l6 = Circle(hex_coord[5],  cn.robot['radius']*100, alpha=0.3)

    circlesB = [l6, l3, l4, l5]
    circlesF = [l1, l2]

    for circle in circlesF:
        circle.set_color("red")
        hp.ax.add_patch(circle)
        art3d.pathpatch_2d_to_3d(circle, z=-height, zdir="z")


    for circle in circlesB:
        circle.set_color("green")
        hp.ax.add_patch(circle)
        art3d.pathpatch_2d_to_3d(circle, z=-height, zdir="z")

    if cn.robot['plot_trio']:
        groupA = Polygon((hex_coord[0], hex_coord[2], hex_coord[4]), alpha=0.2)
        groupB = Polygon((hex_coord[1], hex_coord[3], hex_coord[5]), alpha=0.2)
        groups = [groupA, groupB]
        groupA.set_color("blue")
        groupB.set_color("yellow")

        for group in groups:
            hp.ax.add_patch(group)
            art3d.pathpatch_2d_to_3d(group, z=-height, zdir="z")


    diag_polys = calcDiagonal(hex_off_coord,hex_str_coord,step)

    polygons = []
    for items in diag_polys:
        polygons.append(Polygon(items))

    off = Polygon(hex_str_coord)
    off.set_color("blue")
    hp.ax.add_patch(off)
    art3d.pathpatch_2d_to_3d(off, z=-3.8, zdir="z")

    z = -3.8
    diff = height - height_bot
    counter = 1
    for polygon in polygons:
        polygon.set_color("blue")
        polygon.set_linewidth(1)
        hp.ax.add_patch(polygon)
        art3d.pathpatch_2d_to_3d(polygon, z=z, zdir="z")
        z += diff/step * counter
        counter *= 1


    # polygons = []
    # for i in range(1,10):
    #     polygons.append(Polygon(hex_off_coord))


    # z = -0.8
    # for polygon in polygons:
    #     polygon.set_color("red")
    #     polygon.set_linewidth(2)
    #     hp.ax.add_patch(polygon)
    #     art3d.pathpatch_2d_to_3d(polygon, z=z, zdir="z")
    #     z += 0.2

    hp.show_plot()

if __name__ == "__main__":
    plotStart(cn.robot['height_top'],cn.robot['height_bot'],20)