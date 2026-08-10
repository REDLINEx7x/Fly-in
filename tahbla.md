lkhdma na9ssa

---
The exclude set was designed for an earlier approach where, after finding the first path, you would re-run Dijkstra while excluding zones already used by that path — to find a second disjoint path for the second drone.

But that approach was abandoned because it fails on maps with shared chokepoints — for example a loop map where loop_a and exit_point are required by every possible route. Excluding them after path 1 blocks all future searches entirely.

---
