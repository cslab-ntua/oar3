# Find moldable instance with minimum (walltime*cores) product.
# If two or more instances have the same product, keep them all. Internal scheduler will make the final choice (by minimum ending time).
# Note: After applying rule 19_policies.py, all resource requests come in the form of -l core.

# Author: Alexis Papavasileiou

prev = 2**32 - 1
sofar = []

for rq in resource_request:

    (rq_list, wt) = rq
    res = rq_list[0]['resources']

    if res[0]['value'] * wt < prev:
        prev = res[0]['value'] * wt
        sofar = [rq]
    elif res[0]['value'] * wt == prev:
        sofar.append(rq)

resource_request = sofar

logger.info(str(resource_request))
