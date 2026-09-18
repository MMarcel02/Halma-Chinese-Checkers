# from treelib import Tree

game_tree = Tree()

game_tree.create_node("Root node", "root")
game_tree.create_node("Child1", "child1", parent="root")
game_tree.create_node("Child2", "child2", parent="root")

game_tree.show()
