if 'no-preference' in types:

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

    acc = []

    for mold in resource_request:
        (resource_desc_list, wt) = mold
        for resource_desc in resource_desc_list:
            cores = findcores(resource_desc['resources']) 
            cores += cores % 2
            
            new_mold = ([{'property': resource_desc['property'] , 'resources': [{'resource': 'core', 'value': cores}]}], wt)
            acc.append(new_mold)
            
            prop = 'halfcpu < 0'
            if resource_desc['property']:
                prop += ' ' + 'and' + ' ' + resource_desc['property']
            resource_desc['property'] = prop
            resource_desc['resources'] = [{'resource': 'core', 'value': cores}]

    resource_request += acc
