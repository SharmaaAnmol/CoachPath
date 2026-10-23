"""
Python Programming Question Bank.
Contains 30 verified questions (10 basic, 10 intermediate, 10 advanced).
"""

PYTHON_QUESTIONS = [
    # ─── BASIC (10 Questions) ───────────────────────────────────────────
    {
        "difficulty": "basic",
        "topic": "Variables & Data Types",
        "prompt_text": "Which of the following data types in Python is mutable?",
        "code_snippet": None,
        "options": [
            "tuple",
            "frozenset",
            "list",
            "str"
        ],
        "correct_option_index": 2,
        "explanation": "Lists in Python are mutable sequences whose elements can be modified in-place via indexing, appending, or slicing. In contrast, tuples, frozensets, and strings are immutable."
    },
    {
        "difficulty": "basic",
        "topic": "Operators & Expressions",
        "prompt_text": "What is the output of the following integer arithmetic expression in Python 3?",
        "code_snippet": "result = 17 // 4 + 17 % 4",
        "options": [
            "5",
            "4.25",
            "7",
            "1"
        ],
        "correct_option_index": 0,
        "explanation": "17 // 4 performs floor division, yielding 4. 17 % 4 computes the remainder (modulo), yielding 1. The sum 4 + 1 is 5."
    },
    {
        "difficulty": "basic",
        "topic": "Conditional Statements & Truthiness",
        "prompt_text": "In Python, which of the following values evaluates to True in a boolean context (truthy)?",
        "code_snippet": None,
        "options": [
            "[]",
            "0.0",
            "\"False\"",
            "None"
        ],
        "correct_option_index": 2,
        "explanation": "In Python, non-empty strings (including \"False\" or \" \") evaluate to True. Empty collections ([]), zero values (0, 0.0), and None are falsy."
    },
    {
        "difficulty": "basic",
        "topic": "Loops & Iteration",
        "prompt_text": "What does the 'else' clause in a Python 'for' loop signify?",
        "code_snippet": "for item in items:\n    if item == target:\n        break\nelse:\n    print(\"Not found\")",
        "options": [
            "It runs on every iteration if the loop body executes successfully.",
            "It executes only when the loop terminates naturally without hitting a 'break' statement.",
            "It executes only if an exception is caught during iteration.",
            "It executes only if the iterable 'items' was initially empty."
        ],
        "correct_option_index": 1,
        "explanation": "The 'else' block attached to a for or while loop executes only if the loop completes all iterations without encountering an explicit 'break' statement."
    },
    {
        "difficulty": "basic",
        "topic": "Functions & Default Arguments",
        "prompt_text": "What will be printed when the following code is executed?",
        "code_snippet": "def append_item(val, items=[]):\n    items.append(val)\n    return items\n\nappend_item(1)\nprint(append_item(2))",
        "options": [
            "[2]",
            "[1, 2]",
            "[[1], 2]",
            "TypeError: Default argument cannot be mutable"
        ],
        "correct_option_index": 1,
        "explanation": "Default parameter values are evaluated once when the function definition is executed, not at each call. Because a mutable list [] is used, successive calls mutate and share the exact same list instance."
    },
    {
        "difficulty": "basic",
        "topic": "Strings & Slicing",
        "prompt_text": "What is the result of applying the slice expression s[::-1] to the string s = 'CoachPath'?",
        "code_snippet": "s = \"CoachPath\"\nprint(s[::-1])",
        "options": [
            "CoachPath",
            "htaPhcaoC",
            "hcaoCPath",
            "IndexError: step cannot be negative"
        ],
        "correct_option_index": 1,
        "explanation": "A step of -1 in Python slicing traverses the sequence from right to left, reversing the string to 'htaPhcaoC'."
    },
    {
        "difficulty": "basic",
        "topic": "Lists & Collections",
        "prompt_text": "How do you remove and return the last element from a Python list 'data' in O(1) time?",
        "code_snippet": None,
        "options": [
            "data.pop()",
            "data.remove(-1)",
            "del data[0]",
            "data.drop_last()"
        ],
        "correct_option_index": 0,
        "explanation": "list.pop() removes and returns the last element in amortized O(1) time. data.remove(x) searches for value x in O(n) time, and del data[0] requires shifting elements in O(n) time."
    },
    {
        "difficulty": "basic",
        "topic": "List Comprehensions",
        "prompt_text": "Which comprehension generates a list of squares for all even numbers between 0 and 9 (inclusive)?",
        "code_snippet": None,
        "options": [
            "[x**2 for x in range(10) if x % 2 == 0]",
            "[x**2 if x % 2 == 0 for x in range(10)]",
            "{x**2: x in range(10) if x % 2 == 0}",
            "[for x in range(10) if x % 2 == 0: x**2]"
        ],
        "correct_option_index": 0,
        "explanation": "The standard list comprehension syntax with a filter is `[expression for item in iterable if condition]`. Option A properly squares only values where x % 2 == 0."
    },
    {
        "difficulty": "basic",
        "topic": "Exception Handling",
        "prompt_text": "In a Python try-except-finally block, when is the 'finally' clause executed?",
        "code_snippet": None,
        "options": [
            "Only when no exception is raised in the try block.",
            "Only when an exception is successfully handled by an except block.",
            "Always, regardless of whether an exception occurred or was handled.",
            "Only if an unhandled exception propagates to the caller."
        ],
        "correct_option_index": 2,
        "explanation": "The 'finally' clause is always guaranteed to execute prior to leaving the try statement, whether an exception occurred, was handled, or a return statement was reached."
    },
    {
        "difficulty": "basic",
        "topic": "File I/O & Context Managers",
        "prompt_text": "What is the primary advantage of using the 'with' statement when opening files in Python?",
        "code_snippet": "with open(\"data.txt\", \"r\") as f:\n    content = f.read()",
        "options": [
            "It accelerates read speeds by bypassing the OS disk buffer.",
            "It automatically guarantees file handle closure even if an exception is raised.",
            "It automatically parses file contents into structured JSON.",
            "It locks the file exclusively across all operating system processes."
        ],
        "correct_option_index": 1,
        "explanation": "The 'with' statement invokes the file object's __enter__ and __exit__ methods, ensuring the file descriptor is cleanly closed upon block exit even if unhandled exceptions occur."
    },

    # ─── INTERMEDIATE (10 Questions) ────────────────────────────────────
    {
        "difficulty": "intermediate",
        "topic": "OOP & Dunder Methods",
        "prompt_text": "What is the key semantic difference between __str__ and __repr__ in Python?",
        "code_snippet": None,
        "options": [
            "__str__ is for serialization to disk, while __repr__ is for printing to stdout.",
            "__str__ provides an informal, human-readable display string, while __repr__ should provide an unambiguous, ideally evaluatable developer representation.",
            "__repr__ can only return ASCII bytes, whereas __str__ supports Unicode characters.",
            "__str__ is invoked by print(), whereas __repr__ is only invoked inside unit test frameworks."
        ],
        "correct_option_index": 1,
        "explanation": "__str__ aims to be readable for end-users, while __repr__ aims to be unambiguous for developers, often matching code that could recreate the object (e.g., eval(repr(obj)) == obj)."
    },
    {
        "difficulty": "intermediate",
        "topic": "Inheritance & MRO",
        "prompt_text": "Which algorithm does Python use to compute the Method Resolution Order (MRO) in multiple inheritance?",
        "code_snippet": "class A:\n    pass\nclass B(A):\n    pass\nclass C(A):\n    pass\nclass D(B, C):\n    pass",
        "options": [
            "Depth-First Search (DFS) with cyclic elimination",
            "C3 Superconcurrency Linearization",
            "C3 Linearization Algorithm",
            "Dijkstra Shortest Path Tree"
        ],
        "correct_option_index": 2,
        "explanation": "Python 2.3+ and Python 3 use the C3 Linearization algorithm to determine a deterministic, monotonic Method Resolution Order (MRO) supporting multiple inheritance."
    },
    {
        "difficulty": "intermediate",
        "topic": "Generators & Iterators",
        "prompt_text": "What does a function containing the 'yield' keyword return when initially called?",
        "code_snippet": "def number_stream():\n    for i in range(100):\n        yield i\n\nstream = number_stream()",
        "options": [
            "The first yielded value (0)",
            "A generator iterator object without executing the function body yet",
            "A complete tuple of all 100 integers",
            "None"
        ],
        "correct_option_index": 1,
        "explanation": "Calling a generator function returns a generator object. Code execution inside the function body only begins when next() or a loop iterations consume from the generator."
    },
    {
        "difficulty": "intermediate",
        "topic": "Decorators",
        "prompt_text": "Why is @functools.wraps commonly applied to the wrapper function inside a custom decorator?",
        "code_snippet": "import functools\n\ndef my_decorator(func):\n    @functools.wraps(func)\n    def wrapper(*args, **kwargs):\n        return func(*args, **kwargs)\n    return wrapper",
        "options": [
            "To prevent infinite recursion during execution.",
            "To preserve the original function's metadata, such as __name__ and __doc__.",
            "To make the decorated function thread-safe automatically.",
            "To force synchronous execution in async coroutines."
        ],
        "correct_option_index": 1,
        "explanation": "@functools.wraps copies introspective attributes like __name__, __doc__, __annotations__, and __module__ from the original function onto the wrapper, preventing metadata erasure."
    },
    {
        "difficulty": "intermediate",
        "topic": "Unpacking & Variadic Args",
        "prompt_text": "What is the output of the following dictionary unpacking operation?",
        "code_snippet": "d1 = {'a': 1, 'b': 2}\nd2 = {'b': 99, 'c': 3}\nmerged = {**d1, **d2}\nprint(merged['b'])",
        "options": [
            "2",
            "99",
            "[2, 99]",
            "KeyError: duplicate key 'b'"
        ],
        "correct_option_index": 1,
        "explanation": "When merging dictionaries using {**d1, **d2} (or the union operator d1 | d2 in Python 3.9+), values from later dictionaries overwrite keys present in earlier dictionaries."
    },
    {
        "difficulty": "intermediate",
        "topic": "Shallow vs Deep Copy",
        "prompt_text": "What happens when you modify a nested list inside a shallow copy created by copy.copy()?",
        "code_snippet": "import copy\noriginal = [[1, 2, 3], [4, 5, 6]]\nclone = copy.copy(original)\nclone[0].append(99)",
        "options": [
            "Only clone is modified; original remains unchanged.",
            "Both original[0] and clone[0] contain 99 because the inner list references are shared.",
            "A ShallowCopyError exception is raised.",
            "Python automatically converts the inner list into an immutable tuple."
        ],
        "correct_option_index": 1,
        "explanation": "A shallow copy constructs a new outer container but inserts references to the identical objects found in the original. Mutating a nested mutable object reflects across both copies."
    },
    {
        "difficulty": "intermediate",
        "topic": "Custom Context Managers",
        "prompt_text": "In a class implementing the context manager protocol, what arguments does __exit__ receive?",
        "code_snippet": "class ManagedResource:\n    def __enter__(self):\n        return self\n    def __exit__(self, exc_type, exc_val, exc_tb):\n        ...",
        "options": [
            "Only self",
            "self and the returned resource from __enter__",
            "exc_type, exc_val, exc_tb (exception class, exception instance, traceback)",
            "A single boolean indicating whether an error occurred"
        ],
        "correct_option_index": 2,
        "explanation": "The __exit__ method receives the exception type, exception instance, and traceback (all None if the block completed cleanly). Returning True from __exit__ suppresses the exception."
    },
    {
        "difficulty": "intermediate",
        "topic": "Functional Programming & Lambdas",
        "prompt_text": "What will list(map(lambda x: x * 2, filter(lambda x: x % 2 != 0, [1, 2, 3, 4, 5]))) produce?",
        "code_snippet": None,
        "options": [
            "[2, 6, 10]",
            "[4, 8]",
            "[1, 3, 5]",
            "[2, 4, 6, 8, 10]"
        ],
        "correct_option_index": 0,
        "explanation": "filter keeps odd numbers [1, 3, 5]. map multiplies each by 2, resulting in [2, 6, 10]."
    },
    {
        "difficulty": "intermediate",
        "topic": "Type Hinting & Generics",
        "prompt_text": "In modern Python (3.10+), what is the idiomatic syntax for expressing a type that can be either an int or None?",
        "code_snippet": None,
        "options": [
            "int | None",
            "Union[int, Null]",
            "Optional<int>",
            "Nullable(int)"
        ],
        "correct_option_index": 0,
        "explanation": "PEP 604 introduced the pipe operator for union types in Python 3.10, making `int | None` the concise, native standard replacing `typing.Optional[int]`."
    },
    {
        "difficulty": "intermediate",
        "topic": "Sets & Hashability",
        "prompt_text": "Why can a tuple containing a list NOT be added as an element of a Python set?",
        "code_snippet": "s = set()\nt = (1, 2, [3, 4])\ns.add(t)",
        "options": [
            "Tuples cannot be stored in sets under any circumstances.",
            "Sets only permit primitive scalar numbers and strings.",
            "An object is only hashable if all of its components are recursively immutable; the contained list is unhashable.",
            "Python limits set element nesting depth to 1."
        ],
        "correct_option_index": 2,
        "explanation": "For an object to be hashable, its __hash__ method must return a consistent value across its lifetime. Because lists are mutable, their hash cannot be calculated, raising TypeError: unhashable type: 'list'."
    },

    # ─── ADVANCED (10 Questions) ─────────────────────────────────────────
    {
        "difficulty": "advanced",
        "topic": "Memory Management & Garbage Collection",
        "prompt_text": "How does CPython's garbage collection system handle cyclic references between objects?",
        "code_snippet": "class Node:\n    def __init__(self):\n        self.neighbor = None\n\na = Node()\nb = Node()\na.neighbor = b\nb.neighbor = a\ndel a, b",
        "options": [
            "It cannot detect cycles; cyclic memory leaks indefinitely until process exit.",
            "Reference counting handles them immediately when the reference count drops to 2.",
            "A generational cyclic garbage collector periodically tracks container objects and identifies unreachable reference cycles.",
            "CPython converts circular references into weak references automatically."
        ],
        "correct_option_index": 2,
        "explanation": "While CPython uses reference counting as its primary memory mechanism, it incorporates a generational cyclic garbage collector (gc module, generations 0, 1, 2) that inspects container objects to collect unreachable reference cycles."
    },
    {
        "difficulty": "advanced",
        "topic": "Global Interpreter Lock (GIL)",
        "prompt_text": "Why does standard multithreading in CPython typically fail to achieve speedups for CPU-bound computations?",
        "code_snippet": None,
        "options": [
            "Python threads are green threads simulated entirely in user space without OS scheduling.",
            "The Global Interpreter Lock (GIL) allows only one native thread to execute Python bytecode at any given moment.",
            "CPython disables multi-core CPU affinity by default in the OS kernel.",
            "The GIL serializes network socket I/O rather than CPU instructions."
        ],
        "correct_option_index": 1,
        "explanation": "The GIL is a mutual exclusion lock protecting CPython internal memory structures. Because only one thread can hold the GIL and execute bytecode concurrently, CPU-bound workloads run sequentially on a single core."
    },
    {
        "difficulty": "advanced",
        "topic": "Asyncio & Coroutines",
        "prompt_text": "What happens if a synchronous, CPU-blocking function (e.g., time.sleep(10)) is called directly inside an async coroutine?",
        "code_snippet": "async def fetch_data():\n    time.sleep(10)  # Blocking call\n    return {\"status\": \"ok\"}",
        "options": [
            "The asyncio event loop automatically spawns a background thread to run it.",
            "The entire event loop thread is blocked for 10 seconds, stalling all other scheduled tasks.",
            "Asyncio raises a CoroutineBlockedWarning and skips to the next task.",
            "The operating system interrupts the sleep call whenever an async I/O packet arrives."
        ],
        "correct_option_index": 1,
        "explanation": "Asyncio is single-threaded cooperative multitasking. Calling a blocking function halts the operating thread hosting the event loop, preventing all concurrent tasks from progressing until the call returns."
    },
    {
        "difficulty": "advanced",
        "topic": "Metaclasses & Class Construction",
        "prompt_text": "In Python, which dunder method of a metaclass is responsible for allocating and creating the new class object itself?",
        "code_snippet": "class Meta(type):\n    def __new__(mcs, name, bases, namespace):\n        return super().__new__(mcs, name, bases, namespace)",
        "options": [
            "__init__",
            "__new__",
            "__call__",
            "__prepare__"
        ],
        "correct_option_index": 1,
        "explanation": "In both classes and metaclasses, __new__ is the static constructor that creates and returns the instance (for a metaclass, the instance is a new class object). __init__ initializes it after creation."
    },
    {
        "difficulty": "advanced",
        "topic": "Descriptor Protocol",
        "prompt_text": "What distinguishes a 'data descriptor' from a 'non-data descriptor' in Python's attribute lookup order?",
        "code_snippet": None,
        "options": [
            "A data descriptor defines __set__ or __delete__, overriding instance __dict__ lookups.",
            "A data descriptor can only store primitive scalar types like float and int.",
            "A non-data descriptor executes in C extension space rather than Python bytecode.",
            "Non-data descriptors take precedence over instance __dict__ keys during attribute access."
        ],
        "correct_option_index": 0,
        "explanation": "If an object defines __set__ or __delete__, it is a data descriptor. Data descriptors take precedence over an instance's __dict__. If it only defines __get__ (non-data descriptor), instance dictionary entries take precedence."
    },
    {
        "difficulty": "advanced",
        "topic": "Memory Optimization & __slots__",
        "prompt_text": "What is the primary architectural consequence of defining __slots__ in a Python class definition?",
        "code_snippet": "class Point:\n    __slots__ = ('x', 'y')\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y",
        "options": [
            "It encrypts instance variables in memory for security.",
            "It prevents the creation of an instance __dict__, saving memory and restricting attributes to the declared names.",
            "It makes instances immutable like namedtuples.",
            "It enables automatic multi-threaded parallel execution across member methods."
        ],
        "correct_option_index": 1,
        "explanation": "__slots__ instructs Python to reserve space for declared attributes in fixed array slots rather than allocating a dynamic dictionary (__dict__) for each instance, substantially reducing memory consumption."
    },
    {
        "difficulty": "advanced",
        "topic": "Coroutines & Delegating Generators",
        "prompt_text": "What capability does 'yield from' introduce beyond simple generator delegation?",
        "code_snippet": "def subgen():\n    val = yield \"ready\"\n    return f\"Processed: {val}\"\n\ndef delegator():\n    result = yield from subgen()\n    yield result",
        "options": [
            "It runs the subgenerator inside an OS background worker thread.",
            "It transparently passes values and exceptions sent via send() and throw() directly between caller and subgenerator, and captures the subgenerator's return value.",
            "It prevents memory allocations by converting generator frames into C arrays.",
            "It enforces type validation on yielded values."
        ],
        "correct_option_index": 1,
        "explanation": "'yield from' establishes a bidirectional channel establishing direct communication for .send() and .throw() between caller and subgenerator, and captures the value returned via `return value` in the subgenerator."
    },
    {
        "difficulty": "advanced",
        "topic": "Weak References",
        "prompt_text": "What does a weak reference (weakref module) allow a programmer to do?",
        "code_snippet": "import weakref\n\nclass Cache:\n    def __init__(self):\n        self._cache = weakref.WeakValueDictionary()",
        "options": [
            "Reference an object without increasing its reference count, allowing it to be garbage collected when other references disappear.",
            "Create read-only copies of objects with degraded precision.",
            "Bypass the GIL when querying memory caches.",
            "Serialize objects that do not support the pickle protocol."
        ],
        "correct_option_index": 0,
        "explanation": "Weak references do not hold an owning reference count on the target object. When only weak references remain, the object can be reclaimed immediately, making them ideal for circular caches and observer registries."
    },
    {
        "difficulty": "advanced",
        "topic": "Abstract Base Classes (ABCs)",
        "prompt_text": "How can a Python class satisfy an Abstract Base Class (ABC) without explicitly inheriting from it?",
        "code_snippet": "from collections.abc import Sized\n\nclass CustomBook:\n    def __len__(self):\n        return 100\n\nprint(isinstance(CustomBook(), Sized))",
        "options": [
            "It cannot; Python strictly requires explicit class inheritance to satisfy isinstance.",
            "Through structural subtyping via ABC's __subclasshook__ mechanism, which registers classes providing expected dunder methods (virtual subclasses).",
            "By decorating the class with @dataclass(abc=True).",
            "By setting __metaclass__ = Sized inside the class body."
        ],
        "correct_option_index": 1,
        "explanation": "ABCs like Sized implement a classmethod called __subclasshook__ that inspects the class structure. Since CustomBook defines __len__, isinstance(CustomBook(), Sized) evaluates to True as a virtual subclass."
    },
    {
        "difficulty": "advanced",
        "topic": "Concurrency: Multiprocessing vs Threading",
        "prompt_text": "When using Python's multiprocessing module to share state across processes, why can standard global variables NOT be modified in-place?",
        "code_snippet": "counter = 0\ndef worker():\n    global counter\n    counter += 1",
        "options": [
            "The GIL locks global variables across all processes.",
            "Each process has its own isolated memory address space; modifications in a child process do not affect the parent process memory.",
            "Operating systems prevent Python from modifying variables named 'counter'.",
            "Global variables in Python are automatically converted into thread-local storage."
        ],
        "correct_option_index": 1,
        "explanation": "Unlike threads which share a virtual memory space, processes are sandboxed by the OS kernel in distinct address spaces. Shared state across processes requires explicit IPC mechanisms (e.g., Value, Array, Manager, or pipes)."
    }
]
