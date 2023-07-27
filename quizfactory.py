#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import listdir
from os.path import isfile, isdir, join

import logging
import datetime


# 題目基本資料
class GoQuiz(object):

    def __init__(self):
        self._name = ""
        self._right_cnt = 0
        self._wrong_cnt = 0
        self._last_wrong_date = None
        self._comment = ""

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def right_cnt(self):
        return self._right_cnt

    @right_cnt.setter
    def name(self, new_right_cnt):
        self._right_cnt = new_right_cnt

    @property
    def wrong_cnt(self):
        return self._wrong_cnt

    @wrong_cnt.setter
    def name(self, new_wrong_cnt):
        self._wrong_cnt = new_wrong_cnt

    @property
    def last_wrong_date(self):
        return self._last_wrong_date

    @last_wrong_date.setter
    def name(self, new_last_wrong_date):
        self._last_wrong_date = new_last_wrong_date

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, new_comment):
        self._comment = new_comment



# 題庫工廠
# 與 design pattern 的 factory 模式無關
class QuizFactory(object):

    def __init__(self):
        self._path = ""
        self._quizs = []
        self._current = -1

    def load_quiz(self, sgf_path):
        self._path = ""
        self._quizs = []
        self._current = -1
        self._path = sgf_path
        file_list = listdir(self._path)
        logging.debug(file_list)
        for f in file_list:
            if isfile(join(self._path, f)) and len(f)>3 and f[-3:].upper()=='SGF':
                q = GoQuiz()
                q.name = f
                self._quizs.append(q)
        if len(self._quizs)>0:
            self._current = 0

    def __str__(self):
        return "A Quiz Factory"

    def show(self):
        logging.debug("Quiz count=" + str(len(self._quizs)))
        for q in self._quizs:
            logging.debug("Quiz name=" + q.name)

    def next(self):
        if len(self._quizs)==0:
            return

        self._current += 1
        if self._current >= len(self._quizs):
            self._current = 0

    def prev(self):
        if len(self._quizs)==0:
            return

        self._current -= 1
        if self._current == -1:
            self._current = len(self._quizs) - 1

    def current_quiz_name(self):
        if len(self._quizs)==0:
            return

        return self._quizs[self._current].name

    def current_quiz_full_name(self):
        if len(self._quizs)==0:
            return

        return join(self._path, self._quizs[self._current].name)

    def path(self):
        return self._path

    def current_num(self):
        return self._current + 1

    def cnt(self):
        return len(self._quizs)

    def current_quiz_comment(self):
        return self._quizs[self._current].comment

    def set_current_quiz_comment(self, new_comment):
        self._quizs[self._current].comment = new_comment

    def save_status(self):
        if len(self._quizs)==0:
            return

        save_file = join(self._path, "weiqigo.save")
        with open(save_file, 'w', encoding='utf-8') as f:
            f.write(self._quizs[self._current].name)

    def load_status(self):
        logging.debug(" --- quizfactory load_status --- ")
        if len(self._quizs)==0:
            return

        last_file = ""
        save_file = join(self._path, "weiqigo.save")
        try:
            with open(save_file, 'r', encoding='utf-8') as f:
                last_file = f.readline()
                logging.debug("last quiz file found: " + last_file)
        except FileNotFoundError:
            logging.debug("That's fine, Maybe the first time reading the folder.")

        for i in range(0, len(self._quizs)):
            if self._quizs[i].name == last_file:
                self._current = i
                return
