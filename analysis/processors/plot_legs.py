import sqlite3, sys
import pathlib, pickle
import numpy as np
import matplotlib.pyplot as plt
import util

if len(sys.argv) < 5:
    print('plot_legs.py database suffix interval output_path')
    exit()

source = str(pathlib.Path(sys.argv[1]).resolve())
suffix = sys.argv[2]
interval = float(sys.argv[3])
output = sys.argv[4]

table = 'legs_%s' % suffix

connection = sqlite3.connect(source)
cursor = connection.cursor()

modes = np.array(cursor.execute('select mode from %s group by mode' % table).fetchall()).flatten()

start_time = np.array(cursor.execute('select min(departure_time) from %s' % table).fetchall()).flatten()
end_time = np.array(cursor.execute('select max(arrival_time) from %s' % table).fetchall()).flatten()

start_slot = np.floor(start_time / interval)
end_slot = np.ceil(end_time / interval)

cursor.execute("""
    create temporary view slot_legs as
    select
        round(departure_time / %f - 0.5) as departure,
        round(arrival_time / %f - 0.5) as arrival,
        mode
    from %s
""" % (interval, interval, table))

#query = """
#    select count(*) from slot_legs
#    where mode = ?1
#        and (
#            (?2 >= departure and ?2 < arrival and arrival > departure)
#            or
#            (?2 = departure and arrival = departure)
#        )
#"""

query = """
    select count(*) from slot_legs
    where mode = ?1
        and ?2 >= departure
        and ?2 <= arrival
"""

plt.figure()

accumulate = np.zeros((end_slot - start_slot))

colors = {
    'av':'r',
    'car':'b',
    'pt':'g',
    'transit_walk': 'y',
    'walk': 'c'
}

data = {}

for mode in modes:
    slots = np.arange(start_slot, end_slot)
    counts = np.array([cursor.execute(query, (mode, slot)).fetchone()[0] for slot in slots])
    accumulate += counts

    slots = np.repeat(slots, 2)
    slots[1::2] += 1
    counts = np.repeat(counts, 2)

    if mode in colors:
        plt.plot(slots * interval, counts, color=colors[mode])
    else:
        plt.plot(slots * interval, counts)

    data[mode] = (slots, counts)

plt.grid()
plt.legend(modes, loc = 'upper center')
plt.xlabel('Time of day')
plt.ylabel('Agents')

util.format_time_axis(plt.gca(), start_time, end_time, 7200)

if output == '-':
    plt.show()
else:
    plt.savefig(output)
    with open(output + '.dat', 'wb+') as f: pickle.dump(data,f)
