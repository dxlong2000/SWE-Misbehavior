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
    """ This is a pre-flight check function that will completely ignore
        recipe order or choosing an actual value in any of the multiple
        choice tuples/dependencies, and just do a very basic obvious
        conflict check.
    """
    deps_were_added_by = dict()
    deps = set()
    if blacklist is None:
        blacklist = set()

    # Add dependencies for all recipes:
    to_be_added = [(name_tuple, None) for name_tuple in name_tuples]
    while len(to_be_added) > 0:
        current_to_be_added = list(to_be_added)
        to_be_added = []
        for (added_tuple, adding_recipe) in current_to_be_added:
            assert type(added_tuple) is tuple
            if len(added_tuple) > 1:
                # No obvious commitment in what to add, don't check it itself
                # but throw it into deps for later comparing against
                # (Remember this function only catches obvious issues)
                deps.add(added_tuple)
                continue

            name = added_tuple[0]
            recipe_conflicts = set()
            recipe_dependencies = []
            try:
                # Get recipe to add and who's ultimately adding it:
                recipe = Recipe.get_recipe(name, ctx)
                recipe_conflicts = {c.lower() for c in recipe.conflicts}
                recipe_dependencies = get_dependency_tuple_list_for_recipe(
                    recipe, blacklist=blacklist
                )
            except ValueError:
                pass
            adder_first_recipe_name = adding_recipe or name

            # Collect the conflicts:
            triggered_conflicts = []
            for dep_tuple_list in deps:
                # See if the new deps conflict with things added before:
                if set(dep_tuple_list).intersection(
                       recipe_conflicts) == set(dep_tuple_list):
                    triggered_conflicts.append(dep_tuple_list)
                    continue

                # See if what was added before conflicts with the new deps:
                if len(dep_tuple_list) > 1:
                    # Not an obvious commitment to a specific recipe/dep
                    # to be added, so we won't check.
                    # (remember this function only catches obvious issues)
                    continue
                try:
                    dep_recipe = Recipe.get_recipe(dep_tuple_list[0], ctx)
                except ValueError:
                    continue
                conflicts = [c.lower() for c in dep_recipe.conflicts]
                if name in conflicts:
                    triggered_conflicts.append(dep_tuple_list)

            # Throw error on conflict:
            if triggered_conflicts:
                # Get first conflict and see who added that one:
                adder_second_recipe_name = "'||'".join(triggered_conflicts[0])
                second_recipe_original_adder = deps_were_added_by.get(
                    (adder_second_recipe_name,), None
                )
                if second_recipe_original_adder:
                    adder_second_recipe_name = second_recipe_original_adder

                # Prompt error:
                raise BuildInterruptingException(
                    "Conflict detected: '{}'"
                    " inducing dependencies {}, and '{}'"
                    " inducing conflicting dependencies {}".format(
                        adder_first_recipe_name,
                        (recipe.name,),
                        adder_second_recipe_name,
                        triggered_conflicts[0]
                    ))

            # Actually add it to our list:
            deps.add(added_tuple)
            deps_were_added_by[added_tuple] = adding_recipe

            # Schedule dependencies to be added
            to_be_added += [
                (dep, adder_first_recipe_name or name)
                for dep in recipe_dependencies
                if dep not in deps
            ]
    # If we came here, then there were no obvious conflicts.
    return None


def get_recipe_order_and_bootstrap(ctx, names, bs=None, blacklist=None):
    # Get set of recipe/dependency names, clean up and add bootstrap deps:
    """This function takes in a context, a list of recipe/dependency names, an optional bootstrap instance, and an optional blacklist. It performs various operations on the input names to clean them up and add bootstrap dependencies. It then checks for conflicts and generates all possible order graphs based on the names. It converts each order graph into a linear list and sorts them based on preference. Finally, it returns the chosen order, along with the corresponding recipes, python modules, and bootstrap instance.
    Input-Output Arguments
    :param ctx: The context in which the function is being called.
    :param names: List of strings. The recipe/dependency names.
    :param bs: Bootstrap instance. An optional bootstrap instance. Defaults to None.
    :param blacklist: Set of strings. An optional set of names to be blacklisted. Defaults to None.
    :return: Tuple. The chosen order of dependencies, the corresponding recipes, python modules, and bootstrap instance.
    """