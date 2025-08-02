from datetime import datetime
import time

send_time = ["19:18:11"]

while True:
    current_time = datetime.now().strftime("%H:%M:%S")
    if current_time in send_time:
        print(current_time)
        print("TIME!!!!!!!!!!!")
        time.sleep(1)
    time.sleep(0.5)