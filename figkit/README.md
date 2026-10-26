# figkit

measured, to-scale technical figures in two looks, with all writing in excalifont (the excalidraw hand).

- `drafting`: an engineering drawing on graph paper, with a title block that names the log the numbers came from
- `chalkboard`: a lecture board, chalk strokes, coloured chalk

```python
from figkit import Sheet
s = Sheet("07", "where one cycle goes", "45 prompt eval", "logs/15_eval", theme="chalkboard")
s.part(100, 300, 380, 60, "verify", material="weights")
s.dim(100, 380, 480, 380, "19.0 ms")
s.save("out.png")
```

`blog/figures.py` draws every figure in the hiraishin post from the logs. `FIGKIT_THEME=chalkboard` picks the look.

fonts: excalifont (sil ofl 1.1, `fonts/Excalifont-OFL.txt`). the ibm plex files in `fonts/` are ofl too and unused by the current themes.
