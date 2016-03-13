import sqlite3, sys
import pathlib, pickle
import numpy as np
import matplotlib.pyplot as plt
import util
import re

if len(sys.argv) < 6:
    print('plot_legs.py database initial_suffix final_suffix interval output_path')
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

class SqliteStd:
    def __init__(self):
        self.values = []

    def step(self, value):
        self.values.append(value)

    def finalize(self):
        self.values = np.array(self.values)
        return np.sort(self.values)[np.floor(self.values.shape[0] * 0.9)]

connection.create_aggregate("std", 1, SqliteStd)

cursor.execute("""
    create temporary view _initial_slots as
    select
        round(departure_time / %f - 0.5) as departure,
        round(arrival_time / %f - 0.5) as arrival,
        mode, distance
    from %s
""" % (interval, interval, initial_table))

cursor.execute("""
    create temporary view _final_slots as
    select
        round(departure_time / %f - 0.5) as departure,
        round(arrival_time / %f - 0.5) as arrival,
        mode, distance
    from %s
""" % (interval, interval, final_table))

initial_query = """
    select count(*), avg(distance) from _initial_slots
    where mode = ?1
        and ?2 >= departure
        and ?2 <= arrival
"""

final_query = """
    select count(*), avg(distance) from _final_slots
    where mode = ?1
        and ?2 >= departure
        and ?2 <= arrival
"""

initial_data = {}
final_data = {}
slots = np.arange(start_slot, end_slot)

plot_slots = np.repeat(slots, 2)
plot_slots[1::2] += 1
plot_slots *= interval

for mode in modes:
    initial_data[mode] = np.array([cursor.execute(initial_query, (mode, slot)).fetchone() for slot in slots])
    final_data[mode] = np.array([cursor.execute(final_query, (mode, slot)).fetchone() for slot in slots])

colors = {
    'av':'r',
    'car':'b',
    'pt':'g',
    'transit_walk': 'y',
    'walk': 'c'
}

plt.figure()

for dataset, linestyle in zip([final_data, initial_data], ['solid', 'dotted']):
    for mode in modes:
        times = np.repeat(dataset[mode][:,1], 2).astype(np.float)
        times[np.isnan(times)] = 0.0

        if mode in colors:
            plt.plot(plot_slots, times, color=colors[mode], linestyle=linestyle)
        else:
            plt.plot(plot_slots, times, linestyle=linestyle)

plt.grid()
plt.legend(modes, loc = 'upper center')
plt.xlabel('Time of day')
plt.ylabel('Average Distance')
util.format_time_axis(plt.gca(), start_time, end_time, 7200)

if output != '-':
    path = re.sub(r'(\..*)$', r'_absolute\1', output)
    plt.savefig(path)

plt.figure()

for mode in modes:
    initial_times = np.repeat(initial_data[mode][:,1], 2).astype(np.float)
    initial_times[np.isnan(initial_times)] = 0.0

    final_times = np.repeat(final_data[mode][:,1], 2).astype(np.float)
    final_times[np.isnan(final_times)] = 0.0

    times = final_times - initial_times

    if mode in colors:
        plt.plot(plot_slots, times, color=colors[mode])
    else:
        plt.plot(plot_slots, times)

plt.grid()
plt.legend(modes, loc = 'upper center')
plt.xlabel('Time of day')
plt.ylabel('Delta Average Distance')
util.format_time_axis(plt.gca(), start_time, end_time, 7200)

if output != '-':
    path = re.sub(r'(\..*)$', r'_delta\1', output)
    plt.savefig(path)
else:
    plt.show()
