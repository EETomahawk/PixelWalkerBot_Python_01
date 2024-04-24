from time import sleep
from threading import Thread

def x():
  sleep(1) #Accurate down to ~0.015s precision
  print("x")

def y(y:str):
  sleep(1)
  print(y)

Thread(target=x).start()
Thread(target=y, args=["test"]).start()