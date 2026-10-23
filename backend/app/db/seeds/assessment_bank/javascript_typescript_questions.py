"""
JavaScript & TypeScript Question Bank.
Contains 30 verified questions (10 basic, 10 intermediate, 10 advanced).
"""

JAVASCRIPT_TYPESCRIPT_QUESTIONS = [
    # ─── BASIC (10 Questions) ───────────────────────────────────────────
    {
        "difficulty": "basic",
        "topic": "Variables & Scoping",
        "prompt_text": "What happens when you access a variable declared with 'let' before its declaration in the source code?",
        "code_snippet": "console.log(value);\nlet value = 42;",
        "options": [
            "It outputs 'undefined' due to variable hoisting.",
            "A ReferenceError is thrown due to the Temporal Dead Zone (TDZ).",
            "It outputs 'null'.",
            "The program compiles but silently ignores the statement."
        ],
        "correct_option_index": 1,
        "explanation": "While 'let' and 'const' declarations are hoisted, they remain uninitialized in the Temporal Dead Zone (TDZ) from the beginning of the block until the declaration is reached. Accessing them throws a ReferenceError."
    },
    {
        "difficulty": "basic",
        "topic": "Types & Coercion",
        "prompt_text": "What does the expression typeof null evaluate to in JavaScript?",
        "code_snippet": "console.log(typeof null);",
        "options": [
            "\"null\"",
            "\"undefined\"",
            "\"object\"",
            "\"boolean\""
        ],
        "correct_option_index": 2,
        "explanation": "In JavaScript, typeof null evaluates to 'object'. This is a historical bug in the original 1995 JS implementation where values were represented with a type tag and null shared the 000 object tag."
    },
    {
        "difficulty": "basic",
        "topic": "Equality Operators",
        "prompt_text": "Which of the following comparisons evaluates to true in JavaScript?",
        "code_snippet": None,
        "options": [
            "\"0\" === 0",
            "null === undefined",
            "false == \"0\"",
            "NaN === NaN"
        ],
        "correct_option_index": 2,
        "explanation": "With loose equality (==), type coercion occurs. The boolean false is coerced to 0, and string \"0\" is coerced to 0, so 0 == 0 evaluates to true. Strict equality (===) checks both value and type without coercion, and NaN is never equal to anything, including itself."
    },
    {
        "difficulty": "basic",
        "topic": "Functions & Arrow Syntax",
        "prompt_text": "How does an arrow function handle the 'this' keyword compared to a standard function declaration?",
        "code_snippet": "const obj = {\n  count: 10,\n  getCount: () => this.count\n};",
        "options": [
            "Arrow functions bind 'this' dynamically to the caller object at invocation time.",
            "Arrow functions do not have their own 'this'; they lexically capture 'this' from their enclosing scope.",
            "Arrow functions automatically bind 'this' to the global window/globalThis object only.",
            "Arrow functions throw a TypeError if 'this' is referenced inside them."
        ],
        "correct_option_index": 1,
        "explanation": "Arrow functions lack their own 'this' binding, arguments object, and super. They inherit 'this' lexically from the scope in which they were defined."
    },
    {
        "difficulty": "basic",
        "topic": "Arrays & Functional Methods",
        "prompt_text": "Which Array method creates a new array with all elements that pass a test implemented by the provided function?",
        "code_snippet": None,
        "options": [
            "Array.prototype.map()",
            "Array.prototype.forEach()",
            "Array.prototype.filter()",
            "Array.prototype.reduce()"
        ],
        "correct_option_index": 2,
        "explanation": "filter() iterates over the array and constructs a new array containing all elements for which the predicate callback returns a truthy value."
    },
    {
        "difficulty": "basic",
        "topic": "Destructuring Assignment",
        "prompt_text": "What will be printed by the following object destructuring code?",
        "code_snippet": "const user = { name: \"Alex\", age: 25 };\nconst { name, role = \"Candidate\" } = user;\nconsole.log(`${name} is a ${role}`);",
        "options": [
            "Alex is a undefined",
            "Alex is a Candidate",
            "undefined is a Candidate",
            "SyntaxError: default values not supported in destructuring"
        ],
        "correct_option_index": 1,
        "explanation": "Destructuring supports default fallback values when the unpacked property is undefined. Since 'role' is absent in user, the default 'Candidate' is assigned."
    },
    {
        "difficulty": "basic",
        "topic": "Spread & Rest Operators",
        "prompt_text": "What is the result of using the spread operator to clone an object with nested properties?",
        "code_snippet": "const original = { a: 1, b: { c: 2 } };\nconst copy = { ...original };\ncopy.b.c = 99;",
        "options": [
            "original.b.c remains 2 because spread performs a deep recursive copy.",
            "original.b.c becomes 99 because spread creates a shallow copy sharing nested references.",
            "A TypeError is thrown because objects cannot be spread without Object.assign().",
            "The property copy.b is frozen and cannot be mutated."
        ],
        "correct_option_index": 1,
        "explanation": "Object and array spread syntax performs a shallow copy. Top-level primitive properties are copied by value, but nested object references are copied by reference."
    },
    {
        "difficulty": "basic",
        "topic": "Promises",
        "prompt_text": "In what order are the console logs printed in this asynchronous code snippet?",
        "code_snippet": "console.log(\"1\");\nPromise.resolve().then(() => console.log(\"2\"));\nconsole.log(\"3\");",
        "options": [
            "1, 2, 3",
            "2, 1, 3",
            "1, 3, 2",
            "3, 1, 2"
        ],
        "correct_option_index": 2,
        "explanation": "Synchronous code runs to completion on the call stack first (\"1\", then \"3\"). Promise callbacks are enqueued in the microtask queue and run immediately after the synchronous stack empties (\"2\")."
    },
    {
        "difficulty": "basic",
        "topic": "TypeScript: Basic Types",
        "prompt_text": "In TypeScript, what is the fundamental difference between the types 'any' and 'unknown'?",
        "code_snippet": None,
        "options": [
            "'unknown' disables all type checking just like 'any'.",
            "'any' disables type checking completely, whereas 'unknown' is type-safe: you must perform type narrowing before operating on an unknown value.",
            "'unknown' can only represent null and undefined.",
            "'any' is only available in JavaScript, not TypeScript."
        ],
        "correct_option_index": 1,
        "explanation": "'unknown' is the type-safe counterpart of 'any'. Anything is assignable to 'unknown', but an 'unknown' value cannot be assigned to another type or have its methods called without explicit type assertion or narrowing."
    },
    {
        "difficulty": "basic",
        "topic": "DOM & Event Bubbling",
        "prompt_text": "During standard DOM event dispatch, what is event bubbling?",
        "code_snippet": None,
        "options": [
            "The event travels downwards from Window through ancestors to the target element.",
            "The event bubbles upwards from the target element through its ancestor tree to the document root.",
            "The event fires simultaneously on all sibling nodes in parallel.",
            "The browser reloads the DOM subtree when the user clicks."
        ],
        "correct_option_index": 1,
        "explanation": "In DOM event propagation, the event starts in the capture phase (top down), hits the target phase, and then enters the bubbling phase, propagating upwards from the event target to document ancestors."
    },

    # ─── INTERMEDIATE (10 Questions) ────────────────────────────────────
    {
        "difficulty": "intermediate",
        "topic": "Closures & Lexical Scope",
        "prompt_text": "What will be printed when the following code with closures is executed?",
        "code_snippet": "function createCounter() {\n  let count = 0;\n  return {\n    increment: () => ++count,\n    get: () => count\n  };\n}\nconst c1 = createCounter();\nconst c2 = createCounter();\nc1.increment();\nc1.increment();\nconsole.log(c1.get(), c2.get());",
        "options": [
            "2 2",
            "2 0",
            "0 2",
            "NaN undefined"
        ],
        "correct_option_index": 1,
        "explanation": "Each invocation of createCounter creates a distinct lexical environment with its own private 'count' variable closed over by the returned methods. Mutating c1 has zero impact on c2."
    },
    {
        "difficulty": "intermediate",
        "topic": "Prototypes & Inheritance",
        "prompt_text": "What happens when you look up a property on a JavaScript object that does not exist directly on that instance?",
        "code_snippet": None,
        "options": [
            "The runtime immediately throws an UnresolvedPropertyError.",
            "The JavaScript engine traverses up the prototype chain (__proto__) until the property is found or null is reached.",
            "The engine dynamically queries the global window/globalThis scope for a variable with that name.",
            "The property is automatically created with value undefined on the instance."
        ],
        "correct_option_index": 1,
        "explanation": "Property lookup follows the prototype chain. If the property is not found on the instance, the engine checks its prototype (obj.__proto__), and continues up until null (Object.prototype.__proto__) is reached."
    },
    {
        "difficulty": "intermediate",
        "topic": "Event Loop & Task Queues",
        "prompt_text": "What is the output sequence of this code combining setTimeout and Promise?",
        "code_snippet": "setTimeout(() => console.log(\"timeout\"), 0);\nPromise.resolve().then(() => console.log(\"promise\"));\nconsole.log(\"sync\");",
        "options": [
            "sync, timeout, promise",
            "sync, promise, timeout",
            "promise, sync, timeout",
            "timeout, sync, promise"
        ],
        "correct_option_index": 1,
        "explanation": "1. Synchronous code logs 'sync'. 2. Microtask queue (Promise.then) is processed before macrotasks, logging 'promise'. 3. Macrotask queue (setTimeout timer callback) is processed on the next turn, logging 'timeout'."
    },
    {
        "difficulty": "intermediate",
        "topic": "TypeScript: Interfaces vs Type Aliases",
        "prompt_text": "Which capability is uniquely supported by TypeScript 'interface' declarations but NOT by 'type' aliases?",
        "code_snippet": None,
        "options": [
            "Union types",
            "Declaration merging (re-opening the same interface in the same scope to add fields)",
            "Extending with generic type parameters",
            "Intersection with other types"
        ],
        "correct_option_index": 1,
        "explanation": "Interfaces in TypeScript support declaration merging: defining the same interface name multiple times automatically merges all member definitions into a single interface. Type aliases cannot be re-opened."
    },
    {
        "difficulty": "intermediate",
        "topic": "TypeScript: Type Narrowing & Guards",
        "prompt_text": "What does a custom user-defined type guard return in TypeScript?",
        "code_snippet": "function isFish(pet: Fish | Bird): pet is Fish {\n  return (pet as Fish).swim !== undefined;\n}",
        "options": [
            "A boolean with a type predicate in the form of 'paramName is Type'",
            "A cloned instance of the validated type",
            "A void value that throws an assertion error if false",
            "A Promise resolving to true or false"
        ],
        "correct_option_index": 0,
        "explanation": "User-defined type guards return a boolean, but their return type is declared with a type predicate (`arg is Type`). When the function returns true, TypeScript automatically narrows the variable to that type in conditional branches."
    },
    {
        "difficulty": "intermediate",
        "topic": "TypeScript: Generics",
        "prompt_text": "In the following generic function signature, what does `<T extends { length: number }>` enforce?",
        "code_snippet": "function logLength<T extends { length: number }>(arg: T): number {\n  return arg.length;\n}",
        "options": [
            "T must be an Array of numbers.",
            "T can be any type as long as it has a numeric 'length' property (e.g., string, array).",
            "T is converted into a number primitive.",
            "T must be a class extending the built-in Length class."
        ],
        "correct_option_index": 1,
        "explanation": "This generic constraint specifies that any type passed to T must structurally possess a property named 'length' of type number. Strings, arrays, and custom objects with a length property are valid."
    },
    {
        "difficulty": "intermediate",
        "topic": "TypeScript: Discriminated Unions",
        "prompt_text": "What makes a TypeScript union a 'discriminated union' (or tagged union)?",
        "code_snippet": "type Success = { status: 'success'; data: string };\ntype Error = { status: 'error'; message: string };\ntype ApiResponse = Success | Error;",
        "options": [
            "The presence of a common literal property (the discriminator, like 'status') in every member of the union.",
            "Using the 'enum' keyword inside the interface.",
            "Marking the union with the 'strict' compiler flag.",
            "Exporting the union across multiple files."
        ],
        "correct_option_index": 0,
        "explanation": "A discriminated union requires every variant to have a common property with a distinct singleton literal type (such as string literal 'success' vs 'error'). TypeScript uses this property to exhaustively narrow types in switch/if statements."
    },
    {
        "difficulty": "intermediate",
        "topic": "Event Handling: preventDefault vs stopPropagation",
        "prompt_text": "What is the difference between event.preventDefault() and event.stopPropagation()?",
        "code_snippet": None,
        "options": [
            "preventDefault() stops bubbling; stopPropagation() cancels the default browser action.",
            "preventDefault() cancels the default browser behavior (e.g. form submit or link navigation); stopPropagation() prevents the event from bubbling up the DOM tree.",
            "They are completely synonymous in modern browsers.",
            "stopPropagation() destroys the event object in memory."
        ],
        "correct_option_index": 1,
        "explanation": "preventDefault() inhibits the browser's default native action for the event (such as submitting a form or navigating an anchor tag). stopPropagation() halts further dispatch of the event up the DOM tree."
    },
    {
        "difficulty": "intermediate",
        "topic": "TypeScript: Utility Types",
        "prompt_text": "What does the TypeScript built-in utility type Partial<T> produce?",
        "code_snippet": "interface User { id: string; email: string; }\ntype PartialUser = Partial<User>;",
        "options": [
            "A type where all properties of T are removed.",
            "A type where all properties of T are made optional (?)",
            "A type where all properties of T are made read-only.",
            "A type containing only the first half of T's properties."
        ],
        "correct_option_index": 1,
        "explanation": "Partial<T> is a mapped type defined as `{ [P in keyof T]?: T[P] }`, making every property in T optional."
    },
    {
        "difficulty": "intermediate",
        "topic": "TypeScript: Const Assertions",
        "prompt_text": "What effect does appending 'as const' have on the following object literal in TypeScript?",
        "code_snippet": "const config = {\n  endpoint: \"https://api.coachpath.dev\",\n  retries: 3\n} as const;",
        "options": [
            "It turns the object into an immutable JSON string at runtime.",
            "It makes properties readonly and narrows string/number literals to their exact literal types rather than widening to string/number.",
            "It prevents the file from being modified on disk.",
            "It automatically invokes Object.freeze() at JavaScript runtime."
        ],
        "correct_option_index": 1,
        "explanation": "'as const' signals to the TypeScript type checker that no literal types in that expression should be widened, object properties become readonly, and arrays become readonly tuples."
    },

    # ─── ADVANCED (10 Questions) ─────────────────────────────────────────
    {
        "difficulty": "advanced",
        "topic": "Event Loop & Microtask Draining",
        "prompt_text": "What happens if a microtask recursively schedules another microtask via queueMicrotask() or Promise.resolve()?",
        "code_snippet": "function loop() {\n  queueMicrotask(loop);\n}\nloop();",
        "options": [
            "The browser executes them in a worker thread without affecting UI responsiveness.",
            "The microtask queue never drains, starving macrotasks, UI rendering, and user input events, effectively freezing the tab.",
            "The JavaScript engine throws a 'MicrotaskStackOverflowError' after 10,000 iterations.",
            "The runtime automatically throttles recursive microtasks to 4ms intervals."
        ],
        "correct_option_index": 1,
        "explanation": "The event loop specification states that the entire microtask queue must be drained completely before returning control to the rendering steps or the next macrotask. Recursively queueing microtasks starves all rendering and I/O."
    },
    {
        "difficulty": "advanced",
        "topic": "WeakMap & Memory Management",
        "prompt_text": "Why are WeakMap keys restricted strictly to objects (and non-registered symbols in modern JS), and why cannot a WeakMap be enumerated (no .keys() or .size)?",
        "code_snippet": None,
        "options": [
            "Because JavaScript engines use cryptographic hashes that cannot be decrypted for iteration.",
            "WeakMap holds weak references to keys; if keys were enumerable, their presence would depend on non-deterministic garbage collection timing.",
            "WeakMap is stored in the browser's WebStorage API which does not support iteration.",
            "It is an artificial restriction designed to enforce TypeScript compatibility."
        ],
        "correct_option_index": 1,
        "explanation": "WeakMap holds weak references to keys. If keys were iterable, observable program state would depend on when the garbage collector runs, introducing non-deterministic behavior. Only objects have life cycles managed by the GC."
    },
    {
        "difficulty": "advanced",
        "topic": "V8 Optimization & Hidden Classes",
        "prompt_text": "How does V8 optimize property access on JavaScript objects, and how can careless property initialization degrade performance?",
        "code_snippet": "function Point(x, y) {\n  this.x = x;\n  this.y = y;\n}",
        "options": [
            "V8 compiles all objects into C++ binary structs; adding properties dynamically is impossible in V8.",
            "V8 assigns hidden classes (Shapes/Maps) to objects based on the order and names of added properties; adding properties in different orders creates distinct shapes and causes polymorphic/megamorphic inline caches.",
            "V8 converts all objects into raw hash maps with O(1) lookup regardless of instantiation pattern.",
            "V8 only optimizes objects declared with the 'class' keyword, treating function constructors as slow dictionaries."
        ],
        "correct_option_index": 1,
        "explanation": "V8 generates hidden classes (Maps) tracking property offsets in memory. Objects with matching property addition orders share shapes, enabling monomorphic Inline Caches (ICs). Inconsistent initialization branches the shape transition tree, causing polymorphic access."
    },
    {
        "difficulty": "advanced",
        "topic": "Metaprogramming: Proxy & Reflect",
        "prompt_text": "Why is it best practice to delegate default trap operations to the Reflect API inside a Proxy handler?",
        "code_snippet": "const handler = {\n  set(target, prop, value, receiver) {\n    console.log(`Setting ${prop}`);\n    return Reflect.set(target, prop, value, receiver);\n  }\n};",
        "options": [
            "Reflect.set() bypasses strict mode validation.",
            "Reflect methods properly forward the 'receiver' argument, preserving correct 'this' binding for getters/setters in prototypal inheritance chains.",
            "Reflect methods execute synchronously in native assembly without allocations.",
            "Target[prop] = value throws an error if called inside a Proxy."
        ],
        "correct_option_index": 1,
        "explanation": "Reflect methods match Proxy traps 1:1. When setting or getting properties that involve accessors (getters/setters), passing the `receiver` to Reflect ensures that `this` within the accessor correctly points to the Proxy rather than the raw target."
    },
    {
        "difficulty": "advanced",
        "topic": "Generators & Iterables Protocol",
        "prompt_text": "How can a custom object be made directly iterable with the 'for...of' loop in JavaScript?",
        "code_snippet": None,
        "options": [
            "By implementing a method named 'iterator()'.",
            "By implementing the [Symbol.iterator] method that returns an object adhering to the Iterator protocol (with a .next() method).",
            "By extending the Array prototype.",
            "By setting the property __iterable__ = true."
        ],
        "correct_option_index": 1,
        "explanation": "The JavaScript Iteration Protocol specifies that an object is iterable if it defines a method keyed by Symbol.iterator that returns an iterator object with a `next()` method returning `{ value, done }`."
    },
    {
        "difficulty": "advanced",
        "topic": "TypeScript: Conditional Types & Distributivity",
        "prompt_text": "In TypeScript, why does `ToArray<string | number>` evaluate to `string[] | number[]` rather than `(string | number)[]`?",
        "code_snippet": "type ToArray<T> = T extends any ? T[] : never;",
        "options": [
            "It is a syntax error to use naked type parameters in conditionals.",
            "Unchecked conditional types are distributive over naked type parameters in union types.",
            "TypeScript compiler treats arrays of unions as invalid.",
            "The 'extends any' clause collapses unions to intersection types."
        ],
        "correct_option_index": 1,
        "explanation": "When conditional types act on an unconstrained ('naked') type parameter, they distribute over union types: `(A | B) extends T ? X : Y` resolves to `(A extends T ? X : Y) | (B extends T ? X : Y)`. Wrapping `[T]` disables distributivity."
    },
    {
        "difficulty": "advanced",
        "topic": "TypeScript: The 'infer' Keyword",
        "prompt_text": "What does the 'infer' keyword achieve in TypeScript conditional types?",
        "code_snippet": "type UnpackPromise<T> = T extends Promise<infer U> ? U : T;",
        "options": [
            "It instructs TypeScript to automatically infer the runtime return value using LLM analysis.",
            "It introduces a type variable within the 'extends' clause to extract and deduce a constituent subtype from a composite type.",
            "It forces the compiler to ignore type errors in async functions.",
            "It imports types from external TypeScript declaration files."
        ],
        "correct_option_index": 1,
        "explanation": "The 'infer' keyword allows you to declare a type variable dynamically inside the condition of a conditional type, enabling extraction of internal types (such as the payload inside a Promise or return type of a function)."
    },
    {
        "difficulty": "advanced",
        "topic": "TypeScript: Mapped Types & Key Remapping",
        "prompt_text": "What does the 'as' clause in a TypeScript mapped type allow you to accomplish?",
        "code_snippet": "type Getters<T> = {\n  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K]\n};",
        "options": [
            "Cast the entire type to an external class.",
            "Remap, transform, or filter out keys (via 'never') using template literal types or conditionals.",
            "Enforce that all properties must be asynchronous methods.",
            "Create aliases for JavaScript runtime global variables."
        ],
        "correct_option_index": 1,
        "explanation": "Key remapping with `as` (introduced in TypeScript 4.1) allows transformation of property names in mapped types, including prefixing/suffixing with template literal types and filtering keys out by mapping them to `never`."
    },
    {
        "difficulty": "advanced",
        "topic": "TypeScript: Template Literal Types",
        "prompt_text": "What is the resulting type of EventName in this TypeScript snippet?",
        "code_snippet": "type Entity = \"user\" | \"order\";\ntype Action = \"created\" | \"deleted\";\ntype EventName = `${Entity}_${Action}`;",
        "options": [
            "\"user_order_created_deleted\"",
            "string",
            "\"user_created\" | \"user_deleted\" | \"order_created\" | \"order_deleted\"",
            "Array<string>"
        ],
        "correct_option_index": 2,
        "explanation": "TypeScript template literal types perform a Cartesian product over union types, generating all combinations: 'user_created' | 'user_deleted' | 'order_created' | 'order_deleted'."
    },
    {
        "difficulty": "advanced",
        "topic": "TypeScript: Variance & Strict Function Types",
        "prompt_text": "Under TypeScript's --strictFunctionTypes flag, how do function parameter types behave with respect to subtyping?",
        "code_snippet": None,
        "options": [
            "Function parameters are covariant.",
            "Function parameters are contravariant.",
            "Function parameters are invariant.",
            "Function parameters are bivariant."
        ],
        "correct_option_index": 1,
        "explanation": "Under `--strictFunctionTypes`, method return types are covariant (narrower is allowed), but function parameter types are contravariant (wider is allowed, preventing passing callbacks that expect more specific properties than provided)."
    }
]
