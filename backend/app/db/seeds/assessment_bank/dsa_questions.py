"""
Data Structures & Algorithms Question Bank.
Contains 30 verified questions (10 basic, 10 intermediate, 10 advanced).
"""

DSA_QUESTIONS = [
    # ─── BASIC (10 Questions) ───────────────────────────────────────────
    {
        "difficulty": "basic",
        "topic": "Big-O Notation & Complexity",
        "prompt_text": "What is the worst-case time complexity of binary search on a sorted array of length n?",
        "code_snippet": None,
        "options": [
            "O(1)",
            "O(n)",
            "O(log n)",
            "O(n log n)"
        ],
        "correct_option_index": 2,
        "explanation": "Binary search divides the search space in half with each comparison, yielding a logarithmic worst-case time complexity of O(log n)."
    },
    {
        "difficulty": "basic",
        "topic": "Arrays & Dynamic Sizing",
        "prompt_text": "What is the amortized time complexity of appending an element to the end of a dynamic array (like Python list or C++ std::vector)?",
        "code_snippet": None,
        "options": [
            "O(1)",
            "O(n)",
            "O(log n)",
            "O(n^2)"
        ],
        "correct_option_index": 0,
        "explanation": "While occasional buffer resizing requires copying all n elements in O(n) time, geometric capacity doubling (1.5x or 2x) distributes this cost over many insertions, resulting in an amortized O(1) time per append."
    },
    {
        "difficulty": "basic",
        "topic": "Linked Lists",
        "prompt_text": "What is the primary advantage of a singly linked list over a contiguous array?",
        "code_snippet": None,
        "options": [
            "Constant-time random element access by index (O(1)).",
            "Constant-time insertion or deletion at the head (beginning) without shifting subsequent elements (O(1)).",
            "Significantly lower memory usage per element.",
            "Superior CPU L1 cache locality."
        ],
        "correct_option_index": 1,
        "explanation": "Prepending to a linked list simply updates pointer references in O(1) time. In contrast, prepending to an array requires shifting all n existing elements in O(n) time."
    },
    {
        "difficulty": "basic",
        "topic": "Stacks: LIFO Mechanics",
        "prompt_text": "Which data structure follows the Last-In, First-Out (LIFO) access discipline and is standard for matching balanced parentheses?",
        "code_snippet": None,
        "options": [
            "Queue",
            "Stack",
            "Heap",
            "Hash Table"
        ],
        "correct_option_index": 1,
        "explanation": "A Stack operates on LIFO order: the most recently pushed opening parenthesis is the first to be popped and verified when a closing parenthesis is encountered."
    },
    {
        "difficulty": "basic",
        "topic": "Queues: FIFO Mechanics",
        "prompt_text": "In a standard FIFO (First-In, First-Out) queue, where are elements inserted and removed?",
        "code_snippet": None,
        "options": [
            "Inserted at the head (front), removed from the tail (rear).",
            "Inserted at the rear (tail), removed from the front (head).",
            "Inserted and removed from the exact same end.",
            "Inserted at random positions."
        ],
        "correct_option_index": 1,
        "explanation": "A queue enqueues new elements at the back (rear/tail) and dequeues elements from the front (head), preserving arrival order (FIFO)."
    },
    {
        "difficulty": "basic",
        "topic": "Hash Tables & Collisions",
        "prompt_text": "What is the average-case lookup and insertion time complexity for a key in a well-distributed hash table?",
        "code_snippet": None,
        "options": [
            "O(1)",
            "O(log n)",
            "O(n)",
            "O(n log n)"
        ],
        "correct_option_index": 0,
        "explanation": "A well-distributed hash table maps keys to bucket indices via a hash function, achieving O(1) average-case time complexity for lookups, insertions, and deletions."
    },
    {
        "difficulty": "basic",
        "topic": "Binary Search Tree Traversals",
        "prompt_text": "Which tree traversal order visits the nodes of a Binary Search Tree (BST) in strictly non-decreasing sorted order?",
        "code_snippet": None,
        "options": [
            "Pre-order (Root, Left, Right)",
            "In-order (Left, Root, Right)",
            "Post-order (Left, Right, Root)",
            "Level-order (Breadth-First)"
        ],
        "correct_option_index": 1,
        "explanation": "In-order traversal visits the left subtree, then the root node, then the right subtree. Because a BST satisfies Left < Root < Right, in-order traversal outputs values in ascending sorted order."
    },
    {
        "difficulty": "basic",
        "topic": "Basic Sorting Algorithms",
        "prompt_text": "What is the worst-case time complexity of Selection Sort on an array of size n?",
        "code_snippet": None,
        "options": [
            "O(n)",
            "O(n log n)",
            "O(n^2)",
            "O(2^n)"
        ],
        "correct_option_index": 2,
        "explanation": "Selection Sort repeatedly scans the remaining unsorted subarray to find the minimum element, performing (n-1) + (n-2) + ... + 1 comparisons, resulting in O(n^2) time regardless of initial array ordering."
    },
    {
        "difficulty": "basic",
        "topic": "Recursion & Base Cases",
        "prompt_text": "What happens if a recursive algorithm fails to define or reach a valid base case?",
        "code_snippet": "def recurse(n):\n    return recurse(n + 1)",
        "options": [
            "The function returns 0 immediately.",
            "The program enters infinite recursion until the call stack exceeds its limit, raising a Stack Overflow error.",
            "The runtime automatically converts the function into an iterative while loop.",
            "The compiler optimizes the function out of the program."
        ],
        "correct_option_index": 1,
        "explanation": "Every recursive call allocates a new stack frame on the call stack. Without a terminating base case, stack frames accumulate indefinitely until memory is exhausted, causing a Stack Overflow exception."
    },
    {
        "difficulty": "basic",
        "topic": "Space Complexity Analysis",
        "prompt_text": "What is the auxiliary space complexity of an in-place array reversal algorithm?",
        "code_snippet": "void reverse(int arr[], int n) {\n    int l = 0, r = n - 1;\n    while (l < r) {\n        swap(arr[l++], arr[r--]);\n    }\n}",
        "options": [
            "O(1)",
            "O(n)",
            "O(log n)",
            "O(n^2)"
        ],
        "correct_option_index": 0,
        "explanation": "The algorithm swaps elements within the existing array using only two pointer index variables (`l` and `r`), requiring O(1) auxiliary (extra) memory."
    },

    # ─── INTERMEDIATE (10 Questions) ────────────────────────────────────
    {
        "difficulty": "intermediate",
        "topic": "Divide & Conquer: Merge Sort",
        "prompt_text": "What are the time and auxiliary space complexities of standard Merge Sort on an array of length n?",
        "code_snippet": None,
        "options": [
            "Time: O(n log n); Auxiliary Space: O(1)",
            "Time: O(n log n); Auxiliary Space: O(n)",
            "Time: O(n^2); Auxiliary Space: O(log n)",
            "Time: O(n); Auxiliary Space: O(n)"
        ],
        "correct_option_index": 1,
        "explanation": "Merge Sort recursively divides the array in O(log n) levels and performs linear O(n) merges at each level, guaranteeing O(n log n) time in all cases. Merging arrays requires O(n) auxiliary buffer space."
    },
    {
        "difficulty": "intermediate",
        "topic": "Quick Sort & Pivot Partitioning",
        "prompt_text": "Under what circumstance does Quick Sort degrade to its worst-case time complexity of O(n^2)?",
        "code_snippet": None,
        "options": [
            "When elements are uniformly distributed across powers of two.",
            "When the chosen pivot is consistently the minimum or maximum element (e.g. naive pivot selection on an already sorted or reverse-sorted array).",
            "When the array contains duplicate keys.",
            "When Quick Sort is compiled on a 64-bit architecture."
        ],
        "correct_option_index": 1,
        "explanation": "If the pivot consistently splits the array into sizes 0 and n-1 (as occurs with naive first/last element pivots on sorted arrays), recursion depth becomes n rather than log n, resulting in O(n^2) operations."
    },
    {
        "difficulty": "intermediate",
        "topic": "Binary Heaps & Priority Queues",
        "prompt_text": "What is the time complexity to build a binary heap from an unsorted array of n elements using the bottom-up Floyd's buildHeap algorithm?",
        "code_snippet": None,
        "options": [
            "O(n log n)",
            "O(n)",
            "O(log n)",
            "O(n^2)"
        ],
        "correct_option_index": 1,
        "explanation": "While inserting n elements individually takes O(n log n), bottom-up `buildHeap` sifts down from the lowest internal nodes. Summing the geometric series `(n/2^h) * h` over tree height evaluates mathematically to O(n) linear time."
    },
    {
        "difficulty": "intermediate",
        "topic": "Graph Representations: Matrix vs List",
        "prompt_text": "For a sparse graph with V vertices and E edges where E << V^2, why is an Adjacency List preferred over an Adjacency Matrix?",
        "code_snippet": None,
        "options": [
            "An Adjacency Matrix cannot store directed edges.",
            "An Adjacency List consumes O(V + E) memory, whereas an Adjacency Matrix always consumes O(V^2) memory regardless of edge density.",
            "Adjacency Lists allow O(1) checks for edge existence between arbitrary pairs of vertices.",
            "Adjacency Matrices cannot represent negative weights."
        ],
        "correct_option_index": 1,
        "explanation": "An adjacency matrix allocates a V x V grid consuming O(V^2) space, which is wasteful when E is small. An adjacency list stores only actual edges, consuming O(V + E) space and allowing faster neighbor iterations."
    },
    {
        "difficulty": "intermediate",
        "topic": "Breadth-First Search (BFS)",
        "prompt_text": "Why does Breadth-First Search (BFS) guarantee finding the shortest path from a start vertex to a target vertex in an unweighted graph?",
        "code_snippet": None,
        "options": [
            "Because BFS uses a priority queue with heuristic weights.",
            "Because BFS explores vertices in strictly increasing order of their distance (edge count) from the source node using a FIFO queue.",
            "Because BFS visits nodes in reverse topological order.",
            "Because BFS sorts edge weights before traversing."
        ],
        "correct_option_index": 1,
        "explanation": "BFS expands radially level-by-level using a queue. All nodes at distance d are visited before any node at distance d+1, guaranteeing that the first time the target node is visited, it is along the path with fewest edges."
    },
    {
        "difficulty": "intermediate",
        "topic": "Two-Pointer Technique & Sliding Window",
        "prompt_text": "What is the time complexity of finding the maximum sum of any contiguous subarray of size k in an array of size n using a sliding window?",
        "code_snippet": None,
        "options": [
            "O(n * k)",
            "O(n)",
            "O(n log n)",
            "O(k^2)"
        ],
        "correct_option_index": 1,
        "explanation": "By subtracting the element exiting the left of the window and adding the element entering the right on each step, the window sum is updated in O(1) time per element, achieving linear O(n) total time."
    },
    {
        "difficulty": "intermediate",
        "topic": "Dynamic Programming: Memoization vs Tabulation",
        "prompt_text": "What distinguishes Top-Down Dynamic Programming (Memoization) from Bottom-Up Dynamic Programming (Tabulation)?",
        "code_snippet": None,
        "options": [
            "Memoization only works on graphs; tabulation only works on strings.",
            "Memoization uses recursion and caches subproblem solutions on-demand as they are encountered; tabulation solves subproblems iteratively starting from base cases, populating a table systematically.",
            "Tabulation requires exponential time.",
            "Memoization cannot eliminate overlapping subproblems."
        ],
        "correct_option_index": 1,
        "explanation": "Top-down memoization maintains recursive structure while caching results in a map/array to avoid redundant work. Bottom-up tabulation starts with the smallest subproblems and builds answers iteratively without recursion stack overhead."
    },
    {
        "difficulty": "intermediate",
        "topic": "Balanced Search Trees (AVL vs Red-Black)",
        "prompt_text": "What invariant must hold for every node in an AVL tree to remain balanced?",
        "code_snippet": None,
        "options": [
            "The number of left children must equal the number of right children.",
            "The height difference (balance factor) between the left and right subtrees of any node cannot exceed 1 (|balance factor| <= 1).",
            "Every leaf node must be colored black.",
            "The root node must always contain the median value."
        ],
        "correct_option_index": 1,
        "explanation": "In an AVL tree, the balance factor of every node (height(left) - height(right)) must be in {-1, 0, 1}. If an insertion or deletion violates this balance condition, tree rotations (LL, RR, LR, RL) restore balance."
    },
    {
        "difficulty": "intermediate",
        "topic": "Backtracking & State Restoration",
        "prompt_text": "In backtracking algorithms (e.g., solving N-Queens or Sudoku), why is state restoration (reverting changes) essential?",
        "code_snippet": "path.append(choice);\nbacktrack(state);\npath.pop(); // State restoration",
        "options": [
            "To prevent Python garbage collection from terminating the program.",
            "Because exploration branches share state variables; reverting changes restores the exact environment for alternative exploration branches at the same depth.",
            "To sort the solutions in ascending order.",
            "State restoration is an optional debugging convention."
        ],
        "correct_option_index": 1,
        "explanation": "Backtracking explores candidate decision trees depth-first. When a path reaches a dead end or completes, undoing the state alteration (popping the choice) restores the shared accumulator to allow exploring sibling branches cleanly."
    },
    {
        "difficulty": "intermediate",
        "topic": "Linked Lists: Fast & Slow Pointers",
        "prompt_text": "How does Floyd's Cycle Detection Algorithm (Tortoise and Hare) detect a loop in a singly linked list in O(n) time and O(1) space?",
        "code_snippet": None,
        "options": [
            "By hashing the memory addresses of all visited nodes in a hash set.",
            "By advancing a slow pointer by 1 step and a fast pointer by 2 steps; if a cycle exists, the fast pointer will inevitably lap and intersect the slow pointer inside the loop.",
            "By reversing the linked list and comparing endpoints.",
            "By counting node elements until integer overflow."
        ],
        "correct_option_index": 1,
        "explanation": "Floyd's algorithm advances `slow` by 1 node and `fast` by 2 nodes. If a cycle exists, the relative distance between them decreases by 1 on each step, guaranteeing they collide in at most O(n) steps without extra memory."
    },

    # ─── ADVANCED (10 Questions) ─────────────────────────────────────────
    {
        "difficulty": "advanced",
        "topic": "Shortest Paths: Dijkstra vs Bellman-Ford",
        "prompt_text": "Why does Dijkstra's algorithm fail to guarantee correct shortest paths when a graph contains negative-weight edges?",
        "code_snippet": None,
        "options": [
            "Dijkstra requires undirected graphs only.",
            "Dijkstra greedily assumes that once a vertex is extracted from the priority queue, its shortest distance is finalized and cannot be decreased by future paths through negative edges.",
            "Priority queues cannot store negative numbers.",
            "Dijkstra's algorithm experiences an arithmetic division-by-zero error on negative numbers."
        ],
        "correct_option_index": 1,
        "explanation": "Dijkstra relies on the greedy invariant that adding non-negative edges can only increase path weight. With negative edges, an already finalized node could be reached later via a lower-weight path. Bellman-Ford or SPFA must be used instead."
    },
    {
        "difficulty": "advanced",
        "topic": "Disjoint Set Union (DSU / Union-Find)",
        "prompt_text": "With both Path Compression and Union by Rank/Size optimizations, what is the amortized time complexity of Union-Find operations?",
        "code_snippet": None,
        "options": [
            "O(log n)",
            "O(1) strictly",
            "O(α(n)), where α is the extremely slow-growing inverse Ackermann function (effectively <= 4 for all practical universe inputs)",
            "O(n)"
        ],
        "correct_option_index": 2,
        "explanation": "Combining path compression (flattening tree depths during find) and union by rank yields an amortized complexity of O(α(n)) per operation, where α(n) is the inverse Ackermann function, which is bounded by 4 for any practical input size."
    },
    {
        "difficulty": "advanced",
        "topic": "Topological Sort & Kahn's Algorithm",
        "prompt_text": "How does Kahn's algorithm for topological sorting detect the presence of a cycle in a directed graph?",
        "code_snippet": None,
        "options": [
            "By measuring recursion stack memory.",
            "It tracks the in-degree of all vertices. If the count of processed vertices in the topological output is less than the total vertex count V, a cycle exists.",
            "By checking if the adjacency matrix is symmetric.",
            "By computing the determinant of the graph matrix."
        ],
        "correct_option_index": 1,
        "explanation": "Kahn's algorithm repeatedly removes vertices with in-degree 0. Vertices trapped in a directed cycle never reach in-degree 0 and are never enqueued. If processed vertices < V, the graph contains at least one cycle."
    },
    {
        "difficulty": "advanced",
        "topic": "Segment Trees & Range Queries",
        "prompt_text": "What is the time complexity of a Range Minimum Query (RMQ) and a single element update in a Segment Tree of size n?",
        "code_snippet": None,
        "options": [
            "Query: O(1); Update: O(n)",
            "Query: O(log n); Update: O(log n)",
            "Query: O(n); Update: O(1)",
            "Query: O(log n); Update: O(1)"
        ],
        "correct_option_index": 1,
        "explanation": "A Segment Tree organizes array intervals hierarchically. Querying an arbitrary range decomposes into at most 2 log n canonical sub-segments in O(log n) time, and updating a leaf propagates up the tree height in O(log n) time."
    },
    {
        "difficulty": "advanced",
        "topic": "Trie (Prefix Tree) Complexity",
        "prompt_text": "What is the time complexity of searching for a word of length L in a Trie containing N words?",
        "code_snippet": None,
        "options": [
            "O(N * L)",
            "O(L)",
            "O(log N)",
            "O(N + L)"
        ],
        "correct_option_index": 1,
        "explanation": "In a Trie, traversing each character of the target word takes O(1) pointer transition operations. The search time depends strictly on the word length L, O(L), independent of the total number of words N stored in the tree."
    },
    {
        "difficulty": "advanced",
        "topic": "String Matching: KMP Algorithm",
        "prompt_text": "What is the role of the Pi (LPS - Longest Proper Prefix that is also Suffix) table in the Knuth-Morris-Pratt (KMP) string matching algorithm?",
        "code_snippet": None,
        "options": [
            "It encrypts the search pattern before scanning.",
            "It allows the algorithm to skip redundant character comparisons in the text upon mismatch by shifting the pattern to the length of the longest matching proper prefix/suffix in O(1) time.",
            "It converts the text into a binary Trie.",
            "It hashes 4-byte string chunks using MD5."
        ],
        "correct_option_index": 1,
        "explanation": "The KMP prefix function (LPS table) precomputes the length of the longest proper prefix that matches a suffix within pattern prefixes. On mismatch, this allows jumping the pattern index forward without ever backtracking the text pointer, achieving linear O(N + M) time."
    },
    {
        "difficulty": "advanced",
        "topic": "Dynamic Programming: 0/1 Knapsack Space Optimization",
        "prompt_text": "When optimizing the 0/1 Knapsack DP table from 2D (items x capacity) to a 1D array of size W (capacity), why MUST the capacity loop iterate in reverse (from W down to weight[i])?",
        "code_snippet": "for i in range(n):\n    for w in range(W, weights[i] - 1, -1):\n        dp[w] = max(dp[w], dp[w - weights[i]] + values[i])",
        "options": [
            "To prevent accessing negative array indices.",
            "To ensure that values from the current item are not reused multiple times in the same iteration (which would erroneously model the Unbounded Knapsack problem).",
            "Because CPU hardware prefers backwards memory prefetching.",
            "To sort items by value-to-weight ratio."
        ],
        "correct_option_index": 1,
        "explanation": "In 0/1 Knapsack, an item can be selected at most once. Iterating backwards ensures `dp[w - weights[i]]` represents the state from the PREVIOUS item iteration, preventing an item from contributing to its own capacity updates multiple times."
    },
    {
        "difficulty": "advanced",
        "topic": "Graph Algorithms: Tarjan's SCC & Bridges",
        "prompt_text": "In depth-first search of an undirected graph, what condition indicates that an edge (u, v) is a bridge (critical connection)?",
        "code_snippet": None,
        "options": [
            "v was already visited before u.",
            "low[v] > disc[u] (no vertex in v's DFS subtree has a back-edge to u or any of u's ancestors).",
            "degree(u) == 1 and degree(v) == 1.",
            "u and v share the same color in 2-coloring."
        ],
        "correct_option_index": 1,
        "explanation": "In Tarjan's bridge-finding algorithm, `disc[u]` is discovery time and `low[v]` is the lowest discovery time reachable from v via back-edges. If `low[v] > disc[u]`, no back-edge exists from v's subtree to u or higher, meaning removing (u, v) disconnects the graph."
    },
    {
        "difficulty": "advanced",
        "topic": "Bit Manipulation: Brian Kernighan's Algorithm",
        "prompt_text": "What does the bitwise operation `n = n & (n - 1)` accomplish in constant time?",
        "code_snippet": "while n > 0:\n    n = n & (n - 1)\n    count += 1",
        "options": [
            "It checks whether n is an odd number.",
            "It clears (unsets) the lowest set bit (rightmost 1-bit) of n.",
            "It reverses the bits of n.",
            "It multiplies n by 2."
        ],
        "correct_option_index": 1,
        "explanation": "Subtracting 1 from n flips all bits up to and including the rightmost set bit. Performing bitwise AND with the original n zeroes out that lowest set bit, allowing popcount in iterations equal strictly to the number of set bits."
    },
    {
        "difficulty": "advanced",
        "topic": "Tree Algorithms: Lowest Common Ancestor (LCA)",
        "prompt_text": "What algorithm achieves O(log N) query time for finding the Lowest Common Ancestor (LCA) of two tree nodes after O(N log N) preprocessing?",
        "code_snippet": None,
        "options": [
            "Dijkstra's shortest path algorithm.",
            "Binary Lifting (precomputing 2^k-th ancestors for each node up to log N).",
            "Floyd-Warshall all-pairs shortest path.",
            "Kruskal's algorithm."
        ],
        "correct_option_index": 1,
        "explanation": "Binary Lifting precomputes an ancestor table `up[node][k]` storing the 2^k-th ancestor of each node in O(N log N) time and space. LCA queries then lift nodes in powers of 2 to match depths and locate the common ancestor in O(log N) time."
    }
]
