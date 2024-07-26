import csv
from ai.models import *
import threading
def read_input_output(file_path):
    print('reading rows')
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            input_value = row.get("input")
            output_value = row.get("output")
            #print(f"Input: {input_value}, Output: {output_value}")
            x = model_parameters(user_msg=input_value, model_msg=output_value)
            x.save()

# Example usage:
"""
if model_parameters.objects.all().count() < 500:
    thread = threading.Thread(target=read_input_output,args=(["model.csv"]))
    thread.start()
"""
#thread.join()
