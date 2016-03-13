import sqlite3, sys
import pathlib, pickle
import numpy as np
import matplotlib.pyplot as plt
import util
import re

if len(sys.argv) < 6:
    print('plot_totaldist.py database initial_suffix final_suffix interval output_path')
    exit()

source = str(pathlib.Path(sys.argv[1]).resolve())
initial_suffix = sys.argv[2]
final_suffix = sys.argv[3]
interval = float(sys.argv[4])
output = sys.argv[5]

initial_table = 'distances_%s' % initial_suffix
final_table = 'distances_%s' % final_suffix

connection = sqlite3.connect(source)
cursor = connection.cursor()

modes = ['av', 'car', 'pt', 'walk']

initial_start_time = np.array(cursor.execute('select min(departure_time) from %s' % initial_table).fetchall()).flatten()
initial_end_time = np.array(cursor.execute('select max(arrival_time) from %s' % initial_table).fetchall()).flatten()
final_start_time = np.array(cursor.execute('select min(departure_time) from %s' % final_table).fetchall()).flatten()
final_end_time = np.array(cursor.execute('select max(arrival_time) from %s' % final_table).fetchall()).flatten()
start_time = float(np.min([initial_start_time, final_start_time]))
end_time = float(np.max([initial_end_time, final_end_time]))

start_slot = np.floor(start_time / interval) - 1
end_slot = np.ceil(end_time / interval) + 1

query = """
    select sum(distance) from distances_%s
    where arrival_time < ?
"""

slabels = ['Initial', 'Final (w/o pickup)', 'Final (w/ pickup)']

times = np.arange(start_slot, end_slot) * interval

excess = np.array([cursor.execute("""
    select sum(pickup_distance) from services_%s
    where pickup_arrival_time < ?
""" % final_suffix, (time,)).fetchone()[0] for time in times]).astype(np.float)

plt.figure()

data = {}

for scenario, color in zip(['initial', 'final'], ['b', 'r']):
    distances = np.array([cursor.execute(query % scenario, (time,)).fetchone()[0] for time in times]).astype(np.float)
    distances[np.isnan(distances)] = 0.0
    plt.plot(times, distances, color=color)

    if scenario == 'final':
        distances += excess
        plt.plot(times, distances, color=color, linestyle='--')

    data[scenario] = distances

plt.grid()
plt.legend(slabels, loc = 'upper left')
plt.xlabel('Time of day')
plt.ylabel('Total Distance')
util.format_time_axis(plt.gca(), start_time, end_time, 7200)

delta = data['final'] - data['initial']

proc = delta[-1] / data['initial'][-1]

plt.title('Total Excess Distance: %f km (+ %d%%)' % (int(delta[-1] / 1000), proc * 100))

if output == '-':
    plt.show()
else:
    plt.savefig(output)
