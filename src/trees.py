"""
Инструментарий для работы с деревьями. Нечеткое сравнение деревьев.
"""


class Tree:
    def __init__(self, root, parent=None, kids=None):
        self.root = root
        self.parent = parent
        kids_type = type(kids)
        if kids_type is Tree:
            self.kids = [kids]
        elif kids_type is list:
            self.kids = kids
        elif kids is None:
            self.kids = None
        else:
            raise Exception('Kids can only be Tree or list of Tree')

    def add_kids(self, kids):
        """
        Add one object of class Tree or list of trees to kids.
        Добавляет экземпляр класса Tree или их списка к детям.
        """
        if self.kids is None:
            kids_type = type(kids)
            if kids_type is Tree:
                self.kids = [kids]
            elif kids_type is list:
                self.kids = kids
            elif kids is None:
                self.kids = None
            else:
                raise Exception('Kids can only be Tree or list of Tree')
        elif type(kids) is Tree:
            self.kids.append(kids)
        elif type(kids) is list:
            self.kids += kids

    def to_dict(self):
        """
        Simply convert tree to dict.
        Просто конвертирует дерево в dict.
        """
        if self.kids is not None:
            dic = {self.root: [kid.to_dict() for kid in self.kids]}
        else:
            dic = self.root
        return dic


def dict_to_tree(source, parent=None):
    """
    Convert tree from dict 'source' to tree of class Tree with parent 'parent'.
    Конвертирует дерево source из dict в дерево класса Tree с родителем parent.
    """
    if type(source) is dict:
        keys = list(source.keys())
        if len(keys) > 1:
            print(keys)
            raise Exception('Source is not a tree')
        root = keys[0]
        value = source[root]
        tree = Tree(root, parent)
        if type(value) is dict:
            kid_tree = dict_to_tree(value, tree)
            if kid_tree is not None:
                tree.add_kids(kid_tree)
            else:
                return None
        elif type(value) is list:
            kids = []
            for kid in value:
                kid_tree = dict_to_tree(kid, tree)
                if kid_tree is not None:
                    kids.append(kid_tree)
            if not kids:
                return None
            else:
                tree.add_kids(kids)
        elif value is not None:
            tree.add_kids(Tree(value, tree))
        else:
            return None
        return tree
    else:
        assert type(source) is not list
        return Tree(source, parent)


def preorder_traversal(tree):
    """
    Возвращает список узлов дерева tree, обходя его в прямом порядке.
    """
    nodes = [tree]
    if tree.kids is not None:
        for kid in tree.kids:
            nodes += preorder_traversal(kid)
    return nodes


def get_leaves(tree):
    """
    Возвращает список листьев дерева tree.
    """
    leaves = []
    if tree.kids is not None:
        for kid in tree.kids:
            leaves += get_leaves(kid)
    else:
        return [tree]
    return leaves


def count_all_nodes(tree):
    """
    Возвращает количество всех узлов дерева tree.
    """
    count = 1
    if tree.kids is not None:
        for kid in tree.kids:
            count += count_all_nodes(kid)
    return count


def get_height(tree):
    """
    Возвращает высоту дерева tree.
    """
    height = 1
    if tree.kids is not None:
        height += max([get_height(kid) for kid in tree.kids])
    return height


def nodes(tree):
    """
    Генератор для получения узлов дерева tree.
    """
    yield tree.root
    if tree.kids is not None:
        for kid in tree.kids:
            for node_root in nodes(kid):
                yield node_root


def adjacency(tree):
    """
    Возвращает dict, где ключи - узлы дерева tree, значения - списки смежности.
    """
    d = {tree: []}
    if tree.parent is not None:
        d[tree].append(tree.parent)
    if tree.kids:
        d[tree].extend(tree.kids)
        for kid in tree.kids:
            d.update(adjacency(kid))
    return d


def compare_trees(tree1, tree2):
    """
    Возвращает коэффициент схожести деревьев tree1, tree2
    """
    adjacency1 = adjacency(tree1)
    adjacency2 = adjacency(tree2)
    nodes1 = preorder_traversal(tree1)
    nodes2 = preorder_traversal(tree2)
    neighbors_degrees1 = {}
    neighborhood_count1 = {}
    degrees1 = {}
    neighbors_degrees2 = {}
    neighborhood_count2 = {}
    degrees2 = {}
    for node2 in nodes2:
        kv = list(neighborhood(node2, 3))
        neighbors_degrees2[node2] = sorted([len([i for i in adjacency2[node]
                      if i in kv or i == node2]) for node in kv], reverse=True)
        neighborhood_count2[node2] = len(kv)
        degrees2[node2] = len(adjacency2[node2])
    for node1 in nodes1:
        ku = list(neighborhood(node1, 3))
        neighbors_degrees1[node1] = sorted([len([i for i in adjacency1[node]
                      if i in ku or i == node1]) for node in ku], reverse=True)
        neighborhood_count1[node1] = len(ku)
        degrees1[node1] = len(adjacency1[node1])
    result = []
    for node1 in nodes1:
        du = degrees1[node1]
        d1 = neighbors_degrees1[node1]
        nku = neighborhood_count1[node1]
        for node2 in nodes2:
            dv = degrees2[node2]
            d2 = neighbors_degrees2[node2]
            nkv = neighborhood_count2[node2]
            nmin = min(nku, nkv)
            duv = (min(du, dv) + sum([min(d1[i], d2[i])
                                      for i in range(nmin)])) / 2
            sim = (nmin + 1 + duv) * (nmin + 1 + duv) /\
                    ((2 * nku + 1) * (2 * nkv + 1))
            if sim > 0.9:
                if node1.root == node2.root:
                    result.append((node1, node2, sim))
                elif len(neighborhood(node1, 1)) == \
                        len(neighborhood(node2, 1)) == 1:
                    result.append((node1, node2, sim))
    result.sort(key=lambda x: x[2], reverse=True)
    s = {}
    ss = set()
    for pair in result:
        node1, node2 = pair[0], pair[1]
        if node1 not in s and node2 not in ss:
            s[node1] = node2
            ss = ss | {node2}
    p = [(item[0].root, item[1].root) for item in s.items()]
    return len(p) * 2 / ((len(nodes1) + len(nodes2)))


def neighborhood(node, k):
    """
    Возвращает множество узлов k-окрестности узла node.
    """
    if k == 0:
        return set()
    elif k > 0:
        tmp = []
        parent = node.parent
        kids = node.kids
        if parent is not None:
            tmp.append(parent)
            tmp.extend(neighborhood(parent, k - 1))
        if kids is not None:
            for kid in kids:
                tmp.append(kid)
                tmp.extend(neighborhood(kid, k - 1))
        return set(tmp) - {node}
