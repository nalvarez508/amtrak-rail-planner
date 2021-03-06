---
title: "Usage"
---

## Intent
---
> You're traveling with a Rail Pass.  
> You have some idea of where you want to go, at least a start and end.  
> You're not sure how schedules would line up.

Launching the application, you select an origin and destination alongside your departure date, and start the search. Picking a train from the list that makes sense for your schedule, it's added to your itinerary. Maybe the rest of the stops are undecided, so you open the route map from the menu.  
Repeating this process for the desired number of segments, eventually you'll have a filled out itinerary. Double check the dates and times line up, and export it to a spreadsheet with your desired information. Use this itinerary to speed through ticket booking on Amtrak.

## Usage

### Main Window
---
#### Stations
Origin and destination lists are presented on the left and right. Every *train* station in Amtrak's network is listed here. To search, type something in the box and hit enter. The Swap button will flip the origin and destination locations.

#### Date selection
Click on "Select Departure Date" or the currently listed date to open the calendar selection area. Selecting a date will close the calendar. Alternatively, click either of the two aforementioned buttons to close the calendar. You may increment the date by one with the plus and minus buttons.

#### Finding trains
Click "Find Trains" to initiate a search. A progress bar will appear, and the status bar at the bottom of the window will reflect the current action.

#### Viewing results
Once a search is successful, all results will be displayed in the table below the current search header. Selecting a specific train will enable the "Save Segment" button, which, when clicked, will save that train to your itinerary.

### Itinerary
---

#### Editing segments
Buttons below the table allow you to delete or reorder segments. Additionally, the search results button will bring up *that segment's* search with itself and any other trains found.

#### Exporting the itinerary
Click the export button to bring up a file dialog box, asking where to save the output.

### Settings and Menu Elements
---
#### File

Import: Load a previously generated itinerary file.  
Export: Save your current itinerary to a file.

#### Edit
Display Columns: Change which train attributes are present in the results and itinerary tables.

#### View
Current Itinerary: Open the itinerary window.  
Route Map: Load the PDF of Amtrak's system map.  
On-Time Performance: Inspect OTP data from Amtrak and the Bureau of Transportation Statistics.

#### Status
See a live map of all Amtrak trains nationwide or for a specific region.

#### Help
About: See application version information.  
Github: Open the source code for the app.