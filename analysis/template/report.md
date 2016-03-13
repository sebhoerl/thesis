Report
======

This is the auto-generated report for comparing:

`{{ include initial_path.md }}` (Initial)

and

`{{ include final_path.md }}` (Final)

Relaxation
----------

<center>Mode choice relaxation</center>
![](relaxation.png "Mode choice relaxation")

Mode choice matrices
--------------------

**Destination matrix**

{{ include matrices.dat.destination.md }}

The left column shows the origin mode. The values given in each row state how much of the intial percentage of users of this mode have switched to another mode (columns). "How many people who were using **car** (row) before, switched to **av** (column)?"

**Origin matrix**

{{ include matrices.dat.origin.md }}

The left column shows the final chosen mode. The values given in each row show how many of the users came from which other initial mode. "Howm many people who are using **av** (row) right now, were using **car** before?"

Mode shares
------------------

<center>Initial share</center>
![](initial_share.png "Initial share")

<center>Final share</center>
![](final_share.png "Final share")

AV State Machine and Occupation
------------------

<center>All FSM states</center>
![](services_all.png "All FSM states")

<center>AV Occupation</center>
![](services_main.png "AV Occupation")

The shaded area indicates where the UNDERSUPPLY heuristic is used instead of the OVERSUPPLY strategy.


Travel times
------------------

<center>Absolute Average Travel Time</center>
![](traveltime_absolute.png "Absolute Average Travel Time")

The dotted line shows the initial scenario.

<center>Average Delta Travel Time</center>
![](traveltime_delta.png "Average Delta Travel Time")

Positive values mean longer travel times compared to the initial scenario.

AV Waiting Times
------------------

<center>Waiting times for AV</center>
![](waitingtimes.png "Waiting Times")

Distance Distribution
------------------------

<center>Average distance</center>
![](distances_absolute.png "Distance by daytime")

<center>Average distance delta</center>
![](distances_delta.png "Distance delta by daytime")

Total Distance
------------------------

<center>Total distance with and without excess pickup trips</center>
![](totaldist.png "Total Distance")

Congestion
-------------------------------

<center>Link travel time</center>
![](congestion.gif "Congestion")

Departure Distributions
-------------------------

<center>Distribution of first AV legs</center>
![](avdepartures.png "AV Distribution")

<center>Distribution of first Car legs</center>
![](cardepartures.png "Car Distribution")

Mode choice delta distributions
-------------------------------

<center>Distribution of persons who switched from PT to AV</center>
![](avtransitchange.png "PT to AV")
