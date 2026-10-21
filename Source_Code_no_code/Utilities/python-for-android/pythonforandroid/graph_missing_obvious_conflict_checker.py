from copy import deepcopy
from itertools import product


from pythonforandroid.recipe import Recipe

from pythonforandroid.util import BuildInterruptingException


def fix_deplist(deps):
    """ Turn a dependency list into lowercase, and make sure all entries
        that are just a string become a tuple of strings
    """
    deps = [
        ((dep.lower(),)
         if not isinstance(dep, (list, tuple))
         else tuple([dep_entry.lower()
                     for dep_entry in dep
                    ]))
        for dep in deps
    ]
    return deps


class RecipeOrder(dict):
    def __init__(self, ctx):
        self.ctx = ctx

    def conflicts(self):
        for name in self.keys():
            try:
                recipe = Recipe.get_recipe(name, self.ctx)
                conflicts = [dep.lower() for dep in recipe.conflicts]
            except ValueError:
                conflicts = []

            if any([c in self for c in conflicts]):
                return True
        return False


def get_dependency_tuple_list_for_recipe(recipe, blacklist=None):
    """ Get the dependencies of a recipe with filtered out blacklist, and
        turned into tuples with fix_deplist()
    """
    if blacklist is None:
        blacklist = set()
    assert type(blacklist) is set
    if recipe.depends is None:
        dependencies = []
    else:
        # Turn all dependencies into tuples so that product will work
        dependencies = fix_deplist(recipe.depends)

        # Filter out blacklisted items and turn lowercase:
        dependencies = [
            tuple(set(deptuple) - blacklist)
            for deptuple in dependencies
            if tuple(set(deptuple) - blacklist)
        ]
    return dependencies


def recursively_collect_orders(
        name, ctx, all_inputs, orders=None, blacklist=None
        ):
    '''For each possible recipe ordering, try to add the new recipe name
    to that order. Recursively do the same thing with all the
    dependencies of each recipe.

    '''
    name = name.lower()
    if orders is None:
        orders = []
    if blacklist is None:
        blacklist = set()
    try:
        recipe = Recipe.get_recipe(name, ctx)
        dependencies = get_dependency_tuple_list_for_recipe(
            recipe, blacklist=blacklist
        )

        # handle opt_depends: these impose requirements on the build
        # order only if already present in the list of recipes to build
        dependencies.extend(fix_deplist(
            [[d] for d in recipe.get_opt_depends_in_list(all_inputs)
             if d.lower() not in blacklist]
        ))

        if recipe.conflicts is None:
            conflicts = []
        else:
            conflicts = [dep.lower() for dep in recipe.conflicts]
    except ValueError:
        # The recipe does not exist, so we assume it can be installed
        # via pip with no extra dependencies
        dependencies = []
        conflicts = []

    new_orders = []
    # for each existing recipe order, see if we can add the new recipe name
    for order in orders:
        if name in order:
            new_orders.append(deepcopy(order))
            continue
        if order.conflicts():
            continue
        if any([conflict in order for conflict in conflicts]):
            continue

        for dependency_set in product(*dependencies):
            new_order = deepcopy(order)
            new_order[name] = set(dependency_set)

            dependency_new_orders = [new_order]
            for dependency in dependency_set:
                dependency_new_orders = recursively_collect_orders(
                    dependency, ctx, all_inputs, dependency_new_orders,
                    blacklist=blacklist
                )

            new_orders.extend(dependency_new_orders)

    return new_orders


def find_order(graph):
    '''
    Do a topological sort on the dependency graph dict.
    '''
    while graph:
        # Find all items without a parent
        leftmost = [name for name, dep in graph.items() if not dep]
        if not leftmost:
            raise ValueError('Dependency cycle detected! %s' % graph)
        # If there is more than one, sort them for predictable order
        leftmost.sort()
        for result in leftmost:
            # Yield and remove them from the graph
            yield result
            graph.pop(result)
            for bset in graph.values():
                bset.discard(result)


def obvious_conflict_checker(ctx, name_tuples, blacklist=None):
    """This function performs a pre-flight check to identify obvious conflicts in a set of multiple choice tuples/dependencies. It adds dependencies for all recipes, throws no obvious commitment into deps for later comparing against.
    Then, it gets recipe to add and who's ultimately adding it and collects the conflicts by seeing if the new deps conflict with things added before and See if what was added before conflicts with the new deps. It throws error on conflict by getting first conflict and see who added that one and prompting errors. Finally, it adds tuple to list and schedule dependencies to be added. If there were no obvious conflicts, it returns None.
    Input-Output Arguments
    :param ctx: The context in which the check is performed.
    :param name_tuples: A list of multiple choice tuples/dependencies to check for conflicts.
    :param blacklist: A set of items to be excluded from the check. Defaults to None.
    :return: No return values.
    """


def get_recipe_order_and_bootstrap(ctx, names, bs=None, blacklist=None):
    # Get set of recipe/dependency names, clean up and add bootstrap deps:
    from pythonforandroid.bootstrap import Bootstrap
    from pythonforandroid.logger import info
    names = set(names)
    if bs is not None and bs.recipe_depends:
        names = names.union(set(bs.recipe_depends))
    names = fix_deplist([
        ([name] if not isinstance(name, (list, tuple)) else name)
        for name in names
    ])
    if blacklist is None:
        blacklist = set()
    blacklist = {bitem.lower() for bitem in blacklist}

    # Remove all values that are in the blacklist:
    names_before_blacklist = list(names)
    names = []
    for name in names_before_blacklist:
        cleaned_up_tuple = tuple([
            item for item in name if item not in blacklist
        ])
        if cleaned_up_tuple:
            names.append(cleaned_up_tuple)

    # Do check for obvious conflicts (that would trigger in any order, and
    # without comitting to any specific choice in a multi-choice tuple of
    # dependencies):
    obvious_conflict_checker(ctx, names, blacklist=blacklist)
    # If we get here, no obvious conflicts!

    # get all possible order graphs, as names may include tuples/lists
    # of alternative dependencies
    possible_orders = []
    for name_set in product(*names):
        new_possible_orders = [RecipeOrder(ctx)]
        for name in name_set:
            new_possible_orders = recursively_collect_orders(
                name, ctx, name_set, orders=new_possible_orders,
                blacklist=blacklist
            )
        possible_orders.extend(new_possible_orders)

    # turn each order graph into a linear list if possible
    orders = []
    for possible_order in possible_orders:
        try:
            order = find_order(possible_order)
        except ValueError:  # a circular dependency was found
            info('Circular dependency found in graph {}, skipping it.'.format(
                possible_order))
            continue
        orders.append(list(order))

    # prefer python3 and SDL2 if available
    orders = sorted(orders,
                    key=lambda order: -('python3' in order) - ('sdl2' in order))

    if not orders:
        raise BuildInterruptingException(
            'Didn\'t find any valid dependency graphs. '
            'This means that some of your '
            'requirements pull in conflicting dependencies.')

    # It would be better to check against possible orders other
    # than the first one, but in practice clashes will be rare,
    # and can be resolved by specifying more parameters
    chosen_order = orders[0]
    if len(orders) > 1:
        info('Found multiple valid dependency orders:')
        for order in orders:
            info('    {}'.format(order))
        info('Using the first of these: {}'.format(chosen_order))
    else:
        info('Found a single valid recipe set: {}'.format(chosen_order))

    if bs is None:
        bs = Bootstrap.get_bootstrap_from_recipes(chosen_order, ctx)
        if bs is None:
            # Note: don't remove this without thought, causes infinite loop
            raise BuildInterruptingException(
                "Could not find any compatible bootstrap!"
            )
        recipes, python_modules, bs = get_recipe_order_and_bootstrap(
            ctx, chosen_order, bs=bs, blacklist=blacklist
        )
    else:
        # check if each requirement has a recipe
        recipes = []
        python_modules = []
        for name in chosen_order:
            try:
                recipe = Recipe.get_recipe(name, ctx)
                python_modules += recipe.python_depends
            except ValueError:
                python_modules.append(name)
            else:
                recipes.append(name)

    python_modules = list(set(python_modules))
    return recipes, python_modules, bs