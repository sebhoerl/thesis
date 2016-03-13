import sys, sqlite3, pickle
import numpy as np

if len(sys.argv) < 5:
    print('create_mode_matrix.py database output_path source_suffix target_suffix')
    exit()

connection = sqlite3.connect(sys.argv[1])
cursor = connection.cursor()

output_path = sys.argv[2]
source_suffix, target_suffix = sys.argv[3:5]

source_table = 'population' if len(source_suffix) == 0 else 'population_%s' % source_suffix
target_table = 'population' if len(target_suffix) == 0 else 'population_%s' % target_suffix

# Find all available modes in the data set
modes = cursor.execute("""
    select first_leg from (select first_leg from %s
    union
    select first_leg from %s) group by first_leg
""" % (source_table, target_table))

modes = np.array(modes.fetchall()).flatten().tolist()

# Find the shares in the source set
result = cursor.execute("""
select first_leg, count(*) from %s group by first_leg
""" % source_table)

initial = { row[0] : row[1] for row in result }

# Find the shares in the target set
result = cursor.execute("""
select first_leg, count(*) from %s group by first_leg
""" % target_table)

final = { row[0] : row[1] for row in result }

# Find the transitions from one mode to the other
result = cursor.execute("""
    select source.first_leg as source_mode, target.first_leg, count(*) as target_mode
    from %s as source inner join %s as target on source.id = target.id
    group by source.first_leg, target.first_leg
""" % (source_table, target_table))

matrix = np.zeros((len(modes),) * 2)

for row in result:
    matrix[modes.index(row[0]), modes.index(row[1])] = float(row[2])

loss_matrix = np.copy(matrix).T
gain_matrix = np.copy(matrix)

# Normalize the matrices for better comparison of values
for i in range(len(modes)):
    loss_matrix[:,i] /= (initial[modes[i]] if modes[i] in initial else 1)
    gain_matrix[:,i] /= (final[modes[i]] if modes[i] in final else 1)

if output_path != '-':
    with open(output_path, 'wb+') as f: pickle.dump((matrix, loss_matrix, gain_matrix),f)

# Just markdown printing from here on!

result = ''

labels = {
    'av': 'AV',
    'car': 'Car',
    'transit_walk': 'PT',
    'walk': 'Walk'
}

for i in range(len(modes)):
    modes[i] = labels[modes[i]]

for y in range(len(modes) + 1):
    if y == 0:
        result += '|' + '|'.join([' '] + modes) + '|\n'
        result += '|' + '---:|' * (len(modes) + 1)
    elif modes[y-1] == 'AV': continue
    else:
        result += '|'
        for x in range(len(modes) + 1):
            if x == 0:
                result += '**' + modes[y-1] + '** |'
            else:
                result += '%.2f%%|' % (loss_matrix[x-1,y-1] * 100)

    result += '\n'

if output_path != '-':
    path = output_path + '.destination.md'
    with open(path, 'w+') as f: f.write(result)
else:
    print(result)

result = ''

for y in range(len(modes) + 1):
    if y == 0:
        result += '|' + '|'.join([' '] + [mode for mode in modes if mode != 'AV']) + '|\n'
        result += '|' + '---:|' * (len(modes) + 1)
    else:
        result += '|'
        for x in range(len(modes) + 1):
            if modes[x-1] == 'AV':
                continue
            if x == 0:
                result += '**' + modes[y-1] + '** |'
            else:
                result += '%.2f%%|' % (gain_matrix[x-1,y-1] * 100)

    result += '\n'

if output_path != '-':
    path = output_path + '.origin.md'
    with open(path, 'w+') as f: f.write(result)
else:
    print(result)
