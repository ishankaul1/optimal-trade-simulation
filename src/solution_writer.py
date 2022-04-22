#really just prints our solutions in a helper func
import state

def toScheduleString(schedule: list[state.PersistedState], utility: float):
    header = 'SCHEDULE\n---------\n\tFinal EU: {}\n\tActions:\n'.format(str(utility))
    schedulestr = ''
    for st in schedule:
        schedulestr = schedulestr + (st.toString())
    return header + schedulestr

def toAllScheduleString(results: list):
    final = ''
    for r in results:
        final = final + toScheduleString(r[0], r[1])
    return final