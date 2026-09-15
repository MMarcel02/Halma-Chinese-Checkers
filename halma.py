from collections import deque
from typing import Dict, List, NamedTuple, Tuple
from treelib import Tree
import random
import itertools
import heapq

'''
Helper Class to contain the results
'''

class GameResult(NamedTuple):
    status: str
    winners: List[int]
    tied_players: List[int]
    losers: List[int]

'''
Initial board states for 1v1v1v1 and 1v1
'''
initial_pos: List[List[int]] = [
    [1,1,0,2,2],
    [1,0,0,0,2],
    [0,0,0,0,0],
    [4,0,0,0,3],
    [4,4,0,3,3]
]

initial_pos_1v1: List[List[int]] = [
    [1,1,0,0,0],
    [1,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,2],
    [0,0,0,2,2]
]


'''
Win cells per player for 1v1v1v1 and 1v1
'''
win_cells_all: Dict[int, List[Tuple[int, int]]] = {
    1: [(3, 4), (4, 3), (4, 4)],  # E4, D5, E5
    2: [(3, 0), (4, 0), (4, 1)],  # A4, A5, B5
    3: [(0, 0), (0, 1), (1, 0)],  # A1, B1, A2
    4: [(0, 3), (0, 4), (1, 4)]   # D1, E1, E2
}


win_cells_1v1: Dict[int, List[Tuple[int, int]]] = {
    1: [(3, 4), (4, 3), (4, 4)],  # E4, D5, E5
    2: [(0, 0), (0, 1), (1, 0)]   # A1, B1, A2
}

'''
Converts Board State to a bytes object for faster comparisons
'''
def to_bytes(board: List[List[int]]) -> bytes:
    return bytes(itertools.chain.from_iterable(board))

'''
Utility function to parse input string and transform it into Tuple
'''
def parse_position(position: str) -> Tuple[int, int]:
    position = position.strip().lower()

    if len(position) != 2:
        raise ValueError(
            f"Invalid position '{position}'. Expected something like 'a4'."
        )

    column_character: str = position[0]
    row_character: str = position[1]

    if column_character not in "abcde":
        raise ValueError("Column must be between 'a' and 'e'.")

    if row_character not in "12345":
        raise ValueError("Row must be between 1 and 5.")

    column: int = ord(column_character) - ord("a")
    row: int = int(row_character) - 1

    return row, column

'''
Utility function to parse a Tuple (like [0,2] back into a positon (a, 3) 
'''
def reverse_parse_position(pos: Tuple[int, int]) -> str:
    row, col = pos
    col_char = chr(ord("A") + col)
    row_char = str(row + 1)
    return f"{col_char}{row_char}"

'''
Calculate score based off some heuristics, for now lets just use manhattan distance
'''
def calculate_heuristic_score(player: int, oldPos: Tuple[int, int], newPos: Tuple[int, int]) -> int:
    # best is the most distance that gets us close to the solution
    # assume 1v1 map for now? 

    win_cells = win_cells_1v1[player]
    goal = win_cells[0]

    score = abs(sum(newPos) - sum(oldPos))

    if abs(sum(goal) - sum(oldPos)) < abs(sum(goal) - sum(newPos)):
        score *= -1

    return score


'''
This function detects if the move is legal according to the rulles specified in the assignment
'''
def check_legal_move(
    board: List[List[int]],
    oldPos: Tuple[int, int],
    newPos: Tuple[int, int]
) -> bool:
    
    rest: Tuple[int, int] = tuple(
        map(lambda i, j: abs(i - j), oldPos, newPos)
    )

    # Only one piece may occupy a square.
    if board[newPos[0]][newPos[1]] != 0:
        return False

    # Move one square horizontally or vertically.
    if rest in [(0, 1), (1, 0)]:
        return True

    # Jump exactly two squares horizontally or vertically.
    if rest in [(0, 2), (2, 0)]:
        middlePos: Tuple[int, int] = (
            (oldPos[0] + newPos[0]) // 2,
            (oldPos[1] + newPos[1]) // 2
        )

        # Any piece, including an opponent's piece, may be jumped over.
        if board[middlePos[0]][middlePos[1]] != 0:
            return True

    return False

'''
This function executes the move, if it has been executed it will return True, if not False
'''
def move(
    board: List[List[int]],
    oldPos: Tuple[int, int],
    newPos: Tuple[int, int],
    player: int
) -> bool:
    try:
        assert player in [1, 2, 3, 4], \
            f"Player {player} is not a valid player"

        assert len(board) > 0 and len(board[0]) > 0, \
            "The board is empty"

        assert (
            0 <= oldPos[0] < len(board)
            and 0 <= oldPos[1] < len(board[oldPos[0]])
        ), "Old position is out of bounds"

        assert (
            0 <= newPos[0] < len(board)
            and 0 <= newPos[1] < len(board[newPos[0]])
        ), "New position is out of bounds"

        assert board[oldPos[0]][oldPos[1]] == player, \
            f"Player {player} selected a cell containing " \
            f"{board[oldPos[0]][oldPos[1]]}"

    except AssertionError as e:
        print(e)
        return False

    legal: bool = check_legal_move(board, oldPos, newPos)

    if not legal:
        return False

    board[newPos[0]][newPos[1]] = player
    board[oldPos[0]][oldPos[1]] = 0

    return True

'''
This Function checks for the win or tie conditions
'''
def check_win_condition(
    board: List[List[int]],
    move_count: int,
    maximum_move_limit: int,
    all_players: bool
) -> GameResult:
    if maximum_move_limit <= 0:
        raise ValueError("Maximum move limit must be greater than zero")

    if move_count < 0:
        raise ValueError("Move count cannot be negative")

    if all_players:
        win_cells: Dict[int, List[Tuple[int, int]]] = win_cells_all
    else:
        win_cells = win_cells_1v1

    active_players: List[int] = list(win_cells.keys())
    winners: List[int] = []

    # First check whether any player has reached their end zone.
    for player in active_players:
        player_has_won: bool = all(
            board[row][column] == player
            for row, column in win_cells[player]
        )

        if player_has_won:
            winners.append(player)

    if winners:
        return GameResult(
            status="winner",
            winners=winners,
            tied_players=[],
            losers=[
                player
                for player in active_players
                if player not in winners
            ]
        )

    # The game continues while the move limit has not been reached.
    if move_count < maximum_move_limit:
        return GameResult(
            status="ongoing",
            winners=[],
            tied_players=[],
            losers=[]
        )

    # The move limit has been reached.
    losers: List[int] = []

    # If turn limit is reached and a player has their pieces in another 
    # players end zone then that player is declared a loser and everyone else tied_players
    # this is to prevent blocking strategies
    for player in active_players:
        is_blocking: bool = False

        for other_player in active_players:
            if player == other_player:
                continue

            for row, column in win_cells[other_player]:
                if board[row][column] == player:
                    is_blocking = True
                    break

            if is_blocking:
                break

        if is_blocking:
            losers.append(player)

    tied_players: List[int] = [
        player
        for player in active_players
        if player not in losers
    ]

    return GameResult(
        status="move_limit",
        winners=[],
        tied_players=tied_players,
        losers=losers
    )
    

def random_bot(
    board: List[List[int]],
    player: int,
    visualize_tree: bool
) -> Tuple[str, str]:
    if player not in [1, 2, 3, 4]:
        raise ValueError(f"Player {player} is not a valid player")

    if len(board) != 5 or any(len(row) != 5 for row in board):
        raise ValueError("Board must be 5 by 5")

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

    if not legal_moves:
        raise ValueError(f"Player {player} has no legal moves")

    oldPos, newPos = random.choice(legal_moves)

    if visualize_tree:
        print("Random bot: no minimax search tree to visualize.")

    old_reference: str = chr(ord("A") + oldPos[1]) + str(oldPos[0] + 1)
    new_reference: str = chr(ord("A") + newPos[1]) + str(newPos[0] + 1)

    return old_reference, new_reference

def illegal_bot(
    board: List[List[int]],
    player: int,
    visualize_tree: bool
) -> Tuple[str, str]:
    if player not in [1, 2, 3, 4]:
        raise ValueError(f"Player {player} is not valid")

    for row in range(5):
        for column in range(5):
            if board[row][column] == player:
                position: str = (
                    chr(ord("A") + column)
                    + str(row + 1)
                )

                if visualize_tree:
                    print(
                        f"Illegal bot attempts: "
                        f"{position} -> {position}"
                    )

                return position, position

    raise ValueError(f"Player {player} has no pieces")
    
def searchTree_bot(
    board: List[List[int]],
    player: int,
    visualize_tree: bool
) -> Tuple[str, str]:

    # Basic idea for rn:
    # we'll generate a whole buncha alternative realities until we find one where the bot wins - Dr Strange
    # then we'll pick the next move according to that, after player makes their move we need to repeat
    # the whole process again

    # Use current board postion as root node
    
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
