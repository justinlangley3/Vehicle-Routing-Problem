# Vehicle-Routing-Problem
This project serves as a demonstration in solving the vehicle routing problem (VRP)

The solution here implements a convex-hull strategy with a cost-heuristic used for improved path construction.

The benefit to a convex-hull implementation is that it provides something close to what a human would draw in terms of path planning without additional algorithms for "smoothing" like 2-opt inversion. With some computational geometry on GPS coordinates, and a simple insertion sort, the result is acceptable, though not certifiably "perfect." The downside is that insertion sort is O(n^2) in time complexity, which could use quite a bit of improvement.

Overall estimated time complexity of this solution is bounded between:
O(n^3) and O(n^2), this analysis includes truck loading and route optimization.

See my paper "vrp-paper.pdf" in this repository for pseudo-code and more implementation details.

A walkthrough of the program:

1) Users are greeted with a welcome message: ![alt text](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/welcome.png)
2) On the next screen, data must be loaded from the /data/ directory: ![alt text](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/data_onboarding.png?raw=true)
3) A series of loading/statistics screens are presented: ![alt text](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/.png?) ![alt text](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/build-graph.png?) ![alt text](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/build-packages.png) ![alt text](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/data_statistics.png?) ![alt text](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/route_optimization.png)
4) Afterwards, users are dropped into the CLI: ![alt text](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/cli.png?raw=true)
5) From the CLI, users can search planned routes by a given truck: ![alt text](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/planned-trips-truck1.png)
6) Additionally, lookup features exist by time of day, and specific fields on a package-by-package basis. See /images/lookup-functions for example lookups by package fields.
7) Finally, distance information can be viewed per truck: ![alt text](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/distance-traveled.png)

Example Use-Cases:
  - Small businesses providing their own delivery service
  - Medium size businesses seeking to cut fuel costs
