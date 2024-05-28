import os
import sys
import pdb  # use pdb.set_trace() for debugging
import code # or use code.interact(local=dict(globals(), **locals()))  for debugging.
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image 
class Color:
    def __init__(self, R, G, B):
        self.color=np.array([R,G,B]).astype(np.float64)

    # Gamma corrects this color.
    # @param gamma the gamma value to use (2.2 is generally used).
    def gammaCorrect(self, gamma):
        inverseGamma = 1.0 / gamma;
        self.color=np.power(self.color, inverseGamma)

    def toUINT8(self):
        return (np.clip(self.color, 0,1)*255).astype(np.uint8)
      
class Camera:
    def __init__(self, viewPoint, viewDir, projNormal, viewUp, projDistance, viewWidth, viewHeight):
        self.viewPoint=viewPoint
        self.viewDir=viewDir
        self.projNormal=projNormal
        self.viewUp=viewUp
        self.projDistance=projDistance
        self.viewWidth=viewWidth
        self.viewHeigth=viewHeight

class Shader:
    def __init__(self, type):
        self.type=type
        
class Lambertian(Shader):
    def __init__(self, type, diffuseColor):
        self.type=type
        self.diffuseColor= diffuseColor

class Phong(Shader):
    def __init__(self, type, diffuseColor, specularColor, exponent):
        self.type=type
        self.diffuseColor= diffuseColor
        self.specularColor=specularColor
        self.exponent=exponent

class Sphere:
    def __init__(self, center, radius, shader):
        self.center=center
        self.radius=radius
        self.shader=shader

class Light:
    def __init__(self, position, intensity):
        self.position=position
        self.intensity=intensity

def normalize(v):
    return v/np.sqrt(v@v)

def rayTracing(surfaceList, d, viewPoint):
    d=normalize
    max= sys.maxsize
    c=0
    for i in surfaceList:
        if i.__class__.__name__=='Sphere':
           a=d@d
           b=d@(viewPoint-i.center)
           c=(viewPoint-i.center)**2-(i.radius)**2

           D=b**2-a*c

           if(D>=0):
               if (-b+np.sqrt(D))>=0 and (-b+np.sqrt(D))<max:
                   distance=-b+np.sqrt(D)
                   t_num=c
               if (-b-np.sqrt(D))>=0 and (-b+np.sqrt(D))<max:
                   distance=-b+np.sqrt(D)
                   t_num=c
        c+=1

    return[distance, t_num]
                   
               

def shading:

def main():
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()

    # set default values
    viewDir=np.array([0,0,-1]).astype(np.float64)
    viewUp=np.array([0,1,0]).astype(np.float64)
    viewProjNormal=-1*viewDir  # you can safely assume this. (no examples will use shifted perspective camera)
    viewWidth=1.0
    viewHeight=1.0
    projDistance=1.0
    intensity=np.array([1,1,1]).astype(np.float64)  # how bright the light is.
    print(np.cross(viewDir, viewUp))

    imgSize=np.array(root.findtext('image').split()).astype(np.int32)
    
    #camera
    for c in root.findall('camera'):
        viewPoint=np.array(c.findtext('viewPoint').split()).astype(np.float64)
        print('viewpoint', viewPoint)
        viewDir=np.array(c.findtext('viewDir').split()).astype(np.float64)
        print('viewDir', viewDir)
        projNormal=np.array(c.findtext('projNormal').split()).astype(np.float64)
        print('projNormal', projNormal)
        viewUp=np.array(c.findtext('viewUp').split()).astype(np.float64)
        print('viewUp', viewUp)
        if c.findtext('projDistance'):
            projDistance=np.array(c.findtext('projDistance').split()).astype(np.float64)
            print('projDistance', projDistance)
        viewWidth=np.array(c.findtext('viewWidth').split()).astype(np.float64)
        print('viewWidth', viewWidth)
        viewHeight=np.array(c.findtext('viewHeight').split()).astype(np.float64)
        print('viewHeight', viewHeight)
        
    camera=Camera(viewPoint, viewDir, projNormal, viewUp, projDistance, viewWidth, viewHeight)
    
    #shader
    surfaceList=[]
    for c in root.findall('surface'):
        if c.get('type')=='Sphere':
            center=np.array(c.findtext('center').split()).astype(np.float64)
            radius=np.array(c.findtext('radius').split()).astype(np.float64)
 
        s_ref=c.find('shader').get('ref')
        
        for d in root.findall('shader'):
                if d.get('name')==s_ref:
                    s_type=d.get('type')
                    if s_type =='Phong':
                        diffuseColor_c=np.array(d.findtext('diffuseColor').split()).astype(np.float64)
                        specularColor_c=np.array(d.findtext('specularColor').split()).astype(np.float64)
                        exponent_c=np.array(d.findtext('exponent').split()).astype(np.float64)
                        shader=Phong(s_type, diffuseColor_c, specularColor_c, exponent_c)
                    else:
                        diffuseColor_c=np.array(d.findtext('diffuseColor').split()).astype(np.float64)
                        shader=Lambertian(s_type, diffuseColor_c)

                    surfaceList.append(Sphere(shader, center, radius))
    #code.interact(local=dict(globals(), **locals()))  
    
    #light
    lightList=[]
    for c in root.findall('light'):
        position=np.array(c.findtext('position').split()).astype(np.float64)
        intensity=np.array(c.findtext('intensity').split()).astype(np.float64)
        lightList.append(Light(position,intensity))
        

    # Create an empty image
    channels=3
    img = np.zeros((imgSize[1], imgSize[0], channels), dtype=np.uint8)
    img[:,:]=0
    
    w=camera.viewDir
    u=np.cross(w,camera.viewUp)
    v=np.cross(w,u)
    w_unit=normalize(w)
    u_unit=normalize(u)
    v_unit=normalize(v)

    x_pixel=camera.viewWidth/imgSize[0]
    y_pixel=camera.viewHeight/imgSize[1]

    w_offset=w_unit*camera.projDistance
    u_offset=u_unit*x_pixel*((imgSize[0]/2)+0.5)
    v_offset=v_unit*y_pixel*((imgSize[1]/2)+0.5)
    start=w_offset-u_offset-v_offset
    
    for x in np.arrange(imgSize[0]):
        for y in np.arrange(imgSize[1]):
            ray=start+u_unit*x*x_pixel+v_unit*y*y_pixel
            tmp=rayTracing(surfaceList, ray, camera.viewPoint)
            img[y][x]= shading(tmp[0], ray, camera.viewPoint, surfaceList, tmp[1], lightList)

    rawimg = Image.fromarray(img, 'RGB')
    #rawimg.save('out.png')
    rawimg.save(sys.argv[1]+'.png')


if __name__=="__main__":
    main()