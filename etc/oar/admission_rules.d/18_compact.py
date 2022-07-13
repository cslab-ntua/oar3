import math

if 'compact' in types:

    resource_set = ResourceSet()
    resources_itvs = resource_set.roid_itvs
    logger.info(str(vars(resource_set)))
    
    for mold in resource_request:
        (resource_desc_list, _) = mold
        for resource_desc in resource_desc_list:
            
            hy_levels = []
            hy_nbs = []
            resource_value_lst = resource_desc['resources']
            
            for resource_value in resource_value_lst:
                hy_levels.append(resource_set.hierarchy[resource_value["resource"]])
                hy_nbs.append(int(resource_value["value"]))
            
            res_itvs = find_resource_hierarchies_scattered(resources_itvs, hy_levels, hy_nbs)
            cores = len(res_itvs)
            
            # Works for homogeneous clusters.
            cores_per_node = len(resource_set.hierarchy['network_address'][0])

            nodes = math.ceil(cores / cores_per_node)
            resource_desc['resources'] = [{'resource': 'network_address', 'value': nodes}]
