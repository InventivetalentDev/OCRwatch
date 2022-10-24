# OCRwatch
Using OCR to track team performance in Overwatch 2

## How it works
While this app is running, it listens for key presses of `Tab` and takes a screenshot of the scoreboard if it's held for more than 0.5 seconds.  
It then applies OCR on that screen, including mode and map info, which hero you're playing and stats of you and other players in your game (kills, deaths, healing, etc.) and saves that data.
