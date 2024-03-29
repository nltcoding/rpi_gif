from math import ceil
import os
from datetime import datetime
from time import sleep
from omxplayer.player import OMXPlayer
import moviepy.editor as mp
from haishoku.haishoku import Haishoku
from copy import deepcopy

MINUTE = 60
first_run = True
LUMINOCITY_THREASHOLD = 140
HEIGHT_THREASHOLD = 300
WIDTH_THREASHOLD = 500

def get_time_slot():
    
    current_time = datetime.now()

    hour = current_time.hour
    minute = current_time.minute


    if hour >= 8 and hour < 16:
        slot = "daytime"
    # elif hour >= 12 and hour < 16:
    #     slot = "afternoon"
    # elif hour >= 16 and hour < 19:
    #     slot = "evening"
    elif hour >= 16 or hour < 8:
        slot = "nighttime"

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
    
    
def process_gif(file_list,source_folder,destination_folder):

    modified_file_list = deepcopy(file_list)

    for file_name in modified_file_list:

        if file_name.endswith('.png'):
            file_name = file_name.replace('.png','.mp4')

        if os.path.exists(destination_folder + '/' + file_name.replace('.gif', '.mp4')):
            print(file_name.replace('.gif', '.mp4'), 'already exists')
            continue
        
        print("#####",destination_folder + '/' + file_name.replace('.gif', '.mp4'))
        
        # print(file_name)
        clip = mp.VideoFileClip(f'{source_folder}/{file_name}')

        width, height = clip.size

        if width >= WIDTH_THREASHOLD and height >= HEIGHT_THREASHOLD:

            aspect_ratio = width / height

            if aspect_ratio > 1.3 and aspect_ratio < 2.3:
                clip = clip.resize((1280,720))
                clip_length = clip.duration

                clip = clip.loop(n = ceil(10/clip_length))

                clip.write_videofile(destination_folder + '/' + file_name.replace('.gif','.mp4'))
        
        



if __name__ == '__main__':

    gif_folder = './gif_source'
    unedited_gifs = os.listdir(gif_folder)
    # print(unedited_gifs)
    
    for gif_file in unedited_gifs:
        
        if gif_file.endswith('.mp4'):
            # print(gif_file)
            # print(f'{gif_folder}/{gif_file}')
            clip = mp.VideoFileClip(f'{gif_folder}/{gif_file}')
            modified_file_name = gif_file.replace('.mp4','.png')
            clip.save_frame(f'{gif_folder}/{modified_file_name}',t = 0)
            # print(modified_file_name)

    unedited_gifs = os.listdir(gif_folder)

    daytime_gif_list = []
    nighttime_gif_list = []

    for image_file in unedited_gifs:

        if image_file.endswith('.gif') or image_file.endswith('.png'):
            
            dominant = Haishoku.getDominant(f'{gif_folder}/{image_file}')
            R,G,B = dominant
            luminocity = (0.2126*R + 0.7152*G + 0.0722*B)
            # print(luminocity)
            
            if luminocity > LUMINOCITY_THREASHOLD:
                daytime_gif_list.append(image_file)

            else:
                nighttime_gif_list.append(image_file)


    required_directories = ['daytime','nighttime']

    for folder in required_directories:
        os.makedirs(f'./{folder}',exist_ok = True)


    process_gif(daytime_gif_list,gif_folder,f'./daytime')
    process_gif(nighttime_gif_list, gif_folder, './nighttime')   
    

    
    verbose = 0

    player_1_run = False
    player_2_run = True

    first_run = True

    player_1 = OMXPlayer('/home/pi/Desktop/rpi_gif/image1.mp4', args='--start-paused --loop --no-osd ', dbus_name='org.mpris.MediaPlayer2.omxplayer1')
    player_2 = OMXPlayer('/home/pi/Desktop/rpi_gif/image2.mp4',args='--start-paused --loop --no-osd ', dbus_name='org.mpris.MediaPlayer2.omxplayer2')

    

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



                
                



