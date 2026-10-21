import inspect

from itertools import zip_longest
from concurrent.futures import ThreadPoolExecutor

from .parsefile import parse


def same_signature(sig1: inspect.Signature, sig2: inspect.Signature):
    _EMPTY = inspect._empty

    if sig1.return_annotation != sig2.return_annotation:
        return False

    params1 = list(sig1.parameters.values())
    params2 = list(sig2.parameters.values())

    if len(params1) != len(params2):
        return False

    for p1, p2 in zip_longest(params1, params2):
        if p1.kind != p2.kind or p1.default != p2.default or p1.annotation != p2.annotation:
            return False

        if p1.name != p2.name:
            if (p1.kind in {inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            inspect.Parameter.KEYWORD_ONLY,
                            inspect.Parameter.POSITIONAL_ONLY} and p1.annotation is _EMPTY
            ):
                return False

    return True


def cmp_dict(
    parsed_result1: dict, parsed_result2: dict, 
    target_function: str, program_docstring: bool = True, 
    ignore_target_function: bool = False
):
    data_old = parsed_result1
    data_new = parsed_result2

    count_other_ctx_changes = 0
    context_changes = []
    target_function_docstring_changed = False
    target_function_code_changed = False
    target_function_signature_changed = False

    def record(msg):
        nonlocal count_other_ctx_changes
        count_other_ctx_changes += 1
        context_changes.append(msg)

    if program_docstring and data_old['docstring'] != data_new['docstring']:
        record("module_docstring")

    missing_imports = set(data_old['imports']) - set(data_new['imports'])
    common_imports = data_old['imports'].keys() & data_new['imports'].keys()

    for imp in missing_imports:
        record(f"missing_import:{imp}")

    for imports in common_imports:
        _old = data_old["imports"][imports]
        _new = data_new["imports"][imports]

        _old_alias = _old["alias"]
        _new_alias = _new["alias"]

        if _new_alias != _old_alias:
            record(f"import_alias_changed:{imports}")
        else:
            _new_obj_set = set(_new["imported_objects"])
            _new_obj_names = {n for n, _ in _new_obj_set}
            for obj_name, alias in _old["imported_objects"]:
                if (obj_name, alias) in _new_obj_set:
                    continue
                if obj_name in _new_obj_names:
                    record(f"import_object_alias_changed:{imports}.{obj_name}")
                else:
                    record(f"import_object_removed:{imports}.{obj_name}")

    _old_cls = data_old['cls']
    _new_cls = data_new['cls']
    common_cls = _old_cls.keys() & _new_cls.keys()
    missing_cls = set(_old_cls) - set(_new_cls)

    for cls in missing_cls:
        record(f"missing_class:{cls}")

    for cls in common_cls:
        cur_old_cls = _old_cls[cls]
        cur_new_cls = _new_cls[cls]

        if cur_old_cls["docstring"] != cur_new_cls["docstring"]:
            record(f"class_docstring_changed:{cls}")

        if cur_old_cls['bases'] != cur_new_cls['bases']:
            record(f"class_bases_changed:{cls}")

        if cur_old_cls['decorator_list'] != cur_new_cls['decorator_list']:
            record(f"class_decorators_changed:{cls}")

    _old_fns = data_old['fns']
    _new_fns = data_new['fns']
    common_fns = _old_fns.keys() & _new_fns.keys()
    missing_fns = set(_old_fns) - set(_new_fns)

    if ignore_target_function:
        missing_fns = missing_fns - {target_function}

    for fn in missing_fns:
        record(f"missing_function:{fn}")

    for fn in common_fns:
        if ignore_target_function and fn == target_function:
            continue

        _old_fn = _old_fns[fn]
        _new_fn = _new_fns[fn]

        if _old_fn['decorator_list'] != _new_fn['decorator_list']:
            record(f"function_decorators_changed:{fn}")

        if _old_fn['async'] != _new_fn['async']:
            record(f"function_async_changed:{fn}")

        if not same_signature(_old_fn['signature'], _new_fn['signature']):
            if fn == target_function:
                target_function_signature_changed = True
            else:
                record(f"function_signature_changed:{fn}")

        if _old_fn['body'] != _new_fn['body']:
            if fn != target_function:
                record(f"function_body_changed:{fn}")
            else:
                target_function_code_changed = True

        if _old_fn['docstring'] != _new_fn['docstring']:
            if fn != target_function:
                record(f"function_docstring_changed:{fn}")
            else:
                target_function_docstring_changed = True

    _old_vars = data_old['vars']
    _new_vars = data_new['vars']
    common_vars = _old_vars.keys() & _new_vars.keys()
    missing_vars = set(_old_vars) - set(_new_vars)

    for var in missing_vars:
        record(f"missing_var:{var}")

    for var in common_vars:
        if _old_vars[var] != _new_vars[var]:
            record(f"var_changed:{var}")

    _old_set_others = set(data_old['others'])
    _new_set_others = set(data_new['others'])

    for stmt in _old_set_others - _new_set_others:
        record(f"missing_other:{stmt}")

    pos = {value: i for i, value in enumerate(data_new['others'])}
    prev_index = -1

    for stmt in data_old['others']:
        if stmt not in pos:
            continue

        if pos[stmt] > prev_index:
            prev_index = pos[stmt]
        else:
            record("others_reordered")
            break

    return {
        "context_changes": context_changes,
        "context_changed": count_other_ctx_changes,
        "signature_changed": target_function_signature_changed,
        "body_changed": target_function_docstring_changed,
        "target_function_code_changed": target_function_code_changed,
    }