bl_info = {
    "name": "Devolas DDSConverter UI",
    "blender": (2, 80, 0),
    "category": "Interface",
}


import bpy
from bpy.props import StringProperty, IntProperty, CollectionProperty, BoolProperty, PointerProperty, EnumProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import PropertyGroup, UIList, Operator, Panel, OperatorFileListElement
import pathlib
import subprocess
import os
import ntpath


#operator called during OpenBatchImport
def process_files(context, directory, files):
    import os
    scene = context.scene
    my_list = context.scene.my_list    
    index = context.scene.list_index
    
    for file in files:
        
        path = os.path.join(directory, file.name)
        print(":: set path")
        print(":: path:", path)
        
        #adds new index
        my_list.add()
        print(":: added new images")
        
        #grabs length of list
        list = len(bpy.context.scene.my_list)-1
        print(":: length of list:", list)
        
        item = (scene.my_list[list])
        print(":: item:", item)
        
        item.filepath = path
        
        item.name = ntpath.basename(path)       
        
        
    return{'FINISHED'}


class PT_ListExample(Panel):
    """Demo panel for UI list Tutorial."""

    bl_label = "Devolas DDS Converter"
    bl_idname = "SCENE_PT_LIST_DEMO"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.template_list("MY_UL_List", "The_List", scene,
                          "my_list", scene, "list_index")

        row = layout.row()
        row.operator('my_list.new_item', text='Add')
        row.operator('my_list.delete_item', text='Remove')
        row.operator('my_list.convert', text='Convert')
        row.operator('my_list.convert_all', text='Convert All')


        if scene.list_index >= 0 and scene.my_list:
            item = scene.my_list[scene.list_index]
            
            layout.row().prop(item, 'name')
            layout.row().prop(item, 'filepath')
            
            
            row = layout.row(align = True)
            row.label(text= "DDS Type:")
            row.prop(item, 'typedds')
            
        cvalue = scene.custom_values
        
        row = layout.row()
        row.operator('file.batch_import', icon='OUTLINER_OB_IMAGE')
            
        layout.row().prop(cvalue, 'outputpath')




class MY_UL_List(UIList):
    """Demo UIList."""

    # Filter by the value of name
    filter_by_name: StringProperty(default='')

    # Invert the random property filter
    invert_filter_by_name: BoolProperty(default=False)

    # Order by name
    order_by_name: BoolProperty(default=False)


    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # We could write some code to decide which icon to use here...
        custom_icon = 'TEXTURE_DATA'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon = custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='', icon = custom_icon)


    def draw_filter(self, context, layout):
        """UI code for the filtering/sorting/search area."""

        layout.separator()
        col = layout.column(align=True)

        row = col.row(align=True)
        row.prop(self, 'filter_by_name', text='', icon='VIEWZOOM')
        row.prop(self, 'invert_filter_by_name', text='', icon='ARROW_LEFTRIGHT')


    def filter_items(self, context, data, propname):
        """Filter and order items in the list."""

        # We initialize filtered and ordered as empty lists. Notice that 
        # if all sorting and filtering is disabled, we will return
        # these empty. 

        filtered = []
        ordered = []
        items = getattr(data, propname)

        # Filter
        if self.filter_by_name:

            # Initialize with all items visible
            filtered = [self.bitflag_filter_item] * len(items)

            for i, item in enumerate(items):
                if item.name != self.filter_by_name:
                    filtered[i] &= ~self.bitflag_filter_item


        # Invert the filter
        if filtered and self.invert_filter_by_name:
            show_flag = self.bitflag_filter_item & ~self.bitflag_filter_item

            for i, bitflag in enumerate(filtered):
                if bitflag == filter_flag:
                    filtered[i] = self.bitflag_filter_item
                else:
                    filtered[i] &= ~self.bitflag_filter_item


        # Order by the length of name
        if self.order_by_name:
            sort_items = bpy.types.UI_UL_list.helper_funcs.sort_items_helper
            ordered = sort_items(items, lambda i: len(i.name), True)


        return filtered, ordered



class LIST_OT_NewItem(Operator):
    """Add a new item to the list."""

    bl_idname = "my_list.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        context.scene.my_list.add()

        return{'FINISHED'}


class LIST_OT_DeleteItem(Operator):
    """Delete the selected item from the list."""

    bl_idname = "my_list.delete_item"
    bl_label = "Deletes an item"

    #hides/grey buttons if list index is empty
    @classmethod
    def poll(cls, context):
        return context.scene.my_list

    def execute(self, context):
        my_list = context.scene.my_list
        index = context.scene.list_index

        my_list.remove(index)
        context.scene.list_index = min(max(0, index - 1), len(my_list) - 1)

        return{'FINISHED'}
    
    
    
class LIST_OT_ConvertItem(Operator):
    """Convert a file to DDS format"""
        
    bl_idname = "my_list.convert"
    bl_label = "Convert to DDS"  
    
    #hides/grey buttons if list index is empty
    @classmethod
    def poll(cls, context):
        return context.scene.my_list

    def execute(self, context):
        my_list = context.scene.my_list
        index = context.scene.list_index
        
        scene = context.scene
        item = scene.my_list[scene.list_index]
        cvalue = scene.custom_values
        
        list_length = len(bpy.context.scene.my_list) - 1
        
        print(":: converting", item.name, "to", item.typedds)
        
        input_value = f'"{item.filepath}"'
        print("::", input_value)
        
        output_value = f'"{cvalue.outputpath}'
        print("::", output_value)
        
        if not ((cvalue.outputpath == "") or (cvalue.outputpath == "empty") or (cvalue.outputpath == "Empty")):
            output_value = " -o " + f'"{cvalue.outputpath}'
        else:
            output_value = ""
            print(":: output folder not provided, defaulting to current directory")                   

        
        print(pathlib.Path().resolve())
        #exe_dir= abs_tex_conv_path
        #exe_dir = str(pathlib.Path(__file__).parent.resolve()) + "texconv.exe"
        exe_dir = bpy.utils.script_path_user() + "\\addons\\texconv.exe"
        exe_dir = f'"{exe_dir}"'
        print(":: exe dir: ", exe_dir)
        
        command = exe_dir + " -f " + item.typedds + " -srgb" + " -y " + input_value + output_value
        print(":: arguments being sent:", command)     
   
        
        subprocess.call(command, shell=True)        
       


        return{'FINISHED'}
    
    
    
class LIST_OT_ConvertAll(Operator):
    """Convert all files to DDS format"""
        
    bl_idname = "my_list.convert_all"
    bl_label = "Convert all to DDS"  
    
    #hides/grey buttons if list index is empty
    @classmethod
    def poll(cls, context):
        return context.scene.my_list

    def execute(self, context):
        my_list = context.scene.my_list
        index = context.scene.list_index
        
        scene = context.scene
        item = scene.my_list[scene.list_index]
        
        cvalue = scene.custom_values
        
        list = len(bpy.context.scene.my_list)
        
        for i in range(list):  
            item = (scene.my_list[i])
            print(item)
        
            print(":: converting", item.name, "to", item.typedds)
            
            input_value = f'"{item.filepath}"'
            print("::", input_value)
            
            output_value = f'"{cvalue.outputpath}'
            print("::", output_value)
            
            if not ((cvalue.outputpath == "") or (cvalue.outputpath == "empty") or (cvalue.outputpath == "Empty")):
                output_value = " -o " + f'"{cvalue.outputpath}'
            else:
                output_value = ""
                print(":: output folder not provided, defaulting to current directory")                   

            
            print(pathlib.Path().resolve())
            #exe_dir= abs_tex_conv_path
            #exe_dir = str(pathlib.Path(__file__).parent.resolve()) + "texconv.exe"
            exe_dir = bpy.utils.script_path_user() + "\\addons\\texconv.exe"
            exe_dir = f'"{exe_dir}"'
            print(":: exe dir:", exe_dir)
            
            command = exe_dir + " -f " + item.typedds + " -srgb" + " -y " + input_value + output_value
            print(":: arguments being sent: ", command)     
       
            
            subprocess.call(command, shell=True)        
      
       


        return{'FINISHED'}



class LIST_OT_MoveItem(Operator):
    """Move an item in the list."""

    bl_idname = "my_list.move_item"
    bl_label = "Move an item in the list"

    direction: EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),))
    #hides/grey buttons if list index is empty
    @classmethod
    def poll(cls, context):
        return context.scene.my_list

    def move_index(self):
        """ Move index of an item render queue while clamping it. """

        index = bpy.context.scene.list_index
        list_length = len(bpy.context.scene.my_list) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        bpy.context.scene.list_index = max(0, min(new_index, list_length))

    def execute(self, context):
        my_list = context.scene.my_list
        index = context.scene.list_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        my_list.move(neighbor, index)
        self.move_index()

        return{'FINISHED'}
    
    
class OpenBatchImport(Operator, ImportHelper):
    """Import multiple image files."""

    bl_idname = "file.batch_import"
    bl_label = "Batch Import Images"   
    
    #filters file types
    filter_glob: StringProperty(
            default='*.jpg;*.jpeg;*.png;*.tga;*.hdr;*.ppm;*.hdr;*.pfm;*.bmp;*.jxr',
            options={'HIDDEN'}
        )
        
    directory: StringProperty(subtype='DIR_PATH')
    
    #array of files
    files: CollectionProperty(
                name="File Path",
                type=OperatorFileListElement,
                )
    

    def execute(self, context):
        
        return process_files(context, self.directory, self.files)  

        return{'FINISHED'}
    

            
            
class ListItem(PropertyGroup):
    """Group of properties representing an item in the list."""

    name: StringProperty(
           name="Texture Name",
           description="",
           default="")

    filepath: StringProperty(
           name="Image Filepath",
           description="",
           default="Empty",
           subtype = 'FILE_PATH')

           
    typedds : EnumProperty(
          name = "",
          description = "DXTn type",
          items =  [('DXT1', "DXT1", "Highest compression but loss in Alpha quality"),
                    ('DXT3', "DXT3", "Balance between DXT1 & DXT5"),
                    ('DXT5', "DXT5", "Lowest compression but increase in Alpha quality")
                ]
            )
class MyProperties(PropertyGroup):
    """Static values"""
        
    outputpath: StringProperty(
           name="Output Folder",
           description="",
           default="Empty",
           subtype = 'DIR_PATH')
    
    batchpath: StringProperty(
           name="Batch Import",
           description="",
           default="Empty",
           )
        

def register():

    bpy.utils.register_class(ListItem)
    bpy.utils.register_class(MyProperties)
    bpy.utils.register_class(MY_UL_List)
    bpy.utils.register_class(LIST_OT_NewItem)
    bpy.utils.register_class(LIST_OT_DeleteItem)
    bpy.utils.register_class(LIST_OT_ConvertItem)
    bpy.utils.register_class(LIST_OT_ConvertAll)
    bpy.utils.register_class(LIST_OT_MoveItem)
    bpy.utils.register_class(OpenBatchImport)
    bpy.utils.register_class(PT_ListExample)

    bpy.types.Scene.custom_values = PointerProperty(type= MyProperties)
    bpy.types.Scene.my_list = CollectionProperty(type = ListItem)
    bpy.types.Scene.list_index = IntProperty(name = "Index for my_list",
                                             default = 0)


def unregister():

    del bpy.types.Scene.my_list
    del bpy.types.Scene.list_index
    del bpy.types.Scene.custom_values

    bpy.utils.unregister_class(ListItem)
    bpy.utils.unregister_class(MY_UL_List)
    bpy.utils.unregister_class(LIST_OT_NewItem)
    bpy.utils.unregister_class(LIST_OT_DeleteItem)
    bpy.utils.unregister_class(LIST_OT_ConvertItem)
    bpy.utils.unregister_class(LIST_OT_ConvertAll)
    bpy.utils.unregister_class(LIST_OT_MoveItem)
    bpy.utils.unregister_class(OpenBatchImport)
    bpy.utils.unregister_class(PT_ListExample)


if __name__ == "__main__":
    register()