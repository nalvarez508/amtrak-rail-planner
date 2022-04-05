# Amtrak Rail Planner
Tired of manually inputting all train search information into an Excel file when I was planning my trips, I created this app to do it for me. It's meant for use with a Rail Pass, smaller trips are probably easier on Amtrak's site.

This application is not affiliated with Amtrak in any way.

## Manual Use
If you don't want to, or can't, use the executables in the Releases area, you can run the source code yourself. Clone the repository to start.

You're going to need Python to run this, I developed it on 3.9 but it will *probably* work with 3.7+. You'll also need some modules to run it, which can be installed with `pip install -r requirements.txt` ran in the project directory.

Finally, launch it with `python3 railpass_assistant.py` or `py -3 railpass_assistant.py` for MacOS/Unix and Windows, respectively.

## Notes on Searching
Amtrak blocked the original webdriver method I used, which is why I had to include the undetected chromedriver. I am looking in to alternatives.