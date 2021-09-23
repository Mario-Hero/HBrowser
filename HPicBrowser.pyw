#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# Created by Mario Chen, 23.05.2021, Shenzhen
# My Github site: https://github.com/Mario-Hero

from queue import Queue
import platform
import random
import os
import math
import time
import sys
import re
import tkinter as tk
import threading

try:
    import pypinyin
    from PIL import Image, ImageTk, ImageFile, ImageEnhance, ImageFilter, ImageOps, ImageChops
except:
    os.system('pip install pypiwin32 pillow pypinyin python-vlc')
    from PIL import Image, ImageTk, ImageFile, ImageEnhance, ImageFilter, ImageOps, ImageChops
    import pypinyin

try:
    import vlcVidPlayer
except:
    print('你需要下载 vlcVidPlayer.py文件并放到相同目录')
    os.system("pause")
    sys.exit(1)

if platform.system() == 'Windows':
    import win32com.client

    isWindows = True
else:
    isWindows = False

ImageFile.LOAD_TRUNCATED_IMAGES = True
FOLDER_REPEAT = 0  # 顺序播放时，文件夹内循环
FOLDER_CROSS = 1  # 顺序播放时，到文件夹末尾后进入下一文件夹

MODE_MY_SELECT = 1  # 库播放模式
MODE_NORMAL = 0  # 普通播放模式（使用默认库，或拖入文件夹播放）
modeSelect = MODE_NORMAL

# EDIT THIS 你可以编辑以下部分 >>>>>>
LOOP_TIME = 2000  # 幻灯片播放间隔（单位：毫秒）
SHUFFLE = True  # 是否开启图片随机播放
TWO_COLUMNS = True  # 若为真，则屏幕的宽大于高时，当随机到照片为竖屏时，一页浏览两张竖屏照片。屏幕的宽小于于高时，当随机到照片为横屏时，一页浏览两张横屏照片
WHEN_REACH_END_OF_FOLDER = FOLDER_CROSS  # 顺序播放时，到文件夹末尾后的行为，FOLDER_REPEAT为文件夹内循环，FOLDER_CROSS为进入下一文件夹
MUSIC_LIB = ['E:/Music']  # 音乐库路径
DEFAULT_LIB = './pic/'  # 默认库。如果直接打开该Python文件，则会直接开始播放默认库。
MY_SELECT_LIB = [['./pic', './pic/good', './pic/best', './pic/',
                  'E:/VirtualBox/zz', 'E:/VirtualBox/nmz',
                  'E:/VirtualBox/xww', 'E:/VirtualBox/saku',
                  'E:/VirtualBox/zyx']
             , ['E:/VirtualBox/wyc'] # 你的图片库路径。需要自己设置。
SHOULD_NOT_GO_INTO_THESE_FOLDERS = ["一般", "不好看", "没法看", "视频"]  # 如果文件夹名称包含其中任意一个关键字，则不进入该文件夹
BACKGROUND_COLOR = 'black'  # 背景颜色,可选 black,white,pink,green,blue,red,orange等，或者直接设为'#FFDAB9'等值

#      MY_SELECT_LIB的行列关系:
#                 1 2 3 4 5 6 7 8 9 0
#           F1
#           F2
#           F3
#           ...
#           F12

SHARPEN_ON = True  # 开启锐化。
FULL_SCREEN = True  # 全屏。只有不全屏，下面的FACTOR_WIDTH、FACTOR_HEIGHT、POSITION才会生效。
FACTOR_WIDTH = 0.5  # 打开时的窗口相对于屏幕的宽度比例
FACTOR_HEIGHT = FACTOR_WIDTH  # 打开时的窗口相对于屏幕的高度比例
SCREEN_POSITION = 4  # 如下图所示。数字代表了打开程序时，程序出现在屏幕中的位置

# POSITION 可选位置：
# 左上角 1 2 3 右上角
#       4 5 6
# 左下角 7 8 9 右下角

# <<<<<< 你可以编辑以上部分 EDIT THIS

FILE_LIB = []

select_row = 0
select_col = 0

STATE_PLAY_ALL = 0
STATE_FOLDER = 1
playLevel = -1

LOOP_STEP = 250  # 时钟周期，无需调整（单位：毫秒）
IMAGE_BUFFER_SIZE = 2  # 图片的缓冲层数。无需调整。

statePlay = STATE_PLAY_ALL
pauseAll = False

noParentFolder = False
keyControlGroup = ['NextFolder', './']
keyControl = False
drawCancel = False
rootFolder = ''
drawStep = 0
imageCache = Queue(maxsize=IMAGE_BUFFER_SIZE)
imageAddrCache = []
nowImageAddr = ''
lastImageAddr = ''
parentFolder = ''
NEED_UPDATE = True

top = tk.Tk()
player = vlcVidPlayer.Player()
if isWindows:
    shell = win32com.client.Dispatch("WScript.Shell")
else:
    shell = ''


def generateScreenPosition():
    if not FULL_SCREEN:
        return ((SCREEN_POSITION - 1) % 3) * (1 - FACTOR_WIDTH) * top.winfo_screenwidth() / 2, int(
            (SCREEN_POSITION - 1) / 3) * (1 - FACTOR_HEIGHT) * top.winfo_screenheight() / 2
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
    '''
    if len(name) > len(folder):
        return False
    '''
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


def findFolder(name, folderPath):
    if os.path.isdir(folderPath):
        file_list = os.listdir(folderPath)
        for fld in file_list:
            temp = getRealLnk(os.path.join(folderPath, fld))
            if os.path.isdir(temp) and folderOK(temp):
                if findName(name, os.path.split(temp)[1]):
                    return temp
        for fld in file_list:
            temp = getRealLnk(os.path.join(folderPath, fld))
            if os.path.isdir(temp) and folderOK(temp):
                resultFind = findFolder(name, temp)
                if resultFind:
                    return True
    else:
        return ''
    return ''


def drawCancelRemoveAll(goCancel=False):
    global drawCancel, lastImageAddr
    imageCache.queue.clear()
    imageAddrCache.clear()
    lastImageAddr = nowImageAddr
    fillImageCache()
    if goCancel and not drawCancel:
        drawCancel = True


def isLnk(name):
    return name.lower().endswith('.lnk')


def readLnk(lnk):
    if isWindows:
        shortcut = shell.CreateShortCut(lnk)
        # print(shortcut.Targetpath)
        return shortcut.Targetpath
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


def getMusic(folderTemp):
    global lastImageAddr, parentFolder
    for i in range(10):
        file_list = os.listdir(folderTemp)
        if len(file_list) == 0:
            return getMusic(oneParentFolder(folderTemp))
        folderNext = os.path.join(folderTemp, file_list[random.randint(0, len(file_list) - 1)])
        if os.path.isdir(folderNext):
            folderTemp = folderNext
        elif isMusic(folderNext):
            lastImageAddr = folderNext
            return folderNext
    if os.path.normcase(rootFolder) == os.path.normcase(folderTemp):
        return ''
    else:
        return getMusic(oneParentFolder(folderTemp))


def shuffleMusic():
    folderGetMusic = MUSIC_LIB[random.randint(0, len(MUSIC_LIB) - 1)]
    if not os.path.isdir(folderGetMusic):
        if isMusic(folderGetMusic):
            return folderGetMusic
        else:
            sys.exit(1)
    return getMusic(folderGetMusic)


def folderOK(folderTemp):
    temp = os.path.split(folderTemp)[1]
    for fld in SHOULD_NOT_GO_INTO_THESE_FOLDERS:
        if fld in temp:
            return False
    return True


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
                    return findFirstImageInFolder(rootFolder)
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
                    return findFirstImageInFolder(rootFolder)
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


def nextPic(img):
    parentTemp, img_name = os.path.split(img)
    if os.path.isdir(parentTemp):
        file_list = sorted(os.listdir(parentTemp))
        position = file_list.index(img_name)
        if position == len(file_list) - 1:
            if WHEN_REACH_END_OF_FOLDER == FOLDER_REPEAT:
                return findFirstImageInFolder(parentTemp)
            elif WHEN_REACH_END_OF_FOLDER == FOLDER_CROSS:
                return findFirstImageInFolder(nextFolder(parentTemp))
        else:
            for img in file_list[(position + 1):]:
                temp = getRealLnk(os.path.join(parentTemp, img))
                if isPic(temp):
                    return temp
            return findFirstImageInFolder(nextFolder(parentTemp))
    else:
        return ''


def previousPic(img):
    parentTemp, img_name = os.path.split(img)
    if os.path.isdir(parentTemp):
        file_list = sorted(os.listdir(parentTemp), reverse=True)
        position = file_list.index(img_name)
        if position == 0:
            if WHEN_REACH_END_OF_FOLDER == FOLDER_REPEAT:
                return findLastImageInFolder(parentTemp)
            elif WHEN_REACH_END_OF_FOLDER == FOLDER_CROSS:
                return findLastImageInFolder(previousFolder(parentTemp))
        else:
            for img in file_list[:position]:
                temp = getRealLnk(os.path.join(parentTemp, img))
                if isPic(temp):
                    return temp
            return findLastImageInFolder(previousFolder(parentTemp))
    else:
        return ''


def findFirstImageInFolder(folder):
    if os.path.isdir(folder):
        file_list = sorted(os.listdir(folder))
        for file in file_list:
            temp = getRealLnk(os.path.join(folder, file))
            if os.path.isdir(temp):
                return findFirstImageInFolder(temp)
            else:
                if isPic(temp):
                    return temp
        return findFirstImageInFolder(nextFolder(folder))
    else:
        return folder


def findLastImageInFolder(folder):
    if os.path.isdir(folder):
        file_list = sorted(os.listdir(folder), reverse=True)
        for file in file_list:
            temp = getRealLnk(os.path.join(folder, file))
            if os.path.isdir(temp):
                return findLastImageInFolder(temp)
            else:
                if isPic(temp):
                    return temp
        return findLastImageInFolder(previousFolder(folder))
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


def imageTogether(img1, img2):
    if SCREEN_WIDTH > SCREEN_HEIGHT:
        w1 = math.floor(SCREEN_HEIGHT * img1.size[0] / img1.size[1])
        w2 = math.floor(SCREEN_HEIGHT * img2.size[0] / img2.size[1])
        target_shape = (w1 + w2, SCREEN_HEIGHT)
        background = Image.new('RGB', target_shape, (0, 0, 0))
        img1 = img1.resize((w1, SCREEN_HEIGHT), Image.ANTIALIAS)
        img2 = img2.resize((w2, SCREEN_HEIGHT), Image.ANTIALIAS)
        background.paste(img1, (0, 0))
        background.paste(img2, (w1, 0))
        return betterImage(background)
    else:
        h1 = math.floor(SCREEN_WIDTH * img1.size[1] / img1.size[0])
        h2 = math.floor(SCREEN_WIDTH * img2.size[1] / img2.size[0])
        target_shape = (SCREEN_WIDTH, h1 + h2)
        background = Image.new('RGB', target_shape, (0, 0, 0))
        img1 = img1.resize((SCREEN_WIDTH, h1), Image.ANTIALIAS)
        img2 = img2.resize((SCREEN_WIDTH, h2), Image.ANTIALIAS)
        background.paste(img1, (0, 0))
        background.paste(img2, (0, h1))
        return betterImage(background)


def picRatioCanCombine(img):
    if SCREEN_WIDTH > SCREEN_HEIGHT:
        return (img.size[1] / img.size[0]) > (2 * SCREEN_HEIGHT / SCREEN_WIDTH)
    else:
        return (img.size[0] / img.size[1]) > (2 * SCREEN_WIDTH / SCREEN_HEIGHT)


getImageTry = 0


def fillImageCache():
    global getImageTry, lastImageAddr, imageCache
    if getImageTry >= 5:
        return 1
    tryTime = 0
    # timeStart = time.time()
    while not imageCache.full():
        try:
            imageTemp = getImage()
            # print(imageTemp)
        except:
            if getImageTry >= 5:
                return 1
            getImageTry = getImageTry + 1
            continue
        else:
            getImageTry = 0
        if imageTemp != '':
            try:
                # print(imageTemp)
                imageTkTemp = Image.open(imageTemp)
            except:
                continue
            else:
                if SHUFFLE and TWO_COLUMNS and picRatioCanCombine(imageTkTemp):
                    nextImageTemp = nextPic(imageTemp)
                    if nextImageTemp == '':
                        imageAddrCache.append(imageTemp)
                        lastImageAddr = imageTemp
                        imageCache.put(imageResize(imageTkTemp))
                    else:
                        imageTkTemp2 = Image.open(nextImageTemp)
                        temp2TryTime = 0
                        while not picRatioCanCombine(imageTkTemp2):
                            nextImageTemp = nextPic(nextImageTemp)
                            temp2TryTime = temp2TryTime + 1
                            if temp2TryTime > 10:
                                break
                            if nextImageTemp != '':
                                imageTkTemp2 = Image.open(nextImageTemp)
                            else:
                                continue
                        if temp2TryTime > 10:
                            imageAddrCache.append(imageTemp)
                            lastImageAddr = imageTemp
                            imageCache.put(imageResize(imageTkTemp))
                        else:
                            imageAddrCache.append(nextImageTemp)
                            lastImageAddr = nextImageTemp
                            imageCache.put(imageTogether(imageTkTemp, imageTkTemp2))
                else:
                    imageAddrCache.append(imageTemp)
                    lastImageAddr = imageTemp
                    imageCache.put(imageResize(imageTkTemp))
        else:
            if tryTime > 10:
                return 1
            else:
                tryTime = tryTime + 1
    # timeEnd = time.time()
    # addTime(timeStart, timeEnd)
    return 0


def betterImage(img):
    if SHARPEN_ON:
        try:
            # img2 = img.copy()
            # return img.filter(ImageFilter.SHARPEN)
            enh_sha = ImageEnhance.Sharpness(img)
            img = enh_sha.enhance(factor=1.7)
            # img.filter(ImageFilter.DETAIL)
            # img.filter(ImageFilter.SMOOTH)
            # img2 = ImageOps.invert(img2.filter(ImageFilter.CONTOUR))
            # img_bright = ImageEnhance.Brightness(img2)
            # img2 = img_bright.enhance(0.9)
            # img2 = img2.filter(ImageFilter.BoxBlur(5))
            # img = ImageChops.add(img,img2)
            # img = Image.blend(img,img2,0.9)
        except:
            return img
        return img
    else:
        return img


def imageResize(image):
    if (image.size[0] / image.size[1]) > (SCREEN_WIDTH / SCREEN_HEIGHT):
        needWidth = SCREEN_WIDTH
        needHeight = math.floor(SCREEN_WIDTH * image.size[1] / image.size[0])
    else:
        needHeight = SCREEN_HEIGHT
        needWidth = math.floor(SCREEN_HEIGHT * image.size[0] / image.size[1])
    return betterImage(image.resize((needWidth, needHeight), Image.ANTIALIAS))


oneClicked = False
clickSaveParentFolder = ''
clickSaveState = 0
clickSavePlayLevel = 0


def oneClick(event):  # 左键单击事件或手机上的触摸事件
    global playLevel, statePlay, parentFolder, oneClicked, clickSaveParentFolder, clickSaveState, clickSavePlayLevel
    if not oneClicked:
        clickSaveParentFolder = parentFolder
        clickSaveState = statePlay
        clickSavePlayLevel = playLevel
        playLevel = 0
        statePlay = STATE_FOLDER
        parentFolder = getParentFolder(nowImageAddr)
        drawCancelRemoveAll()
        oneClicked = True
    else:
        playLevel = clickSavePlayLevel
        statePlay = clickSaveState
        drawCancelRemoveAll()
        oneClicked = False


tabState = False
tabInput = ''


def keyPress(event):  # 按键事件响应
    global drawCancel, pauseAll, playLevel, statePlay, LOOP_TIME, select_row, select_col, modeSelect, parentFolder, \
        SHUFFLE, keyControlGroup, keyControl, lastImageAddr, shell, tabState, tabInput, oneClicked, getImageTry
    keyInput = event.keysym.lower()
    # print(repr(keyInput))
    if keyInput == 'escape':  # 退出
        player.release()
        top.destroy()
        sys.exit(0)
    else:
        if not tabState:
            if keyInput == 'tab':
                tabState = True
                tabInput = ''
            elif keyInput == 'd' or keyInput == 'a' or keyInput == 'z' or keyInput == 'x' or keyInput == 'c' or keyInput == 'v':
                if not drawCancel and not keyControl:
                    keyControl = True
                    drawCancel = True
                    lastImageAddr = nowImageAddr
                    getImageTry = 0
                    oneClicked = False
                    if keyInput == 'd':  # 顺序下一张
                        keyControlGroup[0] = 'nextPic'
                        keyControlGroup[1] = nextPic(nowImageAddr)
                    elif keyInput == 'a':  # 顺序上一张
                        keyControlGroup[0] = 'previousPic'
                        keyControlGroup[1] = previousPic(nowImageAddr)
                    elif keyInput == 'z':  # 顺序上一个文件夹
                        keyControlGroup[0] = 'previousFolder'
                        keyControlGroup[1] = findLastImageInFolder(previousFolder(oneParentFolder(nowImageAddr)))
                    elif keyInput == 'x':  # 顺序下一个文件夹
                        keyControlGroup[0] = 'nextFolder'
                        keyControlGroup[1] = findFirstImageInFolder(nextFolder(oneParentFolder(nowImageAddr)))
                    elif keyInput == 'c':  # 顺序第一个文件
                        keyControlGroup[0] = 'firstImage'
                        keyControlGroup[1] = findFirstImageInFolder(oneParentFolder(nowImageAddr))
                    elif keyInput == 'v':  # 顺序最后一个文件
                        keyControlGroup[0] = 'lastImageAddr'
                        keyControlGroup[1] = findLastImageInFolder(oneParentFolder(nowImageAddr))
                    drawCancelRemoveAll()
                    # print(keyControlGroup)
            elif keyInput == 'space':  # 下一张
                if not drawCancel:
                    drawCancel = True
                    # imageCache.get()
                    # imageAddrCache.pop(0)
            elif keyInput == 's':  # 暂停或播放
                if not pauseAll:
                    pauseAll = True
                else:
                    pauseAll = False
            elif keyInput == 'q':  # 本文件夹内随机
                if not oneClicked:
                    playLevel = 0
                    statePlay = STATE_FOLDER
                    parentFolder = getParentFolder(nowImageAddr)
                    getImageTry = 0
                    oneClicked = False
                    drawCancelRemoveAll()
            elif keyInput == 'w':  # 上一级文件夹内随机
                playLevel = 1
                statePlay = STATE_FOLDER
                parentFolder = getParentFolder(nowImageAddr)
                getImageTry = 0
                oneClicked = False
                drawCancelRemoveAll()
            elif keyInput == 'e':  # 上二级文件夹内随机
                getImageTry = 0
                playLevel = 2
                statePlay = STATE_FOLDER
                oneClicked = False
                parentFolder = getParentFolder(nowImageAddr)
                drawCancelRemoveAll()
            elif keyInput == 'r':  # 取消文件夹内随机
                getImageTry = 0
                playLevel = -1
                statePlay = STATE_PLAY_ALL
                oneClicked = False
                drawCancelRemoveAll()
            elif keyInput == 'shift_l':  # 幻灯片播放间隔+0.5秒
                LOOP_TIME = LOOP_TIME + 500
            elif keyInput == 'control_l':  # 幻灯片播放间隔-0.5秒
                LOOP_TIME = LOOP_TIME - 500
                if LOOP_TIME < 500:
                    LOOP_TIME = 500
            elif keyInput == 'quoteleft':  # 按下~取消库内播放
                modeSelect = MODE_NORMAL
                oneClicked = False
            elif keyInput == 'f':  # 取消或开启随机播放
                SHUFFLE = not SHUFFLE
            elif keyInput[0] == 'f' and keyInput != 'f':  # F1 ~ F12 选择库的行数，并进入库内播放
                if keyInput[1:].isdigit():
                    getImageTry = 0
                    select_row = int(keyInput[1:]) - 1
                    modeSelect = MODE_MY_SELECT
                    statePlay = STATE_PLAY_ALL
                    oneClicked = False
                    drawCancelRemoveAll()
            elif keyInput.isdigit():  # 1234567890 选择库的列数，并进入库内播放
                if int(keyInput) == 0:
                    select_col = 9
                else:
                    select_col = int(keyInput) - 1
                # select_col = (int(keyInput)+9) % 10
                getImageTry = 0
                modeSelect = MODE_MY_SELECT
                statePlay = STATE_PLAY_ALL
                oneClicked = False
                drawCancelRemoveAll()
            elif keyInput == 'return':  # 开始随机播放音乐
                player.stop()
                player.play(shuffleMusic())
            elif keyInput == 'shift_r':  # 暂停或播放音乐
                player.pauseOrPlay()
            elif keyInput == 'right':  # 快进10秒
                player.forward()
            elif keyInput == 'left':  # 快退10秒
                player.backward()
            elif keyInput == 'up':  # 音量+5
                player.volumeUp()
            elif keyInput == 'down':  # 音量-5
                player.volumeDown()
        else:
            if keyInput == 'tab':
                if tabInput:
                    tempFolder = findFolder(tabInput.lower(), rootFolder)
                    # print(tabInput,tempFolder)
                    if tempFolder:
                        playLevel = 0
                        statePlay = STATE_FOLDER
                        parentFolder = tempFolder
                        drawCancelRemoveAll()
                    tabInput = ''
                oneClicked = False
                tabState = False
            else:
                if len(keyInput) == 1:
                    tabInput = tabInput + keyInput


def onConfigure(event):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    if event.widget == top:
        SCREEN_WIDTH = event.width
        SCREEN_HEIGHT = event.height


def findImage(folderTemp):
    global lastImageAddr, parentFolder
    if os.path.isdir(folderTemp):
        for i in range(10):
            file_list = os.listdir(folderTemp)
            if len(file_list) == 0:
                return findImage(oneParentFolder(folderTemp))
            folderNext = getRealLnk(os.path.join(folderTemp, file_list[random.randint(0, len(file_list) - 1)]))
            if os.path.isdir(folderNext) and folderOK(folderNext):
                folderTemp = folderNext
            elif isPic(folderNext):
                lastImageAddr = folderNext
                return folderNext
        if os.path.normcase(rootFolder) == os.path.normcase(folderTemp):
            return ''
        else:
            return findImage(oneParentFolder(folderTemp))
    else:
        return ''


def isPic(name):
    namelower = os.path.split(name)[1].lower()
    return (namelower.endswith(".jpg") or namelower.endswith(".jpeg") or namelower.endswith(
        ".png") or namelower.endswith(".bmp")) and not namelower.startswith('.')


def isMusic(name):
    namelower = os.path.split(name)[1].lower()
    return (namelower.endswith("mp3") or namelower.endswith("wav") or namelower.endswith("flac") or namelower.endswith(
        "m4a") or namelower.endswith("ape")) and not namelower.startswith('.')


def getImage():
    global lastImageAddr, modeSelect, SHUFFLE, noParentFolder, keyControl, parentFolder, rootFolder
    if not keyControl:
        if SHUFFLE:
            if statePlay == STATE_PLAY_ALL:
                if modeSelect == MODE_NORMAL:
                    folderGetImage = getRealLnk(FILE_LIB[random.randint(0, len(FILE_LIB) - 1)])
                    if not os.path.isdir(folderGetImage):
                        if isPic(folderGetImage):
                            noParentFolder = True
                            lastImageAddr = folderGetImage
                            return folderGetImage
                        else:
                            return ''
                    rootFolder = folderGetImage
                    noParentFolder = False
                    return findImage(folderGetImage)
                elif modeSelect == MODE_MY_SELECT:
                    if select_row >= len(MY_SELECT_LIB):
                        modeSelect = MODE_NORMAL
                    else:
                        if select_col >= len(MY_SELECT_LIB[select_row]):
                            modeSelect = MODE_NORMAL
                        else:
                            if isinstance(MY_SELECT_LIB[select_row][select_col], list):
                                folderGetImage = getRealLnk(getRandomFromList(MY_SELECT_LIB[select_row][select_col]))
                            else:
                                folderGetImage = getRealLnk(MY_SELECT_LIB[select_row][select_col])
                            rootFolder = folderGetImage
                            noParentFolder = False
                            # print(folder)
                            if not os.path.isdir(folderGetImage):
                                if isPic(folderGetImage):
                                    lastImageAddr = folderGetImage
                                    return folderGetImage
                                else:
                                    sys.exit(1)
                            return findImage(folderGetImage)
            elif statePlay == STATE_FOLDER:
                if not parentFolder:
                    parentFolder = oneParentFolder(lastImageAddr)
                    noParentFolder = False
                return findImage(parentFolder)
        else:
            if not lastImageAddr:
                SHUFFLE = True
            else:
                lastImageAddr = nextPic(nowImageAddr)
                parentFolder = oneParentFolder(lastImageAddr)
                return lastImageAddr
    else:
        keyControl = False
        lastImageAddr = keyControlGroup[1]
        parentFolder = oneParentFolder(lastImageAddr)
        return lastImageAddr


threadRead = threading.Thread(target=fillImageCache, args=())
threadRead.setDaemon(True)


def draw():
    global drawCancel, lastImageAddr, drawStep, nowImageAddr, SCREEN_WIDTH, SCREEN_HEIGHT, threadRead
    if not pauseAll:
        if drawCancel:
            drawCancel = False
            drawStep = 0
        if drawStep == 0:
            if FULL_SCREEN and not (
                    SCREEN_WIDTH == top.winfo_screenwidth() and SCREEN_HEIGHT == top.winfo_screenheight()):
                SCREEN_WIDTH = top.winfo_screenwidth()
                SCREEN_HEIGHT = top.winfo_screenheight()
                top.geometry("%dx%d" % (SCREEN_WIDTH, SCREEN_HEIGHT))
            while (not imageCache.full()) and (not threadRead.join()):
                pass
            photo = ImageTk.PhotoImage(imageCache.get())
            label.configure(image=photo)
            label.image = photo
            label.place(relx=.5, rely=.5, anchor="center")
            nowImageAddr = imageAddrCache[0]
            imageAddrCache.pop(0)
            # top.update()
            threadRead = threading.Thread(target=fillImageCache, args=())
            threadRead.setDaemon(True)
            threadRead.start()
            # fillImageCache()
        if (drawStep * LOOP_STEP) > LOOP_TIME:
            drawStep = 0
        else:
            drawStep = drawStep + 1
    top.after(LOOP_STEP, draw)


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
    label = tk.Label(top, padx=0, pady=0, bg=BACKGROUND_COLOR)
    label.pack(side='top')
    top.configure(bg=BACKGROUND_COLOR)
    top.focus_set()
    top.bind("<Key>", keyPress)
    top.bind("<Button-1>", oneClick)
    top.configure(cursor="none")
    # top.withdraw()
    if imageCache.empty():
        if fillImageCache() == 1:
            print("Cannot find photo.")
    top.after(0, draw)
    top.mainloop()

