#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
__title__ = ""
__author__ = "Shuang"
__mtime__ = "2016/7/24"

"""


class Transaction(object):
	""" A transaction in a transaction database for utility mining."""

	def __init__(self, trans_id, items, sup=1, tu=0):
		self._id = trans_id		# the id of this transaction
		self._items = items		# key = item.name value = item.inner_utility
		self._sup = sup		# the support of this transaction
		self._tu = tu		# transaction utility

	def add_item(self, item_name, inner_util=1):
		if item_name not in self._items:
			self._items[item_name] = inner_util

	def del_item(self, item):
		""" Delete the item from this transaction."""
		if item in self._items:
			self._items.pop(item)

	def set_tu(self, tu):
		self._tu = tu

	def add_tu(self, tu):
		self._tu += tu

	def set_sup(self, sup):
		if not isinstance(sup, int):
			raise TypeError("Transaction support should be an int. ")
		self._sup = sup

	def add_sup(self, sup):
		if not isinstance(sup, int):
			raise TypeError("Transaction support should be an int. ")
		self._sup += sup

	@property
	def id(self):
		""" The transaction id of this transaction. """
		return self._id

	@property
	def items(self):
		""" The items in this transaction."""
		return self._items

	@property
	def sup(self):
		""" The support of this transaction. """
		return self._sup

	@property
	def tu(self):
		""" The transaction utility of this transaction. """
		return self._tu

