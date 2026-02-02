import bpy
from bpy.types import Operator, Context
from bpy.props import BoolProperty, StringProperty, IntProperty
from typing import TYPE_CHECKING

class UDPClientToggleModal(Operator):
    """Simple toggle operator for UDP client on/off"""
    bl_idname = "bthl.udp_client_toggle"
    bl_label = "UDP Client Toggle"
    bl_description = "Toggle UDP client connection on/off"
    bl_options = {'REGISTER', 'UNDO'}

    udp_client_active_prop_name = "udp_client_active"
    udp_target_ip_prop_name = "udp_target_ip"
    udp_target_port_prop_name = "udp_target_port"

    @staticmethod
    def get_udp_client_state(context: Context):
        return getattr(context.scene, UDPClientToggleModal.udp_client_active_prop_name, False)
    
    @staticmethod
    def get_target_ip(context: Context):
        return getattr(context.scene, UDPClientToggleModal.udp_target_ip_prop_name, "127.0.0.1")
    
    @staticmethod
    def get_target_port(context: Context):
        return getattr(context.scene, UDPClientToggleModal.udp_target_port_prop_name, 6454)
    
    def execute(self, context: Context):
        """Toggle UDP client state and exit"""
        
        # Get current state or default to False
        current_state = getattr(context.scene, UDPClientToggleModal.udp_client_active_prop_name, False)
        
        # Toggle the state
        new_state = not current_state
        setattr(context.scene, UDPClientToggleModal.udp_client_active_prop_name, new_state)
        
        # Report the new state
        status = "ON" if new_state else "OFF"
        self.report({'INFO'}, f"UDP Client: {status}")
        
        return {'FINISHED'}

    @staticmethod
    def dynamic_text(context: Context):
        """Dynamically change button text based on state"""
        current_state = getattr(context.scene, UDPClientToggleModal.udp_client_active_prop_name, False)
        return "Stop UDP Client" if current_state else "Start UDP Client"

    @staticmethod
    def register():
        """Register the operator"""
        # Add scene property to store UDP client state globally
        bpy.types.Scene.udp_client_active = BoolProperty(
            name="UDP Client Active",
            description="Global UDP client active state",
            default=False
        )
        
        # Add scene properties for target IP and port
        bpy.types.Scene.udp_target_ip = StringProperty(
            name="Target IP",
            description="Target IP address for UDP packets",
            default="127.0.0.1"
        )
        
        bpy.types.Scene.udp_target_port = IntProperty(
            name="Target Port",
            description="Target port for UDP packets",
            default=6454,
            min=1,
            max=65535
        )

    @staticmethod
    def unregister():
        """Unregister the operator"""
        # Remove scene properties
        if hasattr(bpy.types.Scene, UDPClientToggleModal.udp_client_active_prop_name):
            del bpy.types.Scene.udp_client_active
        if hasattr(bpy.types.Scene, UDPClientToggleModal.udp_target_ip_prop_name):
            del bpy.types.Scene.udp_target_ip
        if hasattr(bpy.types.Scene, UDPClientToggleModal.udp_target_port_prop_name):
            del bpy.types.Scene.udp_target_port
