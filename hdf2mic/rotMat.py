#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
  Author:  Access e.V., Copyright 2018
  
"""

import math
import numpy as np


def eulerAnglesToRotationMatrix(eulerRad, toMicress):
    """
    Parameters
    ----------
    eulerRad : list(3) float
        3 euler angles (zx'z'') in rad
    toMICRESS : bool
        rotation to (True) or from (False) MICRESS axis system
        
    Returns:
    --------
        R : 3x3 np array float
            resulting rotation defined as rotation matrix

    Notes:
    ------
        Can be made more performant or more general  
        Check: quaternion comparison (e.g. given by MICRESS with old and new angles)
               (q0,q1,q2,q3) -> (q0,q1,-q3,q2)
    """

    [phi, theta, psi] = eulerRad

    # z 

    R0 = np.array([[math.cos(phi), -math.sin(phi), 0],
                   [math.sin(phi), math.cos(phi), 0],
                   [0, 0, 1]
                   ])
    # x'             
    R1 = np.array([[1, 0, 0],
                   [0, math.cos(theta), -math.sin(theta)],
                   [0, math.sin(theta), math.cos(theta)]
                   ])
    # z''                 
    R2 = np.array([[math.cos(psi), -math.sin(psi), 0],
                   [math.sin(psi), math.cos(psi), 0],
                   [0, 0, 1]
                   ])

    Ram = np.array([[1, 0, 0],
                    [0, 0, 1],
                    [0, -1, 0]
                    ])
    Rma = np.array([[1, 0, 0],
                    [0, 0, -1],
                    [0, 1, 0]
                    ])
    if (not toMicress):
        Ram, Rma = Rma, Ram

    REuler = np.dot(np.dot(R0, R1), R2)
    R = np.dot(np.dot(Rma, REuler), Ram)
    return R


# Checks if a matrix is a valid rotation matrix.
def isRotationMatrix(R):
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype=R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n < 1e-6


def rotationMatrixToEulerAngles(R):
    assert (isRotationMatrix(R))
    #     Bestimmung von theta
    #     --------------------
    cosTheta = R[2, 2]

    if cosTheta > 1:
        cosTheta = 1
    if cosTheta < -1:
        cosTheta = -1
    sinTheta = math.sqrt(1 - cosTheta * cosTheta)
    theta = math.acos(cosTheta)

    #     Sonderfall theta = 0
    #     --------------------
    if abs(sinTheta) < 1e-5:
        theta = 0
        psi = 0
        sinPhi = R[1, 0]
        cosPhi = R[0, 0]
        if sinPhi > 1:
            sinPhi = 1
        if sinPhi < -1:
            sinPhi = -1
        phi = math.asin(sinPhi)
        if abs(math.cos(phi) - cosPhi) > 5e-3:
            phi = math.pi - phi
        if phi > math.pi + 1e-6:
            phi = phi - 2 * math.pi

    else:

        #       Bestimmung von phi
        #       --------------------
        sinPhi = R[0, 2] / sinTheta
        cosPhi = -R[1, 2] / sinTheta
        if sinPhi > 1:
            sinPhi = 1
        if sinPhi < -1:
            sinPhi = -1
        phi = math.asin(sinPhi)
        if abs(math.cos(phi) - cosPhi) > 5e-3:
            phi = math.pi - phi
        if phi > math.pi + 1e-6:
            phi = phi - 2 * math.pi

        #       Bestimmung von psi
        # !       --------------------
        sinPsi = R[2, 0] / sinTheta
        cosPsi = R[2, 1] / sinTheta
        if sinPsi > 1:
            sinPsi = 1
        if sinPsi < -1:
            sinPsi = -1
        psi = math.asin(sinPsi)
        if abs(math.cos(psi) - cosPsi) > 1e-3:
            psi = math.pi - psi
        if psi > math.pi + 1e-6:
            psi = psi - 2 * math.pi

    if phi < 0:
        phi += 2 * math.pi
    if theta < 0:
        theta += 2 * math.pi
    if psi < 0:
        psi += 2 * math.pi

    return np.array([phi / (math.pi / 180.), theta / (math.pi / 180.), psi / (math.pi / 180.)])


# external interface function
# ===========================
def rotate(eulerDegree, toMICRESS):
    eulerRad = []
    for val in eulerDegree:
        val = val * math.pi / 180.
        if val < 0:
            val += 2 * math.pi
        eulerRad.append(val)
    R = eulerAnglesToRotationMatrix(eulerRad, toMICRESS)
    return rotationMatrixToEulerAngles(R)
