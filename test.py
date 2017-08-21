import matplotlib.pyplot as plt
import numpy as np
import numpy.linalg as npl



np.random.seed(1966)
X = np.random.multivariate_normal([0,0], [[3, 1.5],[1.5, 1]], size=50).T

x_mean = X.mean(axis=1)


X[0] = X[0] - x_mean[0]
X[1] = X[1] - x_mean[1]
plt.scatter(X[0], X[1])


squares = X ** 2
print(np.sum(squares))

v1 = X[:, 0]


u_guessed = np.array([np.cos(np.pi / 4), np.sin(np.pi / 4)] )
u_guessed_row = u_guessed.reshape((1, 2))
c_values = u_guessed_row.dot(X)
projected = u_guessed_row.T.dot(c_values)
print(projected.shape)


plt.plot(projected[0], projected[1], color='blue', linewidth=3)

plt.xticks(())
plt.yticks(())

plt.show()