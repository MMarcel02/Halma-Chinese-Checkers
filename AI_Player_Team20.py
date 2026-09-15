
from treelib import Tree
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
Calculate score just based of distance do goal
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
