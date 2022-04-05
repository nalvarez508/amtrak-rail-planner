---
layout: page
title: "Home"
---

# Overview
---
> *Love taking Amtrak?*
> *Bought a Rail Pass?*
> *Having trouble creating an itinerary?*

Look no further than the Amtrak Rail Planner. Built because I was in that very situation, it performs the legwork of searching for you and compiles all the trains in one, neat table. Specific train segments can be saved to your itinerary, which will be exported to a spreadsheet once you're happy with the trip.

## Abstract

Traveling by train with a Rail Pass is a cost-efficient way to see the country in one month but planning the trip can be a time-consuming process. The Amtrak Rail Pass Assistant will provide travelers an easy way to plan their ten-segment journey to any of the destinations served by train in the United States. Manual work of searching the Amtrak website and inputting information into a spreadsheet will be eliminated. The Python application provides an efficient and easy way to create a travel itinerary which can be exported later. Novel features include full results in one list instead of pages, details of each train in the resulting spreadsheet, and pictures of each selected city in the search.

# Installation and Requirements
---
What's needed:
- Windows/MacOS system (Linux will need to run source code, see readme)
- Google Chrome (just needs to be installed on the computer)

Download the OS-specific zipfile from the Releases page, it's packaged inside. Store the executable wherever is convenient and launch it. If there are issues with launching it, please create an issue and I can try to investigate.

# Usage

## Main Window
---
This is where most work will be done in the app.
### Stations
Origin and destination lists are presented on the left and right. Every *train* station in Amtrak's network is listed here. To search, type something in the box and hit enter. The Swap button will flip the origin and destination locations.

### Date selection
Click on "Select Departure Date" or the currently listed date to open the calendar selection area. Selecting a date will close the calendar. Alternatively, click either of the two aforementioned buttons to close the calendar. You may increment the date by one with the plus and minus buttons.

### Finding trains
Click "Find Trains" to initiate a search. A progress bar will appear, and the status bar at the bottom of the window will reflect the current action.

### Viewing results
Once a search is successful, all results will be displayed in the table below the current search header. Selecting a specific train will enable the "Save Segment" button, which, when clicked, will save that train to your itinerary.

## Itinerary
---
View your saved segments here.

### Editing segments
Buttons below the table allow you to delete or reorder segments. Additionally, the search results button will bring up *that segment's* search with itself and any other trains found.

### Exporting the itinerary
Click the export button to bring up a file dialog box, asking where to save the output.

## Settings and Menu Elements
---
Here, there is some additional functionality.
### File

Import: Load a previously generated itinerary file.

Export: Save your current itinerary to a file.

### Edit
Display Columns: Change which train attributes are present in the results and itinerary tables.

### View
Current Itinerary: Open the itinerary window.

Route Map: Load the PDF of Amtrak's system map.

On-Time Performance: Inspect OTP data from Amtrak and the Bureau of Transportation Statistics.

### Status
See a live map of all Amtrak trains nationwide or for a specific region.

### Help
About: See application version information.

Github: Open the source code for the app.