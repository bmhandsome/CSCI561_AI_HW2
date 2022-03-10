from copy import deepcopy
import time
MAX_INT_IN_THIS_PROGRAM = 1000000000
MIN_INT_IN_THIS_PROGRAM = -1000000000
MAX_TIME_FOR_EACH_MOVE_IN_MILLI = 5000

def getTimeNowInMilli():
    return int(time.time() * 1000)

class GO:
    def __init__(self, n):
        """
        Go game.

        :param n: size of the board n*n
        """
        self.size = n
        #self.previous_board = None # Store the previous board
        self.X_move = True # X chess plays first
        self.died_pieces = [] # Intialize died pieces to be empty
        self.n_move = 0 # Trace the number of moves
        self.max_move = n * n - 1 # The max movement of a Go game
        self.komi = n/2 # Komi rule
        self.verbose = False # Verbose only when there is a manual player

    def init_board(self, n):
        '''
        Initialize a board with size n*n.

        :param n: width and height of the board.
        :return: None.
        '''
        board = [[0 for x in range(n)] for y in range(n)]  # Empty space marked as 0
        # 'X' pieces marked as 1
        # 'O' pieces marked as 2
        self.board = board
        self.previous_board = deepcopy(board)

    def set_board(self, piece_type, previous_board, board):
        '''
        Initialize board status.
        :param previous_board: previous board state.
        :param board: current board state.
        :return: None.
        '''

        # 'X' pieces marked as 1
        # 'O' pieces marked as 2

        for i in range(self.size):
            for j in range(self.size):
                if previous_board[i][j] == piece_type and board[i][j] != piece_type:
                    self.died_pieces.append((i, j))

        # self.piece_type = piece_type
        self.previous_board = previous_board
        self.board = board

    def compare_board(self, board1, board2):
        for i in range(self.size):
            for j in range(self.size):
                if board1[i][j] != board2[i][j]:
                    return False
        return True

    def copy_board(self):
        '''
        Copy the current board for potential testing.

        :param: None.
        :return: the copied board instance.
        '''
        return deepcopy(self)

    def detect_neighbor(self, i, j):
        '''
        Detect all the neighbors of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbors row and column (row, column) of position (i, j).
        '''
        board = self.board
        neighbors = []
        # Detect borders and add neighbor coordinates
        if i > 0: neighbors.append((i-1, j))
        if i < len(board) - 1: neighbors.append((i+1, j))
        if j > 0: neighbors.append((i, j-1))
        if j < len(board) - 1: neighbors.append((i, j+1))
        return neighbors

    def detect_neighbor_ally(self, i, j):
        '''
        Detect the neighbor allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbored allies row and column (row, column) of position (i, j).
        '''
        board = self.board
        neighbors = self.detect_neighbor(i, j)  # Detect neighbors
        group_allies = []
        # Iterate through neighbors
        for piece in neighbors:
            # Add to allies list if having the same color
            if board[piece[0]][piece[1]] == board[i][j]:
                group_allies.append(piece)
        return group_allies

    def ally_dfs(self, i, j):
        '''
        Using DFS to search for all allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the all allies row and column (row, column) of position (i, j).
        '''
        stack = [(i, j)]  # stack for DFS serach
        ally_members = []  # record allies positions during the search
        while stack:
            piece = stack.pop()
            ally_members.append(piece)
            neighbor_allies = self.detect_neighbor_ally(piece[0], piece[1])
            for ally in neighbor_allies:
                if ally not in stack and ally not in ally_members:
                    stack.append(ally)
        return ally_members

    def find_liberty(self, i, j):
        '''
        Find liberty of a given stone. If a group of allied stones has no liberty, they all die.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: boolean indicating whether the given stone still has liberty.
        '''
        board = self.board
        ally_members = self.ally_dfs(i, j)
        for member in ally_members:
            neighbors = self.detect_neighbor(member[0], member[1])
            for piece in neighbors:
                # If there is empty space around a piece, it has liberty
                if board[piece[0]][piece[1]] == 0:
                    return True
        # If none of the pieces in a allied group has an empty space, it has no liberty
        return False

    def find_num_liberty_and_ally_member(self, i, j):
        '''
        Find number of liberty of a given stone as well as list of ally member. If a group of allied stones has no liberty, they all die.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: tuple list of ally member and number of liberty.
        '''
        num_of_liberty = 0
        board = self.board
        list_check_repect_point = []
        ally_members = self.ally_dfs(i, j)
        for member in ally_members:
            neighbors = self.detect_neighbor(member[0], member[1])
            for piece in neighbors:
                # If there is empty space around a piece, it has liberty
                if board[piece[0]][piece[1]] == 0:
                    if ((piece[0], piece[1]) not in list_check_repect_point):
                        num_of_liberty += 1
                        list_check_repect_point.append((piece[0], piece[1]))
        # If none of the pieces in a allied group has an empty space, it has no liberty
        return (ally_members, num_of_liberty)

    def find_died_pieces(self, piece_type):
        '''
        Find the died stones that has no liberty in the board for a given piece type.

        :param piece_type: 1('X') or 2('O').
        :return: a list containing the dead pieces row and column(row, column).
        '''
        board = self.board
        died_pieces = []

        for i in range(len(board)):
            for j in range(len(board)):
                # Check if there is a piece at this position:
                if board[i][j] == piece_type:
                    # The piece die if it has no liberty
                    if not self.find_liberty(i, j):
                        died_pieces.append((i,j))
        return died_pieces

    def remove_died_pieces(self, piece_type):
        '''
        Remove the dead stones in the board.

        :param piece_type: 1('X') or 2('O').
        :return: locations of dead pieces.
        '''

        died_pieces = self.find_died_pieces(piece_type)
        if not died_pieces: return []
        self.remove_certain_pieces(died_pieces)
        return died_pieces

    def remove_certain_pieces(self, positions):
        '''
        Remove the stones of certain locations.

        :param positions: a list containing the pieces to be removed row and column(row, column)
        :return: None.
        '''
        board = self.board
        for piece in positions:
            board[piece[0]][piece[1]] = 0
        self.update_board(board)

    def place_chess(self, i, j, piece_type):
        '''
        Place a chess stone in the board.

        :param i: row number of the board.
        :param j: column number of the board.
        :param piece_type: 1('X') or 2('O').
        :return: boolean indicating whether the placement is valid.
        '''
        board = self.board

        valid_place = self.valid_place_check(i, j, piece_type)
        if not valid_place:
            return False
        self.previous_board = deepcopy(board)
        board[i][j] = piece_type
        self.update_board(board)
        # Remove the following line for HW2 CS561 S2020
        # self.n_move += 1
        return True

    def valid_place_check(self, i, j, piece_type, test_check=False):
        '''
        Check whether a placement is valid.

        :param i: row number of the board.
        :param j: column number of the board.
        :param piece_type: 1(white piece) or 2(black piece).
        :param test_check: boolean if it's a test check.
        :return: boolean indicating whether the placement is valid.
        '''   
        board = self.board
        verbose = self.verbose
        if test_check:
            verbose = False

        # Check if the place is in the board range
        if not (i >= 0 and i < len(board)):
            if verbose:
                print(('Invalid placement. row should be in the range 1 to {}.').format(len(board) - 1))
            return False
        if not (j >= 0 and j < len(board)):
            if verbose:
                print(('Invalid placement. column should be in the range 1 to {}.').format(len(board) - 1))
            return False
        
        # Check if the place already has a piece
        if board[i][j] != 0:
            if verbose:
                print('Invalid placement. There is already a chess in this position.')
            return False
        
        # Copy the board for testing
        test_go = self.copy_board()
        test_board = test_go.board

        # Check if the place has liberty
        test_board[i][j] = piece_type
        test_go.update_board(test_board)
        if test_go.find_liberty(i, j):
            return True

        # If not, remove the died pieces of opponent and check again
        test_go.remove_died_pieces(3 - piece_type)
        if not test_go.find_liberty(i, j):
            if verbose:
                print('Invalid placement. No liberty found in this position.')
            return False

        # Check special case: repeat placement causing the repeat board state (KO rule)
        else:
            if self.died_pieces and self.compare_board(self.previous_board, test_go.board):
                if verbose:
                    print('Invalid placement. A repeat move not permitted by the KO rule.')
                return False
        return True
        
    def update_board(self, new_board):
        '''
        Update the board with new_board

        :param new_board: new board.
        :return: None.
        '''   
        self.board = new_board

    def visualize_board(self):
        '''
        Visualize the board.

        :return: None
        '''
        board = self.board

        print('-' * len(board) * 2)
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] == 0:
                    print(' ', end=' ')
                elif board[i][j] == 1:
                    print('X', end=' ')
                else:
                    print('O', end=' ')
            print()
        print('-' * len(board) * 2)

    def game_end(self, piece_type, action="MOVE"):
        '''
        Check if the game should end.

        :param piece_type: 1('X') or 2('O').
        :param action: "MOVE" or "PASS".
        :return: boolean indicating whether the game should end.
        '''

        # Case 1: max move reached
        if self.n_move >= self.max_move:
            return True
        # Case 2: two players all pass the move.
        if self.compare_board(self.previous_board, self.board) and action == "PASS":
            return True
        return False

    def score(self, piece_type):
        '''
        Get score of a player by counting the number of stones.

        :param piece_type: 1('X') or 2('O').
        :return: boolean indicating whether the game should end.
        '''

        board = self.board
        cnt = 0
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == piece_type:
                    cnt += 1
        return cnt          

    def judge_winner(self):
        '''
        Judge the winner of the game by number of pieces for each player.

        :param: None.
        :return: piece type of winner of the game (0 if it's a tie).
        '''        

        cnt_1 = self.score(1)
        cnt_2 = self.score(2)
        if cnt_1 > cnt_2 + self.komi: return 1
        elif cnt_1 < cnt_2 + self.komi: return 2
        else: return 0
        
    def play(self, player1, player2, verbose=False):
        '''
        The game starts!

        :param player1: Player instance.
        :param player2: Player instance.
        :param verbose: whether print input hint and error information
        :return: piece type of winner of the game (0 if it's a tie).
        '''
        self.init_board(self.size)
        # Print input hints and error message if there is a manual player
        if player1.type == 'manual' or player2.type == 'manual':
            self.verbose = True
            print('----------Input "exit" to exit the program----------')
            print('X stands for black chess, O stands for white chess.')
            self.visualize_board()
        
        verbose = self.verbose
        # Game starts!
        while 1:
            piece_type = 1 if self.X_move else 2

            # Judge if the game should end
            if self.game_end(piece_type):       
                result = self.judge_winner()
                if verbose:
                    print('Game ended.')
                    if result == 0: 
                        print('The game is a tie.')
                    else: 
                        print('The winner is {}'.format('X' if result == 1 else 'O'))
                return result

            if verbose:
                player = "X" if piece_type == 1 else "O"
                print(player + " makes move...")

            # Game continues
            if piece_type == 1: action = player1.get_input(self, piece_type)
            else: action = player2.get_input(self, piece_type)

            if verbose:
                player = "X" if piece_type == 1 else "O"
                print(action)

            if action != "PASS":
                # If invalid input, continue the loop. Else it places a chess on the board.
                if not self.place_chess(action[0], action[1], piece_type):
                    if verbose:
                        self.visualize_board() 
                    continue

                self.died_pieces = self.remove_died_pieces(3 - piece_type) # Remove the dead pieces of opponent
            else:
                self.previous_board = deepcopy(self.board)

            if verbose:
                self.visualize_board() # Visualize the board again
                print()

            self.n_move += 1
            self.X_move = not self.X_move # Players take turn

class MyPlayer():
    def __init__(self):
        self.type = 'my_player'

    def calculate_heuristic(self, go, piece_type, placement):
        
        another_piece_type = 3 - piece_type
        go.remove_died_pieces(another_piece_type)
        
        list_my_stone = []
        list_opponent_stone = []
        count_my_stone = 0 
        count_opponent_stone = 0

        for i in range(go.size):
            for j in range(go.size):
                if go.board[i][j] == piece_type: 
                    count_my_stone += 1
                    list_my_stone.append((i,j))
                elif go.board[i][j] == another_piece_type: 
                    count_opponent_stone += 1
                    list_opponent_stone.append((i,j))
        
        #Heuristic1 Different Number of stones
        diff_count_stone = count_my_stone - count_opponent_stone
        blank = go.size - count_my_stone - count_opponent_stone
        estimate_turn_left = self.estimate_num_turn_left(go, blank, count_my_stone, count_opponent_stone)

        list_my_stone_group_by_neighbor_and_liberty = []
        while list_my_stone:
            one_my_stone = list_my_stone[0]
            ally_members, liberty = go.find_num_liberty_and_ally_member(one_my_stone[0], one_my_stone[1])
            list_my_stone_group_by_neighbor_and_liberty.append((ally_members, liberty))
            list_my_stone = [item for item in list_my_stone if item not in ally_members]

        list_opponent_stone_group_by_neighbor_and_liberty = []
        while list_opponent_stone:
            one_opponent_stone = list_opponent_stone[0]
            ally_members, liberty = go.find_num_liberty_and_ally_member(one_opponent_stone[0], one_opponent_stone[1])
            list_opponent_stone_group_by_neighbor_and_liberty.append((ally_members, liberty))
            list_opponent_stone = [item for item in list_opponent_stone if item not in ally_members]

        heulistic_case_1 = 0
        max_int_for_calculate_heulistic = MAX_INT_IN_THIS_PROGRAM / 1000
        # if black
        if piece_type == 1: 
            if diff_count_stone > go.size / 2:
                heulistic_case_1 += max_int_for_calculate_heulistic
            else: 
                heulistic_case_1 -= max_int_for_calculate_heulistic
        # if white
        elif piece_type == 2:
            if diff_count_stone > -1 * (go.size / 2):
                heulistic_case_1 += max_int_for_calculate_heulistic
            else:
                heulistic_case_1 -= max_int_for_calculate_heulistic

        heulistic_case_1 += diff_count_stone * 100000        
        if estimate_turn_left <= (go.size * go.size) / 2:
            heulistic_case_1 = heulistic_case_1 * 10

        heulistic_case_2 = 0
        #heuristic plus for my liberty
        for group in list_my_stone_group_by_neighbor_and_liberty:
            list_stone_group = group[0]
            liberty = group[1]
            num_of_list_stone = len(list_stone_group)
            fix_constant = 0
            if num_of_list_stone <= 1:
                fix_constant += 10
            elif num_of_list_stone > 1 and num_of_list_stone <= 3:
                fix_constant += 30
            elif num_of_list_stone > 3:
                fix_constant += 100
            heulistic_case_2 += fix_constant * num_of_list_stone * liberty
            if liberty == 1:
                heulistic_case_2 += -3000 * num_of_list_stone
            if liberty == 2:
                heulistic_case_2 += -300 * num_of_list_stone
            if liberty == 3:
                heulistic_case_2 += -100 * num_of_list_stone
        # #heuristic minus for opponent liberty
        for group in list_opponent_stone_group_by_neighbor_and_liberty:
            list_stone_group = group[0]
            liberty = group[1]
            num_of_list_stone = len(list_stone_group)
            fix_constant = 0
            if num_of_list_stone <= 1:
                fix_constant += 100
            elif num_of_list_stone > 1 and num_of_list_stone <= 3:
                fix_constant += 500
            elif num_of_list_stone > 3:
                fix_constant += 2000
            heulistic_case_2 += -1 * fix_constant * num_of_list_stone * liberty

            if liberty == 1:
                heulistic_case_2 += 2500 * num_of_list_stone
            if liberty == 2:
                heulistic_case_2 += 800 * num_of_list_stone
            if liberty == 3:
                heulistic_case_2 += 250 * num_of_list_stone

            heulistic_case_2 = heulistic_case_2 * estimate_turn_left

        heulistic_case_3 = 0
        middle = (go.size - 1) / 2
        if  count_my_stone + count_opponent_stone < go.size:
            if placement == (middle, middle):
                heulistic_case_3 += 1000000
            elif placement == (middle - 1, middle - 1):
                heulistic_case_3 += 100000
            elif placement == (middle + 1, middle - 1):
                heulistic_case_3 += 100000
            elif placement == (middle - 1, middle + 1):
                heulistic_case_3 += 100000
            elif placement == (middle + 1, middle + 1):
                heulistic_case_3 += 100000
        i = placement[0]
        j = placement[1]
        divider = abs(middle - i) + abs(middle - j)
        if divider <= 0:
            divider = 1
        heulistic_case_3 += 10000 / divider
        return heulistic_case_1 + heulistic_case_2 + heulistic_case_3

    def find_possible_placements_and_number_of_blank(self, go, piece_type):
        possible_placements = []
        blank = 0
        num_piece_type = 0
        num_another_piece_type = 0
        another_piece_type = 3 - piece_type
        for i in range(go.size):
            for j in range(go.size):
                if go.board[i][j] == 0:
                    blank += 1
                elif go.board[i][j] == piece_type:
                    num_piece_type += 1
                elif go.board[i][j] == another_piece_type:
                    num_another_piece_type += 1
                if go.valid_place_check(i, j, piece_type, test_check = True):
                    possible_placements.append((i, j))
        middle = (go.size - 1) / 2
        if possible_placements:
            possible_placements.sort(key = lambda x:  abs(middle - x[0]) + abs(middle - x[1]))
        return (possible_placements, (blank, num_piece_type, num_another_piece_type))

    def get_input(self, go, piece_type):
        '''
        Get one input.

        :param go: Go instance.
        :param piece_type: 1('X') or 2('O').
        :return: (row, column) coordinate of input.
        '''     
        possible_placements, tuple_stone = self.find_possible_placements_and_number_of_blank(go, piece_type)

        another_piece_type = 3 - piece_type
        best_placement = ()
        max_heuristic = MIN_INT_IN_THIS_PROGRAM
        temp_heuristic = 0
        best_move_path = []
        temp_move_path = []
        #calculate heuristic for each possible placement
        calculation_time_for_each_placement = MAX_TIME_FOR_EACH_MOVE_IN_MILLI / len(possible_placements)

        num_blank_space = tuple_stone[0]
        num_piece_type = tuple_stone[1]
        num_another_piece_type = tuple_stone[2]
        
        if num_piece_type + num_another_piece_type == 0:
            writeTurn("0")
        elif num_piece_type + num_another_piece_type == 1:
            writeTurn("1")

        max_depth = 0
        num_turn = 0
        try:
            num_turn = int(readTurn())
            max_depth = (go.size ** 2) - num_turn - 2
        except Exception as e:
            print(e)
            max_depth = self.estimate_num_turn_left(go, num_blank_space, num_piece_type, num_another_piece_type)
            num_turn = num_piece_type + num_another_piece_type
        print(f'max depth : {max_depth}')

        for placement in possible_placements:
            go_with_placement = go.copy_board()
            go_with_placement.board[placement[0]][placement[1]] = piece_type
            go_with_placement.remove_died_pieces(another_piece_type)

            temp_heuristic, temp_move_path = self.start_iterative_deepening(go_with_placement, piece_type, placement, max_depth, [placement], calculation_time_for_each_placement)
            if temp_heuristic > max_heuristic:
                max_heuristic = temp_heuristic
                best_move_path = temp_move_path
                best_placement = placement
            
        print(f'best_move: {best_placement}')
        print(f'best_move_path: {best_move_path}')
        print(f'max_heuristic: {max_heuristic}')
        if not possible_placements:
            return "PASS"
        # elif placements_with_heuristic[0][1] < 0:
        #     return "PASS"
        else:
            writeTurn(str(num_turn + 2))
            return best_placement
    
    def estimate_num_turn_left(self, go, num_blank_space, num_piece_type, num_another_piece_type):
        
        all_possible_num = go.size ** 2
        max_stone = 0
        if num_piece_type >= num_another_piece_type:
            max_stone = num_piece_type
        else:
            max_stone = num_another_piece_type
        max_stone = max_stone * 2
        all_possible_num = all_possible_num - max_stone - 1
         #adjust_max_depth
        if all_possible_num <= 8 and all_possible_num > 6:
             all_possible_num = all_possible_num - 4
        elif all_possible_num <= 6 and all_possible_num > 3:
            all_possible_num = all_possible_num - 2
        elif all_possible_num <= 3:
            all_possible_num = 1
        return all_possible_num

    def start_iterative_deepening(self, go, piece_type, placement, max_depth, move_path , time_limit_for_each_search):
        dept = 0
        startTimeThisSearch = getTimeNowInMilli()
        endTimeThisSearch = startTimeThisSearch + time_limit_for_each_search

        heuristic = MIN_INT_IN_THIS_PROGRAM
        best_move_path = []
        while dept <= max_depth:
            now = getTimeNowInMilli()
            if now >= endTimeThisSearch:
                break
            heuristic, best_move_path = self.min(go, piece_type, placement, dept, MIN_INT_IN_THIS_PROGRAM, MAX_INT_IN_THIS_PROGRAM, move_path, endTimeThisSearch)
            dept += 1
        return heuristic, best_move_path

    def max(self, go, piece_type, outest_placement, depth, alpha, beta, move_path, endTime):
        another_piece_type = 3 - piece_type
        now = getTimeNowInMilli()
        if depth == 0 or now >= endTime:
            heuristic = self.calculate_heuristic(go, piece_type, outest_placement)
            return heuristic, move_path
        possible_placements, tuple_stone = self.find_possible_placements_and_number_of_blank(go, piece_type)
        heuristic = MIN_INT_IN_THIS_PROGRAM
        best_move_path = []
        if not possible_placements: 
            heuristic = self.calculate_heuristic(go, piece_type, outest_placement)
            return heuristic, move_path
        for placement in possible_placements:
            go_with_placement = go.copy_board()
            go_with_placement.board[placement[0]][placement[1]] = piece_type
            go_with_placement.remove_died_pieces(another_piece_type)
            temp_path = move_path.copy()
            temp_path.append(placement)
            temp_heuristic, temp_move_path = self.min(go_with_placement, piece_type, outest_placement, depth - 1, alpha, beta, temp_path, endTime)
            if temp_heuristic > heuristic:
                heuristic = temp_heuristic
                best_move_path = temp_move_path
            if heuristic >= beta: 
                return heuristic, best_move_path
            alpha = max(alpha, heuristic)
        return heuristic, best_move_path

    def min(self, go, piece_type, outest_placement, depth, alpha, beta, move_path, endTime):
        now = getTimeNowInMilli()
        if depth == 0 or now >= endTime:
            heuristic = self.calculate_heuristic(go, piece_type, outest_placement)
            return heuristic, move_path
        another_piece_type = 3 - piece_type
        possible_placements, tuple_stone = self.find_possible_placements_and_number_of_blank(go, another_piece_type)
        heuristic = MAX_INT_IN_THIS_PROGRAM
        best_move_path = []
        if not possible_placements: 
            heuristic = self.calculate_heuristic(go, piece_type, outest_placement)
            return heuristic, move_path
        for placement in possible_placements:
            go_with_placement = go.copy_board()
            go_with_placement.board[placement[0]][placement[1]] = another_piece_type
            go_with_placement.remove_died_pieces(piece_type)
            temp_path = move_path.copy()
            temp_path.append(placement)
            temp_heuristic, temp_move_path = self.max(go_with_placement, piece_type, outest_placement, depth - 1, alpha, beta, temp_path, endTime)
            if temp_heuristic < heuristic:
                heuristic = temp_heuristic
                best_move_path = temp_move_path
            if heuristic <= alpha:
                return heuristic, best_move_path
            beta = min(beta, heuristic)
        return heuristic, best_move_path
        
def readInput(n, path="input.txt"):
    with open(path, 'r') as f:
        lines = f.readlines()

        piece_type = int(lines[0])

        previous_board = [[int(x) for x in line.rstrip('\n')] for line in lines[1:n+1]]
        board = [[int(x) for x in line.rstrip('\n')] for line in lines[n+1: 2*n+1]]

        return piece_type, previous_board, board

def writeOutput(result, path="output.txt"):
    res = ""
    if result == "PASS":
        res = "PASS"
    else:
        res += str(result[0]) + ',' + str(result[1])

    with open(path, 'w') as f:
        f.write(res)

def writePass(path="output.txt"):
	with open(path, 'w') as f:
		f.write("PASS")

def readTurn(path="helper.txt"):
    turn = 0
    with open(path, 'rt') as f:
        turn = f.readline()
    return turn

def writeTurn(turn, path="helper.txt"):
    with open(path, 'wt') as f:
        f.write(turn)

if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    go.visualize_board()
    print("--------------------")
    player = MyPlayer()
    action = player.get_input(go, piece_type)
    go.place_chess(action[0], action[1], piece_type)
    go.visualize_board()
    writeOutput(action)