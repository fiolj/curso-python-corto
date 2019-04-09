import numpy as np
import matplotlib.pyplot as plt

v_0 = 2
g = -9.8
z_0 = 10
t = np.linspace(0, 10, 100)
v = v_0 - g * t
z = z_0 + v_0 * t - g * t**2 / 2

plt.ion()

plt.figure()
plt.plot(t, v)
plt.xlabel('tiempo')
plt.ylabel('velocidad')

plt.figure()
plt.plot(t, z)
plt.xlabel('tiempo')
plt.ylabel('altura')

plt.figure()
plt.plot(z, v)
plt.ylabel('velocidad')
plt.xlabel('altura')
