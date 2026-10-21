
class ChainFinder(object):
    def __init__(self):
        self.parent_lookup = {}
        self.descendents_by_top = {}
        self.trees_from_bottom = {}

    def __repr__(self):
        return "<ChainFinder: trees_fb:%s d_b_tops:%s>" % (self.trees_from_bottom, self.descendents_by_top)

    def load_nodes(self, nodes):
        # register everything
        new_hashes = set()
        for h, parent in nodes:
            if h in self.parent_lookup:
                continue
            self.parent_lookup[h] = parent
            new_hashes.add(h)
        if new_hashes:
            self.meld_new_hashes(new_hashes)

    def meld_new_hashes(self, new_hashes):
        # make a list
        while len(new_hashes) > 0:
            h = new_hashes.pop()
            path = [h]
            while 1:
                h = self.parent_lookup.get(h)
                if h is None:
                    break
                new_hashes.discard(h)
                preceding_path = self.trees_from_bottom.get(h)
                if preceding_path:
                    del self.trees_from_bottom[h]
                    path.extend(preceding_path)
                    # we extended an existing path. Fix up descendents_by_top
                    self.descendents_by_top[preceding_path[-1]].remove(preceding_path[0])
                    break
                path.append(h)
            self.trees_from_bottom[path[0]] = path

            # if len(path) <= 1:
            #    # this is a lone element... don't bother trying to extend
            #    continue

            # now, perform extensions on any trees that start below here

            bottom_h, top_h = path[0], path[-1]

            top_descendents = self.descendents_by_top.setdefault(top_h, set())
            bottom_descendents = self.descendents_by_top.get(bottom_h)
            if bottom_descendents:
                for descendent in bottom_descendents:
                    prior_path = self.trees_from_bottom[descendent]
                    prior_path.extend(path[1:])
                    if path[0] in self.trees_from_bottom:
                        del self.trees_from_bottom[path[0]]
                    else:
                        pass  # TODO: improve this
                del self.descendents_by_top[bottom_h]
                top_descendents.update(bottom_descendents)
            else:
                top_descendents.add(bottom_h)

    def all_chains_ending_at(self, h):
        for bottom_h in self.descendents_by_top.get(h, []):
            yield self.trees_from_bottom[bottom_h]

    def missing_parents(self):
        return self.descendents_by_top.keys()

    def maximum_path(self, h, cache={}):
        v = self.trees_from_bottom.get(h)
        if v:
            return v
        h1 = h
        v = []
        while h1 is not None:
            v.append(h1)
            h1 = self.parent_lookup.get(h1)
        for i, h1 in enumerate(v):
            cache[h1] = v[i:]
        return v

    def find_ancestral_path(self, h1, h2, path_cache={}):
        """Find the ancestral path between two nodes in a chain.
        
        Input-Output Arguments
        :param h1: The first node in the chain.
        :param h2: The second node in the chain.
        :param path_cache: Dict, a dictionary that caches computed paths. It is optional and defaults to an empty dictionary.
        :return: Tuple, a tuple containing two lists. The first list is the ancestral path from h1 to the common ancestor. The second list is the ancestral path from h2 to the common ancestor.
        
        """