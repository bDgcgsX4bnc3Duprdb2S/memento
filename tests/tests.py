import pytest
import logging
import rich
from rich.logging import RichHandler
import memento
from memento import cache
from chrono import chrono
from chrono.chrono import Chrono
import time
from datetime import timedelta

log = logging.getLogger(name=__name__)

log.setLevel(logging.DEBUG)
console = rich.get_console()
console.width = 120
handler = RichHandler(console=console)
handler.setLevel(logging.DEBUG)
log.addHandler(handler)

chrono.log.setLevel(logging.NOTSET)
memento.log = log

def test_output_value():
	input_value: int = 1
	expected_output_value: int = 1

	@cache
	def my_test(n):
		log.info(f"function was executed")
		return n

	cache_info: memento.Cache = my_test.cache_info
	log.info(f"Cache:")
	log.info(cache_info)

	log.info(f"Calling function")
	output_value = my_test(input_value)

	log.info(f"Cache:")
	log.info(cache_info)

	log.info(f"Calling function to check output_value")
	output_value = my_test(input_value)

	# Check output_value
	assert output_value == expected_output_value


def test_speed():
	input_value: int = 1
	expected_output_value: int = 2

	@cache
	def my_test(n):
		log.info(f"function was executed")
		time.sleep(2)
		return n

	cache_info: memento.Cache = my_test.cache_info
	cache_info.clear()
	log.info(f"Cache:")
	log.info(cache_info)

	log.info(f"Calling function")
	output_value = my_test(input_value)

	log.info(f"Cache:")
	log.info(cache_info)

	call_key = list(cache_info.entries)[0]
	log.info(f"{call_key=}")

	entry: memento.CacheEntry = cache_info.entries[call_key]
	log.info(f"{entry=}")

	log.info(f"Calling function to check speed improvment")
	cache_chrono: Chrono = Chrono(name="cache_chrono")
	cache_chrono.start()
	output_value = my_test(input_value)
	cache_chrono.stop()

	log.info(f"Function call took {cache_chrono.get_duration()} instead of {entry.call_duration}")
	assert cache_chrono.get_duration() < entry.call_duration

def test_bypass():
	input_value: int = 1
	expected_output_value: int = 2

	@cache
	def my_test(n):
		log.info(f"function was executed")
		return n

	cache_info: memento.Cache = my_test.cache_info
	log.info(f"Cache:")
	log.info(cache_info)

	log.info(f"Calling function")
	output_value = my_test(input_value)

	log.info(f"Cache:")
	log.info(cache_info)

	call_key = list(cache_info.entries)[0]
	log.info(f"{call_key=}")

	entry: memento.CacheEntry = cache_info.entries[call_key]
	log.info(f"{entry=}")

	log.info(f"Changing cached value for the purpose of the check")
	entry.value = expected_output_value

	log.info(f"Cache:")
	log.info(cache_info)

	log.info(f"Calling function to check bypass")
	output_value = my_test(input_value)

	# Check output_value
	assert output_value == expected_output_value


def test_max_size():
	@cache(max_size=2)
	def my_test(n):
		log.info(f"function was executed")
		return n

	cache_info: memento.Cache = my_test.cache_info
	log.info(f"Cache:")
	log.info(cache_info)

	log.info(f"Calling function 1")
	output_value = my_test(1)
	log.info(f"Cache:")
	log.info(cache_info)

	log.info(f"Calling function 2")
	output_value = my_test(2)
	log.info(f"Cache:")
	log.info(cache_info)
	cache_size = len(cache_info)
	assert cache_size == 2

	log.info(f"Calling function 3")
	output_value = my_test(3)
	log.info(f"Cache:")
	log.info(cache_info)
	cache_size = len(cache_info)
	assert cache_size == 2

	log.info(f"Calling function 4")
	output_value = my_test(4)
	log.info(f"Cache:")
	log.info(cache_info)
	cache_size = len(cache_info)
	assert cache_size == 2


def test_max_hits():
	input_value:int = 1
	expected_output_value: int = 1
	@cache(max_hits=2)
	def my_test(n):
		log.info(f"function was executed")
		return n

	cache_info: memento.Cache = my_test.cache_info
	log.info(f"Cache:")
	log.info(cache_info)

	log.info(f"Calling function 1")
	output_value = my_test(input_value)
	log.info(f"Cache:")
	log.info(cache_info)

	call_key = list(cache_info.entries)[0]
	log.info(f"{call_key=}")

	entry: memento.CacheEntry = cache_info.entries[call_key]
	log.info(f"{entry=}")

	log.info(f"Changing cached value for the purpose of the check")
	entry.value = 2

	log.info(f"Cache:")
	log.info(cache_info)

	log.info(f"Calling function 2")
	output_value = my_test(input_value)
	log.info(f"Cache:")
	log.info(cache_info)

	log.info(f"Calling function 3")
	output_value = my_test(input_value)
	log.info(f"Cache:")
	log.info(cache_info)
	assert output_value == expected_output_value


def test_max_timedelta():
	input_value: int = 1
	expected_output_value: int = 1

	@cache(max_timedelta=timedelta(seconds=1))
	def my_test(n):
		log.info(f"function was executed")
		return n

	cache_info: memento.Cache = my_test.cache_info
	log.info(f"Cache:")
	log.info(cache_info)

	log.info(f"Calling function 1")
	output_value = my_test(input_value)
	log.info(f"Cache:")
	log.info(cache_info)

	call_key = list(cache_info.entries)[0]
	log.info(f"{call_key=}")

	entry: memento.CacheEntry = cache_info.entries[call_key]
	log.info(f"{entry=}")

	log.info(f"Changing cached value for the purpose of the check")
	entry.value = 2

	log.info(f"Cache:")
	log.info(cache_info)

	log.info(f"Sleeping...")
	time.sleep(1)

	log.info(f"Calling function 2")
	output_value = my_test(input_value)
	log.info(f"Cache:")
	log.info(cache_info)
	assert output_value == expected_output_value

def test_clear():
	input_value: int = 1
	@cache
	def my_test(n):
		log.info(f"function was executed")
		return n

	cache_info: memento.Cache = my_test.cache_info
	log.info(f"Cache:")
	log.info(cache_info)

	log.info(f"Calling function 1")
	output_value = my_test(input_value)
	log.info(f"Cache:")
	log.info(cache_info)

	log.info(f"Clearing memento...")
	cache_info.clear()

	cache_size = len(cache_info)
	assert cache_size == 0


def test_fibonacci():
	input_value: int = 200

	@cache
	def fibonacci(n: int):
		if n < 2:
			return n
		return fibonacci(n - 1) + fibonacci(n - 2)

	call_chrono: Chrono = Chrono("call")
	call_chrono.start()
	fibonacci(input_value)
	call_chrono.stop()

	cache_chrono: Chrono = Chrono("memento")
	cache_chrono.start()
	fibonacci(input_value)
	cache_chrono.stop()

	log.info(f"Second function call took {cache_chrono.get_duration()} instead of {call_chrono.get_duration()}")
	assert cache_chrono.get_duration() < call_chrono.get_duration()

def test_fun_instead_of_decorator():
	input_value: int = 1
	expected_output_value: int = 1

	def my_test(n):
		log.info(f"function was executed")
		return n
	my_test = cache(fun=my_test)

	cache_info: memento.Cache = my_test.cache_info
	log.info(f"Cache:")
	log.info(cache_info)

	log.info(f"Calling function")
	output_value = my_test(input_value)

	log.info(f"Cache:")
	log.info(cache_info)

	log.info(f"Calling function to check output_value")
	output_value = my_test(input_value)

	# Check output_value
	assert output_value == expected_output_value
