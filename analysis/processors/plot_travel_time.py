import sqlite3, sys
import pathlib, pickle
import numpy as np
import matplotlib.pyplot as plt
import util
import re

if len(sys.argv) < 7:
    print('plot_legs.py database initial_suffix final_suffix interval aggregate output_path')
    exit()

source = str(pathlib.Path(sys.argv[1]).resolve())
initial_suffix = sys.argv[2]
final_suffix = sys.argv[3]
interval = float(sys.argv[4])
aggregate = sys.argv[5]
output = sys.argv[6]

if aggregate not in ['average', 'median']:
    print('aggregate must be "averge" or "median"')
    exit()

initial_table = 'legs_%s' % initial_suffix
final_table = 'legs_%s' % final_suffix

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

class SqliteMedian:
    def __init__(self):
        self.values = []

    def step(self, value):
        self.values.append(value)

    def finalize(self):
        return float(np.median(self.values))

connection.create_aggregate("median", 1, SqliteMedian)

if aggregate == 'median':
    agg_name = 'Median'
    agg_func = 'median'
else:
    agg_name = 'Average'
    agg_func = 'avg'

cursor.execute("""
    create temporary view _initial_slots as
    select
        round(departure_time / %f - 0.5) as departure,
        round(arrival_time / %f - 0.5) as arrival,
        departure_time,
        arrival_time,
        mode
    from %s
""" % (interval, interval, initial_table))

cursor.execute("""
    create temporary view _final_slots as
    select
        round(departure_time / %f - 0.5) as departure,
        round(arrival_time / %f - 0.5) as arrival,
        departure_time,
        arrival_time,
        mode
    from %s
""" % (interval, interval, final_table))

initial_query = """
    select count(*), %s(arrival_time - departure_time) from _initial_slots
    where mode = ?1
        and ?2 >= departure
        and ?2 <= arrival
""" % agg_func

final_query = """
    select count(*), %s(arrival_time - departure_time) from _final_slots
    where mode = ?1
        and ?2 >= departure
        and ?2 <= arrival
""" % agg_func

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
plt.ylabel('%s Travel Time' % agg_name)
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
plt.ylabel('Delta %s Travel Time' % agg_name)
util.format_time_axis(plt.gca(), start_time, end_time, 7200)

if output != '-':
    path = re.sub(r'(\..*)$', r'_delta\1', output)
    plt.savefig(path)
else:
    plt.show()
