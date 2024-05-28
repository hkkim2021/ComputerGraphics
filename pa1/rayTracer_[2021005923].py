#!/usr/bin/env python3
# -*- coding: utf-8 -*
# sample_python aims to allow seamless integration with lua.
# see examples below

import os
import sys
import pdb  # use pdb.set_tcrace() for debugging
import code # or use code.interact(local=dict(globals(), **locals()))  for debugging.
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image 

class Color:
    def __init__(self, R, G, B):
        self.color = np.array([R, G, B]).astype(np.float64)

    # Gamma corrects this color.
    # @param gamma the gamma value to use (2.2 is generally used).
    def gammaCorrect(self, gamma):
        inverseGamma = 1.0 / gamma
        self.color = np.power(self.color, inverseGamma)

    def toUINT8(self):
        return (np.clip(self.color, 0, 1) * 255).astype(np.uint8)

class Sphere:
    def __init__(self, shader, center, radius):
        self.shader = shader
        self.center = center
        self.radius = radius

class Camera:
    def __init__(self, viewPoint, viewDir, projNormal, viewUp, projDistance, viewWidth, viewHeight):
        self.viewPoint = viewPoint
        self.viewDir = viewDir
        self.projNormal = projNormal
        self.viewUp = viewUp
        self.projDistance = projDistance
        self.viewWidth = viewWidth
        self.viewHeight = viewHeight

class Light:
    def __init__(self, position, intensity):
        self.position = position
        self.intensity = intensity

class Shader:
    def __init__(self, type):
        self.type = type

class Lambertian(Shader):
    def __init__(self,type, diffuseColor):
        self.type=type
        self.diffuseColor = diffuseColor

class Phong(Shader):
    def __init__(self,type, diffuseColor, specularColor, exponent):
        self.type=type
        self.diffuseColor = diffuseColor
        self.specularColor = specularColor
        self.exponent = exponent

def normalize(v):
    return v/np.sqrt(v@v)
    
def raytracing(ray, viewPoint, surfaceList):
    min_dis=sys.maxsize
    t_num=-1
    cnt=0

    for i in surfaceList:
        if i.__class__.__name__ == 'Sphere':
            a=np.sum(ray*ray)
            b=np.sum((viewPoint-i.center)*ray)
            c=np.sum((viewPoint-i.center)**2)-i.radius**2
            D=b**2-a*c

            if D>=0:
                if -b+np.sqrt(D)>=0 and min_dis>=(-b + np.sqrt(D))/a:
                    min_dis=(-b + np.sqrt(D))/a
                    t_num=cnt
                if -b-np.sqrt(D)>=0 and min_dis>=(-b - np.sqrt(D))/a:
                    min_dis=(-b - np.sqrt(D))/a
                    t_num=cnt
        cnt+= 1
    return min_dis, t_num
        

def shading(min_dis, t_num, ray, viewPoint, surfaceList, lightList):
    if t_num == -1:
        return np.array([0, 0, 0])
        
    else:
        a=0
        b=0
        c=0
        n=np.array([0, 0, 0])
        v= -min_dis * ray

        if surfaceList[t_num].__class__.__name__ == 'Sphere':
            n=normalize(viewPoint+min_dis*ray-surfaceList[t_num].center)

        for i in lightList:
            light=normalize(v+i.position-viewPoint)
            c_min_dis, c_num = raytracing(-light, i.position,surfaceList)

            if c_num == t_num:
                if surfaceList[t_num].shader.__class__.__name__ == 'Lambertian':
                    a+=surfaceList[t_num].shader.diffuseColor[0]*i.intensity[0]*max(0, np.dot(light, n))
                    b+=surfaceList[t_num].shader.diffuseColor[1]*i.intensity[1]*max(0, np.dot(light, n))
                    c+=surfaceList[t_num].shader.diffuseColor[2]*i.intensity[2]*max(0, np.dot(light, n)) 
                elif surfaceList[t_num].shader.__class__.__name__ == 'Phong':
                    v_unit=normalize(v)
                    h=v_unit+light
                    h=h/np.sqrt(np.sum(h * h))
                    a+=surfaceList[t_num].shader.diffuseColor[0]*max(0, np.dot(n, light))*i.intensity[0]+ surfaceList[t_num].shader.specularColor[0] * i.intensity[0] * pow(max(0, np.dot(n, h)),surfaceList[t_num].shader.exponent[0])
                    b+=surfaceList[t_num].shader.diffuseColor[1]*max(0, np.dot(n, light))*i.intensity[1]+ surfaceList[t_num].shader.specularColor[1]*i.intensity[1]*pow(max(0, np.dot(n, h)),surfaceList[t_num].shader.exponent[0])
                    c+=surfaceList[t_num].shader.diffuseColor[2]*max(0, np.dot(n, light))*i.intensity[2]+ surfaceList[t_num].shader.specularColor[2]*i.intensity[2]*pow(max(0, np.dot(n, h)),surfaceList[t_num].shader.exponent[0])

    result = Color(a,b,c)
    result.gammaCorrect(2.2)
    return result.toUINT8()

def main():
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()

    # set default values
    viewDir = np.array([0, 0, -1]).astype(np.float64)
    viewUp = np.array([0, 1, 0]).astype(np.float64)
    viewProjNormal = -1 * viewDir  # you can safely assume this. (no examples will use shifted perspective camera)
    viewWidth = 1.0
    viewHeight = 1.0
    projDistance = 1.0
    intensity = np.array([1, 1, 1]).astype(np.float64)  # how bright the light is.

    imgSize = np.array(root.findtext('image').split()).astype(np.int32)
    

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
       
    
    lightList=[]
    for c in root.findall('light'):
        position=np.array(c.findtext('position').split()).astype(np.float64)
        intensity=np.array(c.findtext('intensity').split()).astype(np.float64)
        lightList.append(Light(position,intensity))
    
    
    channels = 3
    img = np.zeros((imgSize[1], imgSize[0], channels), dtype = np.uint8)
    img[:, :] = 0

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
    
    for x in np.arange(imgSize[0]):
        for y in np.arange(imgSize[1]):
            ray=start+u_unit*x*x_pixel+v_unit*y*y_pixel
            min_dis, t_num=raytracing(ray, camera.viewPoint, surfaceList)
            img[y][x]= shading(min_dis, t_num, ray, camera.viewPoint, surfaceList, lightList)

    rawimg = Image.fromarray(img, 'RGB')
    #rawimg.save('out.png')
    rawimg.save(sys.argv[1]+'.png')


if __name__=="__main__":
    main()