import argparse
import ast


def io_parser():
    parser = argparse.ArgumentParser(description='Input and output files')
    parser.add_argument('indir', type=str, help='Input file dir')
    parser.add_argument('outdir', type=str, help='Output file dir')
    args = parser.parse_args()
    return args.indir, args.outdir


def r_file(file):
    with open(file, 'r', errors='replace') as f:
        text = f.read()
    return text


def r_file_line(file):
    with open(file, 'r') as f:
        orig, plag = f.readline().split()
    return orig, plag


def w_in_file(file, value):
    with open(file, 'a') as f:
        f.write(str(value))


class FileManager:
    def __init__(self):
        self.input_file, self.output_file = io_parser()
        self.input_origin = None
        self.input_plagiat = None
        self._cur_original_txt = None
        self._cur_plagiat_txt = None

    def next_text(self):
        self.input_origin, self.input_plagiat = r_file_line(self.input_file)
        self._cur_original_txt = r_file(self.input_origin)
        self._cur_plagiat_txt = r_file(self.input_plagiat)

    @property
    def orig(self):
        return self._cur_original_txt

    @orig.setter
    def orig(self, value):
        self._cur_original_txt = value

    @property
    def plag(self):
        return self._cur_plagiat_txt

    @plag.setter
    def plag(self, value):
        self._cur_plagiat_txt = value


class Visitor(ast.NodeVisitor):
    
    def __init__(self):
        self.list = set()

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.list.add(node.id)


class Normalize(ast.NodeTransformer):   # trou
    les
    """
        def visit_Name(self, node):
        if True:    # change if
            return ast.Subscript(
                value=ast.Name(id='y_new', ctx=node.ctx),
                slice=ast.Index(value=ast.Constant(value='something')),
                ctx=node.ctx
            )
    """

    def visit_FunctionDef(self, node):  # deletes annotations
        for i in node.args.args:
            if i.annotation is not None:
                i.annotation = None
        return node


def processed_prog_text(text):
    tree = ast.parse(text)
    tree = ast.fix_missing_locations(Normalize().visit(tree))
    processed_text = ast.unparse(tree)
    return processed_text


def Leven_distance(s1, s2):
    lent1, lent2 = len(s1), len(s2)
    if lent1 > lent2:
        s1, s2 = s2, s1
        lent1, lent2 = lent2, lent1

    cur = range(lent1 + 1)
    for i in range(1, lent2 + 1):
        prev = cur
        cur = [i] + [0] * lent1

        for j in range(1, lent1 + 1):
            add = prev[j] + 1
            delete = cur[j - 1] + 1
            change = prev[j - 1]

            if s1[j - 1] != s2[i - 1]:
                change += 1

            cur[j] = min(add, delete, change)

    return cur[lent1]


def damerau_levenshtein_distance(s1, s2):
    len1 = len(s1)
    len2 = len(s2)
    distance = [[0 for i in range(len2 + 1)] for j in range(len1 + 1)]

    for i in range(len1 + 1):
        distance[i][0] = i

    for j in range(len2 + 1):
        distance[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):

            if s1[i - 1] == s2[j - 1]:
                cost = 0
            else:
                cost = 1

            distance[i][j] = min(
                distance[i - 1][j] + 1,  # delete
                distance[i][j - 1] + 1,  # add
                distance[i - 1][j - 1] + cost,  # change
            )

            if i - 1 and j - 1 and s1[i - 1] == s2[j - 2] and s1[i - 2] == s2[j - 1]:
                distance[i][j] = min(distance[i][j], distance[i - 2][j - 2] + 1)  # transpose

    for i in distance:
        print(i)
    return distance[-1][-1]


def run():
    a = FileManager()

    for line in open(a.input_file, 'r'):
        a.input_origin, a.input_plagiat = line.split()
        a.orig = r_file(a.input_origin)
        a.plag = r_file(a.input_plagiat)
        print(a.input_origin)

        try:
            a.orig = processed_prog_text(a.orig)
            a.plag = processed_prog_text(a.plag)
        except SyntaxError:
            pass

        difference = Leven_distance(a.orig, a.plag)
        maxlen = len(max(a.orig, a.plag))
        if maxlen == 0:
            result = 1.0
            w_in_file(a.output_file, result)
            continue

        result = round((maxlen - difference) / maxlen, 4)
        w_in_file(a.output_file, result)


run()
