<h1>Automation Script to Monitor Audio Bounces and Generate Session Notes</h2>

Music producers and other creatives often work with a large number of files and projects and it can be challenging to keep track of all of them. This automation script builds on the functionality of my last automation blog post and script to help musicians keep track of their audio files by looking only at the relevant ones (most recent) and then by dynamically interacting with session notes automatically. The script uses Python and the Pygame library to play audio files and catalogue notes on the audio files in real time with timestamps that show when and where the note was made.

This script ultimately answers the question "How to randomly play audio files and take notes on them using Python".

You can find the script and try it out on my [Github](https://github.com/elliotmangini/blog-python-notetaker) and take a glance at it here before we dive into how it works.

```py
import shutil
import os
import pygame
import random
import time
import pathlib
import datetime

current_directory = os.path.dirname(os.path.abspath(__file__))  # => this is a string for the directory the script is in
cwd_as_obj = pathlib.Path(current_directory)  # => turn that string into a path obj
items = list(cwd_as_obj.iterdir())  # => list the paths inside our cwd

folder_count = 0
bounce_count = 0
found_count = 0
new_notes_count = 0

green = '\033[92m'
default = '\033[0m'
salmon = '\033[38;2;255;87;51m'
purple = '\033[95m'


discography = {}

version = "1.0"

def read_path(a_string_path):
    return a_string_path.split("/")[-1]

for item in items:
    if item.is_dir():
        folder_count = folder_count + 1

        file_to_create = f"{item}/{item.name}_Notes.txt"  # name a notes file to make (string)
        discography[file_to_create] = ""  # => Add to dictionary

        if not os.path.exists(file_to_create):  # if a notes file already exists
            print(f"No Notes File Found, Making One: {folder_count}: {file_to_create}")
            new_notes_count = new_notes_count + 1  # count it
            with open(file_to_create, "x") as f:  # make a new notes file
                f.write(f"{item.name} Notes:")  # populate it with a correct heading
                f.close()

        subitems = list(item.iterdir())

        most_recent_bounce = None
        latest_time = 0

        for subitem in subitems:  # looping through each item in each song folder
            if subitem.is_file() and str(subitem).endswith((".mp3", ".wav", ".flac", ".ogg")):
                bounce_count = bounce_count + 1

                bounce_time = float(os.stat(subitem).st_birthtime)
                if bounce_time > latest_time:
                    latest_time = bounce_time

                    most_recent_bounce = subitem

        if most_recent_bounce is not None:
            found_count = found_count + 1

            print(f"\u2705 Adding to rotation: {most_recent_bounce.name}")
            discography[file_to_create] = f"{most_recent_bounce}"
        else:
            print(f"\U0001F6A8\U0001F6A8\U0001F6A8 \n \U0001F6A8\U0001F6A8\U0001F6A8 \
            No bounces found for: {subitem.name} \
            \U0001F6A8\U0001F6A8\U0001F6A8 \n \U0001F6A8\U0001F6A8\U0001F6A8")


print(f"\n{purple}{folder_count}{default} Song Folders found in this directory.")
print(f"{new_notes_count} New Notes files were created.")
print(f"{salmon}{bounce_count}{default} Audio Bounces found within subfolders.")
print(f"{green}{found_count}{default} Newest Bounces placed into rotation.\n")

pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_volume(1)

random_notes_file = random.choice(list(discography.keys()))
random_audio_file = discography[random_notes_file]

def mark_session():
    with open(f"{random_notes_file}", "a") as f:
        f.write(f"\n{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - New Session Started w/ SpotMaster3k version {version}"
                f"\nFile playing is: {read_path(random_audio_file)}")
        f.close()

pygame.mixer.music.load(random_audio_file)

play_count = 1
commented = False

audio_length = pygame.mixer.Sound(random_audio_file).get_length()

def play_audio():
    start_time = time.time()
    
    print("\n------------------------------------------------------")
    print(f"Making Notes for: \"{purple}{read_path(random_audio_file).split('.')[0]}{default}\" \n"
          f"at: \"{read_path(random_notes_file)}.txt\"")

    pygame.mixer.music.load(random_audio_file)
    pygame.mixer.music.play()
    return start_time

    while True:
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                print("Music playback finished!")
        if not pygame.mixer.music.get_busy():
            play_audio()

start_time = play_audio()

comment_time = False

def get_time():
    absolute_timestamp = time.time() - start_time
    m, s = divmod(absolute_timestamp, 60)
    timestamp = f"{int(m)}:{int(s):02d}"
    return timestamp

while True:
    if pygame.mixer.music.get_busy():

        # check for user input
        if not comment_time:
            user_input = input(f"\n{green}Enter{default} to grab time, or {green}directly comment{default}-- or {green}command{default} (s, r): \nInput: ")

        elif comment_time:
            user_input = input(f"Comment at {comment_time}: ")
            print("")

        # store a time anytime the user does an input
        get_time()

        if user_input.lower() == "":
            comment_time = get_time()

        # user commands
        elif user_input.lower() == "s":
            print("\nSkipping to next song...")

            if commented:
                with open(f"{random_notes_file}", "a") as f:
                    f.write(f"\n{play_count} listens, skipped to next at {get_time()}.\n  ")
                    f.close()

            play_count = 1
            commented = False

            random_notes_file = random.choice(list(discography.keys()))
            random_audio_file = discography[random_notes_file]
            play_audio()

        elif user_input.lower() == "r":
            print("Restarting playback...")
            if not pygame.mixer.music.get_busy():
                play_count = play_count + 1
            pygame.mixer.music.rewind()
            play_audio()

        else:
            # write the comment to the file
            with open(f"{random_notes_file}", "a") as f:
                if not commented:
                    mark_session()
                    commented = True
                timestamp = get_time()
                if comment_time:
                    timestamp = comment_time
                print(f"\n{salmon}{timestamp} - {user_input}{default}")
                f.write(f"\n{timestamp} - {user_input}")
                f.close()
            comment_time = False



```

The script starts by importing the necessary libraries and defining several variables. The "current_directory" variable is used to identify the directory where the script is running. The "cwd_as_obj" variable converts the current directory into a path object, which makes it easier to navigate the directory structure. The "items" variable is a list of paths inside the current working directory.

The script then loops through each item in the "items" list and checks if it's a directory. If it is a directory, the script creates a notes file for it and looks for the newest audio file in the directory. If it finds an audio file, it adds it to the rotation which is held in a python dictionary. If it doesn't find an audio file, it logs an error message.

Here's the code...
```py
current_directory = os.path.dirname(os.path.abspath(__file__))  # => this is a string for the directory the script is in
cwd_as_obj = pathlib.Path(current_directory)  # => turn that string into a path obj
items = list(cwd_as_obj.iterdir())  # => list the paths inside our cwd
```

```
for item in items:
    if item.is_dir():
        folder_count = folder_count + 1

        file_to_create = f"{item}/{item.name}_Notes.txt"  # name a notes file to make (string)
        discography[file_to_create] = ""  # => Add to dictionary

        if not os.path.exists(file_to_create):  # if a notes file already exists
            print(f"No Notes File Found, Making One: {folder_count}: {file_to_create}")
            new_notes_count = new_notes_count + 1  # count it
            with open(file_to_create, "x") as f:  # make a new notes file
                f.write(f"{item.name} Notes:")  # populate it with a correct heading
                f.close()

        subitems = list(item.iterdir())

        most_recent_bounce = None
        latest_time = 0

        for subitem in subitems:  # looping through each item in each song folder
            if subitem.is_file() and str(subitem).endswith((".mp3", ".wav", ".flac", ".ogg")):
                bounce_count = bounce_count + 1

                bounce_time = float(os.stat(subitem).st_birthtime)
                if bounce_time > latest_time:
                    latest_time = bounce_time

                    most_recent_bounce = subitem

        if most_recent_bounce is not None:
            found_count = found_count + 1

            print(f"\u2705 Adding to rotation: {most_recent_bounce.name}")
            discography[file_to_create] = f"{most_recent_bounce}"
        else:
            print(f"\U0001F6A8\U0001F6A8\U0001F6A8 \n \U0001F6A8\U0001F6A8\U0001F6A8 \
            No bounces found for: {subitem.name} \
            \U0001F6A8\U0001F6A8\U0001F6A8 \n \U0001F6A8\U0001F6A8\U0001F6A8")
```

Using a few variables we print relevant information along the way and color code it in the terminal:

```py
folder_count = 0
bounce_count = 0
found_count = 0
new_notes_count = 0

green = '\033[92m'
default = '\033[0m'
salmon = '\033[38;2;255;87;51m'
purple = '\033[95m'
```

```py
print(f"\n{purple}{folder_count}{default} Song Folders found in this directory.")
print(f"{new_notes_count} New Notes files were created.")
print(f"{salmon}{bounce_count}{default} Audio Bounces found within subfolders.")
print(f"{green}{found_count}{default} Newest Bounces placed into rotation.\n")
```

The script then randomly selects an audio file from the "rotation" held in memory and plays it back using Pygame. While the audio file is playing, the user can mark the session's start and end time and add comments using the script.

```py
random_notes_file = random.choice(list(discography.keys()))
random_audio_file = discography[random_notes_file]

def mark_session():
    with open(f"{random_notes_file}", "a") as f:
        f.write(f"\n{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - New Session Started w/ SpotMaster3k version {version}"
                f"\nFile playing is: {read_path(random_audio_file)}")
        f.close()

pygame.mixer.music.load(random_audio_file)

play_count = 1
commented = False

audio_length = pygame.mixer.Sound(random_audio_file).get_length()
```

Here we are grabbing a random audio file and that file's corresponding notes and then making a first note in that notes file with information on the instance of listening that has just begun.

Below is our play function which prints to the console to make it obvious what is going on and attempts to loop the audio each time it finishes (though I don't think I was able to get that working!). Along with a helper function that gets a timestamp from the audio playing and formats it for use in the notes.

```py
def play_audio():
    start_time = time.time()
    
    print("\n------------------------------------------------------")
    print(f"Making Notes for: \"{purple}{read_path(random_audio_file).split('.')[0]}{default}\" \n"
          f"at: \"{read_path(random_notes_file)}.txt\"")

    pygame.mixer.music.load(random_audio_file)
    pygame.mixer.music.play()
    return start_time

    while True:
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                print("Music playback finished!")
        if not pygame.mixer.music.get_busy():
            play_audio()

start_time = play_audio()

comment_time = False

def get_time():
    absolute_timestamp = time.time() - start_time
    m, s = divmod(absolute_timestamp, 60)
    timestamp = f"{int(m)}:{int(s):02d}"
    return timestamp
```

There is also the comment_time value which I'm toggling between false and a string representing the time this was in the following function the user can input a comment and at the time of input we log the time in the audio, or if the user hits enter with no input (no comment) it will grab the current time in the audio and then use that when the next input is submitted containing the comment. This way if you have a comment that takes 30 seconds to type out you can still control the timestamp in the music that the comment corresponds to. Additionally if you forget to grab the time explicitly you still get to publish the comment and the script does its "best" to mark that comment with a relavent time.

So lastly here is the part of the script responsible for getting those user inputs and handling them appropriately:

```py
while True:
    if pygame.mixer.music.get_busy():

        # check for user input
        if not comment_time:
            user_input = input(f"\n{green}Enter{default} to grab time, or {green}directly comment{default}-- or {green}command{default} (s, r): \nInput: ")

        elif comment_time:
            user_input = input(f"Comment at {comment_time}: ")
            print("")

        # store a time anytime the user does an input
        get_time()

        if user_input.lower() == "":
            comment_time = get_time()

        # user commands
        elif user_input.lower() == "s":
            print("\nSkipping to next song...")

            if commented:
                with open(f"{random_notes_file}", "a") as f:
                    f.write(f"\n{play_count} listens, skipped to next at {get_time()}.\n  ")
                    f.close()

            play_count = 1
            commented = False

            random_notes_file = random.choice(list(discography.keys()))
            random_audio_file = discography[random_notes_file]
            play_audio()

        elif user_input.lower() == "r":
            print("Restarting playback...")
            if not pygame.mixer.music.get_busy():
                play_count = play_count + 1
            pygame.mixer.music.rewind()
            play_audio()

        else:
            # write the comment to the file
            with open(f"{random_notes_file}", "a") as f:
                if not commented:
                    mark_session()
                    commented = True
                timestamp = get_time()
                if comment_time:
                    timestamp = comment_time
                print(f"\n{salmon}{timestamp} - {user_input}{default}")
                f.write(f"\n{timestamp} - {user_input}")
                f.close()
            comment_time = False
```


Overall, this automation script can help music producers keep track of their audio files and sessions more efficiently. By automating the process of monitoring audio files and generating session notes, producers can focus more on creating music and less on administrative tasks. The script could also be adapted and extended to meet other use cases, such as organizing files or generating reports.