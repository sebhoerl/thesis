from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import FixedLocator
import numpy as np

def format_time(secs, pos):
	hour = int(secs / 3600)
	minute = int((secs - hour * 3600) / 60)

	return '%02d:%02d' % (hour, minute)

def format_time_axis(ax, start, end, interval):
    ax.xaxis.set_major_formatter(FuncFormatter(format_time))

    locs = np.arange(int(start / interval), int(end / interval) + 1) * interval
    ax.xaxis.set_major_locator(FixedLocator(locs))
