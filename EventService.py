#
# The original code for this example is credited to S. Subramanian,
# from this post on DZone: https://dzone.com/articles/restful-web-services-with-python-flask
#
import subprocess

from flask import Flask
from flask import jsonify
from flask import request
from flask import abort
from datetime import datetime, timedelta
from threading import Timer

def schedule_execution(interval):
  """
  Schedules the execution of another Python code at specific times within each hour,
  ensuring execution only once per half-hour interval.

  Args:
    interval: A timedelta object specifying the interval between executions.
  """
  # Initialize a flag to track execution within the current interval
  executed_in_current_interval = False

  def execute_script():
    """Function to execute the script and update execution flag."""
    nonlocal executed_in_current_interval
    subprocess.run(["/usr/bin/python3", "/Users/Nir/Projects/RESTful-WS-Example/ChaptMetaDataGen.py"])
    #subprocess.run(ChaptMetaDataGen, + args=)
    executed_in_current_interval = True

  def schedule_next_execution():
    """Function to schedule the next execution."""
    nonlocal executed_in_current_interval
    # Reset execution flag for the next interval
    executed_in_current_interval = False
    # Schedule the next execution after the interval
    Timer(interval.total_seconds(), schedule_next_execution).start()

  current_time = datetime.now()
  # Calculate the next execution time on the half hour within the current hour
  next_execution_time = current_time.replace(minute=30 if current_time.minute < 30 else 0, second=0, microsecond=0)
  # Schedule execution if not already done in the current interval
  if not executed_in_current_interval:
    execute_script()
  # Schedule next execution on the half hour mark in the next hour
  schedule_next_execution()


def time_since_half_hour_start(current_time):
  """
  This function takes a datetime object as input and returns a string
  representing the time since the beginning of the half of hour in clock format.
  """
  # Get the timestamp of the beginning of the hour
  hour_start = datetime(current_time.year, current_time.month, current_time.day,
                         current_time.hour)

  # Calculate the difference in seconds
  diff_in_seconds = (current_time - hour_start).total_seconds()

  # Convert seconds to minutes and seconds
  minutes = int(diff_in_seconds // 60)
  seconds = int(diff_in_seconds % 60)

  # Format the time in clock format
  if minutes < 30:
    clock_format = f"00:{minutes:02}:{seconds:02}"
  else:
    minutes_after_half_hour = minutes - 30
    seconds_after_half_hour = seconds
    clock_format = f"00:{minutes_after_half_hour:02}:{seconds_after_half_hour:02}"

  return clock_format

app = Flask(__name__)
chapterFile = 'chapter_file.txt'
videoFile = 'output_file.webm'

eventDB=[
{
'id':'101',
'time':'current time of event',
'station':'station name 1',
},
{
'id':'102',
'time':'current time of event',
'station':'station name 2',
}
]

@app.route('/evntdb/event',methods=['GET'])
def getAllEvent():
    return jsonify({'evnt':eventDB})

@app.route('/evntdb/event/<evntId>',methods=['GET'])
def getEvnt(evntId):
    evt = [ evnt for evnt in eventDB if (evnt['id'] == evntId) ] 
    return jsonify({'evnt':evt})

@app.route('/evntdb/event/<evntId>',methods=['PUT'])
def updateEvnt(evntId):

    ev = [ evnt for evnt in eventDB if (evnt['id'] == evntId) ]
    now = datetime.now()

    if len(ev) > 0:
        if 'time' in request.json : 
            ev[0]['time'] = now

        if 'station' in request.json:
            ev[0]['station'] = request.json['station']

    return jsonify(ev)
   
@app.route('/evntdb/event',methods=['POST'])
def createEvnt():
    # Get the current date and time
    current_time = datetime.now()
    # format the time to date and time for print a chapter title
    date_time = current_time.strftime("%A, %d. %B %Y %I:%M:%S:%p") 
    print(f"current date and time is: {date_time}")
    # Get the time since the beginning of the hour
    time_since_half_hour = time_since_half_hour_start(current_time)
    print(f"Time since the beginning of the half hour: {time_since_half_hour}")

    dat = {
    'id':request.json['id'],
    'time': current_time,
    'station':request.json['station']
    }
    eventDB.append(dat)
    chapFileIn = open(chapterFile, 'a') ### open file in append more
    stationName = request.json['station']
    line = (time_since_half_hour, stationName, date_time,'\n')
    seperator = " "
    result = seperator.join(line)
    chapFileIn.writelines(result)
    # print(time, stationName, now)
    schedule_execution(timedelta(minutes=30))

    return jsonify(dat)

@app.route('/evntdb/event/<evntId>',methods=['DELETE'])
def deleteEvnt(evntId):
    ev = [ evnt for evnt in eventDB if (evnt['id'] == evntId) ]

    if len(ev) > 0:
        eventDB.remove(ev[0])
        return jsonify({'response':'Success'})
    else:
        return jsonify({'response':'Failure'})

if __name__ == '__main__':
 app.run(host='0.0.0.0', port=4000)
