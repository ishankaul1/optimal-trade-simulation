#Module to hold all logic for representing and generating states, as well as doing calculations around state generation.

from functools import total_ordering
from typing import Callable
import copy
import actions
#rom actions import Actionable_Transfer, Actionable_Transform
import actions
import sigmoid_activation


#Data structure specifically used in writing output schedules, to represent information about the state and state quality in
#a schedule's history WITHOUT having to refer to the entire state
class PersistedState:
    def __init__(self, persisted_action: actions.PersistableAction, schedule_likelihood: float, discounted_reward: float, expected_utility: float):
        self.persisted_action = persisted_action
        self.schedule_likelihood = schedule_likelihood
        self.discounted_reward = discounted_reward
        self.expected_utility = expected_utility

    def toString(self):
        output_str = self.persisted_action.toString()
        output_str = output_str + "\t\t\tStatistics: (Reward: {}, Likelihood: {}, Exp_Utility: {}\n".format(self.discounted_reward, self.schedule_likelihood, self.expected_utility)
        return output_str

#Just use to hold and get information about the state that needs to be memoized
@total_ordering
class StateNode:
    def __init__(self, state: dict, schedule: list[PersistedState], schedule_likelihood: float, expected_utility: float):
        self.state = state
        self.schedule = schedule
        self.schedule_likelihood = schedule_likelihood
        self.expected_utility = expected_utility

    #need ordering for priority queueing
    def __lt__(self, other):
        return self.expected_utility < other.expected_utility

    def __eq__(self, other):
        return self.expected_utility == other.expected_utility

    #safely copy state st operations on the new copy will not affect the old state
    def __copy__(self):
        return StateNode(state=copy.deepcopy(self.state), schedule=copy.deepcopy(self.schedule), schedule_likelihood=self.schedule_likelihood, expected_utility=self.expected_utility)

    # def toScheduleString(self):
    #     scheduleStr = ""
    #     for x in self.schedule:
    #         scheduleStr = scheduleStr + x.toString() + ', '
    #
    #     return scheduleStr[:-2]

    def debug(self):
        print('State:')
        print(self.state)
        print('\nschedule:')
        print(self.toScheduleString())
        print('\nlikelihood: ' + str(self.schedule_likelihood))
        print('\nexpected_utility: ' + str(self.expected_utility))




#All functionality for creating a new state node from a state and transaction
#Is a static, one-use object
class StateGenerator:
    #Initial state - state of the world at the very beginning. Used to calculate initial state qualities for later discounted reward calculation.
    #State quality function - takes in a dict of {resouce: value} mappings for ONE country, and outputs an int that represents the quality of the state for that country.
    def __init__(self, my_country: str, init_state: dict, state_quality_function, gamma: float, k: float, c: int):
        #TODO for pure cleanliness purposes: move my_country, (maybe?) init_state, state_quality_function, k and gamma into a calculation_context object
        #Could generate k from state qual function ouput range
        if gamma < 0 or gamma > 1:
            raise Exception('Gamma must be between 0 and 1')
        if c > 0:
            raise Exception('C must be a negative number')
        self.gamma = gamma
        self.k = k
        self.my_country = my_country
        self.state_quality_function = state_quality_function
        self.c = c
        #For all state generation, we need to have access to the INITIAL utility of each country, so that we can determine
        #the final discounted reward of each transaction
        self.init_utilities: dict = self.calc_init_utilities(init_state)

    def calc_init_utilities(self, init_state: dict) -> dict:
        init_utilities = {}
        for country in init_state:
            init_utilities[country] = self.state_quality_function(init_state[country])

        return init_utilities


    # #Logic for validating a single action against a state
    def isvalidactionforstate(self, action: actions.Action, statenode: StateNode, scalar: int) -> bool:
        if isinstance(action, actions.ActionableTransfer):
            #print('recognizing transfers')
            return self.isvalidtransferforstate(action, statenode, scalar)
        elif isinstance(action, actions.ActionableTransform):
            return self.isvalidtransformforstate(action, statenode, scalar)
        return False

    def isvalidtransferforstate(self, action: actions.ActionableTransfer, statenode: StateNode, scalar: int) -> bool:
        # #TODO: add resource validation
        # print('scalar: ', str(scalar))
        # #print(action.template.resource1_amount)
        # print(action.template.resource2_amount)
        # print('Resource1:\n\tcurrent: ', str(statenode.state[action.country1][action.template.resource1]), ', required: ', str(action.template.resource1_amount * scalar))
        # print('Resource2:\n\tcurrent: ', str(statenode.state[action.country2][action.template.resource2]),
        #       ', required: ', str(action.template.resource2_amount * scalar))
        # if (action.template.resource1_amount * scalar) > statenode.state[action.country1][action.template.resource1] or (action.template.resource2_amount * scalar) > statenode.state[action.country2][action.template.resource2]:
        #     return False
        if action.template.resource1_amount > 0:
            #resource1 positive - country 1 needs enough of this resource
            if (action.template.resource1_amount * scalar) > statenode.state[action.country1][action.template.resource1]:
                return False
        else:
            #resource1 negative - country2 needs enough of this resource
            if abs(action.template.resource1_amount) * scalar > statenode.state[action.country2][action.template.resource1]:
                return False

        if action.template.resource2_amount > 0:
            # resource2 positive - country 2 needs enough of this resource
            if (action.template.resource2_amount * scalar) > statenode.state[action.country2][action.template.resource2]:
                return False
        else:
            # resource2 negative - country1 needs enough of this resource
            if abs(action.template.resource2_amount) * scalar > statenode.state[action.country1][action.template.resource2]:
                return False

        return True

    def isvalidtransformforstate(self, action: actions.ActionableTransform, statenode: StateNode, scalar: int) -> bool:
        # #TODO: add resource validation
        for resource in action.template.input_resources:
            if statenode.state[action.country][resource] < action.template.input_resources[resource] * scalar:
                return False
        return True

    # #Logic for performing a single action on a state
    def performactiononstate(self,action: actions.Action, statenode: StateNode, scalar: int ) -> StateNode:
        if isinstance(action, actions.ActionableTransfer):
            self.performtransferonnewstate(statenode=statenode, action=action, scalar=scalar)
        elif isinstance(action, actions.ActionableTransform):
            self.performtransformonnewstate(statenode=statenode, action=action, scalar=scalar)
        else:
            print("WARNING: performed null action on copied state")
        return statenode

    #Edits state with a transfer action
    def performtransferonnewstate(self, action: actions.ActionableTransfer, statenode: StateNode, scalar: int) -> StateNode:
        if action.template.resource1_amount > 0:
            #resource1 positive - country 1 gives away this resource to country 2
            statenode.state[action.country1][action.template.resource1] = statenode.state[action.country1][action.template.resource1] - (action.template.resource1_amount * scalar)
            statenode.state[action.country2][action.template.resource1] = statenode.state[action.country2][
                                                                              action.template.resource1] + (
                                                                                      action.template.resource1_amount * scalar)
        else:
            #resource1 negative - country2 gives away this resource to country1
            statenode.state[action.country2][action.template.resource1] = statenode.state[action.country2][action.template.resource1] - (abs(action.template.resource1_amount) * scalar)
            statenode.state[action.country1][action.template.resource1] = statenode.state[action.country1][
                                                                              action.template.resource1] + (
                                                                                      abs(action.template.resource1_amount) * scalar)
        if action.template.resource2_amount > 0:
            # resource2 positive - country 2 give away this resource to country1
            statenode.state[action.country2][action.template.resource2] = statenode.state[action.country2][
                                                                              action.template.resource2] - (
                                                                                      action.template.resource2_amount * scalar)
            statenode.state[action.country1][action.template.resource2] = statenode.state[action.country1][
                                                                              action.template.resource2] + (
                                                                                      action.template.resource2_amount * scalar)
        else:
            # resource2 negative - country1 gives away this resource to country2
            statenode.state[action.country1][action.template.resource2] = statenode.state[action.country1][action.template.resource2] - (abs(action.template.resource2_amount) * scalar)
            statenode.state[action.country2][action.template.resource2] = statenode.state[action.country2][
                                                                              action.template.resource2] + (
                                                                                      abs(action.template.resource2_amount) * scalar)
        return statenode

    #Edits state with a transfer action
    def performtransformonnewstate(self, action: actions.ActionableTransform, statenode: StateNode, scalar: int) -> StateNode:
        for resource in action.template.input_resources:
            statenode.state[action.country][resource] = statenode.state[action.country][resource] - (action.template.input_resources[resource] * scalar)
        for resource in action.template.output_resources:
            statenode.state[action.country][resource] = statenode.state[action.country][resource] + (action.template.output_resources[resource] * scalar)
            return statenode

    #Function takes an init state and an action. If the action is valid on the state in the current context, it creates a new statenode with the new state after performing.
    #Then, builds ALL new properties of the state (schedule, schedule likelihood, and expected utility), and returns the state.
    #Returns none if the state was invalid
    #TODO
    def buildNewStateFromAction(self, init_state: StateNode, transaction: actions.Action, scalar: int) -> StateNode or None:
        # #1. Check if action is valid (driver can do this too, might be better)
        if not self.isvalidactionforstate(action=transaction, statenode=init_state, scalar=scalar):
            return None
        #print('do we weven get here')

        # #2. Copy state, perform action, generate a new persistable action for schedule and calculations, and get your discounted reward
        newstate = copy.copy(init_state)
        self.performactiononstate(action=transaction, statenode=newstate, scalar=scalar)
        actionPersistable = transaction.convertToPersistable(scalar)
        #newstate.schedule.append(actionRecord) APPEND TO SCHEDULE LATER
        #print(len(newstate.schedule))
        my_discountedreward = self.calc_discounted_reward(state=newstate.state, country=self.my_country, depth=len(init_state.schedule)+1)

        # #3. If action was a transfer, get the discounted reward of second country to get the action likelihood. Then, multiply by
        # the newstate's current schedule_likelihood to get the new overall likelihood
        if isinstance(transaction, actions.ActionableTransfer): #likelihood only changes when another country is involved
            #print("we're stuck in the transfer loop")
            other_discountedreward = self.calc_discounted_reward(state=newstate.state, country=transaction.country2, depth=len(init_state.schedule)+1) #ASSUMPTION FOR THIS PROGRAM IS THAT COUNTRY2 IS ALWAYS THE OTHER
            action_likelihoood = self.calc_likelihood_from_reward(other_discountedreward)
            newstate.schedule_likelihood = newstate.schedule_likelihood * action_likelihoood

        # #5. Use country1 discounted reward and likelihood to calc expected utility
        newstate.expected_utility = self.calc_expectedutility(schedule_likelihood=newstate.schedule_likelihood,discounted_reward=my_discountedreward)

        # Create persisted information for the schedule
        newPersistedScheduleState = PersistedState(discounted_reward=my_discountedreward, expected_utility=newstate.expected_utility, schedule_likelihood=newstate.schedule_likelihood, persisted_action=actionPersistable)
        newstate.schedule.append(newPersistedScheduleState)
        # #Return!!
        return newstate

    def calc_expectedutility(self, schedule_likelihood, discounted_reward):
        utility_success = schedule_likelihood * discounted_reward
        utility_fail = self.c * (1 - schedule_likelihood)
        return utility_success + utility_fail

    #Calculates overall discounted reward for a state & country. Uses state quality function result of newstate, depth, and init_utility.
    #Formula:
    def calc_discounted_reward(self, state: dict, country: str, depth: int) -> float:
        init_utility = self.init_utilities[country]
        current_utility = self.state_quality_function(state[country])
        discount_factor = self.gamma ** depth
        discounted_utility = current_utility * discount_factor
        return discounted_utility - init_utility

    #Outputs [0, 1] likelihood of a country accepting a transaction based on discounted reward
    def calc_likelihood_from_reward(self, discounted_reward: float) -> float:
        return sigmoid_activation.sig(discounted_reward, self.k)

