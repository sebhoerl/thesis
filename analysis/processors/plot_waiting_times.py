import sqlite3, sys
import pathlib, os
import numpy as np
import matplotlib.pyplot as plt
import util, re

if len(sys.argv) < 5:
    print('plot_waiting_times.py database suffix interval output_path')
    exit()

source = str(pathlib.Path(sys.argv[1]).resolve())
suffix = sys.argv[2]
interval = float(sys.argv[3])
output = sys.argv[4]

connection = sqlite3.connect(source)
cursor = connection.cursor()

start_time = np.array(cursor.execute('select min(time) from events_%s' % suffix).fetchall()).flatten()
end_time = np.array(cursor.execute('select max(time) from events_%s' % suffix).fetchall()).flatten()

start_slot = np.floor(start_time / interval)
end_slot = np.floor(end_time / interval)

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
    create temporary view _slots as
    select
        round(start_time / %f - 0.5) as start_time,
        round(end_time / %f - 0.5) as end_time,
        pickup_time,
        passenger_arrival_time
    from services_%s
""" % (interval, interval, suffix))

slots = np.arange(start_slot, end_slot)
data = []

for slot in slots:
    data.append(cursor.execute("""
        select avg(_slots.pickup_time - _slots.passenger_arrival_time), std(_slots.pickup_time - _slots.passenger_arrival_time)
        from _slots
        where ?1 >= start_time and ?1 < end_time
    """, (slot,)).fetchone())

data = np.array(data).astype(np.float)
data[np.isnan(data[:,0]),:] = 0.0

plot_slots = np.repeat(slots, 2)
plot_slots[1::2] += 1
plot_slots *= interval

plot_data = np.repeat(data, 2, 0)

plt.figure()
plt.fill_between(plot_slots, plot_data[:,0] *0, plot_data[:,1], color='r', alpha=0.25)
plt.plot(plot_slots, plot_data[:,0], 'r')

plt.grid()
util.format_time_axis(plt.gca(), start_time, end_time, 7200)
plt.xlabel('Time of day')
plt.ylabel('Average Waiting Time')

if output != '-':
    plt.savefig(output)
else:
    plt.show()
