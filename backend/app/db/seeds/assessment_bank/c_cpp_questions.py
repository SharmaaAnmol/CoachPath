"""
C & C++ Programming Question Bank.
Contains 30 verified questions (10 basic, 10 intermediate, 10 advanced), tagged C vs C++.
"""

C_CPP_QUESTIONS = [
    # ─── BASIC (10 Questions) ───────────────────────────────────────────
    {
        "difficulty": "basic",
        "topic": "C: Pointers & Addresses",
        "prompt_text": "[C] What is printed by the following pointer code in C?",
        "code_snippet": "#include <stdio.h>\n\nint main() {\n    int x = 10;\n    int *ptr = &x;\n    *ptr = 25;\n    printf(\"%d\", x);\n    return 0;\n}",
        "options": [
            "10",
            "25",
            "Memory address of x",
            "Undefined behavior"
        ],
        "correct_option_index": 1,
        "explanation": "`int *ptr = &x;` stores the memory address of x in ptr. Dereferencing `*ptr = 25;` directly mutates the value stored in x, so `printf(\"%d\", x)` outputs 25."
    },
    {
        "difficulty": "basic",
        "topic": "C: Dynamic Memory Allocation",
        "prompt_text": "[C] What is the difference between malloc() and calloc() in the C standard library?",
        "code_snippet": None,
        "options": [
            "malloc() allocates memory on the stack; calloc() allocates memory on the heap.",
            "malloc() allocates uninitialized memory containing indeterminate (garbage) values; calloc() allocates memory and clears all bits to zero.",
            "malloc() can only allocate up to 1024 bytes.",
            "calloc() automatically frees memory when the enclosing function returns."
        ],
        "correct_option_index": 1,
        "explanation": "malloc(size) allocates requested bytes with indeterminate contents. calloc(num, size) allocates memory for an array and zeroes out all allocated bytes."
    },
    {
        "difficulty": "basic",
        "topic": "C: Pointer Arithmetic & Arrays",
        "prompt_text": "[C] Given an array `int arr[5] = {10, 20, 30, 40, 50};`, what value does `*(arr + 3)` evaluate to?",
        "code_snippet": "int arr[5] = {10, 20, 30, 40, 50};\nprintf(\"%d\", *(arr + 3));",
        "options": [
            "13",
            "30",
            "40",
            "Memory address offset by 3 bytes"
        ],
        "correct_option_index": 2,
        "explanation": "In C, array indexing `arr[i]` is syntactic sugar for `*(arr + i)`. Pointer arithmetic scales by sizeof(int), pointing to element index 3, which is 40."
    },
    {
        "difficulty": "basic",
        "topic": "C: Strings & Null Terminators",
        "prompt_text": "[C] Why does the character array `char s[] = \"Hello\";` require 6 bytes of memory?",
        "code_snippet": "char s[] = \"Hello\";\nprintf(\"%zu\", sizeof(s));",
        "options": [
            "Because C strings store an internal length integer in the first byte.",
            "Because C string literals include an implicit null terminator character ('\\0') at the end.",
            "Because characters in modern C use 16-bit Unicode.",
            "Because 6 is the minimum allocation alignment in GCC."
        ],
        "correct_option_index": 1,
        "explanation": "In C, strings are null-terminated arrays of characters. The string literal \"Hello\" consists of 'H', 'e', 'l', 'l', 'o', and the null terminator '\\0', totaling 6 bytes."
    },
    {
        "difficulty": "basic",
        "topic": "C: Structs & Sizeof Padding",
        "prompt_text": "[C] On a standard 64-bit architecture with 4-byte integers and 8-byte alignment, why might `sizeof(struct Data)` be 16 bytes rather than 9 bytes?",
        "code_snippet": "struct Data {\n    char a;     // 1 byte\n    int b;      // 4 bytes\n    double c;   // 8 bytes\n};",
        "options": [
            "The compiler encrypts structs with a 7-byte header.",
            "Structure padding is inserted by the compiler to ensure members align to memory addresses that are multiples of their natural alignment.",
            "sizeof() always rounds all structs up to powers of 2.",
            "char in structs is automatically promoted to double."
        ],
        "correct_option_index": 1,
        "explanation": "Compilers insert padding bytes so data types align with processor memory bus boundaries (e.g. 3 bytes padding after char 'a' so int 'b' is 4-byte aligned), resulting in 16 total bytes."
    },
    {
        "difficulty": "basic",
        "topic": "C++: References vs Pointers",
        "prompt_text": "[C++] What is a key semantic difference between a C++ reference (`int &ref = x;`) and a pointer (`int *ptr = &x;`)?",
        "code_snippet": None,
        "options": [
            "References can be reseated to refer to another object at any time.",
            "A reference must be initialized upon declaration and cannot be null or reseated to bind to another object.",
            "Pointers cannot be passed to functions in C++.",
            "References allocate 8 bytes on the heap."
        ],
        "correct_option_index": 1,
        "explanation": "A reference is an alias for an existing object. It must be initialized when created, cannot be null, and cannot be reseated to refer to a different object across its lifetime."
    },
    {
        "difficulty": "basic",
        "topic": "C++: Function Overloading",
        "prompt_text": "[C++] What mechanism enables the C++ compiler to support function overloading at the linker level?",
        "code_snippet": "void print(int x);\nvoid print(double x);",
        "options": [
            "Virtual method tables (vtables)",
            "Name mangling (encoding parameter types into symbol names)",
            "Dynamic runtime reflection",
            "Macro preprocessor expansion"
        ],
        "correct_option_index": 1,
        "explanation": "C++ compilers use name mangling to encode function parameter types into unique symbol names for the linker (e.g., `_Z5printi` vs `_Z5printd`), allowing multiple functions with the same name to coexist."
    },
    {
        "difficulty": "basic",
        "topic": "C++: Constructors & Destructors",
        "prompt_text": "[C++] In what order are constructors and destructors called when an automatic (stack-allocated) C++ object leaves scope?",
        "code_snippet": None,
        "options": [
            "Constructors are called in declaration order; destructors are called in reverse order of construction.",
            "Constructors and destructors are called simultaneously on separate threads.",
            "Destructors are only called when delete is invoked explicitly.",
            "Destructors are called in the exact same order as constructors."
        ],
        "correct_option_index": 0,
        "explanation": "Objects on the stack are destroyed in strict reverse order of their construction (LIFO order), ensuring that objects depending on earlier initialized objects are cleaned up safely."
    },
    {
        "difficulty": "basic",
        "topic": "C: The Preprocessor & Macros",
        "prompt_text": "[C] What is the classic flaw in the macro `#define SQUARE(x) x * x` when evaluated with `SQUARE(2 + 3)`?",
        "code_snippet": "#define SQUARE(x) x * x\nint val = SQUARE(2 + 3);",
        "options": [
            "It computes 25 as expected.",
            "It computes 11 because macro text expansion yields `2 + 3 * 2 + 3`.",
            "It throws a compiler syntax error.",
            "It triggers an integer overflow exception."
        ],
        "correct_option_index": 1,
        "explanation": "Preprocessor macros perform naive textual substitution. `SQUARE(2 + 3)` expands to `2 + 3 * 2 + 3`. Because multiplication has higher precedence than addition, this evaluates to `2 + 6 + 3 = 11`. Safe macros require parentheses: `((x) * (x))`."
    },
    {
        "difficulty": "basic",
        "topic": "C++: The 'new' and 'delete' Operators",
        "prompt_text": "[C++] Why must dynamic arrays allocated with `new int[100]` be released using `delete[]` rather than `delete`?",
        "code_snippet": "int *arr = new int[100];\n// Deallocation:",
        "options": [
            "delete and delete[] are completely interchangeable in C++.",
            "delete[] ensures that destructors are called for all elements of the array and the array allocation metadata is correctly interpreted.",
            "delete[] deletes the pointer itself, while delete deletes the data.",
            "delete without brackets throws a compile-time error in all C++ compilers."
        ],
        "correct_option_index": 1,
        "explanation": "`delete[]` queries the array overhead cookie to determine the element count and invokes destructors for each element before deallocating memory. Using `delete` on an array causes undefined behavior."
    },

    # ─── INTERMEDIATE (10 Questions) ────────────────────────────────────
    {
        "difficulty": "intermediate",
        "topic": "C: Dangling Pointers & Double Free",
        "prompt_text": "[C] What is a 'dangling pointer' in C?",
        "code_snippet": "int *p = (int *)malloc(sizeof(int));\n*p = 100;\nfree(p);\n// p is now:",
        "options": [
            "A pointer automatically set to NULL by the free() function.",
            "A pointer that still holds the memory address of deallocated storage, leading to undefined behavior if dereferenced.",
            "A pointer that points to static global memory.",
            "A pointer whose target address is aligned to an odd byte boundary."
        ],
        "correct_option_index": 1,
        "explanation": "Calling `free(p)` returns the memory block to the system allocator but does not modify the variable `p`. `p` becomes a dangling pointer; dereferencing or freeing it again causes undefined behavior."
    },
    {
        "difficulty": "intermediate",
        "topic": "C++: RAII (Resource Acquisition Is Initialization)",
        "prompt_text": "[C++] What is the core design philosophy of RAII in C++?",
        "code_snippet": None,
        "options": [
            "All resources should be allocated in the main() function before execution begins.",
            "Resource lifetimes are bound to object lifetimes: resources are acquired in constructors and deterministically released in destructors when scope is exited.",
            "Memory should be managed by a background garbage collector thread.",
            "All class member variables must be initialized to zero."
        ],
        "correct_option_index": 1,
        "explanation": "RAII ties resource lifecycle (heap memory, file handles, mutexes, sockets) to object scope. The constructor acquires the resource, and the destructor automatically and deterministically releases it, even during exceptions."
    },
    {
        "difficulty": "intermediate",
        "topic": "C++: Virtual Functions & Polymorphism",
        "prompt_text": "[C++] Why must a base class with virtual methods declare a virtual destructor?",
        "code_snippet": "class Base {\npublic:\n    virtual void execute() = 0;\n    virtual ~Base() {}\n};",
        "options": [
            "To allow the base class to be instantiated directly.",
            "To ensure that deleting a derived class object through a pointer to Base invokes the derived class destructor, preventing resource leaks.",
            "Virtual destructors are required for template metaprogramming.",
            "To prevent the compiler from optimizing out empty classes."
        ],
        "correct_option_index": 1,
        "explanation": "If a derived object is deleted through a pointer to Base (`Base *b = new Derived(); delete b;`), a non-virtual base destructor causes undefined behavior where only Base's destructor runs, leaking Derived's resources."
    },
    {
        "difficulty": "intermediate",
        "topic": "C++: Smart Pointers (std::unique_ptr)",
        "prompt_text": "[C++] Why does std::unique_ptr NOT support copy construction or copy assignment?",
        "code_snippet": "std::unique_ptr<int> p1 = std::make_unique<int>(10);\n// std::unique_ptr<int> p2 = p1; // Compile error!",
        "options": [
            "Because C++ templates cannot copy pointers.",
            "Because unique_ptr represents exclusive ownership of a resource; copying would create multiple owners, violating exclusive ownership semantics.",
            "Because unique_ptr is implemented using C void* pointers.",
            "unique_ptr does support copying if the C++20 standard is enabled."
        ],
        "correct_option_index": 1,
        "explanation": "`std::unique_ptr` embodies exclusive ownership. It cannot be copied (its copy constructor is deleted), but it can be moved via `std::move()`, transferring ownership cleanly."
    },
    {
        "difficulty": "intermediate",
        "topic": "C++: Smart Pointers (std::shared_ptr & std::weak_ptr)",
        "prompt_text": "[C++] How does std::weak_ptr resolve cyclical reference issues between std::shared_ptr instances?",
        "code_snippet": None,
        "options": [
            "weak_ptr forces the operating system to delete cyclical nodes.",
            "weak_ptr holds a non-owning reference without incrementing the shared reference count (strong count), preventing mutual reference cycles from causing memory leaks.",
            "weak_ptr encrypts pointers to break cycles.",
            "weak_ptr automatically converts shared_ptr instances into raw C pointers."
        ],
        "correct_option_index": 1,
        "explanation": "Cycles of `std::shared_ptr` prevent strong counts from reaching zero, leaking memory. `std::weak_ptr` tracks the object without incrementing the strong reference count, breaking cyclic retention."
    },
    {
        "difficulty": "intermediate",
        "topic": "C: Double Pointers & Function Modification",
        "prompt_text": "[C] Why must a function receive a pointer-to-pointer (e.g., int **ptr) if it intends to allocate and update the caller's pointer variable?",
        "code_snippet": "void allocate(int **p) {\n    *p = (int *)malloc(sizeof(int));\n}",
        "options": [
            "C passes all function arguments by value; to modify the caller's pointer, you must pass the address of that pointer.",
            "malloc() only accepts double pointers.",
            "To enable multi-threaded memory allocation in the C standard library.",
            "Because 64-bit systems require two 32-bit addresses."
        ],
        "correct_option_index": 0,
        "explanation": "Because C is strictly pass-by-value, passing `int *p` creates a local copy of the pointer. Modifying `p` only updates the local parameter. Passing `int **p` allows dereferencing `*p` to modify the caller's actual pointer variable."
    },
    {
        "difficulty": "intermediate",
        "topic": "C++: STL Containers & Iterator Invalidation",
        "prompt_text": "[C++] What happens to iterators pointing into a std::vector when push_back() causes the vector's capacity to be exceeded?",
        "code_snippet": "std::vector<int> v = {1, 2, 3};\nauto it = v.begin();\nv.push_back(4); // Reallocation occurs!",
        "options": [
            "All existing iterators remain valid and update their internal pointers automatically.",
            "All existing iterators, pointers, and references to elements are invalidated because elements are reallocated to a new contiguous memory block.",
            "The compiler raises a static assertion error.",
            "Only the end() iterator is invalidated; begin() remains valid."
        ],
        "correct_option_index": 1,
        "explanation": "When `push_back()` triggers reallocation because `size() == capacity()`, the vector allocates a larger buffer and moves elements. All iterators, pointers, and references pointing into the old buffer become invalid."
    },
    {
        "difficulty": "intermediate",
        "topic": "C++: Templates & Specialization",
        "prompt_text": "[C++] In C++, what is template full specialization?",
        "code_snippet": "template <typename T>\nstruct Formatter {\n    static void format(T val);\n};\n\ntemplate <>\nstruct Formatter<bool> {\n    static void format(bool val);\n};",
        "options": [
            "Generating templates dynamically during program execution.",
            "Providing a custom implementation of a template for a specific, concrete type parameter.",
            "Restricting a template to only compile on Linux.",
            "Converting a class template into a runtime virtual function."
        ],
        "correct_option_index": 1,
        "explanation": "Full template specialization (`template <> struct Formatter<bool>`) allows authors to define a specialized, custom implementation of a class or function template for a specific type argument."
    },
    {
        "difficulty": "intermediate",
        "topic": "C: Const Correctness with Pointers",
        "prompt_text": "[C] What is the difference between `const int *p` and `int * const p`?",
        "code_snippet": None,
        "options": [
            "They are completely identical in C and C++.",
            "`const int *p` is a pointer to a constant integer (the data cannot be modified via p); `int * const p` is a constant pointer to an integer (the pointer address cannot be changed).",
            "`int * const p` allocates memory in the CPU cache.",
            "`const int *p` forces p to be stored in the code/text segment."
        ],
        "correct_option_index": 1,
        "explanation": "Reading right-to-left: `const int *p` is a pointer to const int (value is read-only via p, but p can point elsewhere). `int * const p` is a const pointer to int (p cannot point to another address, but *p can be mutated)."
    },
    {
        "difficulty": "intermediate",
        "topic": "C++: Lambda Expressions & Captures",
        "prompt_text": "[C++] What does the capture specification `[&]` signify in a C++ lambda expression?",
        "code_snippet": "auto lambda = [&]() { count++; };",
        "options": [
            "Capture all referenced outer variables by value (copy).",
            "Capture all referenced outer variables by reference.",
            "Capture only the 'this' pointer.",
            "Disable access to enclosing lexical variables."
        ],
        "correct_option_index": 1,
        "explanation": "In C++ lambdas, `[&]` captures all automatic variables used in the lambda body by reference. `[=]` captures by value."
    },

    # ─── ADVANCED (10 Questions) ─────────────────────────────────────────
    {
        "difficulty": "advanced",
        "topic": "C++: Move Semantics & Rvalue References",
        "prompt_text": "[C++] What does std::move() actually do at runtime in modern C++?",
        "code_snippet": "std::string s1 = \"data\";\nstd::string s2 = std::move(s1);",
        "options": [
            "It copies the memory buffer of s1 to s2 in an asynchronous background thread.",
            "It does nothing at runtime; it is an unconditional static_cast to an rvalue reference (`static_cast<T&&>(var)`), enabling move constructors to be matched by overload resolution.",
            "It immediately zeroes out all bytes in s1.",
            "It swaps the pointers of s1 and s2 directly in OS virtual memory."
        ],
        "correct_option_index": 1,
        "explanation": "`std::move()` produces no executable machine code at runtime. It is purely a compile-time cast converting an lvalue expression into an rvalue reference (`T&&`), enabling move constructors to steal resources."
    },
    {
        "difficulty": "advanced",
        "topic": "C++: Virtual Method Tables (vtable & vptr)",
        "prompt_text": "[C++] How do C++ compilers implement runtime dynamic dispatch for classes containing virtual functions?",
        "code_snippet": None,
        "options": [
            "By embedding an interpreter into the compiled binary.",
            "By creating a static virtual method table (vtable) per class containing function pointers, and inserting a hidden pointer (vptr) in each object instance pointing to its class vtable.",
            "By performing string lookups on method names at runtime.",
            "By analyzing call graphs using operating system signals."
        ],
        "correct_option_index": 1,
        "explanation": "Compilers generate a vtable for each polymorphic class containing pointers to virtual functions. Each class instance contains a hidden `vptr` pointer pointing to the appropriate vtable, enabling constant-time indirect calls."
    },
    {
        "difficulty": "advanced",
        "topic": "C: Buffer Overflows & Stack Protection",
        "prompt_text": "[C] Why is the standard C library function `gets()` notoriously dangerous, leading to its deprecation and removal in C11?",
        "code_snippet": "char buffer[64];\ngets(buffer); // UNSAFE!",
        "options": [
            "It leaks memory on multi-core systems.",
            "It performs no buffer bounds checking, allowing input to overflow the stack buffer, corrupting frame pointers and return addresses (exploitable for arbitrary code execution).",
            "It only accepts uppercase ASCII characters.",
            "It cannot read input from standard input (stdin)."
        ],
        "correct_option_index": 1,
        "explanation": "`gets()` has no parameter limiting input length. Any input exceeding buffer capacity overflows the stack frame, overwriting the saved frame pointer and return address, creating classic stack buffer overflow vulnerabilities."
    },
    {
        "difficulty": "advanced",
        "topic": "C++: Perfect Forwarding & std::forward",
        "prompt_text": "[C++] What problem does `std::forward<T>()` solve in generic template functions?",
        "code_snippet": "template <typename T>\nvoid wrapper(T&& arg) {\n    target(std::forward<T>(arg));\n}",
        "options": [
            "It prevents compilation errors when passing raw function pointers.",
            "It preserves the exact value category (lvalue vs rvalue) of the argument passed to a universal/forwarding reference (`T&&`), preventing unnecessary copies.",
            "It forces synchronous execution in multithreaded code.",
            "It forwards network packets between sockets."
        ],
        "correct_option_index": 1,
        "explanation": "A named forwarding reference `arg` is itself an lvalue inside the function body. `std::forward<T>(arg)` conditionally casts it back to an rvalue if and only if the original caller argument was an rvalue, preserving value category."
    },
    {
        "difficulty": "advanced",
        "topic": "C++: SFINAE & std::enable_if",
        "prompt_text": "[C++] What does the C++ principle SFINAE (Substitution Failure Is Not An Error) dictate during template compilation?",
        "code_snippet": None,
        "options": [
            "If a syntax error occurs anywhere in a project, the build succeeds anyway.",
            "If substituting a template parameter results in an invalid type or expression during overload resolution, that candidate is silently discarded from the overload set without causing a compilation error.",
            "Templates are substituted at runtime rather than compile time.",
            "Virtual functions take precedence over template specializations."
        ],
        "correct_option_index": 1,
        "explanation": "SFINAE states that if substituting a deduced type into a template signature fails, the compiler does not issue an error; it simply removes that candidate from the overload candidate set."
    },
    {
        "difficulty": "advanced",
        "topic": "C: Volatile Keyword in Embedded C",
        "prompt_text": "[C] In low-level C programming, what does marking a memory-mapped I/O register as `volatile` tell the compiler?",
        "code_snippet": "volatile uint32_t * const UART_STATUS = (uint32_t *)0x40004000;",
        "options": [
            "The memory address is volatile and changes random locations every cycle.",
            "The compiler must not optimize away, reorder, or cache reads/writes to this address in CPU registers, because hardware may alter its value independently of the program.",
            "It encrypts the bus communication.",
            "It makes the variable thread-safe like a mutex."
        ],
        "correct_option_index": 1,
        "explanation": "`volatile` informs the compiler that the value at this memory address can change unexpectedly (e.g., hardware register or interrupt service routine). The compiler is forced to issue a real memory access on every read/write."
    },
    {
        "difficulty": "advanced",
        "topic": "C++: Rule of Five (and Rule of Zero)",
        "prompt_text": "[C++] According to the C++ 'Rule of Five', if a class customizes its destructor, what other four special member functions should it generally declare or define?",
        "code_snippet": None,
        "options": [
            "get(), set(), print(), clone()",
            "Copy constructor, copy assignment operator, move constructor, move assignment operator",
            "Five virtual interface methods",
            "operator==, operator!=, operator<, operator>"
        ],
        "correct_option_index": 1,
        "explanation": "The Rule of Five states that if a class requires a custom destructor (usually to manage a raw resource), it almost certainly requires custom implementations or deletions of: copy constructor, copy assignment, move constructor, and move assignment."
    },
    {
        "difficulty": "advanced",
        "topic": "C++: constexpr vs consteval",
        "prompt_text": "[C++] What is the distinction between `constexpr` and `consteval` functions introduced in C++20?",
        "code_snippet": "consteval int square(int n) { return n * n; }",
        "options": [
            "constexpr functions can only execute at runtime; consteval executes on the GPU.",
            "constexpr functions can be evaluated at compile-time or runtime depending on arguments; consteval functions (immediate functions) MUST evaluate to a compile-time constant, or compilation fails.",
            "consteval functions cannot accept integer arguments.",
            "They are completely synonymous."
        ],
        "correct_option_index": 1,
        "explanation": "`constexpr` functions can be executed at compile time if called with constant expressions, but fall back to runtime execution if given runtime values. `consteval` guarantees that the function MUST evaluate at compile time."
    },
    {
        "difficulty": "advanced",
        "topic": "C++: Memory Model & Atomic Operations",
        "prompt_text": "[C++] In `std::atomic`, what does the `std::memory_order_acquire` / `std::memory_order_release` synchronization pattern guarantee?",
        "code_snippet": "// Thread 1:\ndata = 42;\nflag.store(true, std::memory_order_release);\n\n// Thread 2:\nwhile (!flag.load(std::memory_order_acquire));\nassert(data == 42);",
        "options": [
            "Acquire/Release only synchronizes with sequentially consistent hardware locks.",
            "All memory writes prior to the release store in Thread 1 are guaranteed to be visible to Thread 2 after its acquire load returns true, without requiring a full sequential consistency fence.",
            "The assert fails because acquire/release does not sync non-atomic memory.",
            "It turns Thread 1 and Thread 2 into coroutines."
        ],
        "correct_option_index": 1,
        "explanation": "Release-acquire synchronization creates an inter-thread happens-before relationship. Writes prior to a release store in Thread 1 are guaranteed to become visible to Thread 2 once its acquire load observes the stored value."
    },
    {
        "difficulty": "advanced",
        "topic": "C: Function Pointers & Callbacks",
        "prompt_text": "[C] What is the correct C syntax to declare a function pointer variable `fp` pointing to a function that takes `(int, double)` and returns `char *`?",
        "code_snippet": None,
        "options": [
            "char *fp(int, double);",
            "char * (*fp)(int, double);",
            "fp<char*, (int, double)>;",
            "(char *)(*fp)(int, double);"
        ],
        "correct_option_index": 1,
        "explanation": "The syntax `char * (*fp)(int, double);` declares `fp` as a pointer to a function taking an int and double and returning a pointer to char. Parentheses around `(*fp)` are mandatory to prevent precedence binding to return type."
    }
]
