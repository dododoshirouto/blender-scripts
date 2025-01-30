import bpy
import bmesh
import mathutils

class OBJECT_OT_LerpNormals(bpy.types.Operator):
    bl_idname = "object.lerp_normals"
    bl_label = "選択頂点の法線を補間 + YZ平面ノーマライズ"
    bl_options = {'REGISTER', 'UNDO'}

    lerp_factor: bpy.props.FloatProperty(
        name="Lerp Factor",
        description="現在の法線とローカル軸の補間率",
        default=0.5,
        min=0.0,
        max=1.0
    )

    axis: bpy.props.EnumProperty(
        name="Lerp Axis",
        description="補間するローカル軸",
        items=[
            ('X+', "X+ Axis", "ローカルX+方向"),
            ('X-', "X- Axis", "ローカルX-方向"),
            ('Y+', "Y+ Axis", "ローカルY+方向"),
            ('Y-', "Y- Axis", "ローカルY-方向"),
            ('Z+', "Z+ Axis", "ローカルZ+方向"),
            ('Z-', "Z- Axis", "ローカルZ-方向"),
        ],
        default='Y-'
    )

    threshold: bpy.props.FloatProperty(
        name="X座標の閾値",
        description="X座標がこの値に近い頂点の法線をYZ平面にノーマライズ",
        default=0.01,
        min=0.0
    )

    def execute(self, context):
        obj = context.object
        if obj is None or obj.type != 'MESH':
            self.report({'WARNING'}, "メッシュオブジェクトを選択してください")
            return {'CANCELLED'}

        self.report({'INFO'}, f"法線補間: Lerp Factor={self.lerp_factor}, Axis={self.axis}, 閾値={self.threshold}")

        success = self.lerp_normals(obj, self.lerp_factor, self.axis, self.threshold)

        if success:
            self.report({'INFO'}, "法線補間成功！")
        else:
            self.report({'ERROR'}, "法線補間失敗！")

        return {'FINISHED'}

    def lerp_normals(self, obj, lerp_factor, axis, threshold):
        try:
            bpy.ops.object.mode_set(mode='OBJECT')

            mesh = obj.data
            bm = bmesh.new()
            bm.from_mesh(mesh)

            # **インデックステーブルを更新**
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.faces.ensure_lookup_table()

            bm.normal_update()

            # シャープエッジを取得
            sharp_edges = {e for e in bm.edges if not e.smooth}

            # 頂点ごとの法線を格納
            vertex_normals = {v: mathutils.Vector((0, 0, 0)) for v in bm.verts}

            for face in bm.faces:
                for vert in face.verts:
                    shared_edges = {e for e in vert.link_edges if e in sharp_edges}
                    if shared_edges:
                        vertex_normals[vert] += face.normal
                    else:
                        vertex_normals[vert] += vert.normal

            for vert in vertex_normals:
                vertex_normals[vert].normalize()

            local_axis = {
                'X+': mathutils.Vector((1, 0, 0)),
                'X-': mathutils.Vector((-1, 0, 0)),
                'Y+': mathutils.Vector((0, 1, 0)),
                'Y-': mathutils.Vector((0, -1, 0)),
                'Z+': mathutils.Vector((0, 0, 1)),
                'Z-': mathutils.Vector((0, 0, -1)),
            }[axis]

            print("\n[デバッグ] 選択頂点の元の法線ベクトル:")

            # カスタム法線のリスト作成
            loop_normals = [mathutils.Vector((0, 0, 0))] * len(mesh.loops)

            for loop in mesh.loops:
                vert = bm.verts[loop.vertex_index]

                # **選択されていない頂点は無視**
                if not vert.select:
                    loop_normals[loop.index] = loop.normal
                    continue

                normal = vertex_normals[vert]

                # **X座標が `threshold` に近い場合、YZ平面にノーマライズ**
                if abs(vert.co.x) < threshold:
                    normal = mathutils.Vector((0, normal.y, normal.z)).normalized()
                    print(f"  頂点 {vert.index} (X≈0) → {normal} (YZ平面ノーマライズ)")
                
                # **Lerp補間**
                new_normal = normal.lerp(local_axis, lerp_factor).normalized()
                print(f"  頂点 {vert.index} → {new_normal}")

                loop_normals[loop.index] = new_normal

            # **カスタム法線を適用**
            mesh.normals_split_custom_set(loop_normals)

            # **Auto Smooth を有効にする**
            if hasattr(mesh, "use_auto_smooth"):
                mesh.use_auto_smooth = True

            bm.free()

            bpy.ops.object.mode_set(mode='EDIT')

            return True
        except Exception as e:
            print(f"[エラー] {e}")
            self.report({'ERROR'}, f"エラー: {e}")
            return False

class VIEW3D_PT_LerpNormalsPanel(bpy.types.Panel):
    bl_label = "法線補間ツール"
    bl_idname = "VIEW3D_PT_lerp_normals"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "法線編集"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.lerp_normals")

classes = [OBJECT_OT_LerpNormals, VIEW3D_PT_LerpNormalsPanel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
