import bpy

# コレクションの中のオブジェクトとサブコレクションの名前のプレフィクスを一気に更新する
# Panel: RenamePrefixInCollection

# プロパティを定義
class RenamePrefixInCollection(bpy.types.Panel):
    bl_label = "RenamePrefixInCollection"
    bl_idname = "VIEW3D_PT_text_input"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "RenamePrefixInCollection"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "my_collection", text="コレクション")
        layout.prop(context.scene, "my_prefix", text="新しいプレフィックス")
        layout.operator("object.rename_prefix_in_collection", text="更新する")

# オペレーターを定義
class RenamePrefixInCollectionOperator(bpy.types.Operator):
    bl_idname = "object.rename_prefix_in_collection"
    bl_label = "コレクション内のプレフィクスを書き換える"

    def execute(self, context):
        # ボタンの動作を記述
        prefix = context.scene.my_prefix
        collection = context.scene.my_collection
        self.rename_prefix_in_collection(collection, prefix)
        self.report({'INFO'}, f"入力: {collection.name} : {prefix}")
        return {'FINISHED'}
    
    def rename_prefix_in_collection(self, collection, prefix):
        print(f"rename :{collection}")
        for obj in collection.objects:
            obj.name = '.'.join(obj.name.split('.')[:-1]) + f".{prefix}"
        for sub_col in collection.children:
            sub_col.name = '.'.join(sub_col.name.split('.')[:-1]) + f".{prefix}"
            self.rename_prefix_in_collection(sub_col, prefix)
        pass

# プロパティ登録
def register():
    bpy.utils.register_class(RenamePrefixInCollection)
    bpy.utils.register_class(RenamePrefixInCollectionOperator)
    bpy.types.Scene.my_prefix = bpy.props.StringProperty(
        name="Prefix",
        description="新しいプレフィックス",
        default=""
    )
    bpy.types.Scene.my_collection = bpy.props.PointerProperty(
        name="My Collection",
        description="選択するコレクションを指定",
        type=bpy.types.Collection
    )

def unregister():
    bpy.utils.unregister_class(RenamePrefixInCollection)
    bpy.utils.unregister_class(RenamePrefixInCollectionOperator)
    del bpy.types.Scene.my_prefix
    del bpy.types.Scene.my_collection

if __name__ == "__main__":
    register()