"""Low-profile fighter canopy, shared by the clean builder and existing-file edit.

Blender -Y is forward. The glass is a smooth half-ellipse loft with an elongated
teardrop planform, raked windscreen and a thin surrounding gasket.
"""
import math
import bpy
import bmesh

CANOPY_NAMES = (
    '03 | Armored canopy frame', '04 | Canopy glass', '05 | Canopy reflection',
    '05 | Windscreen hoop', '05 | Canopy sill',
)

# y, half-width, lower edge, crown rise. Compact crown blends toward the nose.
# Peak height is about 0.58; the forward section is deliberately much flatter.
PROFILES = [
    (-1.84, .010, .424, .006), (-1.68, .092, .375, .074),
    (-1.44, .20, .36, .105), (-1.14, .26, .38, .105),
    (-.73, .28, .385, .145), (-.25, .27, .385, .170),
    (.18, .225, .365, .145), (.47, .125, .415, .075),
    (.65, .010, .465, .008),
]
# Clear the fuselage's ink shell while retaining the low crown and noseward rake.
PROFILES = [(y,w,z+.024,h) for y,w,z,h in PROFILES]

def profile_at(y):
    for i in range(len(PROFILES)-1):
        a,b=PROFILES[i:i+2]
        if a[0] <= y <= b[0]:
            t=(y-a[0])/(b[0]-a[0])
            before=PROFILES[max(0,i-1)]
            after=PROFILES[min(len(PROFILES)-1,i+2)]
            values=[]
            for k in range(1,4):
                # Hermite tangents are measured along y, retaining smooth curvature.
                m0=(b[k]-before[k])/(b[0]-before[0])*(b[0]-a[0])
                m1=(after[k]-a[k])/(after[0]-a[0])*(b[0]-a[0])
                values.append((2*t**3-3*t*t+1)*a[k]+(t**3-2*t*t+t)*m0
                              +(-2*t**3+3*t*t)*b[k]+(t**3-t*t)*m1)
            return (y,*values)
    return PROFILES[0] if y<PROFILES[0][0] else PROFILES[-1]

def surface(y, angle, lift=0):
    _,width,base,rise=profile_at(y)
    return (width*math.cos(angle),y,base+rise*math.sin(angle)+lift)

def build_canopy(collection, root, glass, frame, highlight, ink):
    created=[]
    def mesh(name,verts,faces,material,smooth=False,outline=False):
        data=bpy.data.meshes.new(name)
        data.from_pydata(verts,[],faces)
        data.update()
        bm=bmesh.new()
        bm.from_mesh(data)
        bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
        bm.to_mesh(data)
        bm.free()
        for poly in data.polygons: poly.use_smooth=smooth
        obj=bpy.data.objects.new(name,data)
        collection.objects.link(obj)
        obj.parent=root
        obj['kestrel_canopy']=True
        data.materials.append(material)
        if outline:
            data.materials.append(ink)
            shell=obj.modifiers.new('Ink silhouette','SOLIDIFY')
            shell.thickness=.012
            shell.offset=1
            shell.use_flip_normals=True
            shell.use_rim=False
            shell.material_offset=1
        created.append(obj)
        return obj

    def curve(name,points,material,width,closed=False):
        data=bpy.data.curves.new(name,'CURVE')
        data.dimensions='3D'
        data.bevel_depth=width
        data.bevel_resolution=2
        spline=data.splines.new('POLY')
        spline.points.add(len(points)-1)
        for pt,co in zip(spline.points,points): pt.co=(*co,1)
        spline.use_cyclic_u=closed
        obj=bpy.data.objects.new(name,data)
        collection.objects.link(obj)
        obj.parent=root
        obj['kestrel_canopy']=True
        data.materials.append(material)
        created.append(obj)
        return obj

    rows=[profile_at(a[0]+(b[0]-a[0])*j/4)
          for a,b in zip(PROFILES,PROFILES[1:]) for j in range(4)]+[PROFILES[-1]]
    # Slender saddle drops into the existing fuselage, leaving no floating glass.
    verts=[]
    for y,w,z,h in rows:
        verts += [(-w-.025,y,z-.012),(w+.025,y,z-.012),
                  (-w-.025,y,z-.13),(w+.025,y,z-.13)]
    faces=[]
    for i in range(len(rows)-1):
        a=i*4; b=(i+1)*4
        faces += [(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),
                  (a,a+2,b+2,b),(a+1,b+1,b+3,a+3)]
    faces += [(0,1,3,2),tuple((len(rows)-1)*4+k for k in (0,2,3,1))]
    mesh(CANOPY_NAMES[0],verts,faces,frame,True,True)

    arc_segments=16
    verts=[surface(row[0],math.pi*j/arc_segments)
           for row in rows for j in range(arc_segments+1)]
    stride=arc_segments+1
    faces=[]
    for i in range(len(rows)-1):
        for j in range(arc_segments):
            a=i*stride+j
            faces.append((a,a+1,a+stride+1,a+stride))
        a=i*stride; b=(i+1)*stride
        faces.append((a,b,b+arc_segments,a+arc_segments))
    faces += [tuple(range(arc_segments,-1,-1)),
              tuple((len(rows)-1)*stride+j for j in range(stride))]
    mesh(CANOPY_NAMES[1],verts,faces,glass,True,True)

    # Fixed, raked windscreen ahead of the main bubble; minimal structural hoop.
    curve(CANOPY_NAMES[3],[surface(-1.12,math.pi*j/32,.008) for j in range(33)],frame,.012)
    rim=[(-w,y,z+.002) for y,w,z,h in rows]
    rim += [(w,y,z+.002) for y,w,z,h in reversed(rows)]
    curve(CANOPY_NAMES[4],rim,frame,.012,True)

    # Tapered reflection conforms to the glass rather than floating over its crown.
    verts=[]
    for i in range(21):
        t=i/20
        y=-1.19+1.36*t
        angle=.87+.16*t
        half_width=.026*math.sin(math.pi*t)**.6+.001
        verts += [surface(y,angle-half_width,.009),surface(y,angle+half_width,.009)]
    mesh(CANOPY_NAMES[2],verts,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(20)],highlight,True)
    return created
