"""
Java Programming Question Bank.
Contains 30 verified questions (10 basic, 10 intermediate, 10 advanced).
"""

JAVA_QUESTIONS = [
    # ─── BASIC (10 Questions) ───────────────────────────────────────────
    {
        "difficulty": "basic",
        "topic": "Primitive Types & Autoboxing",
        "prompt_text": "What does the following comparison evaluate to in Java, and why?",
        "code_snippet": "Integer a = 127;\nInteger b = 127;\nInteger c = 128;\nInteger d = 128;\nSystem.out.println((a == b) + \" \" + (c == d));",
        "options": [
            "true true",
            "false false",
            "true false",
            "false true"
        ],
        "correct_option_index": 2,
        "explanation": "Java caches Integer objects in the range -128 to 127 via IntegerCache. Autoboxing 127 yields identical cached references (a == b is true). 128 is outside the cache, allocating distinct heap objects (c == d is false)."
    },
    {
        "difficulty": "basic",
        "topic": "String Immutability & String Pool",
        "prompt_text": "How does Java handle string literals versus strings created with 'new String()'?",
        "code_snippet": "String s1 = \"hello\";\nString s2 = \"hello\";\nString s3 = new String(\"hello\");",
        "options": [
            "s1, s2, and s3 all reference the same memory address in the heap.",
            "s1 and s2 share a canonical reference in the String Constant Pool; s3 is an explicitly allocated object in normal heap memory.",
            "Strings are mutable in Java, so s2 can modify s1.",
            "new String() throws an UnsupportedOperationException in modern Java."
        ],
        "correct_option_index": 1,
        "explanation": "String literals are internalized into the JVM String Constant Pool and reused. `new String(...)` explicitly forces the allocation of a new instance on the general heap, so s1 == s2 is true, but s1 == s3 is false."
    },
    {
        "difficulty": "basic",
        "topic": "Access Modifiers",
        "prompt_text": "If a class member in Java has NO access modifier specified (default / package-private), where is it accessible from?",
        "code_snippet": None,
        "options": [
            "Everywhere across the entire application.",
            "Only within the defining class itself.",
            "Only from classes within the same package.",
            "From classes within the same package and subclasses in other packages."
        ],
        "correct_option_index": 2,
        "explanation": "Default (package-private) access restricts visibility strictly to classes declared within the same package. Subclasses in different packages cannot access default members."
    },
    {
        "difficulty": "basic",
        "topic": "OOP: Method Overriding vs Overloading",
        "prompt_text": "What distinguishes method overriding from method overloading in Java?",
        "code_snippet": None,
        "options": [
            "Overloading happens at runtime; overriding happens at compile time.",
            "Overriding provides a specific implementation in a subclass for a method declared in a superclass with identical signature; overloading defines methods with the same name but different parameter lists in the same class.",
            "Overriding requires static methods, while overloading requires instance methods.",
            "Overloaded methods must have identical return types."
        ],
        "correct_option_index": 1,
        "explanation": "Overriding replaces a superclass method's behavior with the exact same name, arguments, and return type (or covariant return). Overloading defines multiple methods with the same name but distinct parameter lists."
    },
    {
        "difficulty": "basic",
        "topic": "Exception Handling: Checked vs Unchecked",
        "prompt_text": "Which of the following classes is an unchecked exception in Java?",
        "code_snippet": None,
        "options": [
            "java.io.IOException",
            "java.sql.SQLException",
            "java.lang.NullPointerException",
            "java.lang.ClassNotFoundException"
        ],
        "correct_option_index": 2,
        "explanation": "Unchecked exceptions inherit from java.lang.RuntimeException (or java.lang.Error). NullPointerException is a RuntimeException and does not require explicit throws declarations or try-catch blocks."
    },
    {
        "difficulty": "basic",
        "topic": "Interfaces & Default Methods",
        "prompt_text": "What was the primary motivation for introducing 'default' methods in Java 8 interfaces?",
        "code_snippet": "public interface Service {\n    void execute();\n    default void log() {\n        System.out.println(\"Executing\");\n    }\n}",
        "options": [
            "To deprecate abstract classes entirely.",
            "To allow backward-compatible evolution of interfaces by adding new methods with implementations without breaking existing implementers.",
            "To enable multiple inheritance of state across interfaces.",
            "To convert interfaces into concrete singleton classes."
        ],
        "correct_option_index": 1,
        "explanation": "Default methods allow library authors to add new methods to existing interfaces (such as Collection.stream() in Java 8) without breaking all classes implementing those interfaces."
    },
    {
        "difficulty": "basic",
        "topic": "Static Keyword & Initializers",
        "prompt_text": "When is a 'static' initialization block executed in Java?",
        "code_snippet": "public class Database {\n    static {\n        System.out.println(\"Static init\");\n    }\n}",
        "options": [
            "Every time a new instance of the class is constructed with 'new'.",
            "Once, when the class is first loaded into memory by the JVM ClassLoader.",
            "Only when the main() method terminates.",
            "Whenever a static method throws an exception."
        ],
        "correct_option_index": 1,
        "explanation": "Static initializer blocks run exactly once when the class is initially loaded and initialized by the JVM ClassLoader, before any instance is instantiated or static member accessed."
    },
    {
        "difficulty": "basic",
        "topic": "String vs StringBuilder vs StringBuffer",
        "prompt_text": "Why should StringBuilder be preferred over String concatenation inside a loop in single-threaded Java code?",
        "code_snippet": None,
        "options": [
            "String concatenation is illegal inside loops in Java.",
            "String is immutable; repeated concatenation creates numerous intermediate String objects in memory, resulting in O(n^2) performance.",
            "StringBuilder automatically offloads processing to the GPU.",
            "StringBuffer is deprecated in Java."
        ],
        "correct_option_index": 1,
        "explanation": "Because Strings are immutable, repeated '+' concatenation allocates a new String on each iteration, copying prior characters and causing O(n^2) time and high GC allocation pressure. StringBuilder mutates an internal char/byte buffer in O(n) total time."
    },
    {
        "difficulty": "basic",
        "topic": "Collections: ArrayList vs LinkedList",
        "prompt_text": "What is the time complexity of getting an element by index (get(i)) in an ArrayList versus a LinkedList in Java?",
        "code_snippet": None,
        "options": [
            "ArrayList: O(1); LinkedList: O(n)",
            "ArrayList: O(n); LinkedList: O(1)",
            "Both are O(1)",
            "Both are O(log n)"
        ],
        "correct_option_index": 0,
        "explanation": "ArrayList is backed by a contiguous array, providing O(1) random access via index arithmetic. LinkedList is a doubly-linked list, requiring traversal from head or tail to index i in O(n) time."
    },
    {
        "difficulty": "basic",
        "topic": "Object Class Methods",
        "prompt_text": "What is the contract between equals() and hashCode() in java.lang.Object?",
        "code_snippet": None,
        "options": [
            "If two objects have equal hash codes, their equals() method must return true.",
            "If two objects are equal according to equals(), their hashCode() method must return the exact same integer value.",
            "hashCode() must always return a positive 64-bit long integer.",
            "equals() and hashCode() can be overridden independently without consequence."
        ],
        "correct_option_index": 1,
        "explanation": "The Java Object contract mandates: if `a.equals(b)` is true, then `a.hashCode() == b.hashCode()` must be true. Violating this breaks hash-based collections like HashMap and HashSet."
    },

    # ─── INTERMEDIATE (10 Questions) ────────────────────────────────────
    {
        "difficulty": "intermediate",
        "topic": "HashMap Internal Architecture",
        "prompt_text": "In Java 8+, what optimization does java.util.HashMap perform when a hash bucket experiences high collision counts exceeding TREEIFY_THRESHOLD (8)?",
        "code_snippet": None,
        "options": [
            "It drops colliding entries to prevent memory exhaustion.",
            "It converts the bucket's linked list into a balanced Red-Black tree (TreeNode), improving worst-case search time from O(n) to O(log n).",
            "It doubles the hash seed and restarts the JVM.",
            "It converts the HashMap into a synchronized Hashtable."
        ],
        "correct_option_index": 1,
        "explanation": "To defend against hash flooding attacks and poor hash distributions, Java 8 converts a bucket's linked list into a Red-Black tree when the bucket contains 8 or more entries and the table capacity is at least 64."
    },
    {
        "difficulty": "intermediate",
        "topic": "Generics & PECS Principle",
        "prompt_text": "In Java Generics, what does the PECS rule dictate?",
        "code_snippet": None,
        "options": [
            "Producer Extends, Consumer Super (use <? extends T> when reading from a collection, and <? super T> when writing to it).",
            "Private Encapsulation Creates Security.",
            "Parameter Evaluation Causes Serialization.",
            "Polymorphic Entities Consume Subclasses."
        ],
        "correct_option_index": 0,
        "explanation": "PECS stands for 'Producer Extends, Consumer Super'. If a collection produces items of type T (you read from it), use `? extends T`. If it consumes items of type T (you write to it), use `? super T`."
    },
    {
        "difficulty": "intermediate",
        "topic": "Java Memory Model: Stack vs Heap",
        "prompt_text": "Where are local primitive variables and object instances stored in Java memory?",
        "code_snippet": "public void execute() {\n    int count = 10;\n    User user = new User(\"Alice\");\n}",
        "options": [
            "Both 'count' and the 'User' instance are allocated in the method's thread stack frame.",
            "'count' and the reference 'user' live on the thread stack frame; the User instance itself is allocated on the heap.",
            "Both are allocated directly in the JVM Metaspace.",
            "Everything in Java is allocated on the stack unless marked with 'static'."
        ],
        "correct_option_index": 1,
        "explanation": "Local variables (primitive values like `count` and object reference pointers like `user`) reside on the thread's call stack. The actual object instance created via `new User(...)` is allocated on the shared heap."
    },
    {
        "difficulty": "intermediate",
        "topic": "Streams: Intermediate vs Terminal",
        "prompt_text": "Why does the following Java Stream code produce NO output when executed?",
        "code_snippet": "List<String> names = List.of(\"Alice\", \"Bob\", \"Charlie\");\nnames.stream().filter(s -> {\n    System.out.println(\"Filtering: \" + s);\n    return s.startsWith(\"A\");\n});",
        "options": [
            "filter() only processes strings with lowercase letters.",
            "Stream operations are lazy: intermediate operations like filter() do not execute until a terminal operation (e.g., collect(), forEach(), count()) is invoked.",
            "List.of() returns an unmodifiable list that cannot be streamed.",
            "System.out is disabled inside stream pipelines."
        ],
        "correct_option_index": 1,
        "explanation": "Streams in Java are evaluated lazily. Intermediate operations (filter, map, sorted) simply construct a pipeline; execution is only triggered when a terminal operation is called."
    },
    {
        "difficulty": "intermediate",
        "topic": "Comparable vs Comparator",
        "prompt_text": "What is the key difference between Comparable<T> and Comparator<T> in Java?",
        "code_snippet": None,
        "options": [
            "Comparable defines the natural ordering of a class within that class itself (compareTo); Comparator defines external, customizable sorting strategies (compare).",
            "Comparable can only sort primitives, while Comparator sorts objects.",
            "Comparable was deprecated in Java 8 in favor of Comparator.",
            "Comparator is thread-safe, while Comparable is not."
        ],
        "correct_option_index": 0,
        "explanation": "A class implements `Comparable<T>` to establish its intrinsic natural ordering via `compareTo(T o)`. `Comparator<T>` is a separate functional interface (`compare(T o1, T o2)`) allowing multiple arbitrary sorting strategies."
    },
    {
        "difficulty": "intermediate",
        "topic": "Garbage Collection Generations",
        "prompt_text": "How does the JVM generational hypothesis optimize garbage collection?",
        "code_snippet": None,
        "options": [
            "It observes that most allocated objects have short lifespans, so collecting the Young Generation frequently is fast and reclaims the vast majority of memory.",
            "It groups objects by the Java package in which they were created.",
            "It requires developers to manually deallocate objects older than 5 minutes.",
            "It migrates all objects directly to disk after 3 minor collections."
        ],
        "correct_option_index": 0,
        "explanation": "The weak generational hypothesis observes that the vast majority of objects die shortly after allocation. By dividing the heap into Young (Eden, Survivor) and Old (Tenured) generations, minor GCs can quickly reclaim young dead objects without scanning the entire heap."
    },
    {
        "difficulty": "intermediate",
        "topic": "Try-With-Resources & AutoCloseable",
        "prompt_text": "What interface must a custom resource implement to be managed automatically in a Java try-with-resources statement?",
        "code_snippet": "try (MyResource r = new MyResource()) {\n    r.process();\n}",
        "options": [
            "java.io.Serializable",
            "java.lang.AutoCloseable (or java.io.Closeable)",
            "java.lang.Cloneable",
            "java.util.concurrent.Callable"
        ],
        "correct_option_index": 1,
        "explanation": "The try-with-resources statement requires any declared resource to implement `java.lang.AutoCloseable` (or its subinterface `java.io.Closeable`), which defines the `void close()` method."
    },
    {
        "difficulty": "intermediate",
        "topic": "Optional API",
        "prompt_text": "What is the semantic difference between optional.orElse(computeDefault()) and optional.orElseGet(() -> computeDefault())?",
        "code_snippet": None,
        "options": [
            "They behave identically under all conditions.",
            "orElse() always evaluates its argument expression eagerly even if the Optional is present; orElseGet() takes a Supplier and evaluates it lazily only when the Optional is empty.",
            "orElseGet() throws a NullPointerException if the value is empty.",
            "orElse() can only be called on non-empty Optionals."
        ],
        "correct_option_index": 1,
        "explanation": "`orElse(expr)` evaluates `expr` eagerly as a standard method argument. `orElseGet(supplier)` is lazy; the supplier function is only executed if the Optional is indeed empty, saving expensive computations."
    },
    {
        "difficulty": "intermediate",
        "topic": "Multithreading & Synchronized",
        "prompt_text": "When a non-static method is marked 'synchronized' in Java, what intrinsic lock (monitor) is acquired?",
        "code_snippet": "public synchronized void updateState() {\n    this.state++;\n}",
        "options": [
            "The lock on the Class object (MyClass.class).",
            "The intrinsic monitor lock of the current instance ('this').",
            "A system-wide global thread lock.",
            "No lock is acquired; it only increments an atomic counter."
        ],
        "correct_option_index": 1,
        "explanation": "Synchronizing a non-static method acquires the intrinsic monitor lock of the instance on which the method is called (`this`). Synchronizing a static method acquires the monitor on the `Class` object."
    },
    {
        "difficulty": "intermediate",
        "topic": "Type Erasure",
        "prompt_text": "What happens to generic type parameters like List<String> at runtime due to type erasure?",
        "code_snippet": None,
        "options": [
            "The type parameter String is retained and verified on every list operation by the JVM bytecode interpreter.",
            "The type parameter is erased; at bytecode level, the collection is treated as raw List with casts inserted by the compiler.",
            "The JVM compiles separate C++ classes for List_String and List_Integer.",
            "Generics cause a runtime reflection fault if queried via getClass()."
        ],
        "correct_option_index": 1,
        "explanation": "Java generics use type erasure for backward compatibility. Generic type information is checked at compile-time and then stripped from bytecode, replacing unbounded parameters with Object and inserting checkcast instructions."
    },

    # ─── ADVANCED (10 Questions) ─────────────────────────────────────────
    {
        "difficulty": "advanced",
        "topic": "Memory Model: Volatile Keyword",
        "prompt_text": "What guarantees does the 'volatile' keyword provide in the Java Memory Model (JMM)?",
        "code_snippet": "private volatile boolean flag = true;",
        "options": [
            "Atomic increment operations (e.g., flag++) without synchronization.",
            "Visibility (writes by one thread are immediately visible to reads by other threads) and ordering (prevents instruction reordering around reads/writes via memory barriers).",
            "Thread mutual exclusion identical to a synchronized block.",
            "Guarantees that the variable is cached in L1 CPU cache and never written to RAM."
        ],
        "correct_option_index": 1,
        "explanation": "`volatile` establishes a happens-before relationship ensuring memory visibility across threads and prevents compiler/CPU instruction reordering across the memory barrier. It does NOT guarantee compound atomicity (like i++)."
    },
    {
        "difficulty": "advanced",
        "topic": "Concurrency: ConcurrentHashMap Mechanics",
        "prompt_text": "How does ConcurrentHashMap in Java 8 achieve high concurrency without locking the entire table?",
        "code_snippet": None,
        "options": [
            "By wrapping all methods in synchronized blocks.",
            "By using CAS (Compare-And-Swap) for empty bucket initialization and synchronizing strictly on the first node of the target bin during updates.",
            "By offloading map operations to background virtual threads.",
            "By utilizing 16 static Segment locks inherited from Java 7."
        ],
        "correct_option_index": 1,
        "explanation": "In Java 8, ConcurrentHashMap discarded Segment locking. It uses lock-free CAS operations for inserting into empty bins, and uses `synchronized` on only the first Node of a specific colliding bucket, minimizing contention."
    },
    {
        "difficulty": "advanced",
        "topic": "ThreadPoolExecutor & Rejection Policies",
        "prompt_text": "In a standard ThreadPoolExecutor, when are new threads beyond corePoolSize created?",
        "code_snippet": None,
        "options": [
            "Whenever a new task arrives and all core threads are currently active.",
            "Only when the task workQueue is completely full and the current pool size is less than maximumPoolSize.",
            "Immediately upon pool instantiation.",
            "Whenever CPU utilization exceeds 80%."
        ],
        "correct_option_index": 1,
        "explanation": "A ThreadPoolExecutor only creates additional threads beyond corePoolSize if the blocking workQueue is completely saturated (full) and the active thread count is below maximumPoolSize."
    },
    {
        "difficulty": "advanced",
        "topic": "JVM ClassLoader Hierarchy",
        "prompt_text": "What principle governs the standard Java ClassLoader delegation model?",
        "code_snippet": None,
        "options": [
            "Child First: A class loader always searches its own classpath before asking its parent.",
            "Parent Delegation: A class loader delegates the request to its parent before attempting to load the class itself, ensuring core Java classes (rt.jar / java.base) cannot be spoofed.",
            "Peer-to-peer: Class loaders broadcast lookup queries across all active threads concurrently.",
            "Randomized selection across registered ClassLoaders."
        ],
        "correct_option_index": 1,
        "explanation": "The parent-delegation model mandates that a classloader delegates class-loading requests to its parent before searching its own repository. This prevents unauthorized replacement of trusted core classes like java.lang.Object."
    },
    {
        "difficulty": "advanced",
        "topic": "Garbage Collection: ZGC & Shenandoah",
        "prompt_text": "What technological innovation enables ultra-low latency Garbage Collectors like ZGC and Shenandoah to maintain sub-millisecond pause times regardless of heap size?",
        "code_snippet": None,
        "options": [
            "Disabling object allocation completely during GC.",
            "Concurrent evacuation/relocation of heap objects using load barriers and colored pointers while application threads continue running.",
            "Storing the entire Java heap in non-volatile SSD flash memory.",
            "Eliminating the heap and running Java entirely in the Metaspace."
        ],
        "correct_option_index": 1,
        "explanation": "Modern concurrent collectors (ZGC, Shenandoah) perform object marking, evacuation, and pointer updating concurrently with application thread execution using colored pointers and load barriers, keeping STW pauses consistently under 1ms."
    },
    {
        "difficulty": "advanced",
        "topic": "False Sharing & Cache Lines",
        "prompt_text": "What is 'false sharing' in multi-core Java applications, and how can it be mitigated?",
        "code_snippet": "class SharedData {\n    volatile long value1;\n    volatile long value2;\n}",
        "options": [
            "When two threads access the same database connection concurrently.",
            "When independent variables accessed by different CPU cores reside on the same 64-byte L1/L2 CPU cache line, causing cache coherence invalidations; mitigated via cache-line padding or @jdk.internal.vm.annotation.Contended.",
            "When an application mistakenly deploys two identical WAR files to Tomcat.",
            "When two threads compute identical hash codes."
        ],
        "correct_option_index": 1,
        "explanation": "False sharing occurs when independent variables reside on the same CPU cache line (typically 64 bytes). Modifying one invalidates the entire cache line across other cores. Padding or `@Contended` inserts bytes to isolate variables onto distinct cache lines."
    },
    {
        "difficulty": "advanced",
        "topic": "Dynamic Proxies & Bytecode Manipulation",
        "prompt_text": "What is a key architectural limitation of java.lang.reflect.Proxy in Java?",
        "code_snippet": "Object proxy = Proxy.newProxyInstance(loader, interfaces, handler);",
        "options": [
            "It cannot proxy interfaces, only concrete classes.",
            "It can only create dynamic proxies for interfaces, not concrete classes without interfaces (which require bytecode libraries like ByteBuddy or CGLIB).",
            "It requires native C++ compilation at runtime.",
            "It can only intercept static methods."
        ],
        "correct_option_index": 1,
        "explanation": "JDK Dynamic Proxies strictly proxy interfaces (`interfaces: Class<?>[]`). To proxy concrete classes without interfaces, runtime bytecode generators (ByteBuddy, CGLIB, Javassist) that subclass the target class must be used."
    },
    {
        "difficulty": "advanced",
        "topic": "JIT Compilation & Escape Analysis",
        "prompt_text": "What optimization does the HotSpot C2 JIT compiler perform when Escape Analysis determines an object does NOT escape the executing method?",
        "code_snippet": None,
        "options": [
            "It automatically serializes the object to JSON.",
            "Scalar Replacement: It decomposes the object into its individual primitive fields in registers/stack, eliminating heap allocation and synchronization overhead.",
            "It immediately schedules a full GC cycle.",
            "It transfers the object to the Metaspace permanent generation."
        ],
        "correct_option_index": 1,
        "explanation": "When escape analysis proves an object's reference never escapes the allocating method/thread, the JIT can perform Scalar Replacement (storing fields in registers or stack frames rather than allocating a heap object) and lock elision."
    },
    {
        "difficulty": "advanced",
        "topic": "Java NIO vs BIO",
        "prompt_text": "How does Java NIO (New I/O) Selector enable a single thread to manage thousands of concurrent network connections?",
        "code_snippet": None,
        "options": [
            "By allocating an OS thread per incoming socket channel.",
            "By multiplexing non-blocking SocketChannels onto OS kernel polling mechanisms (epoll on Linux, kqueue on macOS) via a single Selector loop.",
            "By compressing TCP packets using gzip before socket transmission.",
            "By converting incoming network data into UDP datagrams."
        ],
        "correct_option_index": 1,
        "explanation": "Java NIO Selectors leverage OS I/O multiplexing primitives (epoll, kqueue). A single reactor thread monitors multiple Non-Blocking SocketChannels for readiness events (OP_READ, OP_WRITE, OP_ACCEPT) without thread-per-connection overhead."
    },
    {
        "difficulty": "advanced",
        "topic": "Virtual Threads (Project Loom)",
        "prompt_text": "In Java 21+, what happens under the hood when a Virtual Thread executes a blocking network I/O call?",
        "code_snippet": "Thread.startVirtualThread(() -> {\n    socket.getInputStream().read(); // Blocking I/O\n});",
        "options": [
            "The underlying OS platform thread (carrier thread) is blocked and remains idle until packet arrival.",
            "The Virtual Thread unmounts from its carrier thread, parking its execution frame in heap memory while the carrier thread runs other virtual threads until the I/O event arrives.",
            "The JVM terminates the virtual thread with an IOException.",
            "The virtual thread is promoted to a native OS thread dynamically."
        ],
        "correct_option_index": 1,
        "explanation": "Virtual threads are lightweight user-mode threads managed by the JVM. When a virtual thread performs a blocking operation, the JVM unmounts its Continuation from the carrier platform thread, freeing the carrier to execute other virtual threads."
    }
]
