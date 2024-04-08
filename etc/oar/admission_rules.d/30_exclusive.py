if "exclusive" in types:
    import math

    resource_set = ResourceSet(session, config)
    resources_itvs = resource_set.roid_itvs

    total_nodes = len(resource_set.hierarchy["network_address"])
    total_cores = len(resource_set.hierarchy["core"])
    cores_per_node = total_cores // total_nodes

    for mld_idx, mld_resource_request in enumerate(resource_request):
        resource_desc, walltime = mld_resource_request
        for prop_res in resource_desc:
            for resource_value in prop_res["resources"]:
                if resource_value["resource"] == "core":
                    resource_value["resource"] = "network_address"
                    resource_value["value"] = str(
                        math.ceil(float(resource_value["value"]) / cores_per_node)
                    )
