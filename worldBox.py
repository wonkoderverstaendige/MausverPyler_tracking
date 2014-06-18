#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 01. June 214 16:34
@author: <'Daniel Fängström'> daniel.fengstrom@gmail.com

"""

import Box2D
from Box2D import *
import pygame
from pygame.locals import *

boxScreen = pygame.display.set_mode((640, 480), 0, 32)
pygame.display.set_caption('Just a pygame test')
boxClock = pygame.time.Clock()

exampleWorld = b2World()
#exampleWorld.lowerBound.Set(-100, -100)
#exampleWorld.upperBound.Set(100, 100)
gravity = (0, -10)
doSleep = True
boxWorld = b2World(gravity, doSleep)

#groundBodyDef = b2BodyDef()
#groundBodyDef.position = (10, -10)
groundBody = boxWorld.CreateStaticBody(position=(10, 2), shapes=b2PolygonShape(box=(50, 5)))
groundBox = b2PolygonShape(box=(50, 10))
groundBoxFixture = b2FixtureDef(shape=groundBox)
groundBody.CreateFixture(groundBoxFixture)

#groundShapeDef = b2JointDef()
#groundShapeDef.SetAsBox(50, 10)
#groundBody.CreateShape(groundShapeDef)

#dynBodyDef = b2BodyDef()
#dynBodyDef.position = (0, 4)
dynBody = boxWorld.CreateDynamicBody(position=(10, 35))
dynBox = dynBody.CreatePolygonFixture(box=(1, 1), density=1, friction=0.3)
#dynShapeDef = b2JointDef()
#dynShapeDef.SetAsBox(1, 1)
#dynShapeDef.density = 1
#dynShapeDef.friction = 0.3
#dynBody.CreateShape(dynShapeDef)
#dynBody.SetMassFromShapes()
#dynBodyDef.allowSleep = True
#dynBodyDef.isSleeping = False
#dynBox = dynBody.CreatePolygonFixture(box=(2, 1), density=1, friction=0.3)

secBody = boxWorld.CreateDynamicBody(position=(11, 4))
secBox = secBody.CreatePolygonFixture(box=(1, 1), density=0.1, friction=0.1)


timeStep = 1.0/60.0
velocityIterations = 6
positionIterations = 2

colors = {
    groundBody: (255, 255, 255, 255),
    dynBody: (127, 127, 127, 255),
    secBody: (64, 190, 100, 255),
}

simRunning = True
while simRunning:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            simRunning = False

    boxScreen.fill((0, 0, 0, 0))
    for body in (groundBody, dynBody, secBody):
        #positionBody = body.position()
        #massBody = body.GetMass()
        #for otherBody in (groundBody, dynBody, secBody):
        #    otherPosition = otherBody.GetWorldCenter()
        #    otherMass = otherBody.GetMass()
        #    diffPosition = otherPosition - positionBody
        #    lengthDiff = diffPosition.Length()
        #    endForce = (massBody * otherMass / (lengthDiff*lengthDiff))
        #    diffPosition.Normalize()
        #    body.ApplyForce(endForce * diffPosition, positionBody)
        #    otherBody.ApplyForce(-endForce * diffPosition, otherPosition)
        for fixture in body.fixtures:
            shape = fixture.shape
            vertices = [(body.transform*v)*20.0 for v in shape.vertices]
            vertices = [(v[0], 640-v[1]) for v in vertices]
            #print(boxScreen)
            #print(colors[dynBody])
            #print(body)
            #print(vertices)
            pygame.draw.polygon(boxScreen, colors[body], vertices)



    boxWorld.Step(timeStep, 10, 10)
    pygame.display.flip()
    boxClock.tick(60.0)

pygame.quit()
print('Done!')

#for dynBody in boxWorld:
#    dynBody.WakeUp()
#    dynBody = dynBody.GetNext()

#for i in range(60):
#    boxWorld.Step(timeStep, velocityIterations, positionIterations)
#    print dynBody.position, dynBody.angle
