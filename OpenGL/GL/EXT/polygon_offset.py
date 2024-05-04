'''OpenGL extension EXT.polygon_offset

This module customises the behaviour of the 
OpenGL.raw.GL.EXT.polygon_offset to provide a more 
Python-friendly API

Overview (from the spec)
	
	The depth values of fragments generated by rendering polygons are
	displaced by an amount that is proportional to the maximum absolute
	value of the depth slope of the polygon, measured and applied in window
	coordinates.  This displacement allows lines (or points) and polygons
	in the same plane to be rendered without interaction -- the lines
	rendered either completely in front of or behind the polygons
	(depending on the sign of the offset factor).  It also allows multiple
	coplanar polygons to be rendered without interaction, if different
	offset factors are used for each polygon.  Applications include
	rendering hidden-line images, rendering solids with highlighted edges,
	and applying `decals' to surfaces.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/EXT/polygon_offset.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.EXT.polygon_offset import *
from OpenGL.raw.GL.EXT.polygon_offset import _EXTENSION_NAME

def glInitPolygonOffsetEXT():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION