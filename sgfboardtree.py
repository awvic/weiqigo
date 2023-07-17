#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# from pydlgo.board import *
from board import *
import sgf
from treelib import Node, Tree
import uuid
import codecs

import logging
import datetime

# 將整個 sgf 檔案 load 進 treelib 內
# 方便後續使用

# 棋局樹
# 根結點永遠是root
# root的下一結點是sgf的第一步棋資料


class BoardTree(object):

    def _trace_child(self, child, p):
        nodeslen = len(child.nodes)
        last_parent = p
        for node in child.nodes:
            move = ""
            comment = ""
            for p in node.properties.items():
                if p[0][0] == "B" or p[0][0] == "W":
                    move = p[0][0]+":"+p[1][0]
                if p[0][0] == "C":
                    comment = p[1][0]
            if move:
                uid = uuid.uuid4()
                self._tree.create_node(move+":"+comment, uid, parent=last_parent, data=move)
                last_parent = uid

        for i in range(len(child.children)):
            self._trace_child(child.children[i], last_parent)

    def __init__(self, sgf_file):
        self._tree = Tree()
        self._tree.create_node("root", "root")  # root node
        self._sgf_file = sgf_file
        self._current_node = "root"  # 將 root 設為初始結點
        self._comment = ""
        last_parent = "root"
        with codecs.open(self._sgf_file, "r", "utf-8") as f:
            collection = sgf.parse(f.read())
            # 只使用 Game 0

            # 第 0 個 child 是根 nodes (長子->長孫->長曾孫) (但沒有變化的sgf不會有)
            fc_move = ""  # 第一個變化的位置
            first_div = ""  # 第一個變化的node 的 identifier
            if len(collection.children[0].children)>0:
                first_child = collection.children[0].children[0].nodes[0]
                for p in first_child.properties.items():
                    if len(p[0])==1 and (p[0][0] == "B" or p[0][0] == "W"):
                        fc_move = p[0][0]+":"+p[1][0]  # 第一個變化

                logging.debug("first child move:" + fc_move)

            if_black_white = False # 是否出現過黑或白下子了(為了紀錄SGF的註記)
            for node in collection[0]:
                # collection[0]裏的 nodes 是主節點的所有nodes(整局棋內由第一手到最後一手)
                # 所以要自己找出第一個分支的點，只紀錄第一變化手之前的點
                # 其餘的棋在child內紀錄

                move = ""
                comment = ""
                for p in node.properties.items():
                    if len(p[0])==1 and (p[0][0] == "B" or p[0][0] == "W"):
                        move = p[0][0]+":"+p[1][0]
                        if_black_white = True
                    if len(p[0])==1 and p[0][0] == "C":
                        comment = p[1][0]
                        if if_black_white == False:
                            self._comment = comment # 整個sgf的註記(在B或W出現前的C是整個sgf的註記)
                if move:
                    if move == fc_move:
                        # 第一手變化棋，先跳離，其餘手棋在child那段處理
                        break
                    uid = uuid.uuid4()
                    self._tree.create_node(move+":"+comment, uid, parent=last_parent, data=move)
                    last_parent = uid

            # 第0個child包含在collection[0]的nodes內了。(上一段只處理第一分支前)
            # 後續處理各分支的資料
            for i in range(0, len(collection.children[0].children)):
                self._trace_child(collection.children[0].children[i], last_parent)
              
    def __str__(self):
        return "A Board Tree"

    @property
    def comment(self):
        return self._comment

    def show_tree(self):
        # self._tree.show()
        logging.debug(self._tree.to_json())

    # 移至下一手，並回傳第一手至當手棋資料
    def next_move(self):
        # moves = [] # 存 node
        # childs = self._tree.children(self._current_node)
        # if len(childs)>0:
        #     moves.insert(0, childs[0])
        #     # DEBUG 暫時只到第一手
        #     self._current_node = childs[0].identifier
        #     parent = self._tree.parent(childs[0].identifier)
        #     while parent.identifier != "root":
        #         logging.debug("p=", parent)
        #         moves.insert(0, parent)
        #         # nexts.append(parent)
        #         parent = self._tree.parent(parent.identifier)
        # return moves

        moves = [] # 存 node
        childs = self._tree.children(self._current_node)
        if len(childs)>0:
            # DEBUG 暫時只到第一手
            self._current_node = childs[0].identifier        

        return self.get_current_path()


    # 只回傳下一手
    def get_next_move(self):
        move = [] # 存 node
        move = self._tree.children(self._current_node)
        return move

    def set_next_move(self, m):
        move = [] # 存 node
        move = self._tree.children(self._current_node)
        for mv in move:
            if m == mv.data[2:]:
                self._current_node = mv.identifier

    # 移至上一手棋，並回傳第一手至當手棋資料
    def prev_moves(self):
        if self._current_node == "root":
            return []

        moves = [] # 存 node
        # p = self._tree.get_node(self._current_node)
        self._current_node = self._tree.parent(self._current_node).identifier

        return self.get_current_path()

        # if self._current_node == "root":
        #     return []

        # p = self._tree.get_node(self._current_node)
        # moves.insert(0, p)
        # parent = self._tree.parent(p.identifier)
        # while parent.identifier != "root":
        #     logging.debug("p=", parent)
        #     moves.insert(0, parent)
        #     # nexts.append(parent)
        #     parent = self._tree.parent(parent.identifier)
        # return moves


    # 回傳自第一手至本手
    def get_current_path(self):
        moves = [] # 存 node

        if self._current_node == "root":
            return []

        p = self._tree.get_node(self._current_node)
        moves.insert(0, p)
        parent = self._tree.parent(p.identifier)
        while parent.identifier != "root":
            logging.debug("p=" + parent.tag)
            moves.insert(0, parent)
            parent = self._tree.parent(parent.identifier)
        return moves


    # 回傳第一手至註解為qq當手棋資料(只判斷第一分支)
    # 死活題 qq 是題目的開始
    # r 是 答對
    # w 是 答錯
    def get_question_move(self):

        # 判斷作為死活題標記符號是否存在，若不存在則只留第一手棋
        qq_exist = False

        self._current_node = "root"  # 將 root 設為初始結點

        moves = [] # 存 node

        # p = self._tree.get_node(self._current_node)
        # moves.append(p)

        childs = self._tree.children(self._current_node)
        while len(childs)>0:
            # 只判斷第一分支
            self._current_node = childs[0].identifier
            p = self._tree.get_node(self._current_node)
            moves.append(p)
            # logging.debug("p tag=" + p.tag)
            # logging.debug("len(p.tag)=" + str(len(p.tag)))
            if len(p.tag)>5 and p.tag[5:]=='qq':
                # logging.debug("p tag[5:2]=" + p.tag[5:])
                # logging.debug("i break")
                qq_exist = True
                break
            childs = self._tree.children(self._current_node)           


        # 死活題標記若不存在，則只留第一手棋(若不設qq則以第一手為qq)
        if not qq_exist and len(moves)>1:
            first_move = moves[0]
            moves.clear()
            moves.append(first_move)

         # logging.debug("get question move=", BoardTree.node_list_to_str(moves))
        return moves

    @staticmethod
    def node_list_to_str(nodes):
        # nodes must be a Node class
        str_nodes = ''
        for n in nodes:
            str_nodes += n.tag + ' '

        return str_nodes


