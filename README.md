# OCRwatch
Using OCR to track team performance in Overwatch 2

## How it works
While this app is running, it listens for key presses of `Tab` and takes a screenshot of the scoreboard if it's held for more than 0.5 seconds.  
It then applies OCR on that screen, including mode and map info, which hero you're playing and stats of you and other players in your game (kills, deaths, healing, etc.) and saves that data.

![image](https://user-images.githubusercontent.com/6525296/199619575-3fd903cf-c10d-42b0-882f-e35f388b66b7.png)



![image](https://user-images.githubusercontent.com/6525296/199619556-92f26629-4d76-48b0-9b1c-aa7aa874069e.png)



[Example Dashboard](https://gist.github.com/InventivetalentDev/03b64b8fe516d86cebd2d1f3405c57cc)

## Setup
```
pip install -r requirements.txt
```

Rename `config.example.ini` to `config.ini` and adjust the settings


## Usage
```
python tracker.py
```

Launch Overwatch, play some games and remember to press Tab a couple of times! (you're probably doing that anyway)  
You might want to keep the console window open on a second screen to take a look at the results.  
Note: this currently only supports 16:9 aspect ratios, since the screen coordinates of the ingame UI elements are based on a 1920x1080 display.
