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


# def uct(child_wins: int, child_visits: int, parent_visits: int, exploration: float) -> float:
#     return child_wins / child_visits + exploration * np.sqrt(np.log(parent_visits) / child_visits)



# class BinaryTreeNode:
#     def __init__(self, board, player, parent=None, move=None):
#         self.board = [row[:] for row in board]  # Deep copy of the board
#         self.player = player  # Current player
#         self.parent = parent
#         self.move = move  # Move that led to this node
#         self.children = []
#         self.visits = 0
#         self.wins = 0
#         self.untried_moves = self.get_legal_moves()

#     def get_legal_moves(self):
#         # Use CommandInterface's legal move generator
#         legal_moves = []
#         print(legal_moves)
#         for y in range(len(self.board)):
#             for x in range(len(self.board[0])):
#                 for num in (0, 1):
#                     if self.valid_move(x, y, num):  # Use starter code's valid_move method
#                         legal_moves.append((x, y, num))
#         return legal_moves

#     def valid_move(self, x, y, num):
#         # Use the starter code's valid_move method for consistency
#         legal, _ = CommandInterface.is_legal(self, x, y, num)
#         return legal

# class MCTSBinaryGame:
#     def __init__(self, root_board, root_player):
#         self.root = BinaryTreeNode(root_board, root_player)

#     def select(self, node):
#         while node.untried_moves == [] and node.children != []:
#             node = max(
#                 node.children,
#                 key=lambda child: uct(child.wins, child.visits, node.visits, 1.0)
#             )
#         return node

#     def expand(self, node):
#         if node.untried_moves:
#             move = node.untried_moves.pop()
#             new_board = [row[:] for row in node.board]  # Copy board
#             x, y, num = move
#             new_board[y][x] = num
#             new_node = BinaryTreeNode(new_board, 3 - node.player, node, move)
#             node.children.append(new_node)
#             return new_node
#         return node

#     def simulate(self, node):
#         board = [row[:] for row in node.board]
#         player = node.player
#         while True:
#             legal_moves = node.get_legal_moves()
#             if not legal_moves:
#                 return 1 if player == 2 else 0  # Opponent loses
#             move = random.choice(legal_moves)
#             x, y, num = move
#             board[y][x] = num
#             player = 3 - player  # Switch player

#     def backpropagate(self, node, result):
#         while node:
#             node.visits += 1
#             node.wins += result
#             node = node.parent

#     def best_move(self, time_limit):
#         import time
#         start_time = time.time()
#         while time.time() - start_time < time_limit:
#             leaf = self.select(self.root)
#             expanded = self.expand(leaf)
#             result = self.simulate(expanded)
#             self.backpropagate(expanded, result)
#         return max(self.root.children, key=lambda c: c.visits).move




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
        
        consecutive = 0
        count = 0
        self.board[y][x] = num
        for row in range(len(self.board)):
            if self.board[row][x] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False, "three in a row"
            else:
                consecutive = 0
        too_many = count > len(self.board) // 2 + len(self.board) % 2
        
        consecutive = 0
        count = 0
        for col in range(len(self.board[0])):
            if self.board[y][col] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False, "three in a row"
            else:
                consecutive = 0
        if too_many or count > len(self.board[0]) // 2 + len(self.board[0]) % 2:
            self.board[y][x] = None
            return False, "too many " + str(num)

        self.board[y][x] = None
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

    def minimax(self, alpha = ('-inf'), beta = ('inf')):
        hash = str(self.board)
        if hash in self.tt:
            return self.tt[hash]    # reuse result from transposition table 
        
        moves = self.get_legal_moves()
        if len(moves) == 0: # no legal moves for player, opponent wins
            if self.player == 1:  
                self.add_to_tt(hash, None, 2)
                return None, 2
            
            else:
                self.add_to_tt(hash, None, 1)
                return None, 1    
        
        if self.player == 1: # maximizing player
            for move in moves:
                self.quick_play(move)
                opponent_move, opponent_winner = self.minimax(alpha, beta) 
                self.undo(move)
                
                if opponent_winner == self.player:
                    # win for the maximizing player
                    self.add_to_tt(hash, move, self.player)
                    return move, self.player
                
                if opponent_winner != self.player:
                    # opponent wins
                    score = -1
                    
                else:
                    # current player wins
                    score = 0
                    
                alpha = max(alpha, score)
                
                if beta <= alpha:   # prune
                    break 
            
            # no winning move is found 
            self.add_to_tt(hash, None, 2)
            return None, 2 
        
        
        else:  # minimizing player
            for move in moves:
                self.quick_play(move)  
                opponent_move, opponent_winner = self.minimax(alpha, beta)  
                self.undo(move)  

                if opponent_winner == self.player:
                    # win for the minimizing player
                    self.add_to_tt(hash, move, self.player)
                    return move, self.player

                if opponent_winner != self.player:
                    # opponent wins
                    score = 1
                else:
                    # current player wins
                    score = 0
                
                beta = min(beta, score)

                if beta <= alpha: # prune
                    break

            # no winning move is found
            self.add_to_tt(hash, None, 1)
            return None, 1

            
    
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

        # apply move
        self.play(move)
        print(" ".join(move))

        return True
    
    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ End of Assignment 4 functions. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================
    
if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()