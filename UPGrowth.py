#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
__title__ = ""
__author__ = "Shuang"
__mtime__ = "2016/7/31"

"""
from collections import defaultdict

from Transaction import Transaction
from UPNode import UPNode
from up_util import get_transactions, get_item_weight


def up_growth(transactions, min_utility, item_weight):
	"""
	高效用模式挖掘算法
	:param transactions:事务列表
	:param min_utility: 最低效用阈值
	:param item_weight: 项的外部效用
	:return: 高效用项集及项效用值
	"""
	tu, twu, miut = cal_tu_twu(transactions, item_weight)							# Step 1: 计算事务效用及项的twu
	table = create_table(twu, min_utility)											# Step 2: 创建Header Table
	root, table, reorganized_trans = create_tree(trans_list, table)					# Step 3: 建树
	phuiset = []
	mine_tree(min_utility, table, set([]), phuiset, miut)							# Step 4: 从树中挖掘候选高效用模式集
	huis, hui_utils = find_true_huis(reorganized_trans, min_utility, phuiset)		# Step 5: 选择真正的高效用模式

	root.show()		# 打印全局树
	for hui_id in huis:		# 打印所有高效用模式及相应的效用值
		print huis[hui_id],
		print hui_utils[hui_id]

	return huis, hui_utils


def cal_tu_twu(transactions, item_weight):
	"""
	Step 1:
	Calculate the transaction utility and the transaction weighted utility
	:param transactions: a list of Transaction
	:param item_weight: outer utility of items
	:return: tu & twu & miut(项最小效用值表)
	"""
	twu = defaultdict(lambda: 0)
	tu = defaultdict(lambda: 0)
	miut = defaultdict(lambda: 60000)
	for trans in transactions:
		items = trans.items
		trans_util = 0
		for item in items:
			item_util = int(items[item]) * float(item_weight[item])
			items[item] = item_util  # 保存项在事务中的效用值
			trans_util += float(item_util)
			miut[item] = item_util if item_util < miut[item] else miut[item]
		for item in items:
			twu[item] += float(trans_util)
		tu[trans.id] = trans_util
		trans.set_tu(trans_util)
	return tu, twu, miut


def create_table(twu_dict, min_util):
	"""
	Step 2:创建header table，按照twu值降序排序
	:param twu_dict:
	:param min_util:
	:return:
	"""
	table = {}  # table 是一个二元组列表字典，按照项的twu值降序排序
	for item in twu_dict:
		if float(twu_dict[item]) >= min_util:
			table[item] = [twu_dict[item], None]
	return table


def create_tree(transactions, table):
	"""
	Step 3:建树
	将事务插入UP-Tree中
	并重构数据库，去掉unpromising items及其效用值
	:param transactions:
	:param table:
	:return:树的根节点， header table， 重构后的事务数据库
	"""
	root = UPNode(None, None, None)

	for trans in transactions:
		local_data = {}
		new_tu = trans.tu
		items = trans.items
		low_utils = []
		for item in items:
			if item in table.keys():
				local_data[item] = table[item][0]
			else:
				low_utils.append(item)
				new_tu -= items[item]		# 去掉unpromising items的效用值
		for item in low_utils:		# 去掉unpromising items
			items.pop(item)
		trans.set_tu(new_tu)		# 重置事务效用tu

		if len(local_data) > 0:
			# 将事务中的项按照twu值降序排列
			ordered_items = [h[0] for h in sorted(local_data.items(), key=lambda p: p[1], reverse=True)]
			insert_trans(ordered_items, root, table, trans)
	return root, table, transactions


def insert_trans(items, root, table, trans):
	"""
	将事务插入到以root为根节点的树中
	:param items: 待插入的项
	:param root: 树根节点
	:param table: header table
	:param trans: 当前事务
	:return:
	"""
	first_item = items[0]
	utility = trans.tu
	for item in items[1:]:		# 去掉unpromising 项的效用值/最小效用值
		utility -= trans.items[item]

	if first_item in root.children:
		root.children[first_item].increment(trans.sup)
		root.children[first_item].add_utility(utility)
	else:
		root.children[first_item] = UPNode(first_item, trans.sup, utility, root)
		if table[first_item][1] is None:
			table[first_item][1] = root.children[first_item]
		else:
			node = table[first_item][1]
			while node.neighbor is not None:
				node = node.neighbor
			node.set_neighbor(root.children[first_item])

	if len(items) > 1:
		insert_trans(items[1:], root.children[first_item], table, trans)


def mine_tree(min_util, table, hui, hui_set, miut):
	"""
	Step 4: 从树中挖掘潜在高效用模式
	:param min_util: 最小效用阈值
	:param table: header table
	:param hui: 当前候选高效用模式
	:param hui_set: 当前候选高效用模式集
	:param miut: 最小项效用值表
	:return:
	"""
	table_items = [v[0] for v in sorted(table.items(), key=lambda p: p[1][0])]

	for item in table_items:
		cur_hui = hui.copy()		# 注意，必须使用copy函数进行浅拷贝
		cur_hui.add(item)
		hui_set.append(cur_hui)
		cpb, child_table = find_cpb(table[item][1], min_util, miut)
		child_tree, child_table, reorganized_cpb = create_tree(cpb, child_table)

		if child_table is not None:
			mine_tree(min_util, child_table, cur_hui, hui_set, miut)


def find_cpb(node, min_util, miut):
	"""
	寻找当前节点的条件模式基，存为Transaction列表
	并创建子header table
	:param node:
	:return:
	"""
	path_list = []
	id = 0		# 路径id
	pwu = defaultdict(lambda: 0)
	while node is not None:
		id += 1
		node_util = node.utility
		node_sup = node.count
		parent = node.parent
		items = {}
		while parent.item is not None and parent.count is not None:
			items[parent.item] = miut[parent.item]		# 保存项的miut值，便于建树时减去unpromising items的效用值
			pwu[parent.item] += node_util
			parent = parent.parent
		path = Transaction(id, items, node_sup, node_util)
		path_list.append(path)
		node = node.neighbor
	child_table = create_table(pwu, min_util)
	return path_list, child_table


def find_true_huis(transactions, min_util, phuiset):
	"""
	Step 5:
	从候选高效用模式集中选择真正的高效用模式
	:param transactions:重构后的事务数据库
	:param min_util:最低效用阈值
	:param phuiset:候选高效用模式集
	:return:真正的高效用模式集及模式效用值
	"""
	huiset = {}
	set_utils = {}
	i = 1
	for phui in phuiset:
		set_util = 0
		for trans in transactions:
			items = trans.items
			flag = True		# 标志当前事务是否包含当前高效用项集，只要有一个元素不在trans中，flag即为假
			util = 0
			for item in phui:
				if item in items:
					util += items[item]
				else:
					flag = False
					break
			if flag is True:
				set_util += util
		if set_util >= min_util:
			huiset[i] = phui
			set_utils[i] = set_util
			i += 1
	return huiset, set_utils


if __name__ == '__main__':
	trans_list, word_tran_dict = get_transactions(r'F:\Lab\mPython\data\transactions_up.txt')
	word_weight_dict, word_id_dict = get_item_weight(r'F:\Lab\mPython\data\unit_profit.txt')
	min_utility = 30

	up_growth(trans_list, min_utility, word_weight_dict)

