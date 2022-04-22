#Runs parses input files and runs one instance of schedule_optimizer from the command line
import resource
import sys
from os import path
import csv
import json
import copy
from datetime import datetime

import solution_writer
import actions
import schedule_optimizer
import state_quality

def err(msg: str):
    print('ERROR: ' + msg)
    sys.exit(1)

usage = "python3 schedule_driver.py <initial state filepath> <resource weight filepath> <transforms_filepath> <output schedule filepath> <optimizing country name> <max depth> <# output schedules> <maximum frontier size> <gamma> <k> <c>"
#easy test: python3 schedule_driver.py ../input-states/test_state_1.csv ../input-resource-weights/test_resource_weights_1.csv ../input-transforms/input_transforms1.json pp.pp X1 3 10 30 0.99 0.3 -1

if len(sys.argv) != 12:
    print(usage)
    sys.exit(1)

state_filename, resources_filename, transforms_filename, output_filename, my_country = sys.argv[1:6]
max_depth, num_output_schedules, max_frontier_size = [int(x) for x in sys.argv[6:9]]
gamma = float(sys.argv[9])
k = float(sys.argv[10])
c = int(sys.argv[11])

#sanity check the ints
if max_depth < 1:
    print("Max depth must be a number greater than 1")
    sys.exit(1)
if num_output_schedules < 1:
    print("Number of output schedules must be a number greater than 1")
    sys.exit(1)
if max_frontier_size < 1:
    print("Max frontier size must be a number greater than 1")
    sys.exit(1)
if gamma < 0 or gamma > 1:
    print("Depth penalty must be float between 0 and 1")
    sys.exit(1)
if k < 0 or k > 1:
    #I don't actually remember if this is true; should experiment a bit
    print("Sigmoid parameter must be float between 0 and 1")
    sys.exit(1)
if c > 0:
    print("Cost of failure must be a negative value")
    sys.exit(1)


#sanity check the filepaths
if not path.isfile(state_filename):
    err("INIT STATE file '" + state_filename + "' does not exist")
elif not len(state_filename) > 4 and state_filename[-4:] == '.csv':
    err("INIT STATE file '" + state_filename + "' is not a csv")


if not path.isfile(resources_filename):
    err("RESOURCE file '" + resources_filename + "' does not exist")
elif not len(resources_filename) > 4 and resources_filename[-4:] == '.csv':
    err("RESOURCE file '" + resources_filename + "' is not a csv")

if not path.isfile(transforms_filename):
    err("RESOURCE file '" + transforms_filename + "' does not exist")
elif not len(resources_filename) > 5 and resources_filename[-5:] == '.json':
    err("TRANSFORMS file '" + transforms_filename + "' is not a csv")
    

resources_file = open(resources_filename)
state_file = open(state_filename)
transforms_file = open(transforms_filename)

#parse resources and init state
#resources: DICT {key='resource_name', val=(int)'weight'}
#init_state: DICT {key='country_name', val={key='resource_name': val=(int)current_amount}}
resources = {}
init_state = {}

#read resource file
resources_reader = csv.reader(resources_file)
resources_header = [x.strip() for x in next(resources_reader)]
resources_rows = []

for row in resources_reader:
    resources_rows.append(row)

#print(resources_header) #debug
#print(resources_rows) #debug statement

if len(resources_rows) != 1:
    err('Should only be one row in resource weight file ' + resources_filename)

#build resource dict
for i in range(len(resources_header)):
    try:
        resources[resources_header[i].strip()] = int(resources_rows[0][i])
    except:
        if resources_rows[0][i].strip() != 'x':
            err('Resource weights can only be int or "x"')
        else:
            resources[resources_header[i].strip()] = resources_rows[0][i].strip()

#print(resources) #debug

#read init state file
state_reader = csv.reader(state_file)
state_header = [x.strip() for x in next(state_reader)]
state_rows = []

for row in state_reader:
    state_rows.append(row)

#Ensure state file and resource file resources are the same
if (set(state_header[1:]) != set(resources_header)):
    err('Please ensure resources in resources file "' + resources_filename + '" and state file "' + state_filename + '" match.')

#build state dict:
for row in state_rows:
    country = row[0].strip()
    init_state[country] = {}
    for i in range(1, len(row)):
        try:
            init_state[country][state_header[i].strip()] = int(row[i].strip())
        except:
            err('Please ensure all resource state values in state input file "' + state_filename + '" are integers')
         

#sanity check - country name exists in state structure
all_countries = set(init_state.keys())
if my_country not in init_state:
    err('Please ensure ' + my_country + ' is included in the state file ' + state_filename)

#print('\n\n')
#print(init_state)

#build transforms from inputs
transforms_data = json.load(transforms_file)
raw_transforms = transforms_data['transforms']
all_transformtemplates = actions.build_transformtemplates_from_rawtransforms(raw_transforms)
#only doing transforms for your own country
all_actionabletransforms = []
for template in all_transformtemplates:
    all_actionabletransforms.append(actions.ActionableTransform(country=my_country, template=template))


#build transfers from resource weights
all_transfertemplates = actions.build_transfertemplates_from_resourceweights(resources)
#sys.exit(1) #TODO: remove
all_actionabletransfers = []
#country1 is always my_country, country2 can be any country
other_countries = all_countries.copy()
other_countries.remove(my_country)
for template in all_transfertemplates:
    for other_country in other_countries:
        all_actionabletransfers.append(actions.ActionableTransfer(template=template, country1=my_country, country2=other_country))

#Create header to write to output file
output_header = "OPTIMIZATION OUTPUT\n-----------------\n\nInit State: {}\nMy Country: {}\nParameters: (Frontier size: {}, Maximum depth {}, Output size: {}, Depth penalty(gamma): {}, Sigmoid parameter(k): {}, Cost of failure(c): {})\n".format(str(init_state), my_country, str(max_frontier_size), str(max_depth), str(num_output_schedules), str(gamma), str(k), str(c))


resources_file.close()
state_file.close()
transforms_file.close()

#initialize and run scheduler
print('ALL INPUTS INITIALIZED! BUILDING SCHEDULER')

optimizer = schedule_optimizer.Schedule_Optimizer(init_state=init_state, actionable_transforms=all_actionabletransforms, actionable_transfers=all_actionabletransfers, state_quality_fn=state_quality.state_quality_realistic, my_country=my_country, max_depth=max_depth, max_frontier=max_frontier_size, num_outputs=num_output_schedules, depth_penalty=gamma, likelihood_param=k, cost_of_failure=c)

print('RUNNING OPTIMIZATION')
starttime = datetime.now()
results = optimizer.findschedules()
runtime = (datetime.now() - starttime).total_seconds()

output_runtime = '\nOptimization Runtime (seconds): {}\n\n'.format(runtime)


print('DONE!!')

allschedulestr = "Output Schedules:\n" + solution_writer.toAllScheduleString(results)

output_file = open(output_filename, 'w')
output_file.write(output_header + output_runtime + allschedulestr)


output_file.close()


