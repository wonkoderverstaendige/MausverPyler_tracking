__author__ = 'dfangstrom'
from Box2D import *

exampleWorld = b2AABB()
exampleWorld.lowerBound.Set(-100, -100)
exampleWorld.upperBound.Set(100, 100)
gravity = (0, -10)
doSleep = True
boxWorld = b2World(exampleWorld, gravity, doSleep)

groundBodyDef = b2BodyDef()
groundBodyDef.position = (0, -10)
groundBody = boxWorld.CreateBody(groundBodyDef)
groundShapeDef = b2PolygonDef()
groundShapeDef.SetAsBox(50, 10)
groundBody.CreateShape(groundShapeDef)

dynBodyDef = b2BodyDef()
dynBodyDef.position = (0, 4)
dynBody = boxWorld.CreateBody(dynBodyDef)
dynShapeDef = b2PolygonDef()
dynShapeDef.SetAsBox(1, 1)
dynShapeDef.density = 1
dynShapeDef.friction = 0.3
dynBody.CreateShape(dynShapeDef)
dynBody.SetMassFromShapes()
dynBodyDef.allowSleep = True
dynBodyDef.isSleeping = False

timeStep = 1.0/60.0
velocityIterations = 10
positionIterations = 8

for dynBody in boxWorld:
    dynBody.WakeUp()
    dynBody = dynBody.GetNext()

for i in range(60):
    boxWorld.Step(timeStep, velocityIterations, positionIterations)
    print dynBody.position, dynBody.angle
