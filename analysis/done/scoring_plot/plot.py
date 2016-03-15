import matplotlib.pyplot as plt
import numpy as np

with open('scorestats.txt') as f:
    data = []

    for line in f:
        if line.startswith('ITERATION'): continue
        data.append(line.split("\t"))

data = np.array(data).astype(np.float)

plt.figure()
plt.plot(data[:,0], data[:,1])
plt.plot(data[:,0], data[:,2])
plt.plot(data[:,0], data[:,3])
plt.plot(data[:,0], data[:,4])

plt.grid()
plt.xlabel('Iteration')
plt.ylabel('Average Scores')

plt.legend([
    'Executed',
    'Worst',
    'Average',
    'Best'
], loc='lower right')

plt.savefig('scorestats.pdf')
