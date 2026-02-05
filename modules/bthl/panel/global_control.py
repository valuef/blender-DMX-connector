from bpy.types import Panel, Context
import bthl.operator.sender_modal as sender_modal
import bthl.operator.receiver_modal as receiver_modal
from bthl.tasks.receiver import get_last_timecode_frame

class GlobalControlPanel(Panel):
    bl_label = "HNode Connector"
    bl_idname = "OBJECT_PT_main_panel"

    #Specific controls for the sidebar in the 3d view
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HNode Connector'

    def draw(self, context: Context):
        layout = self.layout
        if layout is None:
            return
        scene = context.scene

        # UDP Client controls
        box = layout.box()
        box.label(text="UDP Client Settings")
        
        # Target IP and Port inputs
        row = box.row()
        row.prop(scene, "udp_target_ip", text="Target IP")
        row.prop(scene, "udp_target_port", text="Port")
        
        # Universe offset input
        box.prop(scene, "universe_offset", text="Universe Offset")
        
        # Toggle button
        box.operator(sender_modal.UDPClientToggleModal.bl_idname, text=sender_modal.UDPClientToggleModal.dynamic_text(context))
        
        # MIDI Timecode controls
        timecode_box = layout.box()
        timecode_box.label(text="MIDI Timecode Settings")
        
        # Enable/disable timecode receiving
        timecode_box.prop(scene, "timecode_receive_enabled", text="Receive MIDI Timecode")
        
        # Display last received timecode
        last_timecode = get_last_timecode_frame()
        if last_timecode is not None:
            info_row = timecode_box.row()
            info_row.label(text=f"Last Timecode: Frame {last_timecode}", icon='TIME')
        else:
            info_row = timecode_box.row()
            info_row.label(text="Last Timecode: None received", icon='ERROR')
        
        # Show timeline controls only when timecode is enabled
        if scene.timecode_receive_enabled:
            timecode_box.prop(scene, "timecode_allow_timeline_move", text="Allow Free Timeline Movement")
            
            # Manual timeline control section
            if scene.timecode_allow_timeline_move:
                control_row = timecode_box.row(align=True)
                # Sync to last received timecode button
                op_sync = control_row.operator(receiver_modal.MIDITimecodeOperator.bl_idname, text="Sync to Last Timecode", icon='TIME')
                op_sync.action = "sync_to_last_timecode"
