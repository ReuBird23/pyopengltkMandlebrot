'''OpenGL extension SGIX.subsample

This module customises the behaviour of the 
OpenGL.raw.GL.SGIX.subsample to provide a more 
Python-friendly API

Overview (from the spec)
	
		Many video image formats and compression techniques utilize
		various component subsamplings, so it is necessary to provide a
		mechanism to specify the up- and down-sampling of components as
		pixel data is drawn from and read back to the client. Though
		subsampled components are normally associated with the video
		color space, YCrCb, use of subsampling in OpenGL does not imply
		a specific color space.
	
		This extension defines new pixel storage modes that are used in
		the conversion of image data to and from component subsampled
		formats on the client side. The extension defines a new pixel
		storage mode to specify these sampling patterns, there are
		three legal values (PIXEL_SUBSAMPLE_4444_SGIX, 
		PIXEL_SUBSAMPLE_4242_SGIX, and 
	        PIXEL_SUBSAMPLE_2424_SGIX).
	
		When pixel data is received from the client and an unpacking
		upsampling mode other than PIXEL_SUBSAMPLE_4444_SGIX is 
	        specified, the upsampling is performed via replication, 
	        unless otherwise specified by RESAMPLE_SGIX.
	
		Similarly, when pixel data is read back to the client and a
		packing downsampling mode other than 
	        PIXEL_SUBSAMPLE_4444_SGIX is specified, downsampling is 
	        performed via simple component decimation (point sampling), 
	        unless otherwise specified by RESAMPLE_SGIX.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/SGIX/subsample.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.SGIX.subsample import *
from OpenGL.raw.GL.SGIX.subsample import _EXTENSION_NAME

def glInitSubsampleSGIX():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION