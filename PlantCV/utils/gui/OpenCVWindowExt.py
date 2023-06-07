# Based on https://github.com/DennisLiu1993/Zoom-In-Out-with-OpenCV by BoKuan Liu
# Ported over to Python, and extended to support ROI drawing
"""
BSD 2-Clause License

Copyright (c) 2022, BoKuan Liu, Curtis Kennedy
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import cv2

def MouseCall(event,x,y,flags,param):
    pParent: CopenCVWindowExt = param
    if event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0 and pParent.m_iScaleTimes != pParent.m_iMaxScaleTimes:
            pParent.m_iScaleTimes+=1
        elif flags < 0 and pParent.m_iScaleTimes != pParent.m_iMinScaleTimes:
            pParent.m_iScaleTimes-=1
        
        if pParent.m_iScaleTimes == 0:
            pParent.m_dCompensationX = 0
            pParent.m_dCompensationY = 0

        x = pParent.ptLButtonDown[0]
        y = pParent.ptLButtonDown[1]
        dPixelX = (pParent.m_iHorzScrollBarPos + x + pParent.m_dCompensationX) / pParent.m_dNewScale
        dPixelY = (pParent.m_iVertScrollBarPos + y + pParent.m_dCompensationY) / pParent.m_dNewScale
        
        pParent.m_dNewScale = pParent.m_dInitialScale * pow(pParent.m_dScaleRatio, pParent.m_iScaleTimes)

        if pParent.m_iScaleTimes != 0:
            iW = pParent.m_iOrgW
            iH = pParent.m_iOrgH
            pParent.m_iHorzScrollBarRange_Max = int (pParent.m_dNewScale * iW - pParent.m_dInitialScale * iW)
            pParent.m_iVertScrollBarRange_Max = int (pParent.m_dNewScale * iH - pParent.m_dInitialScale * iH)
            iBarPosX = int(dPixelX * pParent.m_dNewScale - x + 0.5)
            iBarPosY = int(dPixelY * pParent.m_dNewScale - y + 0.5)
            pParent.SetHorzBarPos(iBarPosX)
            pParent.SetVertBarPos(iBarPosY)
            pParent.m_dCompensationX = -iBarPosX + (dPixelX * pParent.m_dNewScale - x)
            pParent.m_dCompensationY = -iBarPosY + (dPixelY * pParent.m_dNewScale - y)
        else:
            pParent.m_iHorzScrollBarPos = 0
            pParent.m_iVertScrollBarPos = 0
        pParent.RefreshImage()
    
    elif event == cv2.EVENT_RBUTTONDOWN:
        pParent.ptRButtonDown[0] = x
        pParent.ptRButtonDown[1] = y
        pParent.ptLButtonDown[0] = x
        pParent.ptLButtonDown[1] = y
        pParent.m_iHorzScrollBarPos_copy = pParent.m_iHorzScrollBarPos
        pParent.m_iVertScrollBarPos_copy = pParent.m_iVertScrollBarPos

    elif flags == cv2.EVENT_FLAG_RBUTTON:
        iRButtonOffsetX = x - pParent.ptRButtonDown[0]
        iRButtonOffsetY = y - pParent.ptRButtonDown[1]

        iBarPosX = pParent.m_iHorzScrollBarPos_copy - iRButtonOffsetX
        pParent.SetHorzBarPos(iBarPosX)

        iBarPosY = pParent.m_iVertScrollBarPos_copy - iRButtonOffsetY
        pParent.SetVertBarPos(iBarPosY)

        pParent.RefreshImage()

    elif event == cv2.EVENT_MOUSEMOVE:
        pParent.ptLButtonDown[0] = x
        pParent.ptLButtonDown[1] = y
        pParent.m_iHorzScrollBarPos_copy = pParent.m_iHorzScrollBarPos
        pParent.m_iVertScrollBarPos_copy = pParent.m_iVertScrollBarPos

    elif event == cv2.EVENT_LBUTTONDOWN:
        # convert x and y to correct positions on original image
        # must account for both scale and the scrollbar positions
        correct_x = x
        correct_y = y

        if pParent.m_iScaleTimes == 0:
            dPixelX = x//pParent.m_dInitialScale
            dPixelY = y//pParent.m_dInitialScale
        else:
            dPixelX = (pParent.m_iHorzScrollBarPos + x + pParent.m_dCompensationX) / pParent.m_dNewScale
            dPixelY = (pParent.m_iVertScrollBarPos + y + pParent.m_dCompensationY) / pParent.m_dNewScale

        correct_x = int(dPixelX)
        correct_y = int(dPixelY)

        pParent.current_roi.append([correct_x, correct_y])

        # draw point on all scales, meaning we don't have to re-compute on refreshes
        for i in range(pParent.m_iMaxScaleTimes+1):
            if i == pParent.m_iScaleTimes:
                scale_x = int(dPixelX * pParent.m_dNewScale)
                scale_y = int(dPixelY * pParent.m_dNewScale)
            elif i == 0:
                scale_x = int(dPixelX * pParent.m_dInitialScale)
                scale_y = int(dPixelY * pParent.m_dInitialScale)
            else:
                dNewScale = pParent.m_dInitialScale * pow(pParent.m_dScaleRatio, i)
                scale_x = int(dPixelX * dNewScale)
                scale_y = int(dPixelY * dNewScale)
            if not pParent.is_first_point_set:
                pParent.cache[i] = pParent.m_vecMatResize[i].copy()
                cv2.circle(pParent.m_vecMatResize[i],(scale_x,scale_y),4,(0,255,0),-1)
                pParent.first_x[i] = scale_x
                pParent.first_y[i] = scale_y
            else:
                # draw line from previous point to current point
                cv2.line(pParent.m_vecMatResize[i],(pParent.prev_x[i],pParent.prev_y[i]),(scale_x,scale_y),(0,255,0),2)
                pParent.lines[i].append([pParent.prev_x[i],pParent.prev_y[i],scale_x,scale_y])
            pParent.prev_x[i] = scale_x
            pParent.prev_y[i] = scale_y
        pParent.is_first_point_set = True
        pParent.RefreshImage()


    elif event == cv2.EVENT_MBUTTONDOWN:
        if len(pParent.current_roi) >= 3: # each roi must have at least 3 points
            pParent.is_first_point_set = False
            pParent.rois.append(pParent.current_roi)
            pParent.current_roi = []
            for i in range(pParent.m_iMaxScaleTimes+1):
                pParent.m_vecMatResize[i] = pParent.cache[i].copy()
                pParent.lines[i].append([pParent.first_x[i],pParent.first_y[i],pParent.prev_x[i],pParent.prev_y[i]])
                for l in pParent.lines[i]:
                    cv2.line(pParent.m_vecMatResize[i],(l[0],l[1]),(l[2],l[3]),(0,0,255),2)
                pParent.lines[i] = []
            pParent.RefreshImage()


class CopenCVWindowExt:
    def __init__(self, windowName, iFlag=1) -> None:
        cv2.namedWindow(windowName, iFlag)
        cv2.setMouseCallback(windowName, MouseCall, self)
        self.m_matSrc = None
        self.m_vecMatResize = None
        self.m_strWindowName = windowName

        self.m_dInitialScale: float = 1
        self.m_dNewScale: float = 1
        self.m_dScaleRatio: float = 1.25
        self.m_dCompensationX: float = 0
        self.m_dCompensationY: float = 0

        self.m_iScaleTimes: int = 0
        self.m_iMaxScaleTimes: int = 7
        self.m_iMinScaleTimes: int = 0

        self.m_iOrgW: int = 0
        self.m_iOrgH: int = 0

        self.ptLButtonDown = [0, 0]
        self.ptRButtonDown = [0, 0]

        self.m_iHorzScrollBarPos: int = 0
        self.m_iVertScrollBarPos: int = 0
        self.m_iHorzScrollBarPos_copy: int = 0
        self.m_iVertScrollBarPos_copy: int = 0

        self.m_iHorzScrollBarRange_Min: int = 0
        self.m_iHorzScrollBarRange_Max: int = 1
        self.m_iVertScrollBarRange_Min: int = 0
        self.m_iVertScrollBarRange_Max: int = 1

        self.current_roi = [] # current roi, relative to the original image dimensions
        self.rois = [] # all complete rois, relative to the original image dimensions
        self.is_first_point_set = False
        self.first_x = []
        self.first_y = []
        self.prev_x = []
        self.prev_y = []
        self.lines = []
        self.cache = []

    
    def ImRead(self, image, mode="path") -> bool:
        # add mode that lets me pass in a numpy array instead of a filename
        if mode == "path":
            self.m_matSrc = cv2.imread(image)
        else:
            self.m_matSrc = image
        if self.m_matSrc is None:
            return False
        self.m_iOrgW = self.m_matSrc.shape[1]
        self.m_iOrgH = self.m_matSrc.shape[0]

        self.m_vecMatResize = [None] * (self.m_iMaxScaleTimes+1)
        self.first_x = [-1] * (self.m_iMaxScaleTimes+1)
        self.first_y = [-1] * (self.m_iMaxScaleTimes+1)
        self.prev_x = [-1] * (self.m_iMaxScaleTimes+1)
        self.prev_y = [-1] * (self.m_iMaxScaleTimes+1)
        self.lines = [[] for i in range(self.m_iMaxScaleTimes+1)]
        self.cache = [None] * (self.m_iMaxScaleTimes+1)
        

        sizeInitial = (self.m_matSrc.shape[1] * self.m_dInitialScale, self.m_matSrc.shape[0] * self.m_dInitialScale)
        self.m_vecMatResize[0] = cv2.resize(self.m_matSrc, (int(sizeInitial[0]), int(sizeInitial[1])))

        # rather than compute scaled images on the first zoom, compute on program start
        for i in range(1, self.m_iMaxScaleTimes+1):
            dNewScale = self.m_dInitialScale * pow(self.m_dScaleRatio, i)
            size = (self.m_matSrc.shape[1] * dNewScale, self.m_matSrc.shape[0] * dNewScale)
            self.m_vecMatResize[i] = cv2.resize(self.m_matSrc, (int(size[0]), int(size[1])))

        if self.m_vecMatResize is not None:
            cv2.imshow(self.m_strWindowName, self.m_vecMatResize[0])
        return self.m_vecMatResize[0] is not None

    def SetInitialScale(self, dScale) -> None:
        if dScale <= 0:
            return
        self.m_dInitialScale = dScale
        self.m_dNewScale = dScale

    def RefreshImage(self) -> None:
        if self.m_matSrc is None:
            return
        if self.m_vecMatResize[self.m_iScaleTimes] is None:
            print("This shouldn't run because we now pre-compute the scaled images")
            size = (self.m_dNewScale * self.m_matSrc.shape[1], self.m_dNewScale * self.m_matSrc.shape[0])
            self.m_vecMatResize[self.m_iScaleTimes] = cv2.resize(self.m_matSrc, (int(size[0]), int(size[1])))        
        iW = self.m_vecMatResize[0].shape[1] - 1
        iH = self.m_vecMatResize[0].shape[0] - 1

        rectShow = (self.m_iHorzScrollBarPos, self.m_iVertScrollBarPos, iW, iH)
        cv2.imshow(self.m_strWindowName, self.m_vecMatResize[self.m_iScaleTimes][rectShow[1]:rectShow[1] + rectShow[3], rectShow[0]:rectShow[0] + rectShow[2]])

    def SetHorzBarPos(self, iPos) -> None:
        if self.m_iScaleTimes == 0:
            self.m_iHorzScrollBarPos = 0
        else:
            if iPos > self.m_iHorzScrollBarRange_Max:
                self.m_iHorzScrollBarPos = self.m_iHorzScrollBarRange_Max
            elif iPos < self.m_iHorzScrollBarRange_Min:
                self.m_iHorzScrollBarPos = self.m_iHorzScrollBarRange_Min
            else:
                self.m_iHorzScrollBarPos = iPos

    def SetVertBarPos(self, iPos) -> None:
        if self.m_iScaleTimes == 0:
            self.m_iVertScrollBarPos = 0
        else:
            if iPos > self.m_iVertScrollBarRange_Max:
                self.m_iVertScrollBarPos = self.m_iVertScrollBarRange_Max
            elif iPos < self.m_iVertScrollBarRange_Min:
                self.m_iVertScrollBarPos = self.m_iVertScrollBarRange_Min
            else:
                self.m_iVertScrollBarPos = iPos

    def printState(self) -> None:
        print("\n")
        print("m_dInitialScale", self.m_dInitialScale)
        print("m_dNewScale", self.m_dNewScale)
        print("m_dScaleRatio", self.m_dScaleRatio)
        print("m_dCompensationX", self.m_dCompensationX)
        print("m_dCompensationY", self.m_dCompensationY)
        print("m_iScaleTimes", self.m_iScaleTimes)
        print("m_iMaxScaleTimes", self.m_iMaxScaleTimes)
        print("m_iMinScaleTimes", self.m_iMinScaleTimes)
        print("m_iOrgW", self.m_iOrgW)
        print("m_iOrgH", self.m_iOrgH)
        print("ptLButtonDown", self.ptLButtonDown)
        print("ptRButtonDown", self.ptRButtonDown)
        print("m_iHorzScrollBarPos", self.m_iHorzScrollBarPos)
        print("m_iVertScrollBarPos", self.m_iVertScrollBarPos)
        print("m_iHorzScrollBarPos_copy", self.m_iHorzScrollBarPos_copy)
        print("m_iVertScrollBarPos_copy", self.m_iVertScrollBarPos_copy)
        print("m_iHorzScrollBarRange_Min", self.m_iHorzScrollBarRange_Min)
        print("m_iHorzScrollBarRange_Max", self.m_iHorzScrollBarRange_Max)
        print("m_iVertScrollBarRange_Min", self.m_iVertScrollBarRange_Min)
        print("m_iVertScrollBarRange_Max", self.m_iVertScrollBarRange_Max)
        print("current_roi", self.current_roi)
        print("rois", self.rois)
