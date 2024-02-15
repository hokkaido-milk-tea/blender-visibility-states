import bpy

from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty, CollectionProperty
from bpy.types import PropertyGroup, UIList, Operator, Panel

import random
import string

obj_icon_dict = {
    "MESH": "OUTLINER_OB_MESH",
    "LIGHT": "LIGHT",
    "CAMERA": "VIEW_CAMERA",
    "CURVE": "OUTLINER_OB_CURVE",
    "SURFACE": "OUTLINER_OB_SURFACE",
    "META": "OUTLINER_OB_META",
    "FONT": "OUTLINER_OB_FONT",
    "VOLUME": "OUTLINER_OB_VOLUME",
    "GPENCIL": "OUTLINER_OB_GREASEPENCIL",
    "ARMATURE": "OUTLINER_OB_ARMATURE",
    "LATTICE": "OUTLINER_OB_LATTICE",
    "EMPTY": "OUTLINER_OB_EMPTY",
    "IMAGE": "OUTLINER_OB_IMAGE",
    "LIGHT_PROBE": "OUTLINER_OB_LIGHTPROBE",
    "SPEAKER": "OUTLINER_OB_SPEAKER",
}

class MTToolsVisibilityStateSettings(PropertyGroup):

    sync_viewport_disable: BoolProperty(
        name="Sync Viewport Disable",
        description="Toggles whether global viewport disable is synced to visibility state toggles",
        default=True,
        )
    
    collections_always_visible: BoolProperty(
        name="Collections Always Visible",
        description="Toggles whether collections are always visible regardless of what objects or visibility states are shown/hidden",
        default=False,
    )

class MTToolsVisibilityState(PropertyGroup):
    # this class holds info on which groups contain which shape key indices
    
    name: StringProperty(
        name="Visibility State Name",
        description="Visibility state name",
        default="",
    )
    
    id: StringProperty()

class MTToolsVisibilityStateAssignment(PropertyGroup):
    
    name: StringProperty(
        name="Visibility State Assignment",
        description="Visibility state assignment",
        default="",
    )
    
    id: StringProperty()

class MTToolsVisibilityStateUIList(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        row = layout.row(align=True)
        toggle_visibility_op = row.operator("mttools_visibility_state.toggle_visibility", text="", icon="HIDE_OFF", emboss=False)
        toggle_visibility_op.state_index = index
        list_objects_op = row.operator("mttools_visibility_state.list_objects", text="", icon="PRESET", emboss=False)
        list_objects_op.state_index = index
        row.prop(item, "name", text="", emboss=False)
        # row.prop(item, "id", emboss=False, text="")

class MTToolsVisibilityStatesAddState(Operator):
    """Add a new visibility state"""

    bl_idname = "mttools_visibility_state.add_state"
    bl_label = "Add Visibility State"
    
    def execute(self, context):
        scene = context.scene
        
        visibility_states = scene.mttools_visibility_state
        existing_ids = [x.id for x in visibility_states]
        
        new_visibility_state = scene.mttools_visibility_state.add()
        
        # 8-digit alpha-numeric id
        unique_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        
        while unique_id in existing_ids:
            print('generating new id')
            unique_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        
        new_visibility_state.name = "Visibility State"
        new_visibility_state.id = unique_id
        
        return {'FINISHED'}

class MTToolsVisibilityStatesRemoveState(Operator):
    """Removes the selected visibility state"""

    bl_idname = "mttools_visibility_state.remove_state"
    bl_label = "Remove Visibility State"
    
    def execute(self, context):
        scene = context.scene
        objects = scene.objects
        

        # remove assignment from each object first
        current_visibility_state = scene.mttools_visibility_state[scene.mttools_visibility_state_index]
        print(f'Remove id: {current_visibility_state.id}')
        for obj in objects:
            # remove_index = None
            obj_vis_states = [x.id for x in obj.mttools_visibility_state_assignment]
            print(f'Vis states in {obj.name}: {obj_vis_states}')
            
            if current_visibility_state.id in obj_vis_states:
                remove_index = obj_vis_states.index(current_visibility_state.id)
                obj.mttools_visibility_state_assignment.remove(remove_index)
            
            obj_vis_states = [x.id for x in obj.mttools_visibility_state_assignment]
            print(f'Vis states after removal {obj.name}: {obj_vis_states}')
            
            # remove_index = obj_vis_states.index(current_visibility_state.id) if current_visibility_state.id in obj_vis_states else None
            
            # print(f'Remove index: {remove_index}')
            
            # remove_index = obj_vis
            
            # remove_indices.append(obj_vis_states.index(current_visibility_state.id))
            # print(remove_indices)
            # assignments = obj.mttools_visibility_state_assignment
            # for ind, assignment in enumerate(assignments):
            #     if current_visibility_state.id in assignments:
            #         remove_indices.add(ind)
        
        # ...then remove the visibility state
        visibility_states = scene.mttools_visibility_state
        visibility_states.remove(scene.mttools_visibility_state_index)
        
        # obj.mttools_visibility_state_index = min(max(0, obj.mttools_visibility_state_index - 1), len(obj.mttools_visibility_state) - 1)


        return {"FINISHED"}

class MTToolsVisibilityStatesRegisterState(Operator):
    """Registers current visibility configuration to visibility state"""

    bl_idname = "mttools_visibility_state.register_state"
    bl_label = "Register Visibility State"
    
    def execute(self, context):
        scene = bpy.context.scene
        objects = scene.objects
        
        current_visibility_state = scene.mttools_visibility_state[scene.mttools_visibility_state_index]
        # print(current_visibility_state)
        for obj in objects:
            print(f'name: {obj.name}, type: {obj.type}, visible?: {not obj.hide_get()}')
            
            obj_vis_states = [x.id for x in obj.mttools_visibility_state_assignment]
            print(obj_vis_states)
            
            if current_visibility_state.id in obj_vis_states:
                print('already assigned to group')
                continue

            
            if not obj.hide_get():
                new_visibility_state_assignment = obj.mttools_visibility_state_assignment.add()
                new_visibility_state_assignment.id = current_visibility_state.id
                print(f'Adding {obj.name} to visibility state {current_visibility_state.name} at id {current_visibility_state.id}...')
            
        return {"FINISHED"}
    
class MTToolsVisibilityStatesToggleVisibility(Operator):
    """Toggles this visibility state"""

    bl_idname = "mttools_visibility_state.toggle_visibility"
    bl_label = "Toggle Visibility State"
    
    state_index: IntProperty(default=0)
    
    def execute(self, context):
        scene = context.scene
        objects = scene.objects
        state_index = self.state_index
        
        current_visibility_state = scene.mttools_visibility_state[state_index]
        
        for obj in objects:
            obj_vis_states = [x.id for x in obj.mttools_visibility_state_assignment]
            if current_visibility_state.id in obj_vis_states:
                obj.hide_set(False)
                if scene.mttools_visibility_state_settings.sync_viewport_disable:
                    obj.hide_viewport = False
                if scene.mttools_visibility_state_settings.collections_always_visible:
                    toggle_collection_visibility(context, hide=False)
            else:
                obj.hide_set(True)
                if scene.mttools_visibility_state_settings.sync_viewport_disable:
                    obj.hide_viewport = True
                if scene.mttools_visibility_state_settings.collections_always_visible:
                    toggle_collection_visibility(context, hide=False)
                
            
        return {"FINISHED"}

# class MTToolsVisibilityStatesSyncViewportDisable(Operator):
#     """Toggles whether global viewport enable/disable is toggled when toggling visibility states."""
    
#     bl_idname = "mttools_visibility_state.sync_viewport_disable"
#     bl_label = "Toggle sync of global viewport disable to visibility"
    
#     sync_viewport_disable: BoolProperty(
#         name = "Sync Viewport Disable",
#         default = True
#     )
    
#     def execute(self, context):
#         self.sync_viewport_disable = not self.sync_viewport_disable
#         return {"FINISHED"}
    
#     def invoke(self, context, event):
#         wm = context.window_manager
#         return wm.invoke_props_dialog(self)

class MTToolsVisibilityStatesListObjects(Operator):
    """Lists all objects in this visibility state"""

    bl_idname = "mttools_visibility_state.list_objects"
    bl_label = "List Visibility State Objects"
    
    state_index: IntProperty(default=0)
    
    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        objects = scene.objects
        state_index = self.state_index
        
        current_visibility_state = scene.mttools_visibility_state[state_index]
        grid = layout.grid_flow(row_major=True, columns=2)
        
        for obj in objects:
            obj_vis_states = [x.id for x in obj.mttools_visibility_state_assignment]
            if current_visibility_state.id in obj_vis_states:
                obj_icon = obj_icon_dict[obj.type]
                grid.label(text=obj.name, icon=obj_icon)
    
    def execute(self, context):
        return {"FINISHED"}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=150)




class MTToolsVisibilityStatesUnhideAll(Operator):
    """Unhides all objects in the scene (equivalent to the shortcut Alt + H)"""
    
    bl_idname = "mttools_visibility_state.unhide_all"
    bl_label = "Unhide All"
    
    def execute(self, context):
        scene = context.scene
        objects = context.scene.objects
        # collections_in_data = bpy.data.collections
        # collections_in_view_layer = context.view_layer.layer_collection.children
        
        for obj in objects:
            obj.hide_viewport = False
            obj.hide_set(False)
        
        # toggles visibility for collections in bpy.data and bpy.context.view_layer
        if scene.mttools_visibility_state_settings.collections_always_visible:
            toggle_collection_visibility(context, hide=False)
        
        # for coll in collections_in_data:
        #     coll.hide_viewport = False
            
        # for coll in collections_in_view_layer:
        #     coll.hide_viewport = False
            
        return {"FINISHED"}

class MTToolsVisibilityStatesPanel(Panel):
    """"""
    bl_label = "Visibility States"
    bl_idname = "MTToolsVisibilityStatesPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = ""
    bl_category = "MTTools"
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        settings = scene.mttools_visibility_state_settings
        # space = context.space_data
        
        row = layout.row(align=True)
        


        col = row.column()
        col.template_list("MTToolsVisibilityStateUIList", "", scene, "mttools_visibility_state", scene, "mttools_visibility_state_index")

        col.operator("mttools_visibility_state.register_state", icon="FILE_TICK", text="Register Visibility State")

        col.operator("mttools_visibility_state.unhide_all", icon="LOOP_BACK")

        col.prop(scene.mttools_visibility_state_settings, "sync_viewport_disable", text="Sync Viewport Disable")

        col.prop(scene.mttools_visibility_state_settings, "collections_always_visible", text="Collections Always Visible")
        
        col = row.column()
        col.operator("mttools_visibility_state.add_state", icon="ADD", text="")
        col.operator("mttools_visibility_state.remove_state", icon="REMOVE", text="")


class MTToolsVisibilityStatesDebugPanel(Panel):
    """Panel with info for debugging the visibility states tool."""
    bl_label = "DEBUG"
    bl_idname = "MTToolsVisibilityStatesDebugPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = ""
    bl_category = "MTTools"
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        
        row = layout.row()
        
        col = row.column(align=True)
        col.label(text="Name:")
        col.label(text="ID:")
        
        col = row.column(align=True)
        col.label(text=f"{scene.mttools_visibility_state[scene.mttools_visibility_state_index].name}")
        col.label(text=f"{scene.mttools_visibility_state[scene.mttools_visibility_state_index].id}")


def get_view_layer_collections(layer_collection: bpy.types.LayerCollection):
    """Function to recursively walk the layer collection tree of the view layer."""
    yield layer_collection
    for child in layer_collection.children:
        yield from get_view_layer_collections(child)


def toggle_collection_visibility(context: bpy.types.Context, hide: bool):
    collections_in_data = bpy.data.collections
    for coll in collections_in_data:
        coll.hide_viewport = hide
    
    layer_collection = bpy.context.view_layer.layer_collection
    collections_in_view_layer = list(get_view_layer_collections(layer_collection))
    for coll in collections_in_view_layer:
        coll.hide_viewport = hide

classes = [
    MTToolsVisibilityStateSettings,
    MTToolsVisibilityState,
    MTToolsVisibilityStateAssignment,
    MTToolsVisibilityStateUIList,
    MTToolsVisibilityStatesAddState,
    MTToolsVisibilityStatesRemoveState,
    MTToolsVisibilityStatesRegisterState,
    MTToolsVisibilityStatesToggleVisibility,
    # MTToolsVisibilityStatesSyncViewportDisable,
    MTToolsVisibilityStatesListObjects,
    MTToolsVisibilityStatesUnhideAll,
    MTToolsVisibilityStatesPanel,
    MTToolsVisibilityStatesDebugPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.mttools_visibility_state_settings = PointerProperty(type=MTToolsVisibilityStateSettings)
    bpy.types.Scene.mttools_visibility_state = CollectionProperty(type=MTToolsVisibilityState)
    bpy.types.Scene.mttools_visibility_state_index = IntProperty(name="Active Visibility State Index", default=0)
    bpy.types.Object.mttools_visibility_state_assignment = CollectionProperty(type=MTToolsVisibilityStateAssignment)
    bpy.types.Scene.mttools_visibility_state_sync_viewport_disable = BoolProperty(name="Sync Viewport Disable", default=True)
def unregister():
    
    del bpy.types.Scene.mttools_visibility_state_settings
    del bpy.types.Scene.mttools_visibility_state
    del bpy.types.Scene.mttools_visibility_state_index
    del bpy.types.Object.mttools_visibility_state_assignment
    del bpy.types.Scene.mttools_visibility_state_sync_viewport_disable

    for cls in classes:
        bpy.utils.unregister_class(cls)


register()


# if __name__ == "__main__":
#     register()