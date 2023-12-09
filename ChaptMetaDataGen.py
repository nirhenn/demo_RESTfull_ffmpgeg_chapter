#This software needs "FFmpeg" as its dependency. So, install "FFmpeg" and add it to path.

import re
import os
import subprocess

print("This software needs \"FFmpeg\" as it's dependency. So, install \"FFmpeg\" and add it to path.")

chapter_file = '/Users/Nir/Projects/RESTful-WS-Example/chapter_file.txt'
input_video_file = '/Users/Nir/Projects/RESTful-WS-Example/output_file.webm'
print (chapter_file, input_video_file )
chapters = list()

with open(chapter_file, 'r') as f:
   for line in f:
      x = re.match(r"(\d{1,2}):(\d{1,2}):(\d{1,2}) (.*)", line)
      hrs = int(x.group(1))
      mins = int(x.group(2))
      secs = int(x.group(3))
      title = x.group(4)

      minutes = (hrs * 60) + mins
      seconds = secs + (minutes * 60)
      timestamp = (seconds * 1000)
      chap = {
         "title": title,
         "startTime": timestamp
      }
      chapters.append(chap)

command_template = "ffprobe -i {webm_file_path} -show_entries format=duration -v quiet -of csv='p=0'"
webm_file_path = input_video_file
full_command = command_template.format(webm_file_path=webm_file_path)
output = subprocess.getoutput(full_command)
try:
    duration = (float(output) * 1000)
except ValueError:
    print("Error: Unable to convert ffprobe output to float.")

#duration = str(float(subprocess.getoutput("ffprobe -i \"" + input_video_file + "\" -show_entries format=duration -v quiet -of csv=\"p=0\"") * 1000))
print("*** the file duation:",duration)
text = ""

for i in range(len(chapters)):
   chap = chapters[i]
   title = chap['title']
   start = chap['startTime']
   if i == len(chapters)-1:
       end = duration
   else:
       end = chapters[i+1]['startTime']-1
   text += "\n[CHAPTER]\nTIMEBASE=1/1000\nSTART=" + str(start) + "\nEND=" + str(end) + "\ntitle=" + str(title) + "\n"

os.system("ffmpeg -i \"" + input_video_file + "\" -f ffmetadata FFMETADATAFILE")

with open("FFMETADATAFILE", "a", truncate=True) as myfile:
    myfile.write(text)

file_no_ext_list = input_video_file.split(".")[:-1]
file_no_ext = ""
# traverse in the string
for i in range(len(file_no_ext_list)):
    file_no_ext += file_no_ext_list[i]
    if i < len(file_no_ext_list)-1:
        file_no_ext += "."
ext =  str(input_video_file.split(".")[-1])
command = "ffmpeg -i \"" + input_video_file + "\" -i FFMETADATAFILE -map_metadata 1 -codec copy \"" + file_no_ext + " - chapter." + ext + "\""

os.system(command)