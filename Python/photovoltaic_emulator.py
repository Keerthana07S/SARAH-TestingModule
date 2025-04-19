import serial
import time

ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)

irradiance = 800
temperature = 35

def send_data(G, T):
    msg = f"{G},{T}\n"
    ser.write(msg.encode('utf-8'))

def read_data():
    if ser.in_waiting:
        line = ser.readline().decode('utf-8').strip()
        try:
            v, i = map(float, line.split(','))
            return v, i
        except:
            return None, None
    return None, None

while True:
    send_data(irradiance, temperature)
    v, i = read_data()
    if v is not None and i is not None:
        print(f"V = {v:.3f} V, I = {i:.3f} A")
    time.sleep(1)
