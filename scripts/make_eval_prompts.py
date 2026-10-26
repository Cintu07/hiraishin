"""Broader evaluation set: 45 prompts in 8 categories, Qwen3 chat format, non-thinking mode.

Long-context prompts embed files from this repo (docs/PROGRESS.md, harness/spec_harness.cpp) so nothing external
is needed. llama.cpp-style -f strips one trailing newline, so each file gets one extra.
usage: python -I scripts/make_eval_prompts.py   -> prompts/eval/<category>_<nn>.txt
"""
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "prompts", "eval")


def read(rel, max_lines=None):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        lines = f.read().splitlines()
    return "\n".join(lines[:max_lines] if max_lines else lines)


PASSAGE_RAIL = (
    "The city's first electric tram line opened in 1898 and ran for 4.2 kilometres between the harbour and the "
    "central market. It used 12 cars, each seating 28 passengers, and drew power from an overhead wire at 550 volts. "
    "Within two years ridership reached 9,000 passengers a day, far above the 3,500 the planners had expected. "
    "The company responded by ordering 18 more cars and extending the line north to the university district in 1903. "
    "Fares were set at one penny for any distance, which made the tram popular with dock workers who lived on the "
    "hills above the port. By 1925 the network had grown to 31 kilometres and 6 routes, but competition from motor "
    "buses began to cut into its income. The last tram ran on 14 March 1957, and most of the track was paved over. "
    "A 600-metre heritage section near the market was restored in 1994 and now carries tourists on weekends."
)

PASSAGE_ENZYME = (
    "Enzymes speed up chemical reactions by lowering the activation energy needed for the reaction to proceed. "
    "Each enzyme has an active site, a pocket whose shape and chemical properties match a particular substrate. "
    "When the substrate binds, the enzyme can strain chemical bonds, bring reacting groups close together, or "
    "provide a temporary chemical partner, all of which make the reaction easier. Enzymes are not used up, so a "
    "single molecule can process thousands of substrate molecules per second. Their activity depends strongly on "
    "temperature and pH: most human enzymes work best near 37 degrees Celsius and lose their shape, or denature, "
    "at much higher temperatures. Inhibitors can slow enzymes down, either by competing with the substrate for the "
    "active site or by binding elsewhere and changing the enzyme's shape. Many drugs work this way."
)

PASSAGE_MEETING = (
    "Notes from the Tuesday planning meeting. Priya said the payment service migration is two weeks behind because "
    "the old database schema has undocumented triggers. Marco proposed freezing new features on the checkout page "
    "until the migration lands, and the group agreed. Lena raised that the mobile app crash rate rose from 0.4% to "
    "1.1% after the last release; she traced most crashes to the image cache and will ship a fix on Thursday. "
    "The team discussed hiring: one backend role is approved, the frontend role is still waiting on budget. "
    "Action items: Priya documents the triggers by Friday, Marco writes the feature-freeze announcement today, "
    "Lena ships the cache fix Thursday and reports the new crash rate next Tuesday."
)

CODE_SNIPPET_PY = '''def process(items):
    result = []
    for i in range(len(items)):
        if items[i] != None:
            if items[i] > 0:
                result.append(items[i] * 2)
            else:
                result.append(0)
    total = 0
    for r in result:
        total = total + r
    return result, total'''

CODE_SNIPPET_JS = '''function fetchUsers(ids, cb) {
  var out = [];
  var done = 0;
  for (var i = 0; i < ids.length; i++) {
    getUser(ids[i], function (err, user) {
      if (err) { cb(err); return; }
      out.push(user);
      done++;
      if (done == ids.length) cb(null, out);
    });
  }
}'''

CODE_SNIPPET_C = '''int find(int *a, int n, int x) {
    for (int i = 0; i <= n; i++) {
        if (a[i] = x) return i;
    }
    return -1;
}'''

PROMPTS = {
    "code_gen": [
        "Write a Python function that parses a CSV file of transactions (date, description, amount) and returns the total spent per month. Include type hints and a short example.",
        "Write a C function that reverses a singly linked list in place. Include the struct definition and a small main() that tests it.",
        "Implement a thread-safe bounded queue in Rust with push and pop methods that block when full or empty. Explain the design briefly.",
        "Write a JavaScript function that debounces another function, with a cancel method. Add JSDoc comments.",
        "Write a SQL schema for a small library system with books, members and loans, then three example queries: overdue loans, most borrowed books, and members with no loans.",
        "Write a Go HTTP server with two endpoints, GET /health and POST /echo, that returns the JSON body it receives. Include graceful shutdown.",
        "Implement binary search in Python, then write five unit tests with pytest that cover edge cases.",
    ],
    "code_edit": [
        f"Refactor this Python function to be idiomatic and explain each change:\n\n```python\n{CODE_SNIPPET_PY}\n```",
        f"Rewrite this callback-based JavaScript function using async/await and Promise.all, keeping the same behavior and input order:\n\n```javascript\n{CODE_SNIPPET_JS}\n```",
        f"Find and fix the bugs in this C function, then show the corrected version:\n\n```c\n{CODE_SNIPPET_C}\n```",
        f"Add input validation and docstrings to this Python function without changing its results:\n\n```python\n{CODE_SNIPPET_PY}\n```",
        f"Translate this JavaScript function to Python with asyncio, keeping the structure recognizable:\n\n```javascript\n{CODE_SNIPPET_JS}\n```",
    ],
    "math": [
        "A shop sells pens at 3 for $2 and notebooks at $3.50 each. Sam buys 12 pens and some notebooks and pays $29. How many notebooks did Sam buy? Show your steps.",
        "Prove that the sum of the first n odd numbers is n squared.",
        "Solve the system of equations: 2x + 3y = 13 and 5x - y = 7. Then check the solution.",
        "A train travels 180 km at 60 km/h and returns at 90 km/h. What is the average speed for the whole trip? Explain why it is not 75 km/h.",
        "How many ways can 5 people sit around a round table if two of them refuse to sit next to each other? Explain the counting.",
        "Find the derivative of f(x) = x^2 * sin(x) and the equation of the tangent line at x = 0.",
        "A bag has 4 red and 6 blue marbles. Two are drawn without replacement. What is the probability both are the same color? Show the calculation.",
    ],
    "explain": [
        "Explain how a hash table handles collisions, comparing chaining and open addressing, with their trade-offs.",
        "Explain why the sky is blue and why sunsets are red, at the level of a curious high school student.",
        "Explain how public key cryptography lets two strangers agree on a secret over an open channel.",
        "Explain what causes inflation and how central banks try to control it.",
        "Explain the difference between a process and a thread in an operating system, with examples of when to use each.",
        "Explain how vaccines train the immune system, including the role of memory cells.",
        "Explain how GPS works out your position from satellite signals, including why clocks matter.",
    ],
    "summarize": [
        f"Summarize the following text in five bullet points, keeping the key numbers:\n\n{PASSAGE_RAIL}",
        f"Rewrite the following text for a ten-year-old, keeping it accurate:\n\n{PASSAGE_ENZYME}",
        f"Turn these meeting notes into a short status email with an action item list:\n\n{PASSAGE_MEETING}",
        f"Rewrite the following text as a timeline with one line per year mentioned:\n\n{PASSAGE_RAIL}",
        f"Summarize the following text in two sentences, then list three questions a student might ask about it:\n\n{PASSAGE_ENZYME}",
        f"Rewrite these meeting notes as a table with columns Person, Topic, Action, Deadline:\n\n{PASSAGE_MEETING}",
    ],
    "creative": [
        "Write a short story (about 400 words) about a lighthouse keeper who finds a message in a bottle addressed to them.",
        "Write a poem about a city waking up in the rain, in free verse.",
        "Write a polite but firm email to a landlord asking for a broken heater to be repaired this week.",
        "Write the opening scene of a science fiction story set on a cargo ship stuck between two stars.",
        "Write a product description for a reusable water bottle aimed at hikers, in an energetic tone.",
    ],
    "structured": [
        f"Extract every number from this text into a JSON array of objects with fields value, unit and meaning:\n\n{PASSAGE_RAIL}",
        f"Extract the action items from these notes as JSON with fields owner, task and due:\n\n{PASSAGE_MEETING}",
        "Create a JSON object describing a fictional laptop with fields brand, model, cpu, gpu, ram_gb, storage_gb, price_usd and a list of ports. Then write a JSON Schema that validates it.",
        "Write a YAML configuration for a web service with a database, a cache and two worker queues, and comment every field.",
    ],
    "long_context": [
        f"Here is a project log:\n\n{read('docs/PROGRESS.md')}\n\nAnswer: what were the four causes of non-lossless verification, and which file or patch fixes each?",
        f"Here is a project log:\n\n{read('docs/PROGRESS.md')}\n\nWrite a one-paragraph summary of the project for someone who has never heard of speculative decoding.",
        f"Here is part of a C++ program:\n\n```cpp\n{read('harness/spec_harness.cpp', 200)}\n```\n\nExplain what this code does, function by function.",
        f"Here is part of a C++ program:\n\n```cpp\n{read('harness/spec_harness.cpp', 200)}\n```\n\nReview this code: list possible bugs, edge cases and improvements.",
    ],
}

TEMPLATE = "<|im_start|>user\n{}<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"

os.makedirs(OUT, exist_ok=True)
n = 0
for cat, ps in PROMPTS.items():
    for i, text in enumerate(ps, 1):
        with open(os.path.join(OUT, f"{cat}_{i:02d}.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(TEMPLATE.format(text) + "\n")
        n += 1
print(f"wrote {n} prompts to {OUT}")
