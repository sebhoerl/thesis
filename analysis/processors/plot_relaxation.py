import pickle, sys
import matplotlib.pyplot as plt
import numpy as np

if len(sys.argv) < 3:
    print('plot_relaxation.py datafile output_path')

with open(sys.argv[1], 'rb') as f:
    data, modes = pickle.load(f)

plt.figure()

for i in range(len(modes)):
    plt.plot(data[:,0], data[:,i + 1])

plt.legend(modes)
plt.grid()
plt.xlabel('Iteration')
plt.ylabel('Departures')

output = sys.argv[2]

if output == '-':
    plt.show()
else:
    plt.savefig(output)
    with open(output + '.dat', 'wb+') as f: pickle.dump((data, modes),f)
