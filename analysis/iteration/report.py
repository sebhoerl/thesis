import logging
from builder import *
import readers

logging.basicConfig(level = logging.DEBUG)
builder = Builder()

builder.add_task('read_network', readers.NetworkReaderTask('blabla.db', '../../data/output/sioux/output_network.xml.gz'), [])
builder.build('read_network', 24)
