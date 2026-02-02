import socket
import time
import bpy
from bthl.tasks.task import Task
import random
from bthl.api.dmxdata import dmx_buffer
from bthl.operator.sender_modal import UDPClientToggleModal
from bthl.types.artnetpacket import ArtnetPacket

def send_udp_packet(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(message, (ip, port))
        print(f"Sent message to {ip}:{port}")
    except Exception as e:
        print(f"Error sending message: {e}")
    finally:
        sock.close()

def send(scene, depsgraph):
    #print("Sending DMX data via UDP...")
    #we should only send if the udp client is active
    if not UDPClientToggleModal.get_udp_client_state(bpy.context):
        #print("UDP Client is not active, skipping send.")
        return
    
    # Get configurable target IP, port, and universe offset
    target_ip = UDPClientToggleModal.get_target_ip(bpy.context)
    target_port = UDPClientToggleModal.get_target_port(bpy.context)
    universe_offset = UDPClientToggleModal.get_universe_offset(bpy.context)
    
    messages = ArtnetPacket.global_dict_to_packets(dmx_buffer, universe_offset=universe_offset)

    for message in messages:
        send_udp_packet(target_ip, target_port, message.pack())
        #time.sleep(0.001)  # brief pause to avoid overwhelming the network
    
    dmx_buffer.clear()

class UDPClientTasks(Task):
    functions = {
        "depsgraph_update_post": send,

        "frame_change_post": send,

        "load_post": send,
    }
