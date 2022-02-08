import math

# ------------------------------------------------------------
# |                Konfigurationsvariablen                   |
# ------------------------------------------------------------

# -------------------------Roboter---------------------------
robot = dict(
    test=True,
    debug=False,
    simulation=False,
    height_top=0.13,
    height_bot=0.10,
    cycle_time=0.4,
    speed=60,
    radius=0.04,
    triangle=[[0.5, 0, 0.5], [1, 0, 0], [0.5, 0, 0], [0, 0, 0], [-0.5, 0, 0], [-1, 0, 0], [-0.5, 0, 0.5], [0, 0, 1]],
    height_t=0.04,
    height_r=0.06,
    height_f=0.02,
    rectangle=[[1, 0, 1], [1, 0, 0], [0.5, 0, 0], [0, 0, 0], [-0.5, 0, 0], [-1, 0, 0], [-1, 0, 1], [0, 0, 1]],
    fast=[[1, 0, 0.6], [1, 0, 0.5], [0, 0, 0.5], [-1, 0, 0.5], [-1, 0, 0.5], [0, 0, 0.8]],
    plot_trio=False
)

# --------------------------LEG 1 V R------------------------------
leg_v_r = dict(
    measures=[0.042, 0.038, 0.049, 0.059, 0.021, 0.013, 0.092],
    offset=[0.033, -0.032],
    rotation=0,
    motorId=[14, 16, 18],
    angle=[0, 0, math.pi/2],
    startup=[0.175, -0.075, -robot['height_top']],
    ccw=[True, False, True]
)

# --------------------------LEG 2 V L------------------------------
leg_v_l = dict(
    measures=[0.042, 0.038, 0.049, 0.059, 0.021, 0.013, 0.092],
    offset=[0.033, 0.032],
    rotation=0,
    motorId=[13, 15, 17],
    angle=[0, 0, math.pi/2],
    startup=[0.175, 0.075, -robot['height_top']],
    ccw=[True, True, False]
)

# --------------------------LEG 3 M L------------------------------
leg_m_l = dict(
    measures=[0.032, 0.038, 0.049, 0.059, 0.021, 0.013, 0.092],
    offset=[0, 0.0445],
    rotation=math.pi / 2,
    motorId=[7, 9, 11],
    angle=[0, 0, math.pi/2],
    startup=[0, 0.1615, -robot['height_top']],
    ccw=[True, True, False]
)

# --------------------------LEG 4 H L------------------------------
leg_h_l = dict(
    measures=[0.042, 0.038, 0.049, 0.059, 0.021, 0.013, 0.092],
    offset=[-0.033, 0.032],
    rotation=math.pi,
    motorId=[1, 3, 5],
    angle=[0, 0, math.pi/2],
    startup=[-0.175, 0.075, -robot['height_top']],
    ccw=[True, False, True]
)

# --------------------------LEG 5 H R------------------------------
leg_h_r = dict(
    measures=[0.042, 0.038, 0.049, 0.059, 0.021, 0.013, 0.092],
    offset=[-0.033, -0.032],
    rotation=math.pi,
    motorId=[2, 4, 6],
    angle=[0, 0, math.pi/2],
    startup=[-0.175, -0.075, -robot['height_top']],
    ccw=[True, True, False]
)

# --------------------------LEG 6 M R------------------------------
leg_m_r = dict(
    measures=[0.032, 0.038, 0.049, 0.059, 0.021, 0.013, 0.092],
    offset=[0, -0.0445],
    rotation=-math.pi / 2,
    motorId=[8, 10, 12],
    angle=[0, 0, math.pi/2],
    startup=[0, -0.185, -robot['height_top']],
    ccw=[True, False, True]
)
