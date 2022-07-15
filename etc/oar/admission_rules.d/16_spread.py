if 'spread' in types:

    acc = []
    resource_set = ResourceSet()
    resources_itvs = resource_set.roid_itvs

    for mold in resource_request:
        (resource_desc_list, wt) = mold
        for resource_desc in resource_desc_list:
            
            hy_levels = []
            hy_nbs = []
            resource_value_lst = resource_desc['resources']

            for resource_value in resource_value_lst:
                hy_levels.append(resource_set.hierarchy[resource_value["resource"]])
                hy_nbs.append(int(resource_value["value"]))
            
            res_itvs = find_resource_hierarchies_scattered(resources_itvs, hy_levels, hy_nbs)

            cores = len(res_itvs)
            cores += cores % 2
            
            prop = 'halfcpu > 0'
            if resource_desc['property']:
                prop += ' ' + 'and' + ' ' + resource_desc['property']
            
            resource_desc['property'] = prop
            resource_desc['resources'] = [{'resource': 'core', 'value': cores}]
            
            new_mold = ([{'property': prop.replace('>', '<') , 'resources': [{'resource': 'core', 'value': cores}]}], wt)
            acc.append(new_mold)

    resource_request += acc
