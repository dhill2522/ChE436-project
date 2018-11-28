import threading
import datetime
import time

def get_time_interval_days():
    interval_prompt = "Please enter how many days for each time interval: "
    interval_days = raw_input(interval_prompt)
    return int(interval_days)

def get_time_interval_hours():
    interval_prompt = "Please enter how many hours for each time interval: "
    interval_hours = raw_input(interval_prompt)
    return int(interval_hours)

def get_time_interval_minutes():
    interval_prompt = "Please enter how many minutes for each time interval: "
    interval_minutes = raw_input(interval_prompt)
    return int(interval_minutes)

def get_time_interval():
    days = get_time_interval_days()
    hours = get_time_interval_hours()
    minutes = get_time_interval_minutes()
    return (days * 24 * 60 * 60) + (hours * 60 * 60) + (minutes * 60)

def get_interations():
    return int(raw_input("Please enter how many iterations will be run: "))

def get_filename():
    filename_prompt = "Please enter the csv file name to be saved: "
    return raw_input(filename_prompt)

def get_temp_humidity_c():
    temp = 23.00
    humidity = 60.00
    return [temp, humidity]

def take_picture(file_path="image.jpg"):
    file_path = "pics/" + file_path
    # take picture
    pass


def make_entry():
    results  = get_temp_humidity_c()
    now = datetime.datetime.now()
    time_stamp = now.strftime("%A, %d. %B %Y %I:%M%p")
    time_stamp = time_stamp.replace(",", "")
    time_stamp = time_stamp.replace(".", "")
    pic_name = time_stamp.replace(" ", "_")
    pic_name = pic_name.replace(":", "_")
    pic_name = pic_name + ".jpg"

    return {
        "temp" : results[0],
        "humidity" : results[1],
        "time_stamp" : time_stamp,
        "pic_name" : pic_name
    }

def create_csv(filename="master.csv"):
    with open(filename, 'w') as csvfile:
        field_names = "temp, humidity, time_stamp, pic_name\n"
        csvfile.write(field_names)

def append_to_csv(filename="master.csv"):
    data = make_entry()
    data_string = "{:2f}, {:2f}, ".format(data['temp'], data['humidity']) + data['time_stamp'] + ", " + data['pic_name'] + "\n"
    with open(filename, 'a') as csvfile:
        csvfile.write(data_string)
    csvfile.close()
    take_picture(data['pic_name'])


def write_data(filename="master.csv"):
    append_to_csv()
    t = threading.Thread(target=append_to_csv, args=(filename,))
    t.daemon = True
    t.start()

def run():
    seconds = 1 #get_time_interval()
    file_name = str(get_filename())
    num_interations = get_interations()

    create_csv(file_name)
    counter = 0
    while counter < num_interations:
        write_data(filename=file_name)
        time.sleep(seconds)
        counter = counter + 1
        print("iteration " + str(counter) + " saved successfully - " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))

run()
