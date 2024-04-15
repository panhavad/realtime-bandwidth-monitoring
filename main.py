import subprocess
import re
import matplotlib.pyplot as plt
from collections import deque
from datetime import datetime
import socket
import configparser

# Read configuration from the file
config = configparser.ConfigParser()
config.read('config.config')

Y_MIN = int(config['setting']['Y_MIN'])
Y_MAX = int(config['setting']['Y_MAX'])
FIGURE_X = int(config['setting']['FIGURE_X'])
FIGURE_Y = int(config['setting']['FIGURE_Y'])
maxlen = int(config['setting']['maxlen'])
interface = config['setting']['interface']

BLINK = 1

# Initialize empty lists to store incoming and outgoing rates
incoming_rates = deque(maxlen=maxlen)
outgoing_rates = deque(maxlen=maxlen)

def get_hostname():
    return socket.gethostname()

def run_nload(interface, hostname):
    global BLINK
    plt.ion()  # Turn on interactive mode for dynamic updating
    plt.figure(figsize=(FIGURE_X, FIGURE_Y))  # Set figure size
    plt.grid(True)  # Enable gridlines
    
    command = ["nload", interface, "-m", "-u", "m"]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            # Using regular expressions to extract Incoming and Outgoing current bit rates
            match = re.match(r'.*Curr:\s*([\d.]+)\s*MBit/s\s*.*Curr:\s*([\d.]+)\s*MBit/s', output)
            if match:
                incoming_rate = float(match.group(1))
                outgoing_rate = float(match.group(2))
                # Append the rates to the lists
                incoming_rates.append(incoming_rate)
                outgoing_rates.append(outgoing_rate)
                
                # Clear the previous plot and legend
                plt.clf()
                # Adjust subplot parameters to add margin
                plt.subplots_adjust(left=0.05, right=0.80, top=0.9, bottom=0.15)
                plt.ylim(Y_MIN, Y_MAX)  # Change these values according to your preference
                # Plot the graph
                plt.plot(incoming_rates, label='Incoming')
                plt.plot(outgoing_rates, label='Outgoing')
                
                # Annotate current values on the graph lines
                plt.annotate(f'{incoming_rate:.2f} Mbps', (len(incoming_rates) - 1, incoming_rate), textcoords="offset points", xytext=(150,-2.5), ha='center', color='tab:blue')
                plt.annotate(f'{outgoing_rate:.2f} Mbps', (len(outgoing_rates) - 1, outgoing_rate), textcoords="offset points", xytext=(75,-2.5), ha='center', color='tab:orange')
                
                plt.xlabel('Time (s)')
                plt.ylabel('Rate (Mbps)')
                
                # Show current time on the plot
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                plt.text(1.02, 1.025, f'Current Time: {current_time}', transform=plt.gca().transAxes)
                plt.text(1.06, -0.10, f'2024 © Duk Panhavad', transform=plt.gca().transAxes, color='tab:grey', alpha=0.2)

                # Set title dynamically
                plt.title(f'Network Traffic | {interface} | {hostname}')

                # Active blink
                if BLINK:
                    plt.text(1, 1.025, f'●', fontsize=12, color='green', fontweight='bold', transform=plt.gca().transAxes)
                    BLINK = 0
                elif not BLINK:
                    BLINK = 1
                
                plt.legend()
                plt.pause(0.05)  # Pause to allow the plot to update
        
    _, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error: {stderr}")

# Replace 'eno1' with your actual network interface name
run_nload(interface, get_hostname())
