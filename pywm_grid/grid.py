from typing import Optional

class Grid:
    def __init__(self, file: str) -> None:
        self._map: dict[str, str] = {}
        self.grid: list[list[str]] = []
        with open(file, 'r') as inp:
            for l in inp:
                lp = l.strip()
                if "#" in lp:
                    lp = lp[:lp.index("#")]
                if lp == "":
                    continue

                if "=" in lp:
                    self._map[lp.split("=")[0]] = "=".join(lp.split("=")[1:])
                else:
                    tmp: list[str] = list(lp.replace(" ",""))
                    self.grid += [tmp]

        self.grid = [[self._map[x] if x in self._map else "" for x in v] for v in self.grid]
        self._waiting = False
        self._at = (0, -1)

    def get_width(self) -> int:
        return max([len(v) for v in self.grid])

    def get_height(self) -> int:
        return len(self.grid)

    def next_app(self) -> Optional[str]:
        if self._at[0] >= self.get_height():
            return None

        if self._at[1] >= len(self.grid[self._at[0]]) - 1:
            self._at = self._at[0] + 1, 0
        else:
            self._at = self._at[0], self._at[1] + 1

        if self._at[0] < len(self.grid):
            v = self.grid[self._at[0]]
            if self._at[1] < len(v):

                self._waiting = True
                return v[self._at[1]]

        return None

    def find_next_app(self) -> tuple[int, int]:
        self._waiting = False
        return self._at

    def still_waiting(self) -> bool:
        return self._waiting

