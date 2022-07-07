# Modify user request according to the given type:
#   No-preference: Default resource allocation mechanism.

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
# The following line should also change:
#   line 66: cores += cores % 6 --> cores % (cores per cpu / 2)

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


if 'no-preference' in types:
    # Find number of cores requested by user.
    # Explicitly requested resource types are noted in the hier dictionary (resource log).
    # Skipped resource types are added from the default dictionary.
    # Eventual core number is calculated as the product of the values in the hier dictionary.
    def findcores(resource_types):
        hy = {'network_address':0, 'cpu':1, 'halfcpu':2, 'core':3}
        hier = {0:1, 1:1, 2:1, 3:1}
        default = {0:8, 1:2, 2:1, 3:4}
        max_hy = 3
        min_hy = 0
        seen = set()
        for tp in resource_types:
            seen.add(hy[tp['resource']])
            hier[hy[tp['resource']]] = int(tp['value'])
        if 2 in seen:
            default[3] //= 2
        bottom = max(seen)
        for lv in range(max_hy, min_hy, -1):
            if lv == bottom:
                break
            if lv not in seen:
                hier[lv] = default[lv]
        cores = 1
        for key in hier:
            cores *= hier[key]
        return cores

    for mold in resource_request:
        (resource_desc_list, wt) = mold
        for resource_desc in resource_desc_list:
            cores = findcores(resource_desc['resources']) 
            cores += cores % 2
            resource_desc['resources'] = [{'resource': 'core', 'value': cores}]
