import sqlite3, sys
import pathlib, os
import numpy as np
import matplotlib.pyplot as plt
import util, re

if len(sys.argv) < 5:
    print('plot_services.py database suffix interval output_path')
    exit()

source = str(pathlib.Path(sys.argv[1]).resolve())
suffix = sys.argv[2]
interval = float(sys.argv[3])
output = sys.argv[4]

table = 'states_%s' % suffix

connection = sqlite3.connect(source)
cursor = connection.cursor()

# Analyze heuristic

start_time = np.array(cursor.execute('select min(time) from events_%s' % suffix).fetchall()).flatten()
end_time = np.array(cursor.execute('select max(time) from events_%s' % suffix).fetchall()).flatten()

heuristic_changes = np.array([start_time] + cursor.execute("""
    select time from events_%s
    where type="AVDispatchModeChange"
""" % suffix).fetchall() + [end_time]).flatten()

# Analyze states

result = cursor.execute("""
    create temporary table _states as
    select
        a.person,
        a.start_time,
        a.end_time,
        a.act_type as state
    from activities_%s as a
""" % (suffix,))

start_time = np.array(cursor.execute('select min(end_time) from _states where state="AVIdle"').fetchall()).flatten()
end_time = np.array(cursor.execute('select max(end_time) from _states where state != "AVIdle"').fetchall()).flatten()

start_slot = np.floor(start_time / interval)
end_slot = np.floor(end_time / interval)

cursor.execute("""
    create temporary table _slot_states as
    select
        round(start_time / %f - 0.5) as start_time,
        round(end_time / %f - 0.5) as end_time,
        state
    from _states
""" % (interval, interval))

query = """
    select count(*) from _slot_states
    where state = ?1
        and ?2 >= start_time
        and ?2 < end_time
"""

# Obtain distributions

states = ['AVIdle', 'AVPickupDrive', 'AVWaiting', 'AVPickup', 'AVDropoffDrive', 'AVDropoff']
data = {}

slots = np.arange(start_slot, end_slot)

for state in states:
    counts = np.array([cursor.execute(query, (state, slot)).fetchone()[0] for slot in slots])
    data[state] = counts

# Plot all distributions

plt.figure()

plot_slots = np.repeat(slots, 2)
plot_slots[1::2] += 1
plot_slots *= interval

for state in states:
    plot_counts = np.repeat(data[state], 2)
    plt.plot(plot_slots, plot_counts)

plt.grid()
plt.legend(states, loc='upper center')
plt.xlabel('Time of day')
plt.ylabel('Agents')

util.format_time_axis(plt.gca(), start_time, end_time, 7200)

if output != '-':
    path = re.sub(r'(\..*)$', r'_all\1', output)
    plt.savefig(path)

# Plot only idle / driving

data['Busy'] = np.max(data['AVIdle']) - data['AVIdle']
states = ['AVIdle', 'AVDropoffDrive', 'AVPickupDrive', 'Busy']

plt.figure()

upper = np.max(data['AVIdle'])
lower = np.array([0,0])
upper = np.array([upper, upper]).flatten()

for i in range(heuristic_changes.shape[0] - 1):
    if i % 2 == 0: continue
    times = heuristic_changes[i:i+2]
    plt.fill_between(times, lower, upper, facecolor='y', alpha=0.25)

for state in states:
    plot_counts = np.repeat(data[state], 2)
    plt.plot(plot_slots, plot_counts)

plt.grid()
plt.legend(states, loc='upper center')
plt.xlabel('Time of day')
plt.ylabel('Agents')

util.format_time_axis(plt.gca(), start_time, end_time, 7200)

if output != '-':
    path = re.sub(r'(\..*)$', r'_main\1', output)
    plt.savefig(path)
else:
    plt.show()
