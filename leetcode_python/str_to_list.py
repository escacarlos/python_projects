l = ["Carlos", "Karely", "Gael", "Alissa"]
w = l[0]
lc0 = list(w)
lc1 = list(map(str, w))
lc2 = [i for i in w]
lc3 = [i for a, i in enumerate(w)]
lc4 = list(w.split())
lc5 = []
lc5[:0] = w
import re
lc6 = re.findall('[a-zA-Z]',w)
lc7 = list(filter(lambda i:(i in w), w))
import json
ini_list='["Carlos", 2, "for", 4, "karely", "Alissa", "Gael"]'
lc8 = json.loads(ini_list)
import ast
lc9 = ast.literal_eval(ini_list)
print(lc2)

