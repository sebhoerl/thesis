import sqlite3, sys
import pathlib, pickle
import numpy as np
import matplotlib.pyplot as plt
import util

if len(sys.argv) < 6:
    print('plot_legdist.py database suffix starttime endtime output')
    exit()

source = str(pathlib.Path(sys.argv[1]).resolve())
suffix = sys.argv[2]
start_time = float(np.dot(np.array([int(d) for d in sys.argv[3].split(':')]), np.array([3600, 60, 1])))
end_time = float(np.dot(np.array([int(d) for d in sys.argv[4].split(':')]), np.array([3600, 60, 1])))
output = sys.argv[5]

connection = sqlite3.connect(source)
cursor = connection.cursor()

data = np.array(cursor.execute("""
    select
        links.id,
        avg(leave_time - enter_time),
        fromnode.x + (tonode.x - fromnode.x) / 2 as x,
        fromnode.y + (tonode.y - fromnode.y) / 2 as y
    from links
    inner join nodes as fromnode on links.from_id = fromnode.id
    inner join nodes as tonode on links.to_id = tonode.id
    left join link_times_%s as link_times on link_times.link = links.id
    where enter_time >= ? and leave_time <= ?
    group by links.id
""" % (suffix), (start_time, end_time)).fetchall())[:,1:].astype(np.float)

plt.figure()
plt.scatter(data[:,1], data[:,2], s = data[:,0] / 500 * 1000, c = data[:,0], vmin = 0, vmax = 1000, cmap = plt.get_cmap('summer'))

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
plt.title('%s to %s' % (sys.argv[3], sys.argv[4]))

if output == '-':
    plt.show()
else:
    plt.savefig(output)
