from treelib import Tree
from halma import *
import itertools
import heapq

'''
# Judging by wording on the assignment I'm guessing only stuff in this file will be tested
# a bit worried everything not in here will be cut off so rather move everything here 
# even if its messy
'''

'''
Converts Board State to a bytes object for faster comparisons
'''
def to_bytes(board: List[List[int]]) -> bytes:
    return bytes(itertools.chain.from_iterable(board))

'''
Utility function to parse a Tuple (like [0,2] back into a positon (a, 3) 
'''
def reverse_parse_position(pos: Tuple[int, int]) -> str:
    row, col = pos
    col_char = chr(ord("A") + col)
    row_char = str(row + 1)
    return f"{col_char}{row_char}"

'''
Get all legal moves for current player on current board
'''
def get_legal_moves(
    board: List[List[int]],
    player: int,
) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:

    legal_moves: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []
    
    for row in range(5):
        for column in range(5):
            if board[row][column] != player:
                continue

            oldPos: Tuple[int, int] = (row, column)

            for new_row in range(5):
                for new_column in range(5):
                    newPos: Tuple[int, int] = (new_row, new_column)

                    if check_legal_move(board, oldPos, newPos):
                        legal_moves.append((oldPos, newPos))
    return legal_moves


'''
Evaluate postion a player on board (Week 2)
'''
def get_board_score(
    board: List[List[int]],
    player: int,
) -> int:

    win_cells = win_cells_all[player]

    score = 0

    for row in range(5):
        for col in range(5):
            if board[row][col] != player: 
                continue

            closest_dist = float("inf")

            for win_cell in win_cells:
                dist = abs(win_cell[0] - row) + abs(win_cell[1] - col)
                if dist < closest_dist:
                    closest_dist = dist

            score -= closest_dist
    return score

def recursive_max(
    board: List[List[int]],
    player: int,
    curr_depth: int
) -> Tuple[Tuple[int, int, int, int], Tuple[Tuple[int, int], Tuple[int, int]]]:

    #base:
    if curr_depth == 0:
        scores = (
            get_board_score(board, 1),
            get_board_score(board, 2),
            get_board_score(board, 3),
            get_board_score(board, 4),
        ) 
        return scores, None

    legal_moves: List[Tuple[Tuple[int, int], Tuple[int, int]]] = get_legal_moves(board, player) 

    #if not legal_moves:
        #give some kinda error or skip turn
    
    #recursive:
    # simulate all legal moves then call again to let next player do same thing
    # multiplayer so instead becomes max-n meaning each player only wants their best move
    
    next_player = (player % 4) + 1
    best_score = None
    best_move = None

    for move in legal_moves:
        oldPos, newPos = move

        child_board = [row[:] for row in board]
        child_board[oldPos[0]][oldPos[1]] = 0
        child_board[newPos[0]][newPos[1]] = player 

        next_score, next_move = recursive_max(child_board, next_player, curr_depth - 1)
        player_index = player - 1

        if best_score == None or next_score[player_index] > best_score[player_index]:
            best_score = next_score
            best_move = move

    return best_score, best_move

'''
Bot for Week 2 stuff in progress (1v3 game against other ais) 
'''
def minimax_bot(
    board: List[List[int]],
    player: int,
    visualize_tree: bool
) -> Tuple[str, str]:

    tree = Tree()
    #tree.create_node("Root", node_id_counter, data = {"board": board})

    max_depth = 2

    best_score, best_move = recursive_max(board, player, max_depth)
    oldPos, newPos = best_move

    return reverse_parse_position(oldPos), reverse_parse_position(newPos)

'''
Calculate score just based of distance do goal (Week 1)
'''
def calculate_heuristic_score(player: int, oldPos: Tuple[int, int], newPos: Tuple[int, int]) -> int:
    # best is the most distance that gets us close to the solution

    #make this so doesnt just target one cell but all
    win_cells = win_cells_1v1[player]
    goal = win_cells[0]

    score = abs(sum(newPos) - sum(oldPos))

    if abs(sum(goal) - sum(oldPos)) < abs(sum(goal) - sum(newPos)):
        score *= -1

    return score

'''
Bot for Week 1 stuff (1v1 game against player) 
'''
def searchTree_bot(
    board: List[List[int]],
    player: int,
    visualize_tree: bool
) -> Tuple[str, str]:

    # Basic idea for rn:
    # we'll generate a whole buncha alternative realities until we find one where the bot wins - Dr Strange
    # then we'll pick the next move according to that, after player makes their move we need to repeat
    # the whole process again

    # make a node for each legal move (e.g. a2 -> a3)
    # node will also have to store game state copy so actual game state is not affected

    max_heap = []
    node_id_counter = 0
    winning_node_id = None 

    tree = Tree()
    tree.create_node("Root", node_id_counter, data = {"board": board})

    # Each entry is [-score, node_id, board]
    heapq.heappush(max_heap, (0, node_id_counter, board))

    # For quick lookups of already seen board positions (pruning)
    visited = {to_bytes(board)}

    while max_heap and not winning_node_id: 
        parent_score, parent_id, parent_board = heapq.heappop(max_heap)

        # generate all legal moves
        # make the child nodes relate to this parent
        # enqueue the child nodes 

        legal_moves: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []

        for row in range(5):
            for column in range(5):
                if parent_board[row][column] != player:
                    continue

                oldPos: Tuple[int, int] = (row, column)

                for new_row in range(5):
                    for new_column in range(5):
                        newPos: Tuple[int, int] = (new_row, new_column)

                        if check_legal_move(parent_board, oldPos, newPos):
                            legal_moves.append((oldPos, newPos))

        for i in range(len(legal_moves)):
            oldPos, newPos = legal_moves[i]

            child_board = [row[:] for row in parent_board]
            child_board[oldPos[0]][oldPos[1]] = 0
            child_board[newPos[0]][newPos[1]] = player 

            if to_bytes(child_board) in visited:
                continue;
            visited.add(to_bytes(child_board))
            
            node_id_counter += 1
            child_id = node_id_counter
            
            oldPosStr = reverse_parse_position(oldPos)
            newPosStr = reverse_parse_position(newPos)

            score = calculate_heuristic_score(player, oldPos, newPos)
            
            tree.create_node(f"{oldPosStr} -> {newPosStr}", 
                             child_id, 
                             parent = parent_id, 
                             data={"Board": child_board, "oldPos": oldPos, "newPos": newPos, "score": score})

            if all(child_board[row][column] == player 
                for row, column in win_cells_1v1[player]):
                winning_node_id = node_id_counter
                break
            
            heapq.heappush(max_heap, (-score, child_id, child_board))

    if winning_node_id:
        # make a path [winning node ,...., first move]
        path = []
        curr_node = tree.get_node(winning_node_id)
        while curr_node.identifier != 0:
            path.append(curr_node)
            curr_node = tree.parent(curr_node.identifier)

        win_tree = Tree()
        win_tree.create_node("Root", 0)

        for node in reversed(path):
            win_tree.create_node(
                tag = node.tag,
                identifier = node.identifier,
                parent = tree.parent(node.identifier).identifier,
                data = node.data
            )

        if visualize_tree:
            win_tree.show()

        first_move_node = path[-1]
        return reverse_parse_position(first_move_node.data["oldPos"]), reverse_parse_position(first_move_node.data["newPos"])
    else:
        children = tree.children(0)
        first_move_node = None
        max_score = float("-inf")

        for child in children:
            child_score = child.data["score"]
            if child_score > max_score:
                max_score = child_score
                first_move_node = child
        return reverse_parse_position(first_move_node.data["oldPos"]), reverse_parse_position(first_move_node.data["newPos"])
