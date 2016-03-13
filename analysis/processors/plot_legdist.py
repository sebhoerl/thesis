import sqlite3, sys
import pathlib, pickle
import numpy as np
import matplotlib.pyplot as plt
import util

if len(sys.argv) < 4:
    print('plot_legdist.py database suffix mode arrival/departure output')
    exit()

source = str(pathlib.Path(sys.argv[1]).resolve())
suffix = sys.argv[2]
mode = sys.argv[3]
what = sys.argv[4]
output = sys.argv[5]

if what not in ['arrival', 'departure']:
    print('Either arrival or departure must be chosen')

connection = sqlite3.connect(source)
cursor = connection.cursor()

data = np.array(cursor.execute("""
    select
        links.id,
        count(*),
        fromnode.x + (tonode.x - fromnode.x) / 2 as x,
        fromnode.y + (tonode.y - fromnode.y) / 2 as y
    from links
    inner join nodes as fromnode on links.from_id = fromnode.id
    inner join nodes as tonode on links.to_id = tonode.id
    left join legs_%s as leg where leg.mode="%s" and leg.%s_link = links.id
    group by links.id
""" % (suffix, mode, what)).fetchall())[:,1:].astype(np.float)

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

plt.colorbar()
plt.grid()

if output == '-':
    plt.show()
else:
    plt.savefig(output)
