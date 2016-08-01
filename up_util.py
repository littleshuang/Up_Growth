#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
__title__ = ""
__author__ = "Shuang"
__mtime__ = "2016/7/25"

"""
from collections import defaultdict

from Transaction import Transaction


def get_transactions(read_filename):
	"""
	从文件中获取事务，返回事务列表及词汇-事务列表字典
	"""
	trans_list = []
	word_tran_dict = {}		# 词-事务字典，key=词汇，value=包含该词汇的事务id列表, id起始值为0

	f = open(read_filename, 'r')
	f_info = f.readlines()
	for i in range(len(f_info)):
		line = f_info[i]
		item_dict = defaultdict(lambda: 0)
		for item in line.split():
			name = item.split(':')[0]
			num = item.split(':')[1]
			item_dict[name] = num
			if item in word_tran_dict:
				word_tran_dict[item].append(i)
			else:
				word_tran_dict[item] = [i]
		trans = Transaction(i, item_dict, 1, 0)
		trans_list.append(trans)
	return trans_list, word_tran_dict


def get_item_weight(read_filename):
	""" 获取词汇的外部效用值，返回词汇外部效用字典及词汇id字典"""
	word_weight_dict = defaultdict(lambda: 0)
	word_id_dict = defaultdict(lambda: 0)

	f = open(read_filename, 'r')
	line = f.readline()
	i = 0
	while line:
		info = line.split(' ')
		word_weight_dict[info[0]] = info[1]
		word_id_dict[info[0]] = i
		line = f.readline()
		i += 1
	return word_weight_dict, word_id_dict
