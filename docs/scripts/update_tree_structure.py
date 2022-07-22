import os
import datetime


with open(".gitignore") as fd:
    ignore_files = filter(
        lambda x: ("#" not in x) and (len(x) > 0),
        fd.read().splitlines()
    )

ignore_files = set(map(lambda x: x.rstrip("/"), ignore_files))
command = " ".join(["tree", "-I ", "\|".join(ignore_files)])
print(command)
tree = os.popen(command).read()
tree_lines = tree.split("\n")
for n in range(len(tree_lines)):
    if tree_lines[n]:
        tree_lines[n] = "    " + tree_lines[n]

tree = "\n".join(tree_lines)

document = "## Project Tree Structure, "
document += datetime.datetime.now().strftime("%B %e %Y")
document += """


## Table of Contents
- [Project Tree Structure](#project-tree-structure)
- [TODO](#todo)

## Project Tree Structure ## 
"""
document += tree
document += """

## TODO ##
* [ ] None.


*Thank you!*
"""
with open("docs/TREE_STRUCTURE.md", "w") as f:
    f.write(document)
