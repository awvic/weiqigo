#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog
import webbrowser

from board import *
import sgf
from sgfboardtree import *
from quizfactory import *

import os
import glob

import logging
import datetime

# 如果注意到這行，表示你正在(打算)看程式碼。 source code 有點 ugly, 請多包涵。

# 棋盤顯示方式 0:完整 1:放大顯示右上角棋盤 其餘類推
BOARD_DISPLAY_TYPE = {'FULL':0, 'UPPER_RIGHT': 1, 'LOWER_RIGHT': 2, 'LOWER_LEFT': 3, 'UPPER_LEFT': 4}
# 預設顯示完整19路棋盤
board_dis = BOARD_DISPLAY_TYPE['FULL']

# logger setting
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s',
    datefmt='%Y%m%d %H:%M:%S')

# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# ch.setFormatter(formatter)

# log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S.log")
log_filename = datetime.datetime.now().strftime("Honinbo.log")
fh = logging.FileHandler(log_filename)

# DEBUG 目錄或檔案存在時才紀錄DEBUG訊息
if os.path.exists("DEBUG"):
    fh.setLevel(logging.DEBUG)
else:
    fh.setLevel(logging.ERROR)
fh.setFormatter(formatter)

# logger.addHandler(ch)
logger.addHandler(fh)

# 問題庫
qf = QuizFactory()

# 是否提示，預設否
if_hint = False

# 將sgf格式的位置轉成 tk 格式的座標，方便繪圖
def sgf_to_tkcoor(text):
    # sgf move to tk coordinator
    # return nothing if text is illegal.

    x = 0
    y = 0

    LABELS = "abcdefghijklmnopqrstuvwxyz"

    if len(text) != 2:
        return

    if text[0] not in LABELS:
        return

    if text[1] not in LABELS:
        return

    for i in range(len(LABELS)):
        if text[0]==LABELS[i]:
            # x = i
            x = i

    for i in range(len(LABELS)):
        if text[1]==LABELS[i]:
            # y = i
            y = i

    return [x, y]

# 錯誤代碼
error_no = 0

# 錯誤位置
error_pos = []

# 定義變數給SGF使用
sgf_collection = None

# 由sgf讀入的棋盤結構樹
boardtree = None

# 繪製棋盤相關參數
# 19X19標準參數

B_H_SIZE = 24     # 棋盤格高度
B_W_SIZE = 23     # 棋盤格寬度
B_UPPER = 60      # 棋盤與 canvas 上緣的距離
B_LEFT = 80       # 棋盤與 canvas 左緣的距離

# 棋子 size
B_QI_SIZE = 20
B_QI_H_SIZE = B_QI_SIZE / 2


# 繪製棋盤相關參數
# 實際繪製參數(可能是全部或四角，進行解析後的實際用參數)預設全棋盤
D_LEFT = B_LEFT
D_UPPER = B_UPPER
D_H_SIZE = B_H_SIZE
D_W_SIZE = B_W_SIZE
D_QI_H_SIZE = B_QI_H_SIZE


ALPHA = "ABCDEFGHJKLMNOPQRST"
SGF = "abcdefghijklmnopqrs"


# 盤面現況的 Borad 資料結構
b = Board(board_size=19, komi=7.5)


b_w = True

window = tk.Tk()
window.title("圍棋練習 weiqigo")
window.minsize(width=600, height=660)
window.resizable(width=False, height=False)

canvas = tk.Canvas(window, width=560, height=530)

quiz_name = '題目說明'
name_label = tk.StringVar()  # 題目說明
name_label.set(quiz_name)    # 設定 name_label 的內容

step_cnt = 0                # 第幾步
cnt_label = tk.StringVar()  # 設定文字變數
cnt_label.set(step_cnt)     # 設定 a 的內容

quiz_cnt = qf.current_num() # 第幾題
quiz_label = tk.StringVar()
quiz_label.set(quiz_cnt)

ans_right = ""
ans_label = tk.StringVar()   # 是否答對
ans_label.set(ans_right)

def next():
    # 下一步按鈕
    global step_cnt 
    global b

    global error_no
    global error_pos
    error_no = 0
    error_pos = []

    global ans_right

    if boardtree:
        nextmoves = []
        nextmoves = boardtree.next_move()
        logging.debug("nextmoves list = " + BoardTree.node_list_to_str(nextmoves))

        # 顯示第幾手
        step_cnt = len(nextmoves)
        cnt_label.set(step_cnt)

        ans_right = ""
        if len(boardtree.get_next_move())==0:
            ans_right = "終 "

        ans_label.set(ans_right)

        if len(nextmoves)>0:
            b.reset(board_size=19, komi=7.5)
            # 逐步下棋
            for m in nextmoves:
                # p = m.data[2:]
                p = m.data[2:4]
                logging.debug(p)
                # if not b.play(b.sgf_to_vertex(nextmoves[0].data[2:2])):
                # if not b.play(b.sgf_to_vertex(p)):
                #     logging.debug("illegal move at " + p)

                # if len(p)!=2:
                if p==PASS_MARK:
                    # PASS 虛手
                    if not b.play(PASS):
                        logging.debug("illegal move at " + p)
                else:
                    if not b.play(b.sgf_to_vertex(p)):
                        logging.debug("illegal move at " + p)                    

            # 最後一手是虛手時顯示虛手
            # if len(nextmoves[-1].data[2:])!=2:
            if nextmoves[-1].data[2:4] == PASS_MARK:
                ans_right += "虛手"
                ans_label.set(ans_right)

            # 重繪盤面
            draw_board()        


def prev():
    # 上一步按鈕

    global step_cnt
    global b

    global error_no
    global error_pos
    error_no = 0
    error_pos = []

    global ans_right

    if boardtree:
        moves = []
        moves = boardtree.prev_moves()
        logging.debug("moves list = " + BoardTree.node_list_to_str(moves))

        # 顯示第幾手
        step_cnt = len(moves)
        cnt_label.set(step_cnt)

        ans_right = ""
        # if len(moves)==0:
        #     ans_right = "終"
        ans_label.set(ans_right)

        b.reset(board_size=19, komi=7.5)
        if len(moves)>0:

            # b.reset(board_size=19, komi=7.5)
            for m in moves:
                # p = m.data[2:]
                p = m.data[2:4]
                logging.debug(p)
                # if not b.play(b.sgf_to_vertex(nextmoves[0].data[2:2])):
                # if len(p)!=2:
                if p==PASS_MARK:
                    # PASS 虛手
                    if not b.play(PASS):
                        logging.debug("illegal move at " + p)
                else:
                    if not b.play(b.sgf_to_vertex(p)):
                        logging.debug("illegal move at " + p)

            # 最後一手是虛手時顯示虛手
            # if len(moves[-1].data[2:])!=2:
            if moves[-1].data[2:4] == PASS_MARK:
                ans_right = "虛手"
                ans_label.set(ans_right)


        # 重繪盤面
        draw_board()   



# 繪製棋盤面
def draw_board():
    
    global error_no
    global error_pos

    # 畫棋盤
    canvas.delete("all")

    # 棋盤線
    for row in range(19):
        # 水平線
        sx = D_LEFT
        sy = D_UPPER + row * D_H_SIZE
        ex = D_LEFT + D_W_SIZE * 18
        ey = D_UPPER + row * D_H_SIZE
        canvas.create_line(sx, sy, ex, ey, width=1)
    for col in range(19):
        # 垂直線
        sx = D_LEFT + col * D_W_SIZE
        sy = D_UPPER
        ex = D_LEFT + col * D_W_SIZE
        ey = D_UPPER + D_H_SIZE * 18
        canvas.create_line(sx, sy, ex, ey, width=1)


    # 棋盤座標標示
    NUMBER_UPPER_GAP = 6
    NUMBER_LEFT_GAP = 10
    ENGLISH_UPPER_GAP = 10
    ENGLISH_LEFT_GAP = 2
    FONT_SIZE=14

    # 畫數字列
    for row in range(19):
        # 左排數字列
        l_sx = D_LEFT - NUMBER_LEFT_GAP - FONT_SIZE
        l_sy = D_UPPER - NUMBER_UPPER_GAP + row * D_H_SIZE
        canvas.create_text(l_sx, l_sy, text=str(19-row), anchor='nw')

        # 右排數字列        
        r_sx = D_LEFT + NUMBER_LEFT_GAP
        r_sy = D_UPPER - NUMBER_UPPER_GAP + row * D_H_SIZE
        canvas.create_text(r_sx + 18 * D_W_SIZE, r_sy, text=str(19-row), anchor='nw')

    # 畫英文列
    for col in range(19):
        # 上排英文列
        u_sx = D_LEFT - ENGLISH_LEFT_GAP + col * D_W_SIZE
        u_sy = D_UPPER - ENGLISH_UPPER_GAP - FONT_SIZE
        canvas.create_text(u_sx, u_sy, text=ALPHA[col], anchor='nw')

        # 下排英文列        
        d_sx = D_LEFT - ENGLISH_LEFT_GAP + col * D_W_SIZE
        d_sy = D_UPPER + ENGLISH_UPPER_GAP
        canvas.create_text(d_sx, d_sy + 18 * D_H_SIZE, text=ALPHA[col], anchor='nw')

    # 畫星位
    for i in range(3):
        for j in range(3):
            canvas.create_oval(D_LEFT+(3+i*6)*D_W_SIZE-3, D_UPPER+(3+j*6)*D_H_SIZE-3, 
                               D_LEFT+(3+i*6)*D_W_SIZE+3, D_UPPER+(3+j*6)*D_H_SIZE+3, 
                               width=1, fill='#000', outline='#000')

    # 畫棋子
    b_list = b.status()

    for i in range(19):
        for j in range(19):
            if b_list[i*19+j]==BLACK or b_list[i*19+j]==WHITE:
                if b_list[i*19+j]==BLACK:
                    c_col = '#000'
                elif b_list[i*19+j]==WHITE:
                    c_col = '#fff'
                pos_y = j
                canvas.create_oval(D_LEFT+pos_y*D_W_SIZE-D_QI_H_SIZE, D_UPPER+i*D_H_SIZE-D_QI_H_SIZE, 
                                   D_LEFT+pos_y*D_W_SIZE+D_QI_H_SIZE, D_UPPER+i*D_H_SIZE+D_QI_H_SIZE, 
                                   width=1, fill=c_col, outline='#000')

    # DEBUG
    #logging.debug(' '.join(b_list))

    
    # DEBUG
    lpos = []
    lpos = b.get_last_move()
    if len(lpos)>0:
        # logging.debug("最後一手棋：" + BoardTree.node_list_to_str(lpos))
        # 調整成 tk 座標
        lpos[1] = 18 - lpos[1]
        hint_size = D_QI_H_SIZE / 3
        canvas.create_oval(D_LEFT+lpos[0]*D_W_SIZE-hint_size, D_UPPER+lpos[1]*D_H_SIZE-hint_size, 
                           D_LEFT+lpos[0]*D_W_SIZE+hint_size, D_UPPER+lpos[1]*D_H_SIZE+hint_size, 
                           width=1, fill='#f00', outline='#f00')


    # 繪製提示下一手的點(當有多手的可能時)
    if boardtree:
        move = boardtree.get_next_move()
        logging.debug("possible moves=" + BoardTree.node_list_to_str(move))
        pos = []
        # 原本的作法，只顯示有變化的手
        # if len(move)>1:
        #     # 大於一手時顯示
        #     for m in move:
        #         pos.append(sgf_to_tkcoor(m.data[2:]))

        #     for p in pos:
        #         hint_size = B_QI_H_SIZE / 2
        #         canvas.create_oval(B_LEFT+p[0]*B_W_SIZE-hint_size, B_UPPER+p[1]*B_H_SIZE-hint_size, B_LEFT+p[0]*B_W_SIZE+hint_size, B_UPPER+p[1]*B_H_SIZE+hint_size, width=1, fill='#999', outline='#999')

        # 是否顯示提示位置
        global if_hint
        if if_hint:
            for m in move:
                # 考慮虛手
                # if len(m.data[2:])!=2:
                if m.data[2:4]==PASS_MARK:
                    # 虛手
                    pass
                else:
                    pos.append(sgf_to_tkcoor(m.data[2:]))

            for p in pos:
                hint_size = D_QI_H_SIZE / 2
                canvas.create_oval(D_LEFT+p[0]*D_W_SIZE-hint_size, D_UPPER+p[1]*D_H_SIZE-hint_size, 
                                   D_LEFT+p[0]*D_W_SIZE+hint_size, D_UPPER+p[1]*D_H_SIZE+hint_size, 
                                   width=1, fill='#999', outline='#999')


    if error_no == 1 and len(error_pos)==2:
        # 畫一個叉叉
        canvas.create_line(D_LEFT+error_pos[0]*D_W_SIZE-D_QI_H_SIZE, D_UPPER+error_pos[1]*D_H_SIZE-D_QI_H_SIZE, 
                           D_LEFT+error_pos[0]*D_W_SIZE+D_QI_H_SIZE, D_UPPER+error_pos[1]*D_H_SIZE+D_QI_H_SIZE, 
                           width=6, fill='#f00')
        canvas.create_line(D_LEFT+error_pos[0]*D_W_SIZE+D_QI_H_SIZE, D_UPPER+error_pos[1]*D_H_SIZE-D_QI_H_SIZE, 
                           D_LEFT+error_pos[0]*D_W_SIZE-D_QI_H_SIZE, D_UPPER+error_pos[1]*D_H_SIZE+D_QI_H_SIZE, 
                           width=6, fill='#f00')

    # logging.debug("error_no=" + str(error_no))

    ans_right = ""


def key(event):
    global board_dis
    global D_LEFT
    global D_UPPER
    global D_H_SIZE
    global D_W_SIZE
    global D_QI_H_SIZE

    # error_no = 0
    logging.debug("pressed " + repr(event.char))
    logging.debug("pressed " + repr(event.keycode))

    # 棋盤繪製方式
    if event.keycode==112:
        # F1 => 全部 19X19棋盤
        board_dis = BOARD_DISPLAY_TYPE['FULL']
        D_LEFT = B_LEFT
        D_UPPER = B_UPPER
        D_H_SIZE = B_H_SIZE
        D_W_SIZE = B_W_SIZE
        D_QI_H_SIZE = B_QI_H_SIZE
        draw_board()
    elif event.keycode==113:
        # F2 => 右上
        board_dis = BOARD_DISPLAY_TYPE['UPPER_RIGHT']
        D_LEFT = B_LEFT -200
        D_UPPER = B_UPPER
        D_H_SIZE = B_H_SIZE + 14
        D_W_SIZE = B_W_SIZE + 12
        D_QI_H_SIZE = B_QI_H_SIZE + 6
        draw_board()
    elif event.keycode==114:
        # F3 => 右下
        board_dis = BOARD_DISPLAY_TYPE['LOWER_RIGHT']
        D_LEFT = B_LEFT - 200
        D_UPPER = B_UPPER - 260
        D_H_SIZE = B_H_SIZE + 14
        D_W_SIZE = B_W_SIZE + 12
        D_QI_H_SIZE = B_QI_H_SIZE + 6
        draw_board()
    elif event.keycode==115:
        # F4 => 左下
        board_dis = BOARD_DISPLAY_TYPE['LOWER_LEFT']
        D_LEFT = B_LEFT
        D_UPPER = B_UPPER - 260
        D_H_SIZE = B_H_SIZE + 14
        D_W_SIZE = B_W_SIZE + 12
        D_QI_H_SIZE = B_QI_H_SIZE + 6
        draw_board()

    elif event.keycode==116:
        # F5 => 左上
        board_dis = BOARD_DISPLAY_TYPE['UPPER_LEFT']
        D_LEFT = B_LEFT
        D_UPPER = B_UPPER
        D_H_SIZE = B_H_SIZE + 14
        D_W_SIZE = B_W_SIZE + 12
        D_QI_H_SIZE = B_QI_H_SIZE + 6
        draw_board()

# 右滑鼠鍵自由點選，供自由變化
def rmouse_down(event):
    global b_w
    global error_no
    global error_pos
    error_no = 0
    error_pos = []
    logging.debug("clicked at " + str(event.x) + ' ' + str(event.y))
    # logging.debug("B_LEFT - B_QI_H_SIZE : ", B_LEFT - B_QI_H_SIZE)
    # logging.debug("B_LEFT + 18 * B_H_SIZE + B_QI_H_SIZE : ", B_LEFT + 18 * B_H_SIZE + B_QI_H_SIZE)
    # logging.debug("B_UPPER - B_QI_H_SIZE : ", B_UPPER - B_QI_H_SIZE)
    # logging.debug("B_UPPER + 18 * B_W_SIZE + B_QI_H_SIZE : ", B_UPPER + 18 * B_W_SIZE + B_QI_H_SIZE)

    # if not (event.x >= B_LEFT - B_QI_H_SIZE and event.x <= B_LEFT + 18 * B_W_SIZE + B_QI_H_SIZE and 
    #         event.y >= B_UPPER - B_QI_H_SIZE and event.y <= B_UPPER + 18 * B_H_SIZE + B_QI_H_SIZE):
    #     # 棋盤外
    #     # logging.debug('棋盤外')
    #     return

    # # 換算棋盤座標
    # qx = (event.x - B_LEFT + B_W_SIZE // 2 ) // B_W_SIZE
    # qy = (event.y - B_UPPER + B_H_SIZE // 2) // B_H_SIZE


    if not (event.x >= D_LEFT - D_QI_H_SIZE and event.x <= D_LEFT + 18 * D_W_SIZE + D_QI_H_SIZE and 
            event.y >= D_UPPER - D_QI_H_SIZE and event.y <= D_UPPER + 18 * D_H_SIZE + D_QI_H_SIZE):
        # 棋盤外
        # logging.debug('棋盤外')
        return

    # 換算棋盤座標
    qx = (event.x - D_LEFT + D_W_SIZE // 2 ) // D_W_SIZE
    qy = (event.y - D_UPPER + D_H_SIZE // 2) // D_H_SIZE


    tkpos = '{}:{}'.format(qx, qy)
    logging.debug(tkpos)

    # A0 format position
    pos = '{}{}'.format(ALPHA[qx], 19-qy)
    logging.debug(pos)

    # sgf format position
    sgfpos = '{}{}'.format(SGF[qx], SGF[qy])
    logging.debug(sgfpos)

    chi_col = '#000'
    if b_w != True:
        chi_col = '#fff'

    #logging.debug("vertex={}".format(b.text_to_vertex(pos)))
    if not b.play(b.text_to_vertex(pos)):
        logging.debug("illegal move at " + pos)
    else:
        # 重繪盤面
        draw_board()


# click B_LEFT mouse to follow sgf data tree
# 左滑鼠鍵，會判斷是否點在sgf資料內
def lmouse_down(event):
    global b_w
    global error_no
    global error_pos
    error_no = 0
    error_pos = []
    logging.debug("clicked at " + str(event.x) + ' ' + str(event.y))
    # logging.debug("B_LEFT - B_QI_H_SIZE : ", B_LEFT - B_QI_H_SIZE)
    # logging.debug("B_LEFT + 18 * B_H_SIZE + B_QI_H_SIZE : ", B_LEFT + 18 * B_H_SIZE + B_QI_H_SIZE)
    # logging.debug("B_UPPER - B_QI_H_SIZE : ", B_UPPER - B_QI_H_SIZE)
    # logging.debug("B_UPPER + 18 * B_W_SIZE + B_QI_H_SIZE : ", B_UPPER + 18 * B_W_SIZE + B_QI_H_SIZE)

    # if not (event.x >= B_LEFT - B_QI_H_SIZE and event.x <= B_LEFT + 18 * B_W_SIZE + B_QI_H_SIZE and 
    #         event.y >= B_UPPER - B_QI_H_SIZE and event.y <= B_UPPER + 18 * B_H_SIZE + B_QI_H_SIZE):
    #     # 棋盤外
    #     # logging.debug('棋盤外')

    #     return

    # # 換算棋盤座標
    # qx = (event.x - B_LEFT + B_W_SIZE // 2 ) // B_W_SIZE
    # qy = (event.y - B_UPPER + B_H_SIZE // 2) // B_H_SIZE

    if not (event.x >= D_LEFT - D_QI_H_SIZE and event.x <= D_LEFT + 18 * D_W_SIZE + D_QI_H_SIZE and 
            event.y >= D_UPPER - D_QI_H_SIZE and event.y <= D_UPPER + 18 * D_H_SIZE + D_QI_H_SIZE):
        # 棋盤外
        # logging.debug('棋盤外')
        return

    # 換算棋盤座標
    qx = (event.x - D_LEFT + D_W_SIZE // 2 ) // D_W_SIZE
    qy = (event.y - D_UPPER + D_H_SIZE // 2) // D_H_SIZE

    tkpos = '{}:{}'.format(qx, qy)
    logging.debug(tkpos)

    # A0 format position
    pos = '{}{}'.format(ALPHA[qx], 19-qy)
    #logging.debug(pos)

    # sgf format position
    sgfpos = '{}{}'.format(SGF[qx], SGF[qy])
    logging.debug(sgfpos)

    # 取得下一手(sgf資料，可能有紀錄變化，故有多手的可能)
    move = boardtree.get_next_move()
    logging.debug("possible moves=" + BoardTree.node_list_to_str(move))

    # 如果左滑鼠鍵點中可能手，則將這手設為下一手棋
    hit = False
    global ans_right
    ans_right = ""
    for n in move:
        if sgfpos == n.data[2:4]:
            hit = True
            boardtree.set_next_move(sgfpos)
            logging.debug("n.tag=" + n.tag)
            if len(n.tag)>=6 and n.tag[5:]==RIGHT_MARK:
                # problem solved
                logging.debug("problem solved!")
                ans_right = "正確"
            elif len(n.tag)>=6 and n.tag[5:]==WRONG_MARK:
                # problem solved
                logging.debug("wrong!")
                ans_right = "錯誤"


    # 判斷是否為葉結點(sgf無下一手棋)且 無 正確或錯誤訊息時
    if len(boardtree.get_next_move())==0 and len(ans_right)==0:
        ans_right = "終"

    ans_label.set(ans_right)

    if hit == False:
        logging.debug("wrong")
        error_no = 1
        error_pos = (qx, qy)
    logging.debug("qx=" + str(qx) + " qy=" + str(qy))
        

    if boardtree:
        b.reset(board_size=19, komi=7.5)
        moves = boardtree.get_current_path()
        if len(moves)>0:
            # b.reset(board_size=19, komi=7.5)
            for m in moves:
                # p = m.data[2:]
                p = m.data[2:4]
                logging.debug(p)
                # if not b.play(b.sgf_to_vertex(nextmoves[0].data[2:2])):
                # if not b.play(b.sgf_to_vertex(p)):
                #     logging.debug("illegal move at " + p)

                # if len(p)!=2:
                if p==PASS_MARK:
                    # PASS 虛手
                    if not b.play(PASS):
                        logging.debug("illegal move at " + p)
                else:
                    if not b.play(b.sgf_to_vertex(p)):
                        logging.debug("illegal move at " + p)

        # 重繪盤面
        draw_board()   


def motion(event):
    x, y = event.x, event.y

    if not (event.x >= B_LEFT - B_QI_H_SIZE and event.x <= B_LEFT + 18 * B_W_SIZE + B_QI_H_SIZE and 
            event.y >= B_UPPER - B_QI_H_SIZE and event.y <= B_UPPER + 18 * B_H_SIZE + B_QI_H_SIZE):
        logging.debug('棋盤外')
        return

    qx = (event.x - B_LEFT + B_W_SIZE // 2 ) // B_W_SIZE
    qy = (event.y - B_UPPER + B_H_SIZE // 2) // B_H_SIZE

    logging.debug('{}, {}'.format(qx, qy))


def load_file():
    global sgf_collection
    file_path = filedialog.askopenfilename()   # 選擇檔案後回傳檔案路徑與名稱
    logging.debug(file_path)                   # 印出路徑
    # testing read and show sgf
    global boardtree
    boardtree = BoardTree(file_path)
    boardtree.show_tree()
    b.reset(board_size=19, komi=7.5)
    draw_board()


def load_and_show_question_file():
    global sgf_collection
    file_path = filedialog.askopenfilename()   # 選擇檔案後回傳檔案路徑與名稱
    logging.debug(file_path)                   # 印出路徑
    # testing read and show sgf
    global boardtree
    boardtree = BoardTree(file_path)
    boardtree.show_tree()

    # 讀死活題
    global step_cnt 
    global b

    global error_no
    global error_pos
    error_no = 0
    error_pos = []

    if boardtree:
        nextmoves = []
        nextmoves = boardtree.get_question_move()
        logging.debug("nextmoves list = " + BoardTree.node_list_to_str(nextmoves))
        logging.debug("nextmoves len = " + str(len(nextmoves)))

        # # 顯示題目說明
        # quiz_name = boardtree.current_quiz_name()
        # name_label.set(quiz_name)    # 設定 name_label 的內容

        # 顯示第幾手
        step_cnt = len(nextmoves)
        cnt_label.set(step_cnt)

        if len(nextmoves)>0:
            b.reset(board_size=19, komi=7.5)
            for m in nextmoves:
                logging.debug("m.data=" + m.data)
                # p = m.data[2:]
                p = m.data[2:4]
                logging.debug(p)
                # if not b.play(b.sgf_to_vertex(nextmoves[0].data[2:2])):
                # if not b.play(b.sgf_to_vertex(p)):
                #     logging.debug("illegal move at " + p)

                # if len(p)!=2:
                if p==PASS_MARK:
                    # PASS 虛手
                    if not b.play(PASS):
                        logging.debug("illegal move at " + p)
                else:
                    if not b.play(b.sgf_to_vertex(p)):
                        logging.debug("illegal move at " + p)


            # 重繪盤面
            draw_board()        

def switch_question_file():
    global qf
    global sgf_collection
    file_path = qf.current_quiz_full_name()      # 選擇檔案後回傳檔案路徑與名稱
    logging.debug(file_path)                     # 印出路徑
    global boardtree
    boardtree = BoardTree(file_path)
    boardtree.show_tree()
    qf.set_current_quiz_comment(boardtree.comment)
    # 紀錄目前的題目名稱
    qf.save_status()

    # 讀死活題
    global step_cnt
    global b

    global error_no
    global error_pos
    error_no = 0
    error_pos = []

    global ans_right
    ans_right = ""
    ans_label.set(ans_right)

    if boardtree:
        nextmoves = []
        nextmoves = boardtree.get_question_move()
        logging.debug("nextmoves list = " + BoardTree.node_list_to_str(nextmoves))
        logging.debug("nextmoves len = " + str(len(nextmoves)))

        # 顯示題目說明
        quiz_name = qf.current_quiz_name()[:-4] + ' ' + qf.current_quiz_comment()
        name_label.set(quiz_name)    # 設定 name_label 的內容

        # 顯示第幾手
        step_cnt = len(nextmoves)
        cnt_label.set(step_cnt)

        if len(nextmoves)>0:
            b.reset(board_size=19, komi=7.5)
            for m in nextmoves:
                logging.debug("m.data=" + m.data)
                # p = m.data[2:]
                p = m.data[2:4]
                logging.debug(p)
                # if not b.play(b.sgf_to_vertex(nextmoves[0].data[2:2])):
                # if not b.play(b.sgf_to_vertex(p)):
                #     logging.debug("illegal move at " + p)

                # if len(p)!=2:
                if p==PASS_MARK:
                    # PASS 虛手
                    if not b.play(PASS):
                        logging.debug("illegal move at " + p)
                else:
                    if not b.play(b.sgf_to_vertex(p)):
                        logging.debug("illegal move at " + p)


            # 重繪盤面
            draw_board()        


# 讀folder內的sgf們，使成為一系列問題
def load_folder():

    file_path = filedialog.askdirectory()
    logging.debug("==>" + file_path)
    file_list = glob.glob(glob.escape(file_path) + "/*.sgf")
    logging.debug(file_list)
    file_list = listdir(file_path)
    logging.debug(file_list)

    global qf
    qf.load_quiz(file_path)
    qf.show()

    # 前次作到第幾題的紀錄
    qf.load_status()
    switch_question_file()

    # 顯示第幾題
    # quiz_cnt = qf.current_num()
    # quiz_label.set(quiz_cnt)
    quiz_label.set(str(qf.current_num()) + '/' + str(qf.cnt()))


def reload_quiz():
    global qf

    # 顯示第幾題
    quiz_cnt = qf.current_num()
    quiz_label.set(str(qf.current_num()) + '/' + str(qf.cnt()))

    switch_question_file()

def prev_quiz():
    global qf
    qf.prev()

    # 顯示第幾題
    # quiz_cnt = qf.current_num()
    # quiz_label.set(quiz_cnt)
    quiz_label.set(str(qf.current_num()) + '/' + str(qf.cnt()))

    switch_question_file()

def next_quiz():
    global qf
    qf.next()

    # 顯示第幾題
    # quiz_cnt = qf.current_num()
    # quiz_label.set(quiz_cnt)
    quiz_label.set(str(qf.current_num()) + '/' + str(qf.cnt()))

    switch_question_file()

def show_hint():
    global if_hint
    if_hint = not if_hint
    draw_board()

def OpenUrl():
    webbrowser.open_new('https://github.com/awvic/weiqigo')



# 第一次執行，繪製初始盤面
draw_board()

# canvas.bind("<Key>", key)
#canvas.bind('<Motion>', motion)
canvas.bind("<Button-1>", lmouse_down)
canvas.bind("<Button-3>", rmouse_down)
canvas.pack()

window.bind("<Key>", key)


#label 題目
# mylabel_name = tk.Label(window, textvariable=name_label, font=('Arial',18), fg='#00f')  # 放入標籤
mylabel_name = tk.Label(window, textvariable=name_label, font=('微軟正黑體',18), fg='#00f')  # 放入標籤
mylabel_name.place(relx=0.1, rely=0.80)

#label 第幾手
# mylabel1 = tk.Label(window, textvariable=cnt_label, font=('Arial',20))  # 放入標籤
mylabel1 = tk.Label(window, textvariable=cnt_label, font=('微軟正黑體',20))  # 放入標籤
# mylabel1.pack()
mylabel1.place(relx=0.72, rely=0.85)

#label 第幾題
# mylabel2 = tk.Label(window, textvariable=quiz_label, font=('Arial',20))  # 放入標籤
mylabel2 = tk.Label(window, textvariable=quiz_label, font=('微軟正黑體',20))  # 放入標籤
# mylabel2.pack()
mylabel2.place(relx=0.72, rely=0.92)

#label 是否答對
# mylabel3 = tk.Label(window, textvariable=ans_label, font=('Arial',20), fg='#f00')  # 放入標籤
mylabel3 = tk.Label(window, textvariable=ans_label, font=('微軟正黑體',20), fg='#f00')  # 放入標籤
# mylabel3.pack()
mylabel3.place(relx=0.86, rely=0.80)

# Button 設定 command 參數
btn1 = tk.Button(window,
                text='上一步',
                # font=('Arial',14,'bold'),
                font=('微軟正黑體',14),
                command=prev
              )
# btn1.pack(side='right')
btn1.place(relx=0.36, rely=0.85)

btn2 = tk.Button(window,
                text='下一步',
                # font=('Arial',14,'bold'),
                font=('微軟正黑體',14),
                command=next
              )
# btn2.pack(side='right')
btn2.place(relx=0.50, rely=0.85)


# Button 設定 command 參數，點擊按鈕時執行 show 函式
# btn3 = tk.Button(window,
#                 text='讀檔案',
#                 # font=('Arial',14,'bold'),
#                 font=('微軟正黑體',14,'bold'),
#                 command=load_file
#                 #command=load_and_show_question_file
#               )
# # btn3.pack()
# btn3.place(relx=0.1, rely=0.85)


# Button 設定 command 參數，點擊按鈕時執行 show 函式
btn_folder = tk.Button(window,
                text='選目錄',
                # font=('Arial',14,'bold'),
                font=('微軟正黑體',14),
                command=load_folder
              )
btn_folder.place(relx=0.1, rely=0.92)


btn_reload_quiz = tk.Button(window,
                text='重答',
                # font=('Arial',14,'bold'),
                font=('微軟正黑體',14),
                command=reload_quiz
              )
# btn1.pack(side='right')
btn_reload_quiz.place(relx=0.23, rely=0.92)



# Button 設定 command 參數
btn_prev_quiz = tk.Button(window,
                text='上一題',
                # font=('Arial',14,'bold'),
                font=('微軟正黑體',14),
                command=prev_quiz
              )
# btn1.pack(side='right')
btn_prev_quiz.place(relx=0.36, rely=0.92)

btn_next_quiz = tk.Button(window,
                text='下一題',
                # font=('Arial',14,'bold'),
                font=('微軟正黑體',14),
                command=next_quiz
              )
# btn2.pack(side='right')
btn_next_quiz.place(relx=0.50, rely=0.92)


hint_label = tk.StringVar()
hint_btn = tk.Checkbutton(window, text='提示', font=('微軟正黑體',10),
                            variable=hint_label, onvalue='1', offvalue='0',
                            command=show_hint)
hint_btn.place(relx=0.01, rely=0.92)
hint_btn.deselect()

# msgLabel = tk.Label(window, text='錯誤', font=('Arial',14,'bold'))  # 建立 label 標籤
# msgLabel.pack()                                                     # 加入視窗中

info_btn = tk.Button(window, text="?", command=OpenUrl)
info_btn.place(relx=0.96, rely=0.96)

window.mainloop()
