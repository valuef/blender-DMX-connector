bl_info = {
    "name": "Blender to HNode link",
    "blender": (4, 5, 0),
    "category": "Object",
}

import bpy
import inspect
import sys
from bthl.panel.global_control import GlobalControlPanel
from bthl.operator.sender_modal import UDPClientToggleModal
from bthl.operator.receiver_modal import MIDITimecodeOperator, MIDITimecodeToggleModal
from bthl.operator.copy_property import OBJECT_OT_copy_custom_property_to_selected
from bthl.operator.setup_dmx_properties import OBJECT_OT_add_base_dmx_custom_properties
from bthl.operator.duplicate_property import OBJECT_OT_duplicate_custom_property
from bthl.tasks.sender import UDPClientTasks
from bthl.tasks.customproperties import CustomPropertiesTask
from bthl.tasks.receiver import receive

classes = {
    GlobalControlPanel,
    UDPClientToggleModal,
    MIDITimecodeOperator,
    MIDITimecodeToggleModal,
    OBJECT_OT_copy_custom_property_to_selected,
    OBJECT_OT_add_base_dmx_custom_properties,
    OBJECT_OT_duplicate_custom_property,
}

tasks = {
    CustomPropertiesTask,
    UDPClientTasks, #This MUST be last so everything above it is allowed to run
}

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    for task in tasks:
        task.register(task)
    
    # Register MIDI timecode properties
    MIDITimecodeToggleModal.register()
    
    bpy.app.timers.register(receive, persistent=True)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    for task in tasks:
        task.unregister(task)
    
    # Unregister MIDI timecode properties
    MIDITimecodeToggleModal.unregister()
    
    bpy.app.timers.unregister(receive)
