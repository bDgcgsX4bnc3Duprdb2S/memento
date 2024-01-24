# memento

Python lib to provide caching to functions

	>>> import time
	>>> from chrono import Chrono
	>>> from memento import cache
	>>>
	>>> @cache(max_size=255, max_hits=None, max_age=None)
	... def fibonacci(n: int):
	... time.sleep(0.1)  # For the purpose of the demo
	... 	if n < 2:
	... 		return n
	... 	return fibonacci(n - 1) + fibonacci(n - 2)
	>>> 
	>>> fibonacci(1)
	1
	>>> fibonacci.cache_info
	Cache(
	|	func=fibonacci(),
	|	max_size=255,
	|	max_hits=None,
	|	max_age=None,
	|	entries=OrderedDict([
	|	|	(	7060431079079814790, 
	|	|	|	CacheEntry(
	|	|	|	|	func_call=fibonacci(1),
	|	|	|	|	value=1,
	|	|	|	|	insert_time=2024-01-24 17:04:21.470752,
	|	|	|	|	access_time=2024-01-24 17:04:21.470774,
	|	|	|	|	hits=1,
	|	|	|	|	call_duration=0:00:00.000007),
	|	|	),
	|	])
	)
	>>>
	>>> call_chrono = Chrono("call") ; fibonacci(200) ; call_chrono.stop()
	>>> call_chrono.get_duration()
	datetime.timedelta(seconds=20, microseconds=257113)
	>>> 
	>>> cache_chrono = Chrono("cache") ; fibonacci(200) ; cache_chrono.stop()
	>>> cache_chrono.get_duration()
	datetime.timedelta(microseconds=182)
