# CMPUT 455 Assignment 4 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification here: https://webdocs.cs.ualberta.ca/~mmueller/courses/cmput455/assignments/a4.html

import sys
import random
import signal

import math 
import time 
import numpy as np

# Function that is called when we reach the time limit
def handle_alarm(signum, frame):
    raise TimeoutError

class CommandInterface:

    def __init__(self):
        # Define the string to function command mapping
        self.command_dict = {
            "help" : self.help,
            "game" : self.game,
            "show" : self.show,
            "play" : self.play,
            "legal" : self.legal,
            "genmove" : self.genmove,
            "winner" : self.winner,
            "timelimit": self.timelimit
        }
        self.board = [[None]]
        self.player = 1
        self.max_genmove_time = 1
        signal.signal(signal.SIGALRM, handle_alarm)
        self.tt = {}
        self.n = len(self.board[0])  # Number of columns
        self.m = len(self.board)     # Number of rows

    
    #====================================================================================================================
    # VVVVVVVVVV Start of predefined functions. You may modify, but make sure not to break the functionality. VVVVVVVVVV
    #====================================================================================================================

    # Convert a raw string to a command and a list of arguments
    def process_command(self, str):
        str = str.lower().strip()
        command = str.split(" ")[0]
        args = [x for x in str.split(" ")[1:] if len(x) > 0]
        if command not in self.command_dict:
            print("? Uknown command.\nType 'help' to list known commands.", file=sys.stderr)
            print("= -1\n")
            return False
        try:
            return self.command_dict[command](args)
        except Exception as e:
            print("Command '" + str + "' failed with exception:", file=sys.stderr)
            print(e, file=sys.stderr)
            print("= -1\n")
            return False
        
    # Will continuously receive and execute commands
    # Commands should return True on success, and False on failure
    # Every command will print '= 1' or '= -1' at the end of execution to indicate success or failure respectively
    def main_loop(self):
        while True:
            str = input()
            if str.split(" ")[0] == "exit":
                print("= 1\n")
                return True
            if self.process_command(str):
                print("= 1\n")

    # Will make sure there are enough arguments, and that they are valid numbers
    # Not necessary for commands without arguments
    def arg_check(self, args, template):
        converted_args = []
        if len(args) < len(template.split(" ")):
            print("Not enough arguments.\nExpected arguments:", template, file=sys.stderr)
            print("Recieved arguments: ", end="", file=sys.stderr)
            for a in args:
                print(a, end=" ", file=sys.stderr)
            print(file=sys.stderr)
            return False
        for i, arg in enumerate(args):
            try:
                converted_args.append(int(arg))
            except ValueError:
                print("Argument '" + arg + "' cannot be interpreted as a number.\nExpected arguments:", template, file=sys.stderr)
                return False
        args = converted_args
        return True

    # List available commands
    def help(self, args):
        for command in self.command_dict:
            if command != "help":
                print(command)
        print("exit")
        return True

    def game(self, args):
        if not self.arg_check(args, "n m"):
            return False
        n, m = [int(x) for x in args]
        if n < 0 or m < 0:
            print("Invalid board size:", n, m, file=sys.stderr)
            return False
        
        self.board = []
        for i in range(m):
            self.board.append([None]*n)
        self.player = 1
        return True
    
    def show(self, args):
        for row in self.board:
            for x in row:
                if x is None:
                    print(".", end="")
                else:
                    print(x, end="")
            print()                    
        return True

    def is_legal(self, x, y, num):
        if self.board[y][x] is not None:
            return False, "occupied"

        # Check row for violations
        row_count = 0
        consecutive = 0
        for col in range(len(self.board[0])):
            if col == x:  # Simulate placing the number
                cell_value = num
            else:
                cell_value = self.board[y][col]
            
            if cell_value == num:
                row_count += 1
                consecutive += 1
                if consecutive >= 3:
                    return False, "three in a row"
            else:
                consecutive = 0

        # Check if too many of `num` in the row
        if row_count > len(self.board[0]) // 2 + len(self.board[0]) % 2:
            return False, f"too many {num}"

        # Check column for violations
        col_count = 0
        consecutive = 0
        for row in range(len(self.board)):
            if row == y:  # Simulate placing the number
                cell_value = num
            else:
                cell_value = self.board[row][x]
            
            if cell_value == num:
                col_count += 1
                consecutive += 1
                if consecutive >= 3:
                    return False, "three in a row"
            else:
                consecutive = 0

        # Check if too many of `num` in the column
        if col_count > len(self.board) // 2 + len(self.board) % 2:
            return False, f"too many {num}"

        return True, ""

    
    def valid_move(self, x, y, num):
        if  x >= 0 and x < len(self.board[0]) and\
                y >= 0 and y < len(self.board) and\
                (num == 0 or num == 1):
            legal, _ = self.is_legal(x, y, num)
            return legal

    def play(self, args):
        err = ""
        if len(args) != 3:
            print("= illegal move: " + " ".join(args) + " wrong number of arguments\n")
            return False
        try:
            x = int(args[0])
            y = int(args[1])
        except ValueError:
            print("= illegal move: " + " ".join(args) + " wrong coordinate\n")
            return False
        if  x < 0 or x >= len(self.board[0]) or y < 0 or y >= len(self.board):
            print("= illegal move: " + " ".join(args) + " wrong coordinate\n")
            return False
        if args[2] != '0' and args[2] != '1':
            print("= illegal move: " + " ".join(args) + " wrong number\n")
            return False
        num = int(args[2])
        legal, reason = self.is_legal(x, y, num)
        if not legal:
            print("= illegal move: " + " ".join(args) + " " + reason + "\n")
            return False
        self.board[y][x] = num
        if self.player == 1:
            self.player = 2
        else:
            self.player = 1
        return True
    
    def legal(self, args):
        if not self.arg_check(args, "x y number"):
            return False
        x, y, num = [int(x) for x in args]
        if self.valid_move(x, y, num):
            print("yes")
        else:
            print("no")
        return True
    
    def get_legal_moves(self):
        moves = []
        for y in range(len(self.board)):
            for x in range(len(self.board[0])):
                for num in range(2):
                    legal, _ = self.is_legal(x, y, num)
                    if legal:
                        moves.append([str(x), str(y), str(num)])
        return moves

    def winner(self, args):
        if len(self.get_legal_moves()) == 0:
            if self.player == 1:
                print(2)
            else:
                print(1)
        else:
            print("unfinished")
        return True

    def timelimit(self, args):
        self.max_genmove_time = int(args[0])
        return True

    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ End of predefined functions. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================

    #===============================================================================================
    # VVVVVVVVVV Start of Assignment 4 functions. Add/modify as needed. VVVVVVVV
    #===============================================================================================

    def add_to_tt(self, hash, move, winner):
        if len(self.tt) < 1000000:
            self.tt[hash] = (move, winner)
            
    def undo(self, move):
        self.board[int(move[1])][int(move[0])] = None
        if self.player == 1:
            self.player = 2
        else:
            self.player = 1

    def quick_play(self, move):
        self.board[int(move[1])][int(move[0])] = int(move[2])
        if self.player == 1:
            self.player = 2
        else:
            self.player = 1

    def game_stage(self):
        total_cells = self.n * self.m
        filled_cells = sum(1 for row in self.board for cell in row if cell is not None)
        if filled_cells < total_cells * 0.2:  # Early game: less than 20% of the board is filled
            return "early"
        elif filled_cells < total_cells * 0.8:  # Mid game: 20%-80% filled
            return "mid"
        else:  # Late game
            return "late"

    def heuristic_value(self, move):
        x, y, value = int(move[0]), int(move[1 ]), int(move[2])  
        center_x, center_y = self.n // 2, self.m // 2

        # Heuristic components
        distance_to_center = abs(x - center_x) + abs(y - center_y)
        neighbors = sum(
            1 for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
            if 0 <= x + dx < self.n and 0 <= y + dy < self.m and self.board[y + dy][x + dx] is not None
        )
        row_balance = abs(self.board[y].count(0) - self.board[y].count(1))
        col_balance = abs(
            [self.board[i][x] for i in range(self.m)].count(0) - 
            [self.board[i][x] for i in range(self.m)].count(1)
        )

        # Dynamic weights
        stage = self.game_stage()
        if stage == "early":
            w_center = 3  # Strongly prioritize centrality
            w_neighbors = 1  # Weaken neighbor importance
            w_balance = 1  # Balance still matters
        elif stage == "mid":
            w_center = 2
            w_neighbors = 2
            w_balance = 2
        else:  # Late game
            w_center = 1  # Centrality is less important
            w_neighbors = 3  # Blocking and forming clusters are crucial
            w_balance = 3

        # Combine heuristics
        score = (
            -w_center * distance_to_center +
            w_neighbors * neighbors -
            w_balance * (row_balance + col_balance)
        )
        return score

    def get_ordered_moves(self, moves):
        # sort moves by heuristic value in descending order (higher score = higher priority)
        return sorted(moves, key=self.heuristic_value, reverse=True)    

    def minimax(self, alpha = ('-inf'), beta = ('inf')):
        hash = str(self.board)
        if hash in self.tt:
            return self.tt[hash]    # reuse result from transposition table 
        
        moves = self.get_legal_moves()
        if not moves: # no legal moves for player, opponent wins
            if self.player == 1:  
                self.add_to_tt(hash, None, 2)
                return None, 2
            
            else:
                self.add_to_tt(hash, None, 1)
                return None, 1    
        
        best_move = None

        if self.player == 1:  # Maximizing player
            best_score = float('-inf')
            ordered_moves = self.get_ordered_moves(moves)  # order moves using heuristic

            for move in ordered_moves:  # evaluate moves in heuristic order
                self.quick_play(move)
                opponent_move, opponent_winner = self.minimax(alpha, beta)
                self.undo(move)

                if opponent_winner == self.player:
                    # win for the maximizing player
                    self.add_to_tt(hash, move, self.player)
                    return move, self.player

                elif opponent_winner != self.player:
                    # opponent wins
                    score = -1
                else:
                    # current player wins
                    score = 0

                if score > best_score:
                    best_score = score
                    best_move = move

                alpha = max(alpha, score)

                if beta <= alpha:  # Prune
                    break

            # no winning move found
            self.add_to_tt(hash, best_move, 2 if best_score == -1 else self.player)
            return best_move, 2 if best_score == -1 else self.player
        
        else:  # Minimizing player
            best_score = float('inf')
            ordered_moves = self.get_ordered_moves(moves)  # order moves using heuristic

            for move in ordered_moves:  # evaluate moves in heuristic order
                self.quick_play(move)
                opponent_move, opponent_winner = self.minimax(alpha, beta)
                self.undo(move)

                if opponent_winner == self.player:
                    #win for the minimizing player
                    self.add_to_tt(hash, move, self.player)
                    return move, self.player

                elif opponent_winner != self.player:
                    # opponent wins
                    score = 1
                else:
                    # current player wins
                    score = 0

                if score < best_score:
                    best_score = score
                    best_move = move

                beta = min(beta, score)

                if beta <= alpha:  # prune
                    break

            # no winning move found
            self.add_to_tt(hash, best_move, 1 if best_score == 1 else self.player)
            return best_move, 1 if best_score == 1 else self.player

 
    def genmove(self, args):
        moves = self.get_legal_moves()  # all legal moves
        if len(moves) == 0:
            print("resign")  # resign if no moves are available
            return True

        # save a copy of the current board and player
        player_copy = self.player
        board_copy = [list(row) for row in self.board]  # copy of the board

        try:
            # Set a time limit for the move calculation
            signal.alarm(self.max_genmove_time)

            # minimax with alpha-beta pruning to determine the best move
            self.tt = {}  # Reset transposition table
            move, value = self.minimax(alpha=float('-inf'), beta=float('inf'))

            # if the program cant find a winning move just pick a random spot
            if move is None:
                move = moves[random.randint(0, len(moves) - 1)]
               
            # Disable the time limit alarm
            signal.alarm(0)

        except TimeoutError:
            move = moves[random.randint(0, len(moves) - 1)]
           
        # restore the board and player state
        self.board = board_copy
        self.player = player_copy
        self.play(move)
        print(" ".join(move))

        return True

    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ End of Assignment 4 functions. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================
    
if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()