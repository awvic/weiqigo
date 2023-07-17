#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
# from pydlgo.board import *
from board import *
import sgf
from sgfboardtree import BoardTree

from tkinter import filedialog

import glob

import logging
import datetime

from quizfactory import *


# logger setting
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s',
    datefmt='%Y%m%d %H:%M:%S')

# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# ch.setFormatter(formatter)

log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S.log")
fh = logging.FileHandler(log_filename)
fh.setLevel(logging.DEBUG)
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


h_size = 24  # 棋盤格高度
w_size = 23  # 棋盤格寬度
upper = 60   # 棋盤與 canvas 上緣的距離
left = 80    # 棋盤與 canvas 左緣的距離

# 棋子 size
qi_size = 20
qi_h_size = qi_size / 2


text_upper_r = upper - 28
text_left_r = left -2

ALPHA = "ABCDEFGHJKLMNOPQRST"
SGF = "abcdefghijklmnopqrs"


# 盤面現況的 Borad 資料結構
b = Board(board_size=19, komi=7.5)


b_w = True

window = tk.Tk()
window.title("圍棋練習")
window.minsize(width=600, height=660)
window.resizable(width=False, height=False)

canvas = tk.Canvas(window, width=600, height=660)

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
    global step_cnt        # n 是全域變數
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
            ans_right = "終"

        ans_label.set(ans_right)

        if len(nextmoves)>0:
            b.reset(board_size=19, komi=7.5)
            for m in nextmoves:
                p = m.data[2:]
                logging.debug(p)
                # if not b.play(b.sgf_to_vertex(nextmoves[0].data[2:2])):
                if not b.play(b.sgf_to_vertex(p)):
                    logging.debug("illegal move at " + p)

            # 重繪盤面
            draw_board()        


def prev():
    # 上一步按鈕

    global step_cnt        # n 是全域變數
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
                p = m.data[2:]
                logging.debug(p)
                # if not b.play(b.sgf_to_vertex(nextmoves[0].data[2:2])):
                if not b.play(b.sgf_to_vertex(p)):
                    logging.debug("illegal move at " + p)
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
        sx = left
        sy = upper + row * h_size
        ex = left + w_size * 18
        ey = upper + row * h_size
        canvas.create_line(sx, sy, ex, ey, width=1)
    for col in range(19):
        # 垂直線
        sx = left + col * w_size
        sy = upper
        ex = left + col * w_size
        ey = upper + h_size * 18
        canvas.create_line(sx, sy, ex, ey, width=1)

    # 棋盤座標標示
    text_upper_c = upper - 8
    text_left_c = left - 30

    # for row in reversed(range(19)):
    for row in range(19):
        sx = text_left_c
        sy = text_upper_c + row * h_size
        canvas.create_text(sx, sy, text=str(19-row), anchor='nw')
        canvas.create_text(sx + 19 * w_size + 28, sy, text=str(19-row), anchor='nw')

    for col in range(19):
        sx = text_left_r + col * w_size
        sy = text_upper_r
        canvas.create_text(sx, sy, text=ALPHA[col], anchor='nw')
        canvas.create_text(sx, sy + 19 * w_size + 38, text=ALPHA[col], anchor='nw')

    # 畫星位
    for i in range(3):
        for j in range(3):
            canvas.create_oval(left+(3+i*6)*w_size-3, upper+(3+j*6)*h_size-3, left+(3+i*6)*w_size+3, upper+(3+j*6)*h_size+3, width=1, fill='#000', outline='#000')

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
                canvas.create_oval(left+pos_y*w_size-qi_h_size, upper+i*h_size-qi_h_size, left+pos_y*w_size+qi_h_size, upper+i*h_size+qi_h_size, width=1, fill=c_col, outline='#000')

    # DEBUG
    #logging.debug(' '.join(b_list))

    # DEBUG
    lpos = []
    lpos = b.get_last_move()
    if len(lpos)>0:
        # logging.debug("最後一手棋：" + BoardTree.node_list_to_str(lpos))
        # 調整成 tk 座標
        lpos[1] = 18 - lpos[1]
        hint_size = qi_h_size / 3
        canvas.create_oval(left+lpos[0]*w_size-hint_size, upper+lpos[1]*h_size-hint_size, left+lpos[0]*w_size+hint_size, upper+lpos[1]*h_size+hint_size, width=1, fill='#f00', outline='#f00')

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
        #         hint_size = qi_h_size / 2
        #         canvas.create_oval(left+p[0]*w_size-hint_size, upper+p[1]*h_size-hint_size, left+p[0]*w_size+hint_size, upper+p[1]*h_size+hint_size, width=1, fill='#999', outline='#999')

        # 是否顯示提示位置
        global if_hint
        if if_hint:
            for m in move:
                pos.append(sgf_to_tkcoor(m.data[2:]))

            for p in pos:
                hint_size = qi_h_size / 2
                canvas.create_oval(left+p[0]*w_size-hint_size, upper+p[1]*h_size-hint_size, left+p[0]*w_size+hint_size, upper+p[1]*h_size+hint_size, width=1, fill='#999', outline='#999')

    # message = ""
    if error_no == 1 and len(error_pos)==2:
        # message += "錯誤"
        # 畫一個叉叉
        canvas.create_line(left+error_pos[0]*w_size-qi_h_size, upper+error_pos[1]*h_size-qi_h_size, left+error_pos[0]*w_size+qi_h_size, upper+error_pos[1]*h_size+qi_h_size, width=6, fill='#f00')
        canvas.create_line(left+error_pos[0]*w_size+qi_h_size, upper+error_pos[1]*h_size-qi_h_size, left+error_pos[0]*w_size-qi_h_size, upper+error_pos[1]*h_size+qi_h_size, width=6, fill='#f00')

    # logging.debug("error_no=" + str(error_no))

    # reset label
    ans_right = ""


# draw_board()

def key(event):
    # error_no = 0
    logging.debug("pressed " + repr(event.char))

# 右滑鼠鍵自由點選，供自由變化
def rmouse_down(event):
    global b_w
    global error_no
    global error_pos
    error_no = 0
    error_pos = []
    logging.debug("clicked at " + str(event.x) + ' ' + str(event.y))
    # logging.debug("left - qi_h_size : ", left - qi_h_size)
    # logging.debug("left + 18 * h_size + qi_h_size : ", left + 18 * h_size + qi_h_size)
    # logging.debug("upper - qi_h_size : ", upper - qi_h_size)
    # logging.debug("upper + 18 * w_size + qi_h_size : ", upper + 18 * w_size + qi_h_size)

    if not (event.x >= left - qi_h_size and event.x <= left + 18 * w_size + qi_h_size and 
            event.y >= upper - qi_h_size and event.y <= upper + 18 * h_size + qi_h_size):
        # 棋盤外
        # logging.debug('棋盤外')

        # boardtree = BoardTree("test02.sgf")
        # boardtree = BoardTree("test03.sgf")
        # boardtree.show_tree()

        return

    # 換算棋盤座標
    qx = (event.x - left + w_size // 2 ) // w_size
    qy = (event.y - upper + h_size // 2) // h_size


    tkpos = '{}:{}'.format(qx, qy)
    logging.debug(tkpos)

    # A0 format position
    pos = '{}{}'.format(ALPHA[qx], 19-qy)
    logging.debug(pos)
    #logging.debug('{}{}'.format(ALPHA[qx], 19-qy))

    # sgf format position
    # sgfpos = '{}{}'.format(ALPHA3[qx], ALPHA2[18-qy])
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


# click left mouse to follow sgf data tree
# 左滑鼠鍵，會判斷是否點在sgf資料內
def lmouse_down(event):
    global b_w
    global error_no
    global error_pos
    error_no = 0
    error_pos = []
    logging.debug("clicked at " + str(event.x) + ' ' + str(event.y))
    # logging.debug("left - qi_h_size : ", left - qi_h_size)
    # logging.debug("left + 18 * h_size + qi_h_size : ", left + 18 * h_size + qi_h_size)
    # logging.debug("upper - qi_h_size : ", upper - qi_h_size)
    # logging.debug("upper + 18 * w_size + qi_h_size : ", upper + 18 * w_size + qi_h_size)

    if not (event.x >= left - qi_h_size and event.x <= left + 18 * w_size + qi_h_size and 
            event.y >= upper - qi_h_size and event.y <= upper + 18 * h_size + qi_h_size):
        # 棋盤外
        # logging.debug('棋盤外')

        # boardtree = BoardTree("test02.sgf")
        # boardtree = BoardTree("test03.sgf")
        # boardtree.show_tree()

        return

    # 換算棋盤座標
    qx = (event.x - left + w_size // 2 ) // w_size
    qy = (event.y - upper + h_size // 2) // h_size

    tkpos = '{}:{}'.format(qx, qy)
    logging.debug(tkpos)

    # A0 format position
    pos = '{}{}'.format(ALPHA[qx], 19-qy)
    #logging.debug(pos)
    #logging.debug('{}{}'.format(ALPHA[qx], 19-qy))

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
        # if sgfpos == n.data[2:]:
        if sgfpos == n.data[2:4]:
            hit = True
            boardtree.set_next_move(sgfpos)
            logging.debug("n.tag=" + n.tag)
            if len(n.tag)>=6 and n.tag[5:]=='r':
                # problem solved
                logging.debug("problem solved!")
                ans_right = "正確"
            elif len(n.tag)>=6 and n.tag[5:]=='w':
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
                p = m.data[2:]
                logging.debug(p)
                # if not b.play(b.sgf_to_vertex(nextmoves[0].data[2:2])):
                if not b.play(b.sgf_to_vertex(p)):
                    logging.debug("illegal move at " + p)
        # 重繪盤面
        draw_board()   


def motion(event):
    x, y = event.x, event.y

    if not (event.x >= left - qi_h_size and event.x <= left + 18 * w_size + qi_h_size and 
            event.y >= upper - qi_h_size and event.y <= upper + 18 * h_size + qi_h_size):
        logging.debug('棋盤外')
        return

    qx = (event.x - left + w_size // 2 ) // w_size
    qy = (event.y - upper + h_size // 2) // h_size

    logging.debug('{}, {}'.format(qx, qy))


def load_file():
    global sgf_collection
    file_path = filedialog.askopenfilename()   # 選擇檔案後回傳檔案路徑與名稱
    logging.debug(file_path)                           # 印出路徑
    # testing read and show sgf
    global boardtree
    boardtree = BoardTree(file_path)
    boardtree.show_tree()
    b.reset(board_size=19, komi=7.5)
    draw_board()


def load_and_show_question_file():
    global sgf_collection
    file_path = filedialog.askopenfilename()   # 選擇檔案後回傳檔案路徑與名稱
    logging.debug(file_path)                           # 印出路徑
    # testing read and show sgf
    global boardtree
    boardtree = BoardTree(file_path)
    boardtree.show_tree()

    # 讀死活題
    global step_cnt        # n 是全域變數
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
                p = m.data[2:]
                logging.debug(p)
                # if not b.play(b.sgf_to_vertex(nextmoves[0].data[2:2])):
                if not b.play(b.sgf_to_vertex(p)):
                    logging.debug("illegal move at " + p)

            # 重繪盤面
            draw_board()        

def switch_question_file():
    global qf
    global sgf_collection
    file_path = qf.current_quiz_full_name()      # 選擇檔案後回傳檔案路徑與名稱
    logging.debug(file_path)                             # 印出路徑
    global boardtree
    boardtree = BoardTree(file_path)
    boardtree.show_tree()
    qf.set_current_quiz_comment(boardtree.comment)

    # 讀死活題
    global step_cnt        # n 是全域變數
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
                p = m.data[2:]
                logging.debug(p)
                # if not b.play(b.sgf_to_vertex(nextmoves[0].data[2:2])):
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

    # 顯示第幾題
    # quiz_cnt = qf.current_num()
    # quiz_label.set(quiz_cnt)
    quiz_label.set(str(qf.current_num()) + '/' + str(qf.cnt()))

    switch_question_file()

def reload_quiz():
    global qf

    # 顯示第幾題
    quiz_cnt = qf.current_num()
    quiz_label.set(quiz_cnt)

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



# 第一次執行，繪製初始盤面
draw_board()

canvas.bind("<Key>", key)
#canvas.bind('<Motion>', motion)
canvas.bind("<Button-1>", lmouse_down)
canvas.bind("<Button-3>", rmouse_down)

canvas.pack()


#label 題目
mylabel_name = tk.Label(window, textvariable=name_label, font=('Arial',18), fg='#00f')  # 放入標籤
mylabel_name.place(relx=0.1, rely=0.80)

#label 第幾手
mylabel1 = tk.Label(window, textvariable=cnt_label, font=('Arial',20))  # 放入標籤
# mylabel1.pack()
mylabel1.place(relx=0.76, rely=0.85)

#label 第幾題
mylabel2 = tk.Label(window, textvariable=quiz_label, font=('Arial',20))  # 放入標籤
# mylabel2.pack()
mylabel2.place(relx=0.76, rely=0.92)

#label 是否答對
mylabel3 = tk.Label(window, textvariable=ans_label, font=('Arial',20), fg='#f00')  # 放入標籤
# mylabel3.pack()
mylabel3.place(relx=0.86, rely=0.80)

# Button 設定 command 參數
btn1 = tk.Button(window,
                text='上一步',
                font=('Arial',14,'bold'),
                command=prev
              )
# btn1.pack(side='right')
btn1.place(relx=0.36, rely=0.85)

btn2 = tk.Button(window,
                text='下一步',
                font=('Arial',14,'bold'),
                command=next
              )
# btn2.pack(side='right')
btn2.place(relx=0.54, rely=0.85)


# Button 設定 command 參數，點擊按鈕時執行 show 函式
btn3 = tk.Button(window,
                text='讀檔案',
                font=('Arial',14,'bold'),
                command=load_file
                #command=load_and_show_question_file
              )
# btn3.pack()
btn3.place(relx=0.1, rely=0.85)


# Button 設定 command 參數，點擊按鈕時執行 show 函式
btn_folder = tk.Button(window,
                text='選目錄',
                font=('Arial',14,'bold'),
                command=load_folder
              )
btn_folder.place(relx=0.1, rely=0.92)


btn_reload_quiz = tk.Button(window,
                text='重答',
                font=('Arial',14,'bold'),
                command=reload_quiz
              )
# btn1.pack(side='right')
btn_reload_quiz.place(relx=0.25, rely=0.92)



# Button 設定 command 參數
btn_prev_quiz = tk.Button(window,
                text='上一題',
                font=('Arial',14,'bold'),
                command=prev_quiz
              )
# btn1.pack(side='right')
btn_prev_quiz.place(relx=0.36, rely=0.92)

btn_next_quiz = tk.Button(window,
                text='下一題',
                font=('Arial',14,'bold'),
                command=next_quiz
              )
# btn2.pack(side='right')
btn_next_quiz.place(relx=0.54, rely=0.92)


hint_label = tk.StringVar()
hint_btn = tk.Checkbutton(window, text='提示',
                            variable=hint_label, onvalue='1', offvalue='0',
                            command=show_hint)
hint_btn.place(relx=0.01, rely=0.92)
hint_btn.deselect()

# msgLabel = tk.Label(window, text='錯誤', font=('Arial',14,'bold'))  # 建立 label 標籤
# msgLabel.pack()                                                     # 加入視窗中


window.mainloop()
