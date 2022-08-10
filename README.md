# Vehicle-Routing-Problem
This project serves as a demonstration in solving the vehicle routing problem (VRP)

The solution here implements a convex-hull strategy with a cost-heuristic used for improved path construction.

The benefit to a convex-hull implementation is that it provides something close to what a human would draw in terms of path planning without additional algorithms for "smoothing" like 2-opt inversion. With some computational geometry on GPS coordinates, and a simple insertion sort, the result is acceptable, though not certifiably "perfect." The downside is that insertion sort is O(n^2) in time complexity, which could use quite a bit of improvement.

Overall estimated time complexity of this solution is bounded between:
O(n^3) and O(n^2), this analysis includes truck loading and route optimization.

# Academic Paper and Write-up
  - See my paper "vrp-paper.pdf" in this repository for pseudo-code and more implementation details.

  - ## Mapped Route Example (Google Earth)
    - Page 27 of the paper documents an example delivery route, mapped using Google Earth from the program output.
    - We can see clearly in the example that the program found the convex hull and inserted the inner points between its closest neighbors on the hull, forming the delivery route.
    - ![An example route mapped on Google Earth](https://github.com/justinlangley3/Vehicle-Routing-Problem/blob/Vehicle-Routing-Problem/images/route-example-google-earth.png)

# Example Program Usage
  - ## A Walkthrough
  - Disclaimer: The terminal colors here are optimized for viewing in a Linux environment. Color patterns are not great in Windows at this time.
  - 
  1) Users are greeted with a welcome message:
  - ![A welcome message](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/welcome.png)
  2) On the next screen, data must be loaded from the /data/ directory:
  - ![Loading data from files](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/data_onboarding.png)
  3) A series of loading/statistics screens are presented:
  - ![Constructing the graph](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/build-graph.png)
  - ![Computing package data](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/build-packages.png)
  - ![Statistical overview of packages for the day](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/data_statistics.png)
  - ![Optimizing delivery route](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/route_optimization.png)
  4) Afterwards, users are dropped into the CLI:
  - ![Command Line Interface](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/cli.png)
  5) From the CLI, users can search planned routes by a given truck:
  - ![Planned trips for Truck 1](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/planned-trips-truck1.png)
  7) Additionally, lookup features exist by time of day, and specific fields on a package-by-package basis. See /images/lookup-functions for example lookups by package fields. Lookup by time of day is shown here:
  - ![Package lookup functions](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/lookup-by-timeofday.png)
  8) Finally, distance information can be viewed per truck:
  - ![Distances traveled](https://raw.githubusercontent.com/justinlangley3/Vehicle-Routing-Problem/Vehicle-Routing-Problem/images/distance-traveled.png)

Example Use-Cases:
  - Small businesses providing their own delivery service
  - Medium size businesses seeking to cut fuel costs, delivery time, etc.
