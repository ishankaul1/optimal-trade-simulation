# optimal-trade-simulation

Simulates a world with several different actors competing for resources, with configurable amounts of available resources.
Then, runs a state space search over possible actions, attempting to find an optimal path.

I ran several tests to figure out what configuration worked best; TLDR is that a best space frontier combined with random walk worked pretty well.

## Source Code
All of the source code is located in the 'src/' directory. The top-level function is schedule_driver.py, which takes in all required input filename and parameters, runs the schedule optimizer, and writes to output files.
Usage of schedule_driver.py from the command line (assuming you are already in the src/ directory) is as follows:

```
python3 schedule_driver.py <initial state filepath> <resource weight filepath> <transforms_filepath> <output schedule filepath> <optimizing country name> <max depth> <# output schedules> <maximum frontier size> <gamma> <k> <c>
```

Example command that I actually used to run one of my tests, using the input files in this repository:

```
python3 schedule_driver.py ../input-states/test_state_5.csv ../input-resource-weights/test_resource_weights_1.csv ../input-transforms/input_transforms1.json ../output/experiment_initstate_results/state5.out X1 5 15 15 0.99 0.3 -1
```

In addition, the src directory now contains a file 'experiment.sh'. It is a bash script which will run all experiments associated with the project. I run it on my Mac as 'sh experiment.sh' from the src directory.

To shortly summarize the logic flow, schedule_driver creates one instance of Schedule_Optimizer from schedule_optimizer.py, initialized based on the inputs to the driver. This optimizer contains all the main logic for the search algorithm and generation of successors.

'state.py' contains the StateNode and PersistedState data structures, as well a StateGenerator class that does most of the heavy lifting for calculating new states, utilities, etc.

'actions.py' contains a bunch of data structures and classes that I used for creating transform and transfer templates, converting them to performable actions in the program, and finally persisting information in the schedules.

'state_quality.py' contains a couple possible state quality functions; the more interesting one is 'state_quality_realistic()'

'sigmoid_activation.py' contains my implementation of the sigmoid activation function, and solution_writer is just a helper function for creating a massive string that summarizes the schedule outputs.

The directory 'test/' contains some unit tests I used for some of the lower level logic surrounding states and actions at the early stages of the project.

## Video and Powerpoint
Located in the 'presentation_and_powerpoint/' directory. Video is a text file link in 'video.txt', powerpoint is 'Presentation1.pptx' file.

## Input Files
I organized my input files by directory.
'input-states' contains different initial state files I used for experiments in CSV format.
'input-transforms' contains the transform file I used, in JSON format.
'input-resource-weights' contains a csv with 'weights' for each resource that I used for trades in my game world. The weights really represent the value of each resource (or cost of waste) with respect to some global currency, to make logic around trading easier. This is explained in more detail in the video/slides. The file is in CSV format.

## Output Files
All output files for my experiment are located in the 'output/' directory. The outputs for each experiment are organized by sub-directory.
'output/experiment_depth_results' contains all output files for my depth experiment.
'output/experiment_frontiersize_results' contains all output files for my frontier size experiment.
'output/experiment_initstate_results' contains all output files for my initial state experiment.
Experiments are explained in more detail in the Test Case Summary.
