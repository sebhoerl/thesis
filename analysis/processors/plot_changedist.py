import sqlite3, sys
import pathlib, pickle
import numpy as np
import matplotlib.pyplot as plt
import util

if len(sys.argv) < 7:
    print('plot_changedist.py database initial_suffix final_suffix initial_mode final_mode output')
    exit()

source = str(pathlib.Path(sys.argv[1]).resolve())
initial_suffix = sys.argv[2]
final_suffix = sys.argv[3]
initial_mode = sys.argv[4]
final_mode = sys.argv[5]
output = sys.argv[6]

connection = sqlite3.connect(source)
cursor = connection.cursor()

cursor.execute("""
    create temporary table _first_initial as
    select evt.person as person, min(evt.time) as time, link
    from events_%s as evt
    where evt.type="departure"
    group by evt.person
    having evt.legMode="%s"
""" % (initial_suffix, initial_mode))

cursor.execute("""
    create temporary table _first_final as
    select evt.person as person, min(evt.time) as time, link
    from events_%s as evt
    where evt.type="departure"
    group by evt.person
    having evt.legMode="%s"
""" % (final_suffix, final_mode))

cursor.execute("""
    create temporary table _link_counts as
    select
        initial.link as link,
        count(*) as cnt
    from _first_initial as initial
    inner join _first_final as final on initial.person = final.person
    group by initial.link
""")

data = np.array(cursor.execute("""
    select
        links.id,
        _link_counts.cnt,
        fromnode.x + (tonode.x - fromnode.x) / 2 as x,
        fromnode.y + (tonode.y - fromnode.y) / 2 as y
    from links

    inner join _link_counts on links.id = _link_counts.link

    inner join nodes as fromnode on links.from_id = fromnode.id
    inner join nodes as tonode on links.to_id = tonode.id

    group by links.id
""").fetchall())[:,1:].astype(np.float)

plt.figure()
plt.scatter(data[:,1], data[:,2], s = data[:,0] / np.max(data[:,0]) * 1000, c = data[:,0], cmap = plt.get_cmap('summer'))

lines = cursor.execute("""
    select links.id, fromnode.x, tonode.x, fromnode.y, tonode.y
    from links
    inner join nodes as fromnode on links.from_id = fromnode.id
    inner join nodes as tonode on links.to_id = tonode.id
""")

for line in lines:
    coords = np.array(line[1:])
    plt.plot(coords[0:2], coords[2:4], 'k')

plt.title('Switch from %s to %s ' % (initial_mode, final_mode))
plt.colorbar()
plt.grid()

if output == '-':
    plt.show()
else:
    plt.savefig(output)
