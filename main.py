from math import ceil
import os
from datetime import datetime
from time import sleep
from omxplayer.player import OMXPlayer


MINUTE = 60
first_run = True

def get_time_slot():
    
    current_time = datetime.now()

    hour = current_time.hour
    minute = current_time.minute


    if hour >= 8 and hour < 12:
        slot = "morning"
    elif hour >= 12 and hour < 16:
        slot = "afternoon"
    elif hour >= 16 and hour < 19:
        slot = "evening"
    elif hour >= 19 or hour < 8:
        slot = "night"

    return slot


def next_file_index(i,length):
    return (i+1)%length

def loop_and_buffer(file_1, file_2, player_1, player_2, first_run, player_1_run, player_2_run):

    if player_2_run:
        file_1 = file_1 
        player_1.load(file_1)
        sleep(2)

    if not first_run: 
        sleep(10)

    if first_run:
        first_run = False
    
    player_1.play()
    player_2.pause()
    
    
    player_2_run = False
    player_1_run = True


    duration_1 = player_1.duration()
    play_time_1 = duration_1 * ceil(MINUTE / duration_1)

    if player_1_run:
        file_2 = file_2 
        sleep(2)
        player_2.load(file_2)

    sleep(10)
    
    player_2.play()
    #sleep(0.1)
    player_1.pause()
    sleep(2)
    

    player_2_run = True
    player_1_run = False
    
    duration_2 = player_2.duration()
    play_time_2 = duration_2 * ceil(MINUTE / duration_2)

    #sleep(play_time_2)
    
    


if __name__ == '__main__':
    
    verbose = 0

    player_1_run = False
    player_2_run = True

    first_run = True

    player_1 = OMXPlayer('/home/pi/Desktop/rpi_gif/image1.mp4', args='--start-paused --loop --no-osd ', dbus_name='org.mpris.MediaPlayer2.omxplayer1')
    player_2 = OMXPlayer('/home/pi/Desktop/rpi_gif/image2.mp4',args='--start-paused --loop --no-osd ', dbus_name='org.mpris.MediaPlayer2.omxplayer2')

    required_directories = ['morning','afternoon','evening','night']

    available_directories = os.listdir()

    if (set(required_directories) & set(available_directories)) == set(required_directories):
        print("All directories are available")
    
    else:
        print("Some directories are missing")
        print(os.listdir())

    try:
        while 1:
                            
            slot = get_time_slot()

            directory = slot
            
            print(f'Inside {directory} folder')
            
            files_in_dir = os.listdir(directory)
            file_index = 0

            while file_index < len(files_in_dir):
                
                

                if verbose: print(f'looping {files_in_dir[file_index]} for 1 minute')

                file_1 = f'/home/pi/Desktop/rpi_gif/{directory}/{files_in_dir[file_index]}'
                file_index = next_file_index(file_index,len(files_in_dir))

                file_2 = f'/home/pi/Desktop/rpi_gif/{directory}/{files_in_dir[file_index]}'
                file_index = next_file_index(file_index,len(files_in_dir))

                loop_and_buffer(file_1, file_2, player_1, player_2, first_run, player_1_run, player_2_run)

                current_slot = get_time_slot()


                if current_slot != slot:
                    break



    except:
        player_1.quit()
        player_2.quit()

        exit(-1)



                
                



