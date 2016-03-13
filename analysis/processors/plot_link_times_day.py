import subprocess
import tempfile
import pathlib
import sys, os

if len(sys.argv) < 4:
    print('plot_legdist.py database suffix output')
    exit()

source = str(pathlib.Path(sys.argv[1]).resolve())
suffix = sys.argv[2]
output = sys.argv[3]

script = os.path.dirname(os.path.abspath(__file__)) + '/plot_link_times.py'
directory = tempfile.mkdtemp()

interval = 1

for i in range(6, 23, interval):
    start_time = '%02d:00:00' % i
    end_time = '%02d:00:00' % (i+interval)
    print('%s to %s' % (start_time, end_time))
    subprocess.call(['python3', script, sys.argv[1], sys.argv[2], start_time, end_time, directory + '/%02d.png' % i])

subprocess.call(['convert', '-delay', '100', '-loop', '0', directory + '/*.png', output])
