from icecream import ic
class Game:
    EMPTY = 0
    X = 1
    O = -1
    DRAW = 2

    def __init__(self):
        self.state = [[]]*3
        for r in range(0,3):
            self.state[r] = [0]*3

        self.empty_cells = 3**2
        self.current = Game.X
        self.last_move = (-1, -1, 0)

    def set_cell_at(self, r: int, c: int, val):
        if self.state[r][c] == Game.EMPTY:
            self.state[r][c] = val
            self.last_move = (r,c,val)
            self.empty_cells -= 1
            return True
    
        return False

    def check_gameover(self):
        n = 3

        if self.empty_cells > (n**2) - (n*2 - 1):
            # Need at least 3+2 moves to have a winner
            return Game.EMPTY

        r,c,val = self.last_move

        #check col
        for i in range(n):
            if self.state[r][i] != val:
                break
        else:
            return val

        #check row
        for i in range(n):
            if self.state[i][c] != val:
                break
        else:
            return val

        #check diag
        if r == c:
            for i in range(n):
                if self.state[i][i] != val:
                    break
            else:
                return val

        #check anti-diag
        if (r+c) == (n-1):
            for i in range(n):
                if self.state[i][(n-1) - i] != val:
                    break
            else:
                return val

        #check draw AFTER ALL OTHER CASES HAVE FALED
        if self.empty_cells == 0:
            return Game.DRAW

        return Game.EMPTY

    @staticmethod
    def grid_pos_to_idx(r: int, c: int) -> int:
        return r*3 + c

######################### TEST CODE
if __name__ == "__main__":
    g = Game()
    ic(g.state)
    g.set_cell_at(0, 2, Game.X)
    ic(g.state)