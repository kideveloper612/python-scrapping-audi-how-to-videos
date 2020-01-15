import requests
import os
import csv
from tqdm import *

def write_csv(lines, filename):
    """
    Write lines to csv named as filename
    """
    if not os.path.isdir('output'):
        os.mkdir("output")
    file_path = "output/%s" % filename
    with open(file_path, 'a', encoding='utf-8', newline='') as writeFile:
        writer = csv.writer(writeFile, delimiter=',')
        writer.writerows(lines)

def model_list():
    URL = "https://www.audiusa.com/content/audiusa/en/help/video-tutorials/jcr:content/par/responsive_container/par/dtufilters.data.json"
    res = requests.get(url=URL).json()
    return (res['filters'])

def model_loop(list):
    filename = 'Audi_how_to_video_download.csv'
    start_line = [['YEAR', 'MAKE', 'MODEL', 'SECTION', 'TITLE', 'DESCRIPTION', 'THUMBNAIL_URL', 'VIDEO_URL']]
    write_csv(lines=start_line, filename=filename)
    make = 'Audi'
    for record in list:
        year = record['year']
        if year=='All years':
            continue
        models = record['models']
        for model in models:
            model_name = model['name']
            vehicleName = model['value']
            URL = "https://www.audiusa.com/content/audiusa/en/help/video-tutorials/jcr:content/par/" \
                  "responsive_container/par/dtu.data.json?vehicleYear=%s&vehicleName=%s" % (year, vehicleName)
            print(URL)
            res_lines = requests.get(url=URL).json()
            if res_lines is None:
                continue
            for res_line in res_lines:
                title = res_line['title']
                description = res_line['description']
                thumbnail_url = res_line['poster']
                video_url = res_line['desktopmp4']

                line = [[year, make, model_name, '', title, description, thumbnail_url, video_url]]
                print(line)
                write_csv(lines=line, filename=filename)
list = model_list()
model_loop(list=list)

def exist_file_list():
    exist_files = []
    for file in os.listdir("videos"):
        if file.endswith(".mp4"):
            exist_files.append(file)
    return exist_files

def download_video_series(video_links):
    exist_files = exist_file_list()
    for link in video_links:
        if link in exist_files:
            continue

        '''iterate through all links in video_links 
        and download them one by one'''

        # obtain filename by splitting url and getting
        # last string
        file_name = link.split('/')[-1]
        print("Downloading file: %s" % file_name)

        # download started
        file_path = "videos/%s" % file_name
        if not os.path.isdir('videos'):
            os.mkdir('videos')
        with requests.get(link, stream=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                progress = tqdm(total=int(r.headers['Content-Length']))
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        progress.update(len(chunk))

        print("\n%s download!\n" % file_name)

    print("All videos were downloaded!")
    return

def get_video_links():
    video_links = []
    file = "output/Audi_how_to_video_download.csv"
    with open(file, "r", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count < 1:
                line_count += 1
                continue
            print(row[7])
            video_links.append(row[7])
    return video_links

if __name__ == "__main__":
    video_links = get_video_links()
    video_links = list(dict.fromkeys(video_links))
    download_video_series(video_links)
