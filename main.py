#https://graphviz.readthedocs.io/en/stable/examples.html

import zlib
import graphviz
import sys

repo_path = sys.argv[1]

def getContent(sha):
    sys_folder = sha[:2]
    nameOfCommit = sha[2:]
    path = repo_path + '/.git/objects/' + sys_folder + '/' + nameOfCommit
    f = open(path, 'rb').read()
    bin_str = zlib.decompress(f)
    return bin_str

def splitTree(contentTree):

    files = []

    files_string = contentTree.split(b'\x00', maxsplit=1)[1]

    while len(files_string) > 0:
        parts = files_string.split(maxsplit=1)[1].split(b'\x00', maxsplit=1)
        fileName = parts[0].decode('utf-8')
        sha = parts[1][:20].hex()
        files_string = parts[1][20:]
        files.append({'fileName': fileName, 'sha': sha})
    return files

def addTree(tree, parent_id):
    contentTree = getContent(tree)
    files = splitTree(contentTree)

    for i in range(len(files)):
        fileName = files[i]['fileName']
        sha = files[i]['sha']
        id = files[i]['sha'] + fileName

        type = getContent(sha).split()[0].decode('utf-8')

        if type == 'tree':
            graph.node(id, fileName, shape='doublecircle')
        else:
            graph.node(id, fileName, shape='circle')
        graph.edge(parent_id, id)

        if type == 'tree':
            addTree(sha, id)
        else:
            content = getContent(sha)
            text = content.split(maxsplit=1)[1].split(b'\x00', maxsplit=1)[1].decode('utf-8')
            if len(text) > 0:
                graph.node(id + 'text', text)
                graph.edge(id, id + 'text')


graph = graphviz.Digraph(format='png', strict=True)

head = open(repo_path + '/.git/logs/HEAD')
lines = head.readlines()

for i in range(len(lines)):
    parent = lines[i][:40]
    commit = lines[i][41:81]
    nameOfCommit = lines[i].split()[-1]

    graph.node(commit, nameOfCommit, color='yellow', style='filled', shape='square')
    
    if (parent != '0'*40):
        graph.edge(parent, commit)

    commit_content = getContent(commit).decode('utf-8')
    tree = commit_content.split()[2][:40]
    
    addTree(tree, commit)
    

graph.render('output.dot', view=True)




















