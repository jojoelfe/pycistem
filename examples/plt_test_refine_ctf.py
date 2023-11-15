import pandas as pd
import matplotlib.pyplot as plt


data = pd.read_csv("test.csv")

f, ax = plt.subplots()

#data = data[data["score"] < 0.185]

points = ax.scatter(data["beam_tilt_x"], data["beam_tilt_y"], c=data["score"], s=50, cmap="plasma")
f.colorbar(points)
plt.show()


plt.hist(data["beam_tilt_x"],bins=10)

plt.show()