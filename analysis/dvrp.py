import numpy as np
import matplotlib.pyplot as plt
import sys, re
import matplotlib.pyplot as plt

path = sys.argv[1]
stopwatch_path = '%s/stopwatch.txt' % path
iters_path = '%s/ITERS' % path

tdata = []

convert_time = lambda x: np.dot(np.array(x.split(":")).astype(np.float), np.array([3600, 60, 1]))

with open(stopwatch_path) as f:
    for line in f:
        if line.startswith('Iteration'): continue
        values = line.split("\t")
        times = [v if re.match(r'[0-9]{2}:[0-9]{2}:[0-9]{2}', v) else '00:00:00' for v in values[1:]]
        tdata.append([values[0]] + [convert_time(t) for t in times])

tdata = np.array(tdata).astype(np.float)

hdata = []

for i in range(tdata.shape[0]):
    histogram_path = '%s/it.%d/%d.legHistogram.txt' % (iters_path, i, i)

    _hdata = []
    with open(histogram_path) as f:
        for line in f:
            if line.startswith('time'): continue
            _hdata.append(line.split("\t")[1:])

    _hdata = np.array(_hdata).astype(np.float)
    _hdata = np.sum(_hdata, 0)
    hdata.append(_hdata[6])

hdata = np.array(hdata).astype(np.float)

plt.figure()
plt.plot(hdata[1:100], tdata[1:100,11] - tdata[1:100,10])
plt.show()
