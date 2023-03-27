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

# print(f"Rotation populated as:")
# print(f"{discography}")

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
        print("true")
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


