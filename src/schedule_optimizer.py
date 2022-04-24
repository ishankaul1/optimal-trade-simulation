import math

import actions
import state
import random

from depq import DEPQ
from collections import deque

#Constant for now
RECIPROCAL_OF_BESTFRONTIER_SIZE_RATIO = 3
class Schedule_Optimizer:
    #requirements: init_state, actionable_transforms, actionable_transfers, state_quality_func, my_country, max_depth, max_frontier, num_outputs
    def __init__(self, init_state: dict, actionable_transforms: list[actions.ActionableTransform], actionable_transfers: list[actions.ActionableTransfer], state_quality_fn, my_country: str, max_depth: int, max_frontier: int, num_outputs: int, depth_penalty: float, likelihood_param: float, cost_of_failure: int ):
        self.init_state = init_state
        self.actionable_transforms = actionable_transforms
        self.actionable_transfers = actionable_transfers
        self.state_quality_fn = state_quality_fn
        self.my_country = my_country
        self.max_depth = max_depth
        self.max_frontier = max_frontier
        self.num_outputs = num_outputs
        self.state_generator = state.StateGenerator(my_country=my_country, init_state=init_state, state_quality_function=state_quality_fn, k=likelihood_param, gamma=depth_penalty, c=cost_of_failure)

        #stuff needed to start optimizing
        init_statenode = state.StateNode(state=init_state, schedule=[], schedule_likelihood=1, expected_utility=0)
        self.best_states = DEPQ(maxlen=num_outputs)

        #TODO: split into 2 frontiers; one DEPQ length 1/3 frontier size, one array length 2/3. Pop from either with probability
        #   proportional to size. We add to good frontier if FULL only if better than worst, BUT if worse frontier is full, add to it with
        #   probability 1/size. We will also RANDOMLY choose which index of the worse frontier we will replace (randint 0-size)

        self.best_frontier_size = math.floor(max_frontier / RECIPROCAL_OF_BESTFRONTIER_SIZE_RATIO)
        self.randomized_frontier_size = max_frontier - self.best_frontier_size

        self.best_frontier = DEPQ(maxlen=max_frontier)
        self.best_frontier.insert(init_statenode, init_statenode.expected_utility)
        self.randomized_frontier = deque([])

    def isBestFrontierFull(self) -> bool:
        return len(self.best_frontier) > self.best_frontier_size

    def isRandomizedFrontierFull(self) -> bool:
        return len(self.randomized_frontier) > self.randomized_frontier_size

    def bothFrontiersEmpty(self):
        return len(self.randomized_frontier) == 0 and len(self.best_frontier) == 0

    def isRandomizedFrontierEmpty(self):
        return len(self.randomized_frontier) == 0

    def isBestFrontierEmpty(self):
        return len(self.best_frontier) == 0

    def randomlyPopFromOneOfTheFrontiers(self):
        if self.bothFrontiersEmpty():
            return None
        elif self.isRandomizedFrontierEmpty():
            self.best_frontier.popfirst()
        elif self.isBestFrontierEmpty():
            return self.randomized_frontier.pop()
        rint = random.randint(1, RECIPROCAL_OF_BESTFRONTIER_SIZE_RATIO)
        if rint == 1:
            return self.best_frontier.popfirst()
        else:
            return self.randomized_frontier.pop()

    #Called when both frontiers are full, and the node doesn't belong in the best frontier
    def performRandomizedInsert(self, newState: state.StateNode):
        #step 1: decide if we're even going to put this node in.
        # TODO: experiment with the probability function of whether we choose to add this node
        randomFactor = random.randint(1, self.max_frontier)
        if randomFactor == 1:
            self.insertIntoRandomIndex(newState)
        else:
            del newState

    def insertIntoRandomIndex(self, newState: state.StateNode):
        randomIndex = random.randint(0, self.randomized_frontier_size-1)
        self.randomized_frontier[randomIndex] = newState


    def tryInsertStateToFrontiers(self, newState: state.StateNode):
        #TODO: We add to good frontier if FULL only if better than worst. If not full, just add it? BUT if worse frontier is full, add to it with
        #   probability 1/size. We will also RANDOMLY choose which index of the worse frontier we will replace (randint 0-size)
        #Step 1: if good frontier not full, just add
        if not self.isBestFrontierFull():
            self.best_frontier.insert(newState, newState.expected_utility)
        elif not self.isRandomizedFrontierFull():
            self.randomized_frontier.appendleft(newState)
        else:
            #both are full. Now check if we need to replace anything in best frontier
            if newState.expected_utility > self.best_frontier.low():
                self.best_frontier.insert(newState, newState.expected_utility)
            else:
                #try inserting into randomized frontier
                self.performRandomizedInsert(newState)

    def findschedules(self) -> list: #list of schedules & utilities; i never made a data type for it (hehe)
        while not (self.isBestFrontierEmpty() and self.isRandomizedFrontierEmpty()):
            curStateNode = self.randomlyPopFromOneOfTheFrontiers()
            if curStateNode is None:
                print('Should not reach here; why is it none?')
                break
            self.generatesuccessors(curStateNode)

        #loop done; convert best_output states into schedules
        return self.extractschedulesfrombeststates()

    def generatesuccessors(self, statenode: state.StateNode):
        #don't generate at depth level
        if len(statenode.schedule) >= self.max_depth:
            return
        self.generatesuccessorsfromlistofactions(statenode=statenode, actions=self.actionable_transforms)
        self.generatesuccessorsfromlistofactions(statenode=statenode, actions=self.actionable_transfers)

    #TODO: IMPLEMENT WITH UPDATED FRONTIERS AND INSERT (tryInsertStateToFrontiers) FUNCTIONS; SHOULD BE STRAIGHTFORWARD
    def generatesuccessorsfromlistofactions(self, statenode: state.StateNode, actions: list[actions.Action]):
        for action in actions:
            scalar = 1
            while self.state_generator.isvalidactionforstate(action=action, statenode=statenode, scalar=scalar):
                newstate = self.state_generator.buildNewStateFromAction(transaction=action, init_state=statenode,
                                                                        scalar=scalar)
                #debug logs
                # print('frontier len: ', str(len(self.frontier)))
                # print('best states: ', str(len(self.best_states)))
                # print(len(newstate.schedule))
                # print(newstate.expected_utility)

                deleteGeneratedState = True
                if len(newstate.schedule) <= self.max_depth:
                    #totally disregard if not less than the max depth. we shouldn't even hit this case really
                    if len(self.frontier) < self.max_frontier or (newstate.expected_utility > self.frontier.low()):
                        #if frontier not yet full or the new state is better than the worst of the frontier, insert in frontier and dont delete from mem
                        #can mess with this logic to expand search space - may need to shy away from usage of the depq
                        self.frontier.insert(newstate, newstate.expected_utility)
                        deleteGeneratedState = False
                    if len(self.best_states) < self.num_outputs or newstate.expected_utility > self.best_states.low():
                        #don't add to output states unless better than worst output state
                        self.best_states.insert(newstate, newstate.expected_utility)
                        deleteGeneratedState = False
                if deleteGeneratedState:
                    del newstate #lol memory management in Python :P
                scalar = scalar + 1


    def extractschedulesfrombeststates(self) -> list:
        schedules = []
        for stateutilitypair in self.best_states:
            schedules.append((stateutilitypair[0].schedule, stateutilitypair[1]))

        return schedules







