from os.path import *
from pprint import pformat

def doit():
    recipes_path = expanduser("recipes.pprint")
    with open(recipes_path) as f:
        recipe_dicts = eval(f.read())
    for r in recipe_dicts:
        for key in r.keys():
            if key not in ('desc', 'comments'):
                del r[key]
        for c in r['comments']:
            for key in c.keys():
                if key not in ('comment', 'title'):
                    del c[key]

    f = open("stripped.pprint", 'w')
    f.write(pformat(recipe_dicts))
    f.close()


doit()
