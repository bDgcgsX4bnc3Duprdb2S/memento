import logging
import os
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from datetime import timedelta
from functools import wraps
from typing import Any
from chrono.chrono import Chrono

log = logging.getLogger(name=__name__)


@dataclass
class FuncCall:
	func: callable
	args: list[Any] = field(default_factory=list)
	kwargs: dict[Any] = field(default_factory=dict)

	def signature(self) -> str:
		args_signature = str(self.args).strip("(").strip(")").strip(",")
		kwargs_signature = str(self.kwargs).strip('{').strip('}').strip(',')
		args_signature = (args_signature + "," + kwargs_signature).strip(',')
		return f"{self.func.__name__}({args_signature})"

	def key(self):
		return self.signature().__hash__()

	def __str__(self):
		return self.signature()


@dataclass
class CacheEntry:
	func_call: FuncCall
	value: Any
	insert_time: datetime = None
	access_time: datetime = None
	hits: int = 0
	call_duration: timedelta = None

	def __post_init__(self):
		# A time object representing now must be initialized at instanciation, not definition...
		if self.insert_time is None:
			self.insert_time = datetime.now()
		if self.access_time is None:
			self.access_time = datetime.now()


@dataclass
class Cache:
	fun: callable
	max_size: int = None
	max_hits: int = None
	max_timedelta: timedelta = None
	entries: OrderedDict[Any, CacheEntry] = field(default_factory=OrderedDict)

	def __repr__(self):
		result = f"{self.__class__.__name__}(" + os.linesep
		result += f"|	func={self.fun.__name__}()," + os.linesep
		result += f"|	max_size={self.max_size}," + os.linesep
		result += f"|	max_hits={self.max_hits}," + os.linesep
		result += f"|	max_timedelta={self.max_timedelta}," + os.linesep
		result += f"|	entries={self.entries.__class__.__name__}([" + os.linesep
		for key, entry in self.entries.items():
			result += f"|	|	(	{key}, " + os.linesep
			result += f"|	|	|	{entry.__class__.__name__}(" + os.linesep
			result += f"|	|	|	|	func_call={entry.func_call}," + os.linesep
			result += f"|	|	|	|	value={entry.value}," + os.linesep
			result += f"|	|	|	|	insert_time={entry.insert_time}," + os.linesep
			result += f"|	|	|	|	access_time={entry.access_time}," + os.linesep
			result += f"|	|	|	|	hits={entry.hits}," + os.linesep
			result += f"|	|	|	|	call_duration={entry.call_duration})," + os.linesep
			result += f"|	|	)," + os.linesep
		result += f"|	])" + os.linesep
		result += f")"
		return result

	def items(self):
		return list(self.entries.items())

	def __len__(self):
		return len(self.entries)

	def clear(self):
		# Fully clear the cache
		self.entries.clear()
		log.info(f"{self.fun.__name__}(): Cache cleared")

	def compact(self):
		# Compact cache if too big
		if self.max_size is not None:
			size = len(self.entries)
			for i in range(size, self.max_size, -1):
				# Remove last accessed cache_entry
				# Cache_info is ordered and cache_entry are moved to the end of it.
				# Removing the first cache_entry of cache_info removes the oldest accessed cache_entry
				# This is easier and faster to do than doing complex computing with hits to remove less
				#  hitted cache_entry whille allowing new cache_entry to grow up...
				self.entries.popitem(last=False)
				log.info(f"{self.fun.__name__}(): Cache size reduced from {size} to {self.max_size}")

	def update(self, cache_entry: CacheEntry):
		log.info(f"{cache_entry.func_call.signature()}: Updating cache...")
		update_chrono = Chrono(name="update").start()

		# Update and check hits
		cache_entry.hits += 1
		if self.max_hits is not None and cache_entry.hits > self.max_hits:
			log.info(f"{cache_entry.func_call.signature()}: Cache_entry flushed because of too many hits")
			# If cache is not empty
			if len(self.entries) != 0:
				self.entries.pop(cache_entry.func_call.key())
			# Refresh cache
			value = self.call(cache_entry.func_call)
			cache_entry.value = value

		# Update and check access_time
		cache_entry.access_time = datetime.now()
		if self.max_timedelta is not None and cache_entry.access_time - cache_entry.insert_time > self.max_timedelta:
			log.info(f"{cache_entry.func_call.signature()}: Cache_entry flushed because of its age")
			# If cache is not empty
			if len(self.entries) != 0:
				self.entries.pop(cache_entry.func_call.key())
			# Refresh cache
			value = self.call(cache_entry.func_call)
			cache_entry.value = value

		# Update cache so cache_entry is the lastest cache_entry in cache
		try:
			self.entries.move_to_end(cache_entry.func_call.key())
		except KeyError:
			self.entries[cache_entry.func_call.key()] = cache_entry

		self.compact()
		update_chrono.stop()
		log.debug(f"{cache_entry.func_call.signature()}: Cache update took {update_chrono.get_duration()}")

	def search(self, func_call: FuncCall):
		# Search cache for a result to func call
		search_chrono = Chrono(name="search").start()
		try:
			cache_entry = self.entries[func_call.key()]
			search_chrono.stop()
			log.debug(f"{func_call.signature()}: Cache search took {search_chrono.get_duration()}")
			return cache_entry
		except KeyError as e:
			log.info(f"{func_call.signature()}: Did NOT found cache_entry")
			raise e

	def call(self, func_call: FuncCall) -> Any:
		log.debug(f"{func_call.signature()}: Calling {func_call.signature()}...")
		call_chrono = Chrono(name="call").start()
		value = self.fun(*func_call.args, **func_call.kwargs)
		call_chrono.stop()
		log.debug(f"{func_call.signature()}: Call took {call_chrono.get_duration()}")

		# Update cache
		self.update(CacheEntry(value=value, call_duration=call_chrono.get_duration(), func_call=func_call))
		log.info(f"{func_call.signature()}: Cache updated")
		return value


def cache(fun: callable = None, max_size: int = None, max_hits: int = None, max_timedelta: timedelta = None):
	"""
	Decorator to cache function returns.

	cache: Function call can use "cache:bool = True" to bypass cache
		Eg: func("hello world", cache=True) => will not use or update cache
		It's highly suggested to include "cache:bool = True" in function signature to allow hints from IDE

	:param fun: Cached function
	:param max_size: Max size of cache after which it'll be reduced
	:param max_hits: Max hits of a cache entry after which it'll be removed from cache
	:param max_timedelta: Max time delta of a cache entry after which it'll be removed from cache
	:return: func return
	"""

	def cache_decorator(fun: callable):
		cache_info = Cache(fun=fun, max_size=max_size, max_hits=max_hits, max_timedelta=max_timedelta)

		@wraps(fun)
		def wrapper(*args, **kwargs):
			func_call: FuncCall = FuncCall(func=fun, args=args, kwargs=kwargs)

			use_cache = True
			# If cache arg is defined
			if "cache" in kwargs.keys():
				# Remove cache arg from final function call
				use_cache = kwargs.pop("cache")

			# If cache must be bypassed
			if not use_cache:
				log.info(f"{func_call.signature()}: Cache search bypassed. But cache is still updated")
				# Call function and update cache
				return cache_info.call(func_call=func_call)

			# Else, if cache must be searched
			else:
				# Search cache for a result to func call
				try:
					log.info(f"{func_call.signature()}: Searching cache...")
					cache_entry = cache_info.search(func_call=func_call)

					# If found, update cache
					log.info(f"{func_call.signature()}: Cache entry found")
					cache_info.update(cache_entry)
					# Return value
					return cache_entry.value

				# Else, if cache_entry not found
				except KeyError:
					# Call function and update cache
					value = cache_info.call(func_call=func_call)
					return value

		# Add attributes to the func to control cache from outside the decorator
		wrapper.cache_info = cache_info
		wrapper.cache_function = fun

		return wrapper

	# Boilerplate for wrapper
	if fun is None:
		return cache_decorator
	else:
		return cache_decorator(fun)
