#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# Created by Mario Chen, 28.05.2021, Shenzhen
# My Github site: https://github.com/Mario-Hero

import random
import os, platform
import sys
import re
import tkinter as tk
import time

try:
    import pypinyin
    import vlc
    from PIL import Image, ImageTk, ImageFile, ImageEnhance, ImageFilter,ImageOps,ImageChops
except:
    os.system('pip install pypiwin32 pillow pypinyin python-vlc')
    from PIL import Image, ImageTk, ImageFile, ImageEnhance, ImageFilter, ImageOps, ImageChops
    import pypinyin
    import vlc

try:
    import vlcVidPlayer
except:
    print('你需要下载 vlcVidPlayer.py文件并放到相同目录')
    os.system("pause")
    sys.exit(1)


if platform.system() == 'Windows':
    import win32com.client
    import pythoncom
    isWindows = True
else:
    isWindows = False

FOLDER_REPEAT = 0  # 顺序播放时，文件夹内循环
FOLDER_CROSS = 1  # 顺序播放时，到文件夹末尾后进入下一文件夹

MODE_MY_SELECT = 1  # 库播放模式
MODE_NORMAL = 0  # 普通播放模式（使用默认库，或拖入文件夹播放）
modeSelect = MODE_NORMAL

# EDIT THIS 你可以编辑以下部分 >>>>>>
SHUFFLE = True  # 是否开启视频随机播放
WHEN_REACH_END_OF_FOLDER = FOLDER_REPEAT  # 顺序播放时，到文件夹末尾后的行为，FOLDER_REPEAT为文件夹内循环，FOLDER_CROSS为进入下一文件夹
DEFAULT_LIB = './lmy'  # 默认库。如果直接打开该Python文件，则会直接开始播放默认库。
MY_SELECT_LIB = [['E:/VirtualBox/vid/nyo', 'E:/VirtualBox/vid/nier', 'E:/VirtualBox/VirtualBox/vid/honoka'],
                 ['E:/VirtualBox/avi/']
                 ]  # 你的视频库路径
SHOULD_NOT_GO_INTO_THESE_FOLDERS = ["一般", "不好看", "没法看", "图"]  # 如果文件夹名称包含其中任意一个关键字，则不进入该文件夹
SHOULD_NOT_GO_INTO_THESE_FILES = ["一般", "不好看", "没法看"]  # 如果文件名包含其中任意一个关键字，则不打开该文件
COLLECTION_FOLDER = 'E:/VirtualBox/VID收集/'  # 你的收藏夹。收藏的视频的快捷方式会保存在该文件夹。
#      MY_SELECT_LIB的行列关系:
#                 1 2 3 4 5 6 7 8 9 0
#           F1
#           F2
#           F3
#           ...
#           F12

CAN_DELETE_FILE = True  # 如果为真，则按下Del删除键时，会直接删除正在播放的文件。
ADD_THIS_TO_FILE_IF_NOT_DELETE = '不好看'  # 如果CAN_DELETE_FILE为假，则给该文件的文件名前面面添加一个 ADD_THIS_TO_FILE_IF_NOT_DELETE
COLOR_PROGRESS_BAR = 'red'  # 进度条颜色

FULL_SCREEN = True # 全屏。只有不全屏，下面的FACTOR_WIDTH、FACTOR_HEIGHT、POSITION才会生效。
FACTOR_WIDTH = 0.5  # 打开时的窗口相对于屏幕的宽度比例
FACTOR_HEIGHT = FACTOR_WIDTH  # 打开时的窗口相对于屏幕的高度比例
SCREEN_POSITION = 1  # 如下图所示。数字代表了打开程序时，程序出现在屏幕中的位置

# POSITION 可选位置：
# 左上角 1 2 3 右上角
#       4 5 6
# 左下角 7 8 9 右下角

PHONE_SUPPORT = False # 触摸屏模式。进度条变宽。在屏幕左上角和右上角添加按键区域，只要按下即会播放下一个视频。
TOUCH_BAR_COLOR = '#202020'  # 触摸条的颜色。
# <<<<<< 你可以编辑以上部分 EDIT THIS

FILE_LIB = []
VIDEO_SUPPORT = ['mp4', 'webm', 'avi', 'mov', '.mkv', '.wmv', '.m3u8', '.3g2', '.3gp', '.3gp2', '.3gpp', '.amv', '.asf', '.bik',
                 '.bin',
                 '.divx', '.drc', '.dv', '.f4v', '.flv', '.gvi', '.gxf', '.iso', '.m1v', '.m2v', '.m2t', '.m2ts',
                 '.m4v', '.mp2', '.mp4v', '.mpe', '.mpeg', '.mpeg1', '.mpeg2', '.mpeg4', '.mpg', '.mpv2', '.mts',
                 '.mxf', '.mxg', '.nsv', '.nuv', '.ogg', '.ogm', '.ogv', '.ps', '.rec', '.rm', '.rmvb', '.rpl', '.thp',
                 '.tod', '.ts', '.tts', '.txd', '.vob', '.vro', '.webm', '.wm', '.wtv', '.xesc']  # VLC支持的视频格式
BACKGROUND_COLOR = 'black'  # 背景颜色
HEIGHT_PROGRESS_BAR = 2  # 进度条宽度。如果设置为0，则不显示进度条。不建议设置超过3.

select_row = 0
select_col = 0

STATE_PLAY_ALL = 0
STATE_FOLDER = 1
playLevel = -1

statePlay = STATE_PLAY_ALL
pauseAll = False

noParentFolder = False
keyControlGroup = ['NextFolder', './']
keyControl = False
drawCancel = False
rootFolder = ''
drawStep = 0
nowVideoAddr = ''
parentFolder = ''
videoTryTimes = 0
videoWidth = 0
videoHeight = 0
barWidth = 0
barHeight = 0

top = tk.Tk()

def generateScreenPosition():
    if not FULL_SCREEN:
        return ((SCREEN_POSITION-1)%3)*(1-FACTOR_WIDTH)*top.winfo_screenwidth()/2, int((SCREEN_POSITION-1)/3)*(1-FACTOR_HEIGHT)*top.winfo_screenheight()/2
    else:
        return 0, 0


def getRandomFromList(listTemp):
    return listTemp[random.randint(0, len(listTemp) - 1)]


def containsChinese(name):
    for ch in name:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def findName(name, folder):
    if name in folder:
        return True
    if len(name) > len(folder):
        return False
    if containsChinese(folder):
        chineseWord = re.findall('[\u4e00-\u9fa5]', folder)
        ch = ''
        chStart = ''
        for chineseOneWord in chineseWord:
            ch = ch + pypinyin.pinyin(chineseOneWord, style=pypinyin.NORMAL)[0][0]
            chStart = chStart + pypinyin.pinyin(chineseOneWord, style=pypinyin.NORMAL)[0][0][0]
        if name in ch or name in chStart:
            # print(name,ch,chStart)
            return True
    en = (''.join(re.findall('[\x00-\xff]', folder))).lower()
    if name in en:
        return True
    else:
        '''
        enStart = ''
        for enTemp in en.split(' '):
            enStart = enStart + enTemp[0]
        if name in enStart:
            return True
        else:
            return False
        '''
        return False


def findFolder(name, folderPath, level=1):
    if os.path.isdir(folderPath):
        file_list = os.listdir(folderPath)
        for fld in file_list:
            temp = getRealLnk(os.path.join(folderPath, fld))
            if os.path.isdir(temp) and folderOK(temp):
                if findName(name, os.path.split(temp)[1]):
                    return temp
        if level >= 1:
            for fld in file_list:
                temp = getRealLnk(os.path.join(folderPath, fld))
                if os.path.isdir(temp) and folderOK(temp):
                    resultFind = findFolder(name, temp, level-1)
                    if resultFind:
                        return temp
        else:
            return ''
    else:
        return ''
    return ''


def isLnk(name):
    return name.lower().endswith('.lnk') or name.lower().endswith('.url')


def readLnk(lnk):
    if isWindows:
        pythoncom.CoInitialize()
        shell = win32com.client.Dispatch("WScript.Shell")
        return shell.CreateShortCut(lnk).Targetpath
    else:
        return ''


def getRealLnk(lnk):
    if isWindows:
        tempPath = lnk
        while isLnk(tempPath):
            tempPath = readLnk(tempPath)
        return tempPath
    else:
        return lnk


def folderOK(folderTemp):
    temp = os.path.split(folderTemp)[1]
    for fld in SHOULD_NOT_GO_INTO_THESE_FOLDERS:
        if fld in temp:
            return False
    return True


def createShorCutInCollectionFolder(file):
    if isWindows:
        collTargetFolder = COLLECTION_FOLDER
        fullPath = os.path.abspath(file)
        fileName = os.path.split(file)[1]
        if isinstance(collTargetFolder, list):
            lnkPath = os.path.join(collTargetFolder[0], fileName)
        else:
            lnkPath = os.path.join(collTargetFolder, fileName)
        dotPos = lnkPath.rfind('.')
        lnkPath = lnkPath[:(dotPos + 1)] + 'lnk'
        shortcut = shell.CreateShortCut(lnkPath)
        shortcut.TargetPath = fullPath
        shortcut.save()


def oneParentFolder(folderTemp):
    if os.path.normcase(rootFolder) == os.path.normcase(folderTemp):
        return folderTemp
    else:
        return os.path.split(folderTemp)[0]


def nextFolder(folderTemp):
    if os.path.isdir(folderTemp):
        parentTemp, folder_name = os.path.split(folderTemp)
        if os.path.isdir(parentTemp):
            file_list = sorted(os.listdir(parentTemp))
            position = file_list.index(folder_name)
            if position == len(file_list) - 1:
                if os.path.normcase(rootFolder) == os.path.normcase(parentTemp):
                    return findFirstVideoInFolder(rootFolder)
                else:
                    return nextFolder(parentTemp)
            else:
                for fld in file_list[(position + 1):]:
                    temp = getRealLnk(os.path.join(parentTemp, fld))
                    if os.path.isdir(temp):
                        if folderOK(fld):
                            return temp
                return nextFolder(parentTemp)
        else:
            return ''
    else:
        return folder


def previousFolder(folderTemp):
    if os.path.isdir(folderTemp):
        parentTemp, folder_name = os.path.split(folderTemp)
        if os.path.isdir(parentTemp):
            file_list = sorted(os.listdir(parentTemp), reverse=True)
            position = file_list.index(folder_name)
            if position == 0:
                if os.path.normcase(rootFolder) == os.path.normcase(parentTemp):
                    return findFirstVideoInFolder(rootFolder)
                else:
                    return previousFolder(parentTemp)
            else:
                for fld in list(reversed(file_list[:position])):
                    temp = getRealLnk(os.path.join(parentTemp, fld))
                    if os.path.isdir(temp) and folderOK(fld):
                        return temp
                return previousFolder(oneParentFolder(parentTemp))
        else:
            return ''
    else:
        return folderTemp


def deleteNowPlayFile():
    deleteTemp = nowVideoAddr
    for i in range(10):
        if nowVideoAddr == deleteTemp:
            if videoEnd():
                return
        else:
            break
    if nowVideoAddr == deleteTemp:
        top.player.stop()
    if os.path.isfile(deleteTemp):
        if CAN_DELETE_FILE:
            os.remove(deleteTemp)
            # print(deleteTemp)
        else:
            os.rename(deleteTemp, os.path.join(os.path.split(deleteTemp)[0],
                                               ADD_THIS_TO_FILE_IF_NOT_DELETE + os.path.split(deleteTemp)[1]))


def nextPic(img):
    parentTemp, img_name = os.path.split(img)
    if os.path.isdir(parentTemp):
        file_list = sorted(os.listdir(parentTemp))
        position = file_list.index(img_name)
        if position == len(file_list) - 1:
            if WHEN_REACH_END_OF_FOLDER == FOLDER_REPEAT:
                return findFirstVideoInFolder(parentTemp)
            elif WHEN_REACH_END_OF_FOLDER == FOLDER_CROSS:
                return findFirstVideoInFolder(nextFolder(parentTemp))
        else:
            for img in file_list[(position + 1):]:
                temp = getRealLnk(os.path.join(parentTemp, img))
                if isVid(temp):
                    return temp
            return findFirstVideoInFolder(nextFolder(parentTemp))
    else:
        return ''


def previousPic(img):
    parentTemp, img_name = os.path.split(img)
    if os.path.isdir(parentTemp):
        file_list = sorted(os.listdir(parentTemp), reverse=True)
        position = file_list.index(img_name)
        if position == 0:
            if WHEN_REACH_END_OF_FOLDER == FOLDER_REPEAT:
                return findLastVideoInFolder(parentTemp)
            elif WHEN_REACH_END_OF_FOLDER == FOLDER_CROSS:
                return findLastVideoInFolder(previousFolder(parentTemp))
        else:
            for img in file_list[:position]:
                temp = getRealLnk(os.path.join(parentTemp, img))
                if isVid(temp):
                    return temp
            return findLastVideoInFolder(previousFolder(parentTemp))
    else:
        return ''


def findFirstVideoInFolder(folder):
    if os.path.isdir(folder):
        file_list = sorted(os.listdir(folder))
        for file in file_list:
            temp = getRealLnk(os.path.join(folder, file))
            if os.path.isdir(temp):
                return findFirstVideoInFolder(temp)
            else:
                if isVid(temp):
                    return temp
        return findFirstVideoInFolder(nextFolder(folder))
    else:
        return folder


def findLastVideoInFolder(folder):
    if os.path.isdir(folder):
        file_list = sorted(os.listdir(folder), reverse=True)
        for file in file_list:
            temp = getRealLnk(os.path.join(folder, file))
            if os.path.isdir(temp):
                return findLastVideoInFolder(temp)
            else:
                if isVid(temp):
                    return temp
        return findLastVideoInFolder(previousFolder(folder))
    else:
        return folder


def getParentFolder(folder):
    temp = folder
    for i in range(playLevel + 1):
        if os.path.normcase(rootFolder) == os.path.normcase(temp):
            return temp
        else:
            temp = os.path.split(temp)[0]
    return temp


tabState = False
tabInput = ''


def controlProgressBar(event):
    top.player.set_position(event.x / videoWidth)


def keyPress(event):  # 按键事件响应
    global drawCancel, pauseAll, playLevel, statePlay, LOOP_TIME, select_row, select_col, modeSelect, parentFolder, \
        SHUFFLE, keyControlGroup, keyControl, nowVideoAddr, shell, tabState, tabInput, nowVideoAddr, videoTryTimes
    keyInput = event.keysym.lower()
    # print(repr(keyInput))
    if keyInput == 'escape':  # 退出
        top.player.release()
        top.destroy()
        sys.exit(0)
    else:
        try:
            if top.player and top.showPlayer:
                pass
        except:
            return
        else:
            if not tabState:
                if keyInput == 'tab':
                    tabState = True
                    tabInput = ''
                elif keyInput == 'd' or keyInput == 'a' or keyInput == 'z' or keyInput == 'x':
                    if not keyControl:
                        keyControl = True
                        if keyInput == 'd':  # 顺序下一张
                            keyControlGroup[0] = 'nextPic'
                            keyControlGroup[1] = nextPic(nowVideoAddr)
                        elif keyInput == 'a':  # 顺序上一张
                            keyControlGroup[0] = 'previousPic'
                            keyControlGroup[1] = previousPic(nowVideoAddr)
                        elif keyInput == 'z':  # 顺序上一个文件夹
                            keyControlGroup[0] = 'previousFolder'
                            keyControlGroup[1] = findLastVideoInFolder(previousFolder(oneParentFolder(nowVideoAddr)))
                        elif keyInput == 'x':  # 顺序下一个文件夹
                            keyControlGroup[0] = 'nextFolder'
                            keyControlGroup[1] = findFirstVideoInFolder(nextFolder(oneParentFolder(nowVideoAddr)))
                        # print(keyControlGroup)
                        videoTryTimes = 0
                        videoEnd()
                elif keyInput == 'q':  # 本文件夹内随机
                    playLevel = 0
                    statePlay = STATE_FOLDER
                    parentFolder = getParentFolder(nowVideoAddr)
                elif keyInput == 'w':  # 上一级文件夹内随机
                    playLevel = 1
                    statePlay = STATE_FOLDER
                    parentFolder = getParentFolder(nowVideoAddr)
                    videoTryTimes = 0
                elif keyInput == 'e':  # 上二级文件夹内随机
                    playLevel = 2
                    statePlay = STATE_FOLDER
                    parentFolder = getParentFolder(nowVideoAddr)
                    videoTryTimes = 0
                elif keyInput == 'r':  # 取消文件夹内随机
                    playLevel = -1
                    statePlay = STATE_PLAY_ALL
                    videoTryTimes = 0
                elif keyInput == 'v':  # 播放加速
                    top.player.faster()
                elif keyInput == 'c':  # 播放减速
                    top.player.slower()
                elif keyInput == 'delete':
                    deleteNowPlayFile()
                elif keyInput == 'quoteleft':  # 按下~取消库内播放
                    modeSelect = MODE_NORMAL
                elif keyInput == 'f':  # 取消或开启随机播放
                    SHUFFLE = not SHUFFLE
                elif keyInput[0] == 'f' and keyInput != 'f':  # F1 ~ F12 选择库的行数，并进入库内播放
                    if keyInput[1:].isdigit():
                        select_row = int(keyInput[1:]) - 1
                        modeSelect = MODE_MY_SELECT
                        statePlay = STATE_PLAY_ALL
                        videoEnd()
                elif keyInput.isdigit():  # 1234567890 选择库的列数，并进入库内播放
                    if int(keyInput) == 0:
                        select_col = 9
                    else:
                        select_col = int(keyInput) - 1
                    modeSelect = MODE_MY_SELECT
                    statePlay = STATE_PLAY_ALL
                    videoEnd()
                elif keyInput == 'alt_l':  # 发送该文件的快捷方式到默认库
                    createShorCutInCollectionFolder(nowVideoAddr)
                elif keyInput == 'return' or keyInput == 'space':  # 开始随机播放视频
                    videoEnd()
                elif keyInput == 'shift_r' or keyInput == 's':  # 暂停或播放视频
                    top.player.pauseOrPlay()
                elif keyInput == 'right' or keyInput == 'shift_l':  # 快进10秒
                    top.player.forward()
                elif keyInput == 'left' or keyInput == 'control_l':  # 快退10秒
                    top.player.backward()
                elif keyInput == 'up':  # 音量+5
                    top.player.volumeUp()
                elif keyInput == 'down':  # 音量-5
                    top.player.volumeDown()
            else:
                if keyInput == 'tab':
                    if tabInput:
                        tempFolder = findFolder(tabInput.lower(), rootFolder)
                        # print(tabInput,tempFolder)
                        if tempFolder:
                            playLevel = 0
                            statePlay = STATE_FOLDER
                            parentFolder = tempFolder
                            videoEnd()
                        tabInput = ''
                    tabState = False
                else:
                    if len(keyInput) == 1:
                        tabInput = tabInput + keyInput


def findVideo(folderTemp):
    global nowVideoAddr, parentFolder
    if os.path.isdir(folderTemp):
        for i in range(10):
            file_list = os.listdir(folderTemp)
            if len(file_list) == 0:
                return findVideo(oneParentFolder(folderTemp))
            folderNext = getRealLnk(os.path.join(folderTemp, file_list[random.randint(0, len(file_list) - 1)]))
            if os.path.isdir(folderNext) and folderOK(folderNext):
                folderTemp = folderNext
            elif isVid(folderNext):
                nowVideoAddr = folderNext
                return folderNext
        if os.path.normcase(rootFolder) == os.path.normcase(folderTemp):
            return ''
        else:
            return findVideo(oneParentFolder(folderTemp))
    else:
        return ''


def isVid(name):
    namelower = os.path.split(name)[1].lower()
    if not namelower.startswith('.'):
        for formVid in VIDEO_SUPPORT:
            if namelower.endswith(formVid):
                for fld in SHOULD_NOT_GO_INTO_THESE_FILES:
                    if fld in namelower:
                        return False
                return True
    return False


def isMusic(name):
    namelower = os.path.split(name)[1].lower()
    return (namelower.endswith("wav") or namelower.endswith("mp3") or namelower.endswith("flac") or namelower.endswith(
        "m4a") or namelower.endswith("ape")) and not namelower.startswith('.')


def drawDuration(event=''):
    try:
        if top.player:
            pass
    except:
        return
    else:
        if top.player.is_playing():
            if top.player.get_length():
                pos = top.player.get_position()
                top.canvas.coords(fill_rec, (0, 0, pos * videoWidth, HEIGHT_PROGRESS_BAR))
                # top.canvas.pack(side='bottom')
                # top.update()


def onConfigure(event):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    if event.widget == top:
        SCREEN_WIDTH = event.width
        SCREEN_HEIGHT = event.height
        updateScreenInfo()
        top.canvas.configure(width=videoWidth, height=HEIGHT_PROGRESS_BAR, cursor='none')
        try:
            top.showPlayer.configure(width=videoWidth, height=videoHeight, cursor='none')
        except:
            pass


def getVideo():
    global nowVideoAddr, modeSelect, SHUFFLE, noParentFolder, keyControl, parentFolder, rootFolder
    if not keyControl:
        if SHUFFLE:
            if statePlay == STATE_PLAY_ALL:
                if modeSelect == MODE_NORMAL:
                    folderGetVideo = getRealLnk(FILE_LIB[random.randint(0, len(FILE_LIB) - 1)])
                    if not os.path.isdir(folderGetVideo):
                        if isVid(folderGetVideo):
                            noParentFolder = True
                            nowVideoAddr = folderGetVideo
                            return folderGetVideo
                        else:
                            return ''
                    rootFolder = folderGetVideo
                    noParentFolder = False
                    return findVideo(folderGetVideo)
                elif modeSelect == MODE_MY_SELECT:
                    if select_row >= len(MY_SELECT_LIB):
                        modeSelect = MODE_NORMAL
                    else:
                        if select_col >= len(MY_SELECT_LIB[select_row]):
                            modeSelect = MODE_NORMAL
                        else:
                            if isinstance(MY_SELECT_LIB[select_row][select_col], list):
                                folderGetVideo = getRealLnk(getRandomFromList(MY_SELECT_LIB[select_row][select_col]))
                            else:
                                folderGetVideo = getRealLnk(MY_SELECT_LIB[select_row][select_col])
                            rootFolder = folderGetVideo
                            noParentFolder = False
                            # print(folder)
                            if not os.path.isdir(folderGetVideo):
                                if isVid(folderGetVideo):
                                    nowVideoAddr = folderGetVideo
                                    return folderGetVideo
                                else:
                                    sys.exit(1)
                            return findVideo(folderGetVideo)
            elif statePlay == STATE_FOLDER:
                if not parentFolder:
                    parentFolder = oneParentFolder(nowVideoAddr)
                    noParentFolder = False
                return findVideo(parentFolder)
        else:
            if not nowVideoAddr:
                SHUFFLE = True
            else:
                nowVideoAddr = nextPic(nowVideoAddr)
                parentFolder = oneParentFolder(nowVideoAddr)
                return nowVideoAddr
    else:
        keyControl = False
        nowVideoAddr = keyControlGroup[1]
        parentFolder = oneParentFolder(nowVideoAddr)
        return nowVideoAddr


def mouseClick(event):
    updateScreenInfo()
    if event.widget == top.leftBar:
        videoEnd()
    elif event.widget == top.rightBar:
        top.player.forward(30000)


def updateScreenInfo():
    global HEIGHT_PROGRESS_BAR,barHeight,videoHeight,barWidth,videoWidth,SCREEN_WIDTH,SCREEN_HEIGHT
    if FULL_SCREEN and not (SCREEN_WIDTH == top.winfo_screenwidth() and SCREEN_HEIGHT == top.winfo_screenheight()):
        SCREEN_WIDTH = top.winfo_screenwidth()
        SCREEN_HEIGHT = top.winfo_screenheight()
        top.geometry("%dx%d" % (SCREEN_WIDTH, SCREEN_HEIGHT))

    if PHONE_SUPPORT:
        HEIGHT_PROGRESS_BAR = int(SCREEN_HEIGHT/14)
        barHeight = int(SCREEN_HEIGHT*5/6)
        videoHeight = int(SCREEN_HEIGHT - HEIGHT_PROGRESS_BAR)
        if (SCREEN_WIDTH/SCREEN_HEIGHT)>1.78:
            barWidth = int((SCREEN_WIDTH-(SCREEN_HEIGHT - HEIGHT_PROGRESS_BAR)*1.78)/2)
        else:
            barWidth = int(SCREEN_WIDTH*0.08)
        videoWidth = int(SCREEN_WIDTH - 2 * barWidth)
    else:
        if HEIGHT_PROGRESS_BAR > 5:
            HEIGHT_PROGRESS_BAR = 2
        videoWidth = SCREEN_WIDTH
        videoHeight = SCREEN_HEIGHT - HEIGHT_PROGRESS_BAR
        barHeight = 0
        barWidth = 0


multiVideoEnd = True
def videoEnd():
    global nowVideoAddr, SCREEN_WIDTH, SCREEN_HEIGHT, videoTryTimes, needDuration, HEIGHT_PROGRESS_BAR, multiVideoEnd
    if videoTryTimes >= 5:
        return 1
    if multiVideoEnd:
        multiVideoEnd = False
        if top.player:
            if not top.player.is_Opening():
                if FULL_SCREEN and not (SCREEN_WIDTH == top.winfo_screenwidth() and SCREEN_HEIGHT == top.winfo_screenheight()):
                    SCREEN_WIDTH = top.winfo_screenwidth()
                    SCREEN_HEIGHT = top.winfo_screenheight()
                    top.geometry("%dx%d" % (SCREEN_WIDTH, SCREEN_HEIGHT))
                try:
                    vidTemp = getVideo()
                except:
                    if videoTryTimes >= 5:
                        top.player.stop()
                        return 1
                    else:
                        videoTryTimes = videoTryTimes + 1
                        return 0
                else:
                    if vidTemp:
                        try:
                            # top.player.remove_callback(vlc.EventType.MediaPlayerPositionChanged)
                            videoTryTimes = 0
                            nowVideoAddr = vidTemp
                            top.showPlayer.destroy()
                            top.update()
                            if top.player:
                                top.player.remove_callback(vlc.EventType.MediaPlayerPositionChanged)
                                # top.player.media.get_media_player().pause()
                                del top.player
                            # top.player.release()
                            # del top.showPlayer
                            top.player = vlcVidPlayer.Player()
                            # updateScreenInfo()
                            if PHONE_SUPPORT:
                                top.showPlayer = tk.Canvas(top, width=videoWidth,
                                                           height=videoHeight, bd=0,
                                                           highlightthickness=0, bg=BACKGROUND_COLOR)
                            else:
                                top.showPlayer = tk.Canvas(top, width=videoWidth, height=videoHeight, bd=0,
                                                           highlightthickness=0, bg=BACKGROUND_COLOR)
                            top.showPlayer.pack(side='top')
                            top.showPlayer.configure(cursor='none')
                            top.update()
                            if not top.showPlayer.winfo_ismapped():
                                time.sleep(0.05)
                            top.player.set_window(top.showPlayer.winfo_id())
                            top.player.set_url(vidTemp)
                            top.player.play()
                            # top.player.add_callback(vlc.EventType.MediaPlayerPaused, canPlay)
                            top.player.add_callback(vlc.EventType.MediaPlayerPositionChanged, drawDuration)
                        except:
                            pass
                    else:
                        if videoTryTimes >= 5:
                            top.player.stop()
                            return 1
                        else:
                            videoTryTimes = videoTryTimes + 1
                            return 0
        multiVideoEnd = True


# MediaPlayerEndReached MediaPlayerTimeChanged

def playingMedia(event):
    # top.player.add_callback(vlc.EventType.MediaPlayerPositionChanged, drawDuration)
    print("Is playing")

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        # sys.quit(1)
        if not DEFAULT_LIB:
            sys.exit(1)
        else:
            FILE_LIB.append(DEFAULT_LIB)
    else:
        for folder in sys.argv[1:]:
            FILE_LIB.append(getRealLnk(folder))
    if FULL_SCREEN:
        SCREEN_WIDTH = top.winfo_screenwidth()
        SCREEN_HEIGHT = top.winfo_screenheight()
        top.overrideredirect(True)
    else:
        SCREEN_WIDTH = int(top.winfo_screenwidth() * FACTOR_WIDTH)
        SCREEN_HEIGHT = int(top.winfo_screenheight() * FACTOR_HEIGHT)
        top.bind("<Configure>", onConfigure)
    screenStartX, screenStartY = generateScreenPosition()
    top.geometry("%dx%d+%d+%d" % (SCREEN_WIDTH, SCREEN_HEIGHT, screenStartX, screenStartY))
    top.configure(bg=BACKGROUND_COLOR,cursor='none')
    top.focus_set()
    top.bind("<Key>", keyPress)
    # top.bind("<Button-1>",controlProgressBar)
    top.player = vlcVidPlayer.Player()
    updateScreenInfo()
    if PHONE_SUPPORT:
        top.showPlayer = tk.Canvas(top, width=videoWidth, height=videoHeight, bd=0,
                                   highlightthickness=0, bg=BACKGROUND_COLOR)
        top.canvas = tk.Canvas(top, width=videoWidth, height=HEIGHT_PROGRESS_BAR, bd=0, highlightthickness=0,
                               bg=BACKGROUND_COLOR)
        top.leftBar = tk.Canvas(top, width=barWidth, height=barHeight, bd=0, highlightthickness=0, bg=BACKGROUND_COLOR)
        top.rightBar = tk.Canvas(top, width=barWidth, height=barHeight, bd=0, highlightthickness=0,bg=BACKGROUND_COLOR)
        fill_rec = top.canvas.create_rectangle(0, 0, 0, 10, outline="", width=0, fill=COLOR_PROGRESS_BAR)
        top.leftBar.create_rectangle(0,0,barWidth,barHeight,outline="",width=0,fill=TOUCH_BAR_COLOR)
        top.rightBar.create_rectangle(0, 0, barWidth, barHeight, outline="", width=0, fill=TOUCH_BAR_COLOR)
        top.leftBar.pack(side='left', anchor='n')
        top.rightBar.pack(side='right', anchor='n')
        top.canvas.bind("<Button-1>", controlProgressBar)
        top.bind('<Button-1>', mouseClick)
    else:
        top.showPlayer = tk.Canvas(top, width=videoWidth, height=videoHeight, bd=0,
                                   highlightthickness=0, bg=BACKGROUND_COLOR)
        top.canvas = tk.Canvas(top, width=videoWidth, height=HEIGHT_PROGRESS_BAR, bd=0, highlightthickness=0,
                               bg=BACKGROUND_COLOR)
        fill_rec = top.canvas.create_rectangle(0, 0, 0, 10, outline="", width=0, fill=COLOR_PROGRESS_BAR)
        top.canvas.bind("<Enter>", controlProgressBar)

    top.showPlayer.pack(side='top')
    top.canvas.pack(side='bottom')
    top.player.set_window(top.showPlayer.winfo_id())
    # top.player.add_callback(vlc.EventType.MediaPlayerPlaying, playingMedia)
    # top.withdraw()
    top.player.add_callback(vlc.EventType.MediaPlayerPositionChanged, drawDuration)
    videoEnd()
    # top.after(500, drawDuration)
    top.mainloop()
