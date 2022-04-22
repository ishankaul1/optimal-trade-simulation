import actions
import state

from depq import DEPQ

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
        self.frontier = DEPQ(maxlen=max_frontier)
        self.frontier.insert(init_statenode, init_statenode.expected_utility)

    def findschedules(self) -> list: #list of schedules & utilities; i never made a data type for it (hehe)
        while len(self.frontier) > 0:
            curstatenode = self.frontier.popfirst()[0]
            self.generatesuccessors(curstatenode) #implement

        #loop done; convert best_output states into schedules
        return self.extractschedulesfrombeststates()

    def generatesuccessors(self, statenode: state.StateNode):
        #don't generate at depth level
        if len(statenode.schedule) >= self.max_depth:
            return
        self.generatesuccessorsfromlistofactions(statenode=statenode, actions=self.actionable_transforms)
        self.generatesuccessorsfromlistofactions(statenode=statenode, actions=self.actionable_transfers)

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







