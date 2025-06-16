import csv
import random

with open("./assets/elements_table.csv", "r") as csv_file:
  csv_reader = csv.reader(csv_file)
  next(csv_reader)
  elements_list = list(csv_reader)
  print(elements_list)
  for i in range (100):
    chosen_row = random.choice(elements_list)
    print(f"The element with atomic number of {chosen_row[2]} is {chosen_row[0]}, whose symbol is {chosen_row[1]}")

#  for line in csv_reader: 
#    print(line[1])
