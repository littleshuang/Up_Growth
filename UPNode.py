#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
__title__ = ""
__author__ = "Shuang"
__mtime__ = "2016/7/25"

"""


class UPNode(object):
	"""A node in a UP tree."""

	def __init__(self, item, count=1, utility=0, parent=None):
		self._item = item
		self._count = count
		self._utility = utility
		self._parent = parent
		self._children = {}		# key = child.item value = child node
		self._neighbor = None

	def add(self, child):
		"""Adds the given UPNode `child` as a child of this node."""

		if not isinstance(child, UPNode):
			raise TypeError("Can only add other UPNodes as children")

		if child.item not in self._children:
			self._children[child.item] = child
			child.parent = self

	def search(self, item_name):
		"""
		Checks to see if this node contains a child node for the given item.
		If so, that node is returned; otherwise, `None` is returned.
		"""

		try:
			return self._children[item_name]
		except KeyError:
			return None

	def remove(self, child):
		""" Delete the given child node. """
		try:
			if self._children[child.item] is child:
				del self._children[child.item]
				child.parent = None
				for sub_child in child.children.values():
					try:
						# Merger case: we already have a child for that item, so
						# add the sub-child's count to our child's count.
						self._children[sub_child.item].increment(sub_child.count)
						self._children[sub_child.item].add_utility(sub_child.utility)
						sub_child.parent = None  # it's an orphan now
					except KeyError:
						# Turns out we don't actually have a child, so just add
						# the sub-child as our own child.
						self.add(sub_child)
				child._children = {}
			else:
				raise ValueError("that node is not a child of this node")
		except KeyError:
			raise ValueError("that node is not a child of this node")

	def __contains__(self, item):
		return item in self._children

	def set_parent(self, value):
		if value is not None and not isinstance(value, UPNode):
			raise TypeError("A node must have an UPNode as a parent.")
		self._parent = value

	def set_neighbor(self, value):
		if value is not None and not isinstance(value, UPNode):
			raise TypeError("A node must have an UPNode as a neighbor.")
		self._neighbor = value

	def increment(self, inc=1):
		"""Increments the count associated with this node's item."""
		if self._count is None:
			raise ValueError("Root nodes have no associated count.")
		self._count += inc

	def add_utility(self, utility=0):
		"""Increments the utility associated with this node's item."""
		if self._utility is None:
			raise ValueError("Root nodes have no associated utility.")
		self._utility += utility

	@property
	def item(self):
		"""The item contained in this node."""
		return self._item

	@property
	def count(self):
		"""The count associated with this node's item."""
		return self._count

	@property
	def utility(self):
		"""The utility associated with this node's item."""
		return self._utility

	@property
	def parent(self):
		return self._parent

	@property
	def neighbor(self):
		return self._neighbor

	@property
	def children(self):
		"""The nodes that are children of this node."""
		return self._children

	def inspect(self, depth=0):		# using for print the up tree
		print ('  ' * depth) + repr(self)
		for child in self.children:
			child.inspect(depth + 1)

	def show(self, ind=1):
		print ' ' * ind, self.item, ' ', self.count, ' ', self.utility
		for child in self.children.values():
			child.show(ind + 2)
