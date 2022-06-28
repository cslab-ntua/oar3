# Make dont-care the default job type.

# Author: Alexis Papavasileiou

exists = 0

for t in types:
    if not re.match('^(?:exclusive|spread|dont-care)$', t):
        exists = 1
        break

if not exists:
    types.append('dont-care')
