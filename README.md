# OCRwatch
Using OCR to track team performance in Overwatch 2

## How it works
While this app is running, it listens for key presses of `Tab` and takes a screenshot of the scoreboard if it's held for more than 0.5 seconds.  
It then applies OCR on that screen, including mode and map info, which hero you're playing and stats of you and other players in your game (kills, deaths, healing, etc.) and saves that data.

![image](https://user-images.githubusercontent.com/6525296/197821711-60773e50-ae40-4565-9970-436d10cbce9f.png)


![image](https://user-images.githubusercontent.com/6525296/197821504-7d1cf908-e92b-48ac-a902-02763f6b319d.png)


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