# Modify user request according to the given type:
#   Exclusive: Select required number of cores (plus extra, to fully occupy the respective nodes).
#   Spread: Cores should satisfy halfcpu > 0.
#   Dont-care: Cores should satisfy halfcpu < 0. If these are not enough, select without restrictions (two moldable instances).
#

import math

# Right now:
#   cores per cpu = 4
#   cpu per nodes = 2
#   nodes = 8
# If these change, the file should be modified accordingly (by hand). 
# e.g. cores per cpu = 12, cpu per nodes = 2, nodes = 4. In that case:
# default = {
#   0:4,
#   1:2.
#   2:1,
#   3:12
# }
# The following lines should also change:
#   line 96: nodes, mod = divmod(cores, 2 * 12) --> nodes, mod = divmod(cores, cpu per nodes * cores per cpu)
#   line 99 cores += (24 * nodes) % cores --> cores += ((cpu per node * cores per cpu) * nodes) % cores
#   line 101: cores += cores % 6 --> cores += cores % (cores per cpu / 2) 
#   line 103: cores += cores % 6 --> cores += cores % (cores per cpu / 2)

# Similarly for the max_hy and min_hy. 
# These numbers represent the bottom (i.e. core) and top (i.e. node) hierarchy levels respectively.
# e.g. A new hierarchy level is added:
# swith --> node --> cpu -- > halfcpu --> core
# In that case:
#   min_hy = 0
#   max_hy = 4
#   hy = {
#       'switch': 0,
#       'network_address': 1,
#       'cpu': 2,
#       'halfcpu': 3,
#       'core': 4
#   }

# Author: Alexis Papavasileiou

acc = []

hy = {
        'network_address':0, 
        'cpu':1, 
        'halfcpu':2, 
        'core':3
}

max_hy = 3
min_hy = 0

for rq in resource_request:
        
    hier = {
            0:1, 
            1:1, 
            2:1, 
            3:1
    }

    default = {
            0:8,
            1:2,
            2:1,
            3:4
    }

    (rq_list, wt) = rq
    res, prop = rq_list[0]['resources'], rq_list[0]['property']
    logger.info(res)
    
    seen = set()
    for r in res:
        seen.add(hy[r['resource']])
        hier[hy[r['resource']]] = int(r['value'])

    if 2 in seen:
        default[3] //= 2

    bottom = max(seen)
    for lv in range(max_hy, min_hy, -1):
        if lv == bottom:
            break
        if lv not in seen:
            hier[lv] = default[lv]
    
    logger.info(str(hier))
    cores = 1
    for key in hier:
        cores *= hier[key]

    res.clear()
    if 'exclusive' in types:
        nodes, mod = divmod(cores, 2 * 4)
        if mod:
            nodes +=1
        cores += (8 * nodes) % cores
        res.append({'resource':'core', 'value':cores})
        new_prop = ''
    elif 'spread' in types:
        cores += cores % 2
        res.append({'resource':'core', 'value':cores})
        new_prop = 'halfcpu > 0'
    else:
        new_rq = ([{'property': prop, 'resources': [{'resource': 'core', 'value': cores}]}], wt)
        acc.append(new_rq)

        cores += cores % 2
        res.append({'resource':'core', 'value':cores})
        new_prop = 'halfcpu < 0'
    
    logger.info(str(res))
    
    if prop:
        if new_prop:
            new_prop = prop + ' ' + 'and' + ' ' + new_prop
    rq_list[0]['property'] = new_prop

for rq in acc:
    resource_request.append(rq)

logger.info(str(resource_request))
