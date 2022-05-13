---
title: ""
---

## Overview
---
> *Love taking Amtrak?*<br>
> *Bought a Rail Pass?*<br>
> *Having trouble creating an itinerary?*

Look no further than the Amtrak Rail Planner. Built because I was in that very situation, it performs the legwork of searching for you and compiles all the trains in one, neat table. Specific train segments can be saved to your itinerary, which will be exported to a spreadsheet once you're happy with the trip.

### Abstract

Traveling by Amtrak train with a Rail Pass is a cost-efficient way to see the country in one month, but planning the trip can be a time-consuming process, due to the limitations of the Amtrak website. The Amtrak Rail Planner will provide travelers an easy way to formulate their multi-segment journey to any of the destinations served by train in the United States. The manual process of searching Amtrak's website for each travel leg and inputting information into an itinerary spreadsheet will be eliminated. Novel features include “click once” searching on Amtrak’s site, archival of previous searches for potential reference later, displaying multiple pages of results in a single list, links to relevant train maps, and photo displays of each selected cities. This Python application provides an efficient and easy way to search for trains and create a travel itinerary which can be exported to a file.

### Motivation

I was taking a cross-country trip with the Rail Pass, with less than three weeks to do it, and had multiple routes I wanted to try. Searching Amtrak's site required me to input all train information into a spreadsheet so I could consult it later. This was a slow, tedious process, and I set out to create a simpler way to accomplish this.

## Notes
---
### Paper
You can read the initial paper regarding the application design and structure [here](https://github.com/nalvarez508/amtrak-rail-planner/raw/master/Rail%20Planner.pdf).

### License
Licensed under GNU General Public License v3. Read it - sure - but here's what I want you to take away: If you want to package it with something, credit the project and include the source, as mentioned. You want to improve it? Awesome, create a pull request so we can all benefit.

Basically, it's a side project, but it's still my work.

### Issues with App
If there are problems with running the application, please submit an issue. I cannot test for everything but tried to make it as resilient as possible during normal use.

The most common thing I would expect to see is Amtrak blocking the underlying search feature (a web scraper), which would break the application. At that point, I might investigate loading timetables into the app and attempting to "search" manually.

### Future Work
Lots of you have reached out with suggestions for the application. That's great!  
However, I cannot necessarily implement them all, as much as I would love to. This may be due to a technical roadblock, infeasability, or lack of public interest. I'm still a college student with other things to keep up on, and this was always a side project for me.

With that being said, here are some suggestions I've received.
- Accessible timetables for each route
- App schedules with layovers/connections in mind
- Train filtering during search*
- Note-taking area for each train in itinerary window
- Map displaying markers for origin/destination and route*
- Station info
  - Attractions in destination cities
  - Places to eat
  - Availability of parking
  - Transit connections/routes served
  - Hotels
  - In-station amenities
  - Distance to final location
- Train info
  - Number and names of stops along a route*
  - Amenities on-board*
  - On-time performance, or if prone to delays
  
\* seems possible based on what I've found