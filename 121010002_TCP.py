import simpy
from ns.flow.cc import TCPReno
from ns.flow.cubic import TCPCubic
from ns.flow.flow import Flow
from ns.packet.tcp_generator import TCPPacketGenerator
from ns.packet.tcp_sink import TCPSink
from ns.port.wire import Wire
from ns.switch.switch import SimplePacketSwitch
import re
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

def packet_arrival():
    """Packets arrive with a constant interval of 0.1 seconds."""
    return 0.1
def packet_size():
    """The packets have a constant size of 1024 bytes (1KB)."""
    return 1024

def delay_dist():
    """Network wires experience a constant propagation delay of 0.1 seconds."""
    return 0.1

env = simpy.Environment()

# Define two separate flows for S1 -> D1 and S2 -> D2
flow1 = Flow(fid=0, 
        src="S1", 
        dst="D1", 
        finish_time=500, 
        arrival_dist=packet_arrival, 
        size_dist=packet_size
        )
flow2 = Flow(fid=1, 
        src="S2", 
        dst="D2", 
        finish_time=500, 
        arrival_dist=packet_arrival, 
        size_dist=packet_size
        )

cc1 = TCPReno()
cc2 = TCPCubic()
# Initialize two TCP packet generators for each sender with TCPReno congestion control (change cc=cc2 for Cubic)
sender1 = TCPPacketGenerator(
    env, flow=flow1, cc=cc1, element_id=flow1.src, debug=True
    )
sender2 = TCPPacketGenerator(
    env, flow=flow2, cc=cc1, element_id=flow2.src, debug=True
    )

# Create wires for connections between senders, routers, and receivers
wire1_downstream = Wire(env, delay_dist) # wire A
wire1_upstream = Wire(env, delay_dist) # wire B
wire2_downstream = Wire(env, delay_dist) # wire C
wire2_upstream = Wire(env, delay_dist) # wire D
wire3_downstream = Wire(env, delay_dist) # wire E
wire3_upstream = Wire(env, delay_dist) # wire F
wire4_downstream = Wire(env, delay_dist) # wire G
wire4_upstream = Wire(env, delay_dist) # wire H
wire5_downstream = Wire(env, delay_dist) # wire I
wire5_upstream = Wire(env, delay_dist) # wire J


switch1 = SimplePacketSwitch(
    env,
    nports=3,
    port_rate=100000,  # in bits/second
    buffer_size=100,  # in packets
    debug=True,
    element_id=1,
)

switch2 = SimplePacketSwitch(
    env,
    nports=3,
    port_rate=100000,  # in bits/second
    buffer_size=100,  # in packets
    debug=True,
    element_id=2,
)

# Initialize two TCP sinks for each receiver
receiver1 = TCPSink(env, rec_waits=True, debug=True, element_id=1)
receiver2 = TCPSink(env, rec_waits=True, debug=True, element_id=2)
receiver1.out


sender1.out = wire1_downstream # wire A - S1 Out Connection
wire1_downstream.out = switch1 # Wire A - Connect S1 to R1
wire3_downstream.out = switch2 # wire E Connect R1 to R2
wire4_downstream.out = receiver1 # wire G connect R2 to D1
receiver1.out = wire4_upstream # wire H D1 out of connection
wire4_upstream.out = switch2 # wire H connect D1 to R2

sender2.out = wire2_downstream # wire C - S2 out connection
wire2_downstream.out = switch1 # wire C - connect s2 to R1
wire3_downstream.out = switch2 # wire E Connect R1 to R2
wire5_downstream.out = receiver2 # Wire I connect r2 to d2
receiver2.out = wire5_upstream # wire J D2 out of connection
wire5_upstream.out = switch2 # wire J connect D2 to R2
wire3_upstream.out = switch1 # wire F connect D2 to D1

fib1 = {0:2, 1:2,10000:0,10001:1}
switch1.demux.fib = fib1
switch1.demux.outs[2].out = wire3_downstream
switch1.demux.outs[1].out = wire2_upstream
switch1.demux.outs[0].out = wire1_upstream
fib2 = {10000:0,10001:0,0:1,1:2}
switch2.demux.fib = fib2
switch2.demux.outs[0].out = wire3_upstream
switch2.demux.outs[1].out = wire4_downstream
switch2.demux.outs[2].out = wire5_downstream

# Feedback
wire1_upstream.out = sender1
wire2_upstream.out = sender2
# Run the simulation
# env.run(until=500)

# Text from the result file (reno and cubic)


def visualize():
    # Regex pattern to extract average throughput
    throughput_pattern = r'Sink 1 Average throughput \(last 10 packets\): ([\d.]+) bytes/second\.'
    # print(re.findall(throughput_pattern, reno_reno))
    throughput_item = (re.findall(throughput_pattern, reno_reno))
    throughput_floats = [float(value) for value in throughput_item]
    
    throughput_pattern_2 = r'Sink 2 Average throughput \(last 10 packets\): ([\d.]+) bytes/second\.'
    # print(re.findall(throughput_pattern, sample_text))
    throughput_item_2 = (re.findall(throughput_pattern_2, reno_reno))
    throughput_floats_2 = [float(value) for value in throughput_item_2]
    # # Find all matches in the sample text
    # for i in throughput_item:
    #     throughput_dict.append((throughput_item)[i])

    # Regex pattern to extract average throughput from Cubic
    throughput_pattern_3 = r'Sink 1 Average throughput \(last 10 packets\): ([\d.]+) bytes/second\.'
    # print(re.findall(throughput_pattern, sample_text))
    throughput_item_3 = (re.findall(throughput_pattern_3, reno_cubic))
    throughput_floats_3 = [float(value) for value in throughput_item_3]

    # Regex pattern to extract average throughput
    throughput_pattern_4 = r'Sink 2 Average throughput \(last 10 packets\): ([\d.]+) bytes/second\.'
    # print(re.findall(throughput_pattern, sample_text))
    throughput_item_4 = (re.findall(throughput_pattern_4, reno_cubic))
    throughput_floats_4 = [float(value) for value in throughput_item_4]
    
    
    # Regex pattern to extract congestion window size
    window_pattern = r'TCPPacketGenerator S1 congestion window size = ([\d.]+)'
    # print(re.findall(throughput_pattern, sample_text))
    window_item = (re.findall(window_pattern, reno_reno))
    window_floats = [float(value) for value in window_item]
    
    # Regex pattern to extract congestion window size
    window_pattern_2 = r'TCPPacketGenerator S2 congestion window size = ([\d.]+)'
    # print(re.findall(throughput_pattern, sample_text))
    window_item_2 = (re.findall(window_pattern_2, reno_reno))
    window_floats_2 = [float(value) for value in window_item_2]
    
    # Regex pattern to extract congestion window size
    window_pattern_3 = r'TCPPacketGenerator S1 congestion window size = ([\d.]+)'
    # print(re.findall(throughput_pattern, sample_text))
    window_item_3 = (re.findall(window_pattern_3, reno_cubic))
    window_floats_3 = [float(value) for value in window_item_3]
    
    # Regex pattern to extract congestion window size
    window_pattern_4 = r'TCPPacketGenerator S2 congestion window size = ([\d.]+)'
    # print(re.findall(throughput_pattern, sample_text))
    window_item_4 = (re.findall(window_pattern_4, reno_cubic))
    window_floats_4 = [float(value) for value in window_item_4]
    

    # Create the first plot in a separate figure
    # Reno - Reno S1 Figure
    plt.figure(figsize=(10, 6))
    plt.plot(throughput_floats)
    plt.title('Receiver S1 Throughput')
    # plt.xlabel('Categories')
    plt.xlim(0,200)
    plt.ylabel('Throughput (bytes/second)')
    plt.xlabel('Time')

    # # Set a fixed interval for y-axis
    # ax = plt.gca()  # Get the current axis
    # ax.yaxis.set_major_locator(ticker.MultipleLocator(base=10000))  # Set the interval to 1000
    # plt.show()

    #Reno - Reno S2 Figure
    plt.figure(figsize=(10, 6))
    plt.plot(throughput_floats_2)
    plt.title('Receiver S2 Throughput')
    # plt.xlabel('Categories')
    plt.ylabel('Throughput (bytes/second)')
    plt.xlabel('Time')
    plt.xlim(0,200)
    # plt.xlim(0,100)
    # Show the second plot
    # plt.show()

    #Reno - Cubic S1 Figure
    plt.figure(figsize=(10, 6))
    plt.plot(throughput_floats_3)
    plt.title('Receiver S1 Throughput')
    # plt.xlabel('Categories')
    plt.ylabel('Throughput (bytes/second)')
    plt.xlabel('Time')
    plt.xlim(0,200)
    # plt.xlim(0,100)
    # Show the third plot
    # plt.show()

    #Reno - Cubic S2 Figure
    plt.figure(figsize=(10, 6))
    plt.plot(throughput_floats_4)
    plt.title('Receiver S2 Throughput')
    # plt.xlabel('Categories')
    plt.ylabel('Throughput (bytes/second)')
    plt.xlabel('Time')
    plt.xlim(0,200)
    # plt.xlim(0,100)

    # Create the first plot in a separate figure
    # Reno - Reno S1 Figure
    plt.figure(figsize=(10, 6))
    plt.plot(window_floats)
    plt.title('Reno - Reno Receiver S1 Congestion Window')
    # plt.xlabel('Categories')
    plt.ylabel('Congestion Window Size')
    plt.xlabel('Time')

    # Create the first plot in a separate figure
    # Reno - Reno S1 Figure
    plt.figure(figsize=(10, 6))
    plt.plot(window_floats_2)
    plt.title('Reno - Reno Receiver S2 Congestion Window')
    # plt.xlabel('Categories')
    plt.ylabel('Congestion Window Size')
    plt.xlabel('Time')

    # Create the first plot in a separate figure
    # Reno - Cubic S1 Figure
    plt.figure(figsize=(10, 6))
    plt.plot(window_floats_3)
    plt.title('Reno - Cubic Receiver S1 Congestion Window')
    # plt.xlabel('Categories')
    plt.ylabel('Congestion Window Size')
    plt.xlabel('Time')

    # Create the first plot in a separate figure
    # Reno - Reno S1 Figure
    plt.figure(figsize=(10, 6))
    plt.plot(window_floats_4)
    plt.title('Reno - Cubic Receiver S2 Congestion Window')
    # plt.xlabel('Categories')
    plt.ylabel('Congestion Window Size')
    plt.xlabel('Time')

    
    # Show the eight plot
    plt.show()
    
visualize()
