"""Write the fixed prompt set as Qwen3 chat-formatted files (non-thinking mode, empty think block).

llama.cpp's -f strips exactly one trailing '\n', so each file gets one extra newline.
usage: python -I scripts/make_prompts.py prompts
"""
import os
import sys

PROMPTS = {
    "code": (
        "Write a Python implementation of an LRU cache class with get and put methods, "
        "using a doubly linked list and a dict. Include docstrings, type hints, and a short usage example."
    ),
    "explain": (
        "Explain how a CPU cache hierarchy (L1, L2, L3) works and why cache misses hurt performance. "
        "Use concrete latency numbers and one worked example."
    ),
    "rewrite": (
        "Rewrite the following text as a bulleted list of key facts, keeping the original wording where possible.\n\n"
        "The James Webb Space Telescope launched on 25 December 2021 on an Ariane 5 rocket from Kourou, French Guiana. "
        "It reached the Sun-Earth L2 point, about 1.5 million kilometres from Earth, in January 2022. "
        "Its primary mirror is 6.5 metres across and is made of 18 hexagonal segments of gold-coated beryllium. "
        "A five-layer sunshield the size of a tennis court keeps the instruments below 50 kelvin. "
        "The telescope observes mainly in the infrared, from 0.6 to 28.5 micrometres, which lets it see the first galaxies, "
        "look through dust clouds where stars form, and study the atmospheres of exoplanets. "
        "It is a collaboration between NASA, the European Space Agency and the Canadian Space Agency, "
        "and its first full-colour images were released on 12 July 2022."
    ),
    "math": (
        "Solve step by step: a tank is filled by pipe A in 6 hours and by pipe B in 9 hours, and drained by pipe C in 12 hours. "
        "All three are opened at 8:00 with the tank empty. At what time is the tank full? Then verify the answer."
    ),
}

TEMPLATE = "<|im_start|>user\n{}<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
for name, text in PROMPTS.items():
    with open(os.path.join(out, f"{name}.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(TEMPLATE.format(text) + "\n")
    print(name)
