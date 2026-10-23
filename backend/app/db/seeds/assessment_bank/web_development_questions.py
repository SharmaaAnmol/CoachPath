"""
Full-Stack Web Development Question Bank.
Contains 30 verified questions (10 basic, 10 intermediate, 10 advanced).
"""

WEB_DEVELOPMENT_QUESTIONS = [
    # ─── BASIC (10 Questions) ───────────────────────────────────────────
    {
        "difficulty": "basic",
        "topic": "HTTP Protocol & Methods",
        "prompt_text": "Which HTTP method is designed for partial modification of an existing resource and is NOT required to be idempotent?",
        "code_snippet": None,
        "options": [
            "GET",
            "PUT",
            "PATCH",
            "OPTIONS"
        ],
        "correct_option_index": 2,
        "explanation": "PUT is idempotent and replaces the entire resource. PATCH is intended for partial modifications where only specified fields are altered, and is not inherently idempotent."
    },
    {
        "difficulty": "basic",
        "topic": "HTTP Status Codes",
        "prompt_text": "What is the difference between HTTP status code 401 Unauthorized and 403 Forbidden?",
        "code_snippet": None,
        "options": [
            "401 means the server is down; 403 means the URL does not exist.",
            "401 indicates that authentication is required or credentials are invalid; 403 indicates that the user is authenticated but lacks permission to access the requested resource.",
            "401 is returned for GET requests; 403 is returned for POST requests.",
            "They are exact synonyms in the HTTP/1.1 specification."
        ],
        "correct_option_index": 1,
        "explanation": "401 Unauthorized signifies missing or invalid authentication credentials (you are unauthenticated). 403 Forbidden signifies that the server understands your identity, but you do not have permission to access that resource (unauthorized)."
    },
    {
        "difficulty": "basic",
        "topic": "CSS Box Model",
        "prompt_text": "What effect does setting `box-sizing: border-box;` have on element layout in CSS?",
        "code_snippet": "* {\n  box-sizing: border-box;\n}",
        "options": [
            "It removes all borders and margins from the element.",
            "It causes an element's declared width and height to include content, padding, and border (preventing elements from expanding when padding is added).",
            "It turns every element into an inline-block container.",
            "It forces elements to render as 3D boxes."
        ],
        "correct_option_index": 1,
        "explanation": "Under standard `content-box`, padding and borders add to the declared width. With `border-box`, padding and borders are absorbed inside the specified width and height, dramatically simplifying layout calculations."
    },
    {
        "difficulty": "basic",
        "topic": "CSS Flexbox",
        "prompt_text": "In a flex container with `flex-direction: row;`, which CSS property aligns items along the cross axis (vertically)?",
        "code_snippet": ".container {\n  display: flex;\n  flex-direction: row;\n  /* vertical alignment */\n}",
        "options": [
            "justify-content",
            "align-items",
            "flex-grow",
            "align-content"
        ],
        "correct_option_index": 1,
        "explanation": "In a row-oriented flex container, the main axis is horizontal and controlled by `justify-content`. The cross axis is vertical and controlled by `align-items`."
    },
    {
        "difficulty": "basic",
        "topic": "HTML5 Semantic Elements",
        "prompt_text": "Why should semantic HTML elements like `<header>`, `<nav>`, `<main>`, and `<article>` be used instead of generic `<div>` tags?",
        "code_snippet": None,
        "options": [
            "Semantic elements compile to WebAssembly for faster rendering.",
            "They convey meaning and structure to search engine crawlers (SEO) and assistive screen-reading technologies (accessibility / a11y).",
            "Semantic elements are mandatory to connect CSS stylesheets.",
            "div tags are deprecated in modern HTML specifications."
        ],
        "correct_option_index": 1,
        "explanation": "Semantic tags clearly describe their role to both browser and developer. They form accessibility landmarks used by screen readers and assistive devices, and enhance search engine indexing."
    },
    {
        "difficulty": "basic",
        "topic": "Web Storage: Local vs Session vs Cookies",
        "prompt_text": "How does `sessionStorage` differ from `localStorage` in browser Web Storage?",
        "code_snippet": None,
        "options": [
            "sessionStorage is sent with every HTTP header to the server.",
            "sessionStorage data persists only for the lifetime of the specific browser tab/window and is cleared when the tab is closed, whereas localStorage persists indefinitely until cleared.",
            "sessionStorage can store up to 500MB while localStorage stores only 5MB.",
            "sessionStorage is accessible across different browser domains."
        ],
        "correct_option_index": 1,
        "explanation": "Both store key-value strings client-side. `sessionStorage` scope is restricted to the current browser tab and destroyed when the tab closes. `localStorage` persists across sessions until explicitly cleared."
    },
    {
        "difficulty": "basic",
        "topic": "Responsive Design & Viewport",
        "prompt_text": "Why is the `<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">` tag essential in mobile-first web pages?",
        "code_snippet": None,
        "options": [
            "It turns off JavaScript execution on mobile devices to save battery.",
            "It instructs mobile browsers to render the viewport width to the physical screen width at a 1:1 scale rather than simulating a wide 980px desktop viewport.",
            "It forces mobile browsers to install a progressive web app.",
            "It restricts the page to portrait orientation."
        ],
        "correct_option_index": 1,
        "explanation": "Without this viewport meta tag, mobile browsers assume a desktop layout (~980px wide) and scale it down to fit the screen. Setting width to device-width ensures responsive CSS media queries evaluate correctly."
    },
    {
        "difficulty": "basic",
        "topic": "RESTful API Conventions",
        "prompt_text": "According to RESTful design standards, what is the recommended URL pattern and HTTP method to create a new comment on post 42?",
        "code_snippet": None,
        "options": [
            "GET /createComment?postId=42",
            "POST /posts/42/comments",
            "PUT /posts/new_comment",
            "DELETE /comments/42"
        ],
        "correct_option_index": 1,
        "explanation": "REST conventions utilize plural nouns for resource collections and HTTP verbs for actions. Creating a child resource in a sub-collection is expressed via `POST /posts/42/comments`."
    },
    {
        "difficulty": "basic",
        "topic": "CSS Specificity",
        "prompt_text": "Given conflicting CSS rules targeting the same element, which selector has the highest specificity?",
        "code_snippet": "/* Selector A */ button.primary { color: blue; }\n/* Selector B */ #submit-btn { color: red; }\n/* Selector C */ .btn.action.large { color: green; }\n/* Selector D */ div > button { color: yellow; }",
        "options": [
            "Selector A (element + class)",
            "Selector B (ID selector)",
            "Selector C (three classes)",
            "Selector D (element combinator)"
        ],
        "correct_option_index": 1,
        "explanation": "CSS specificity hierarchy is: Inline styles (1,0,0,0) > ID selectors (0,1,0,0) > Class / attribute / pseudo-class (0,0,1,0) > Elements / pseudo-elements (0,0,0,1). A single ID selector (#submit-btn) outweighs any number of classes."
    },
    {
        "difficulty": "basic",
        "topic": "Cookies: HttpOnly Flag",
        "prompt_text": "What security protection is provided by marking a session cookie with the `HttpOnly` flag?",
        "code_snippet": "Set-Cookie: session_id=xyz123; HttpOnly; Secure; SameSite=Strict",
        "options": [
            "It prevents the cookie from being transmitted over HTTPS connections.",
            "It blocks client-side JavaScript (e.g. document.cookie) from reading the cookie, mitigating session hijacking via Cross-Site Scripting (XSS).",
            "It deletes the cookie after 60 seconds.",
            "It encrypts the cookie with the user's password."
        ],
        "correct_option_index": 1,
        "explanation": "The `HttpOnly` directive informs the browser that the cookie should not be accessible through client-side scripts (`document.cookie`), preventing malicious scripts injected via XSS from reading session tokens."
    },

    # ─── INTERMEDIATE (10 Questions) ────────────────────────────────────
    {
        "difficulty": "intermediate",
        "topic": "CORS (Cross-Origin Resource Sharing)",
        "prompt_text": "When does a web browser initiate a CORS preflight request (OPTIONS method) before sending an HTTP request?",
        "code_snippet": None,
        "options": [
            "For all GET requests without exception.",
            "When the request is cross-origin and does not qualify as a 'simple request' (e.g. uses methods like PUT/DELETE, or custom headers like Authorization, or content-type application/json).",
            "Only when the browser is running in incognito mode.",
            "Whenever the response payload exceeds 1MB."
        ],
        "correct_option_index": 1,
        "explanation": "Browsers issue an OPTIONS preflight request when a cross-origin request uses non-simple HTTP methods (PUT, DELETE, PATCH), custom request headers (Authorization), or non-simple Content-Types (application/json) to verify server permissions."
    },
    {
        "difficulty": "intermediate",
        "topic": "Web Security: CSRF Mitigation",
        "prompt_text": "How does setting the cookie attribute `SameSite=Lax` or `SameSite=Strict` defend against Cross-Site Request Forgery (CSRF)?",
        "code_snippet": None,
        "options": [
            "It stops cookies from being sent on cross-site requests initiated by third-party origins (such as malicious forms or image tags on external sites).",
            "It disables cookies in mobile browsers.",
            "It requires the user to enter a CAPTCHA before submitting forms.",
            "It hashes passwords with bcrypt."
        ],
        "correct_option_index": 0,
        "explanation": "CSRF exploits the browser's automatic inclusion of cookies on cross-site requests. `SameSite=Strict` never sends cookies in cross-site contexts; `SameSite=Lax` allows cookies only on top-level safe GET navigations, neutralizing cross-site POST attacks."
    },
    {
        "difficulty": "intermediate",
        "topic": "Web Security: XSS Types",
        "prompt_text": "What is the key mechanism of a Stored (Persistent) Cross-Site Scripting (XSS) vulnerability?",
        "code_snippet": None,
        "options": [
            "An attacker intercepts unencrypted Wi-Fi packets.",
            "Malicious JavaScript input is permanently stored in the application database (e.g. in a comment or profile) and subsequently served unescaped to other users visiting the page.",
            "An attacker forces the user's browser to send a cross-origin POST request.",
            "A memory leak in the browser's JavaScript garbage collector."
        ],
        "correct_option_index": 1,
        "explanation": "Stored XSS occurs when unvalidated, unescaped user input is persisted in a database or file system. Whenever other users request that data, the stored malicious script executes within their browser context."
    },
    {
        "difficulty": "intermediate",
        "topic": "Rendering Paradigms: SSR vs SSG vs SPA",
        "prompt_text": "In modern web frameworks (e.g., Next.js), what is the difference between Server-Side Rendering (SSR) and Static Site Generation (SSG)?",
        "code_snippet": None,
        "options": [
            "SSR compiles pages to native mobile apps; SSG runs only in Node.js.",
            "SSG pre-renders HTML pages at build time and serves them via CDN; SSR dynamically renders HTML on the server for each incoming client request.",
            "SSR disables JavaScript on the client entirely.",
            "SSG cannot fetch data from external APIs."
        ],
        "correct_option_index": 1,
        "explanation": "SSG generates HTML once at compile/build time, making it ideal for content that changes infrequently and can be cached on CDNs. SSR renders fresh HTML on the server upon every incoming user request, ideal for dynamic personalized content."
    },
    {
        "difficulty": "intermediate",
        "topic": "HTTP Caching: ETag & Validation",
        "prompt_text": "How do HTTP ETags (Entity Tags) optimize bandwidth during browser caching?",
        "code_snippet": "GET /api/v1/profile\nIf-None-Match: \"w/33a2f4edd244e1\"",
        "options": [
            "They automatically compress JSON into gzip format.",
            "The browser sends the cached ETag in the `If-None-Match` header; if the resource has not changed, the server responds with status 304 Not Modified and an empty body, avoiding re-transmitting data.",
            "They encrypt the response body on the server.",
            "They permanently store the resource in browser ROM."
        ],
        "correct_option_index": 1,
        "explanation": "An ETag is an opaque token or hash representing a specific version of a resource. When revalidating, the browser sends `If-None-Match: <hash>`. If unchanged, the server returns `304 Not Modified` with no body, saving bandwidth."
    },
    {
        "difficulty": "intermediate",
        "topic": "Real-Time: WebSockets vs SSE",
        "prompt_text": "When is Server-Sent Events (SSE) a more lightweight and appropriate choice than WebSockets?",
        "code_snippet": None,
        "options": [
            "When full-duplex, bidirectional communication (like an online multiplayer game) is required.",
            "When the communication is strictly unidirectional from server to client (like live stock tickers, notification feeds, or LLM token streaming) over standard HTTP with automatic reconnection.",
            "When the client needs to stream binary video files to the server.",
            "SSE is only supported in Internet Explorer 6."
        ],
        "correct_option_index": 1,
        "explanation": "Server-Sent Events (SSE) operates over standard HTTP, provides built-in reconnection and event IDs, and is simpler than WebSockets when communication only flows from server to client (e.g. streaming AI chat responses or live alerts)."
    },
    {
        "difficulty": "intermediate",
        "topic": "Web Performance: Code Splitting",
        "prompt_text": "What is the primary benefit of dynamic imports (`import('./heavyComponent')`) and route-based code splitting in frontend applications?",
        "code_snippet": "const AnalyticsChart = React.lazy(() => import('./AnalyticsChart'));",
        "options": [
            "It decreases the number of lines in the source code.",
            "It breaks large JavaScript bundles into smaller chunks loaded on-demand, significantly reducing initial page load time and improving First Contentful Paint (FCP).",
            "It converts React components into server-side PHP scripts.",
            "It prevents CSS styles from colliding."
        ],
        "correct_option_index": 1,
        "explanation": "Code splitting breaks the single monolithic bundle into smaller chunks. The browser only downloads the minimal JavaScript needed for the current route, deferring heavy components until needed and improving Core Web Vitals."
    },
    {
        "difficulty": "intermediate",
        "topic": "Progressive Web Apps: Service Workers",
        "prompt_text": "Where does a Service Worker execute in the browser architecture?",
        "code_snippet": None,
        "options": [
            "Inside the main UI thread sharing DOM access.",
            "In a separate background worker thread with no direct DOM access, acting as a programmable network proxy intercepting fetch requests.",
            "Directly inside the operating system kernel.",
            "Inside the database server."
        ],
        "correct_option_index": 1,
        "explanation": "Service Workers run on a background thread decoupled from the page and DOM. They act as client-side network proxies, intercepting outgoing network requests to implement offline caching strategies via the Cache API."
    },
    {
        "difficulty": "intermediate",
        "topic": "JWT Architecture & Revocation",
        "prompt_text": "Why is immediate revocation of a stateless JSON Web Token (JWT) challenging before its expiration (exp) timestamp?",
        "code_snippet": None,
        "options": [
            "JWTs cannot be decrypted by servers.",
            "Because stateless JWTs are self-contained and validated cryptographically via signatures; without checking a centralized revocation store (like Redis), any server verifying the signature will consider the token valid until exp.",
            "Browsers automatically renew JWTs without server consent.",
            "JWTs are permanently stored on the blockchain."
        ],
        "correct_option_index": 1,
        "explanation": "A stateless JWT encapsulates user claims and expiration signed by a secret key. Any service verifying the cryptographic signature accepts the token without querying a database. Immediate invalidation requires maintaining a blacklist/revocation list in memory (e.g., Redis)."
    },
    {
        "difficulty": "intermediate",
        "topic": "Content Delivery Networks (CDN)",
        "prompt_text": "How does a Content Delivery Network (CDN) reduce latency for global end users?",
        "code_snippet": None,
        "options": [
            "By increasing the user's home broadband speed.",
            "By caching static assets and terminating TLS connections on geographically distributed edge servers (Points of Presence / PoPs) physically close to end users.",
            "By compiling JavaScript code into native machine code.",
            "By eliminating the need for backend web servers."
        ],
        "correct_option_index": 1,
        "explanation": "CDNs deploy Edge Point of Presence (PoP) servers worldwide. By serving cached static content and terminating TCP/TLS handshakes near the client, physical round-trip time (RTT) and latency are drastically minimized."
    },

    # ─── ADVANCED (10 Questions) ─────────────────────────────────────────
    {
        "difficulty": "advanced",
        "topic": "HTTP Protocols: HTTP/2 vs HTTP/3",
        "prompt_text": "What fundamental network limitation of HTTP/2 did HTTP/3 resolve by replacing TCP with QUIC over UDP?",
        "code_snippet": None,
        "options": [
            "HTTP/2 lacked TLS encryption.",
            "TCP Head-of-Line (HoL) blocking: in HTTP/2, a single dropped packet stalls all multiplexed streams in the single TCP connection; QUIC streams over UDP are independent, so packet loss only affects the single stream that lost the packet.",
            "HTTP/2 could only transmit text, not binary data.",
            "HTTP/2 connections were limited to 10 requests total."
        ],
        "correct_option_index": 1,
        "explanation": "While HTTP/2 multiplexes streams over one TCP connection, TCP guarantees in-order delivery. If a single packet is lost, the entire TCP window halts (TCP Head-of-Line blocking). HTTP/3 uses QUIC over UDP, isolating streams so lost packets only delay their own stream."
    },
    {
        "difficulty": "advanced",
        "topic": "Critical Rendering Path & Reflow",
        "prompt_text": "What is the difference between a 'Reflow' (Layout) and a 'Repaint' in the browser rendering pipeline, and which CSS properties trigger only Compositing?",
        "code_snippet": None,
        "options": [
            "Reflow updates colors; Repaint calculates element geometries.",
            "Reflow recalculates the physical geometry, dimensions, and positions of nodes in the render tree (computationally expensive); Repaint draws pixels to screen; `transform` and `opacity` skip both Reflow and Repaint, executing directly on the GPU Compositor thread.",
            "They are synonymous terms for garbage collection.",
            "Reflow only occurs when an external script fails."
        ],
        "correct_option_index": 1,
        "explanation": "Reflow (Layout) computes element geometries and triggers subsequent repaints. Properties like `width` or `top` trigger reflow. Properties like `color` trigger repaints. `transform` and `opacity` skip layout and paint entirely, animated directly on the GPU compositor thread for 60fps performance."
    },
    {
        "difficulty": "advanced",
        "topic": "OAuth 2.0 & PKCE",
        "prompt_text": "Why is the Authorization Code Flow with PKCE (Proof Key for Code Exchange) mandatory for Single Page Applications (SPAs) and mobile apps rather than the traditional Authorization Code Flow with a client_secret?",
        "code_snippet": None,
        "options": [
            "Because PKCE encrypts data using RSA-4096.",
            "SPAs and mobile apps are public clients that cannot securely store a confidential client_secret without exposing it in decompiled code or browser memory; PKCE dynamically generates a code_verifier and code_challenge to prevent authorization code interception attacks.",
            "PKCE eliminates the need for user login credentials.",
            "Because client_secret is deprecated across all backend servers."
        ],
        "correct_option_index": 1,
        "explanation": "Public clients (SPAs, native mobile apps) run on end-user devices where static secrets cannot be protected. PKCE generates a cryptographic dynamic `code_verifier` and hashed `code_challenge` per authorization flow, ensuring intercepted authorization codes cannot be exchanged without the verifier."
    },
    {
        "difficulty": "advanced",
        "topic": "Web Security: Content Security Policy (CSP)",
        "prompt_text": "How does a modern Nonce-based Content Security Policy (CSP) provide robust protection against Cross-Site Scripting (XSS)?",
        "code_snippet": "Content-Security-Policy: script-src 'nonce-rAnd0m123' 'strict-dynamic';",
        "options": [
            "It disables all external CSS stylesheets.",
            "The server generates a cryptographically random, unpredictable nonce per HTTP response; the browser strictly executes `<script>` tags that carry the matching nonce attribute, blocking any attacker-injected inline script.",
            "It forces all network requests to route through a VPN.",
            "It encrypts DOM nodes using AES."
        ],
        "correct_option_index": 1,
        "explanation": "A nonce-based CSP instructs the browser to execute only scripts bearing the exact, single-use cryptographically random nonce generated by the server for that HTTP request (`<script nonce=\"rAnd0m123\">`). Injected scripts lack this secret nonce and are blocked."
    },
    {
        "difficulty": "advanced",
        "topic": "Core Web Vitals: INP & LCP",
        "prompt_text": "What does the Google Core Web Vital metric 'Interaction to Next Paint' (INP) measure?",
        "code_snippet": None,
        "options": [
            "The time taken to download the initial HTML document.",
            "The overall responsiveness of a page by measuring the latency of all user interactions (clicks, taps, keypresses) throughout the page lifecycle and reporting the worst-case interaction latency.",
            "The speed at which images are rendered by the GPU.",
            "The percentage of pixels that shift position unexpectedly."
        ],
        "correct_option_index": 1,
        "explanation": "INP replaced FID (First Input Delay) as a Core Web Vital. While FID only measured the delay of the very first interaction, INP evaluates page responsiveness by sampling all user clicks, taps, and keypresses, tracking the delay until the browser presents the next visual frame."
    },
    {
        "difficulty": "advanced",
        "topic": "HTTP Caching: Stale-While-Revalidate",
        "prompt_text": "What behavior does the Cache-Control directive `stale-while-revalidate=60` instruct the browser or CDN to perform?",
        "code_snippet": "Cache-Control: max-age=600, stale-while-revalidate=60",
        "options": [
            "Reject all cached responses after 60 seconds.",
            "Immediately serve a stale cached response to the user for instant page loading, while asynchronously sending a background request to fetch and update the cache with fresh data.",
            "Throw a 504 Gateway Timeout error if the server is busy.",
            "Clear browser cookies every 60 seconds."
        ],
        "correct_option_index": 1,
        "explanation": "`stale-while-revalidate` delivers zero-latency user experiences: the client immediately receives the cached content even if expired (stale), while the browser/CDN revalidates in the background, updating the cache for future requests."
    },
    {
        "difficulty": "advanced",
        "topic": "WebSockets at Scale: Sticky Sessions vs Pub/Sub",
        "prompt_text": "When scaling a WebSocket backend across multiple horizontal server instances behind a load balancer, why is a Redis Pub/Sub backplane necessary?",
        "code_snippet": None,
        "options": [
            "WebSockets cannot run over TCP without Redis.",
            "A client is connected to a specific server instance; if User A on Server 1 sends a message to User B connected to Server 2, Server 1 must broadcast the event across the Redis backplane so Server 2 can forward it to User B.",
            "To encrypt WebSocket payloads using SSL.",
            "To convert WebSocket connections into HTTP GET polling requests."
        ],
        "correct_option_index": 1,
        "explanation": "WebSocket connections are persistent stateful TCP sockets tied to specific server nodes. In a multi-node cluster, a message intended for a user connected to a different server instance must be routed via a message broker/pub-sub bus (e.g. Redis, RabbitMQ, Kafka)."
    },
    {
        "difficulty": "advanced",
        "topic": "TLS 1.3: 0-RTT and Replay Attacks",
        "prompt_text": "What security vulnerability is introduced when enabling TLS 1.3 Zero Round Trip Time (0-RTT) connection resumption?",
        "code_snippet": None,
        "options": [
            "Passphrases are transmitted in plaintext.",
            "Replay attacks: an eavesdropping attacker can capture the early 0-RTT data packet and replay it to the server, potentially duplicating non-idempotent actions (like financial transactions) unless application-level anti-replay mechanisms are implemented.",
            "The browser crashes on mobile networks.",
            "TLS certificates are invalidated."
        ],
        "correct_option_index": 1,
        "explanation": "TLS 1.3 0-RTT allows clients to send data in the first flight of packets before the TLS handshake completes. Because early data cannot have forward secrecy or replay protection at the TLS layer, an attacker can replay early data packets. 0-RTT must only be permitted for idempotent GET requests."
    },
    {
        "difficulty": "advanced",
        "topic": "Multithreading: Web Workers & SharedArrayBuffer",
        "prompt_text": "How can two Web Workers communicate and share memory without serialization copy overhead in modern browsers?",
        "code_snippet": None,
        "options": [
            "Through window.localStorage.",
            "By allocating a `SharedArrayBuffer` and synchronizing concurrent reads and writes using the `Atomics` API (e.g. Atomics.wait(), Atomics.notify()).",
            "By querying the IndexedDB database in an infinite while loop.",
            "Web Workers cannot share memory under any circumstance."
        ],
        "correct_option_index": 1,
        "explanation": "`SharedArrayBuffer` provides shared memory accessible across threads (workers). The `Atomics` object provides low-level atomic operations (load, store, compareExchange, wait, notify) ensuring thread safety and preventing race conditions without serialization."
    },
    {
        "difficulty": "advanced",
        "topic": "Module Federation & Micro-Frontends",
        "prompt_text": "In micro-frontend architectures, what capability does Webpack Module Federation provide at runtime?",
        "code_snippet": None,
        "options": [
            "It merges multiple Git repositories into a single monorepo at compile time.",
            "It allows a JavaScript application to dynamically load and execute compiled modules (remotes) from completely independent deployment pipelines at runtime, sharing common vendor dependencies like React.",
            "It translates frontend code to WebAssembly binaries.",
            "It replaces Docker containers in browser tabs."
        ],
        "correct_option_index": 1,
        "explanation": "Module Federation enables a host application to dynamically import remote builds at runtime. Independent teams can deploy micro-frontends independently, and shared singletons (e.g., React, design systems) are negotiated at runtime to avoid duplicate bundle downloads."
    }
]
