#!/bin/sh

trials=("1" "2" "3")
states2=("4" "5")

# frontier size experiment - might need to edit sizes and choose depths based on performance from depth exp
# frontierSizes=("5" "15" "30" "50" "100")
# for s in ${states2[@]}
# do
#     for f in ${frontierSizes[@]}
#     do
#         for t in ${trials[@]}
#         do
#             python3 schedule_driver.py "../input-states/test_state_${s}.csv" ../input-resource-weights/test_resource_weights_1.csv ../input-transforms/input_transforms1.json "../output/randomandbeststatefrontier_results/experiment_frontiersize_results/fs${f}-r${t}-s${s}.txt" X1 3 15 $f 0.99 0.3 -1
#         done
#     done
# done


# #depth experiment
# depths=("1" "2" "3" "4" "5" "6" "7" "8")
# trials=("1" "2" "3" "4" "5")
# for s in ${states2[@]}
# do
#     for d in ${depths[@]}
#     do
#         for t in ${trials[@]}
#         do
#             python3 schedule_driver.py "../input-states/test_state_${s}.csv" ../input-resource-weights/test_resource_weights_1.csv ../input-transforms/input_transforms1.json "../output/randomandbeststatefrontier_results/experiment_depth_results/d${d}-r${t}-s${s}.txt" X1 $d 15 15 0.99 0.3 -1
#         done
#     done
# done

# initstate experiment
# states=("1" "2" "3" "4" "5")
# for s in ${states[@]}
# do
#     for t in ${trials[@]}
#     do
#         python3 schedule_driver.py "../input-states/test_state_${s}.csv" ../input-resource-weights/test_resource_weights_1.csv ../input-transforms/input_transforms1.json "../output/randomandbeststatefrontier_results/experiment_initstate_results/state${s}-r${t}.txt" X1 3 15 50 0.99 0.3 -1
#     done
# done

# #k experiment
# #initstate experiment
# ks=("0.01" "0.1" "0.3" "0.5" "1" "2" "5")
# states2=("4" "5")
# for s in ${states2[@]}
# do
#     for k in ${ks[@]}
#     do
#         for t in ${trials[@]}
#         do
#             python3 schedule_driver.py "../input-states/test_state_${s}.csv" ../input-resource-weights/test_resource_weights_1.csv ../input-transforms/input_transforms1.json "../output/randomandbeststatefrontier_results/experiment_k_results/k${k}-r${t}s${s}.txt" X1 5 15 50 0.99 $k -1
#         done
#     done
# done


#gamma experiment

gs=("0.99" "0.9" "0.75")
states2=("4" "5")
for s in ${states2[@]}
do
    for g in ${gs[@]}
    do
        for t in ${trials[@]}
        do
            python3 schedule_driver.py "../input-states/test_state_${s}.csv" ../input-resource-weights/test_resource_weights_1.csv ../input-transforms/input_transforms1.json "../output/randomandbeststatefrontier_results/experiment_gamma_results/g${g}-r${t}s${s}.txt" X1 5 15 50 $g 1 -1
        done
    done
done
