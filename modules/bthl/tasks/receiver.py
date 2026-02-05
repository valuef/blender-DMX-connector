import bpy
from bthl.tasks.task import Task
import socket
import struct
import random

sock = None
last_timecode_frame = None

def is_timecode_receive_enabled(scene) -> bool:
    """Check if timecode receiving is enabled for the given scene"""
    from bthl.operator.receiver_modal import MIDITimecodeToggleModal
    prop_name = MIDITimecodeToggleModal.timecode_receive_enabled_prop_name
    return hasattr(scene, prop_name) and getattr(scene, prop_name)

def is_timecode_allow_timeline_move(scene) -> bool:
    """Check if timeline movement is allowed for the given scene"""
    from bthl.operator.receiver_modal import MIDITimecodeToggleModal
    prop_name = MIDITimecodeToggleModal.timecode_allow_timeline_move_prop_name
    return hasattr(scene, prop_name) and getattr(scene, prop_name)

def receive() -> float:
    global sock
    update_rate = 0.001
    scene = bpy.context.scene

    if not is_timecode_receive_enabled(scene):
        return update_rate

    receivebuffer_size = 64

    #receive via udp socket
    if sock is None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #make the receive buffer small
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, receivebuffer_size)
        #bind localhost on port 7001
        sock.bind(("localhost", 7001))
        sock.setblocking(False)

    try:
        data, addr = sock.recvfrom(receivebuffer_size)
        print(f"Received message from {addr}: {data}")
        #the data coming in is a signed long long in bytes, big endian
        milliseconds = int.from_bytes(data[0:4], byteorder='big', signed=True)
        frames = data[4]
        
        #get the scene
        fps = scene.render.fps / scene.render.fps_base
        #convert the value to frames
        frame = frames
        frame += int((milliseconds / 1000) * fps)
        
        global last_timecode_frame
        #set the current frame of the scene
        #check if we are still on this frame, if so do nothing
        should_set_frame = False
        
        if not is_timecode_allow_timeline_move(scene):
            # If timeline move is FALSE: set frame whenever scene frame is different
            should_set_frame = (scene.frame_current != frame)
        else:
            # If timeline move is TRUE: set frame when scene frame is different AND timecode frame has changed
            should_set_frame = (scene.frame_current != frame and last_timecode_frame != frame)
        
        if should_set_frame:
            scene.frame_set(frame)
            
        # Track the last received timecode frame
        last_timecode_frame = frame
        
        return update_rate
    except BlockingIOError:
        #no data received
        return update_rate


def get_last_timecode_frame():
    """Get the last received timecode frame value"""
    global last_timecode_frame
    return last_timecode_frame
