#! /usr/bin/env python3
"En este script queremos simular las condiciones que dan lugar a la pluma gaussiana"

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
# import scipy as sp

xcm = 0
ycm = 0
zcm = 3

u = 2                            # velocidad del viento en m/s
time = np.linspace(0, 12, 12)     # Tiempo, en segundos
Npart = 1000              # Número de partículas emitidas en cada paso

dt = np.diff(time)
K = 1.

x = np.zeros((len(time), Npart))
y = np.zeros((len(time), Npart))
z = np.zeros((len(time), Npart))

for j, t in enumerate(time):
  xcm = xcm + u * dt                # posición del centro de masas

  sigma_x = sigma_y = sigma_z = K / (u * t)

  x[j] = np.random.normal(loc=x, scale=sigma_x, N)
  y[j] = np.random.normal(loc=0, scale=sigma_y, N)
  z[j] = np.random.normal(loc=0, scale=sigma_z, N)
