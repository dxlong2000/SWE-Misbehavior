from __future__ import unicode_literals
from collections import namedtuple
from sqlparse import parse
from sqlparse.tokens import Keyword, CTE, DML
from sqlparse.sql import Identifier, IdentifierList, Parenthesis
from .meta import TableMetadata, ColumnMetadata


# TableExpression is a namedtuple representing a CTE, used internally
# name: cte alias assigned in the query
# columns: list of column names
# start: index into the original string of the left parens starting the CTE
# stop: index into the original string of the right parens ending the CTE
TableExpression = namedtuple('TableExpression', 'name columns start stop')


def isolate_query_ctes(full_text, text_before_cursor):
    """Simplify a query by converting CTEs into table metadata objects
    """

    if not full_text:
        return full_text, text_before_cursor, tuple()

    ctes, _ = extract_ctes(full_text)
    if not ctes:
        return full_text, text_before_cursor, ()

    current_position = len(text_before_cursor)
    meta = []

    for cte in ctes:
        if cte.start < current_position < cte.stop:
            # Currently editing a cte - treat its body as the current full_text
            text_before_cursor = full_text[cte.start:current_position]
            full_text = full_text[cte.start:cte.stop]
            return full_text, text_before_cursor, meta

        # Append this cte to the list of available table metadata
        cols = (ColumnMetadata(name, None, ()) for name in cte.columns)
        meta.append(TableMetadata(cte.name, cols))

    # Editing past the last cte (ie the main body of the query)
    full_text = full_text[ctes[-1].stop:]
    text_before_cursor = text_before_cursor[ctes[-1].stop:current_position]

    return full_text, text_before_cursor, tuple(meta)


def extract_ctes(sql):
    """This function extracts constant table expressions (CTEs) from a given SQL query. It parses the query using a parser and checks if the first meaningful token is "WITH", which indicates the presence of CTEs. It then extracts the CTEs from the query and returns them as a list of TableExpression namedtuples. The function also returns the remaining SQL text after the CTEs have been stripped.
    Input-Output Arguments
    :param sql: String. The SQL query from which to extract CTEs.
    :return: Tuple. The first element is a list of TableExpression namedtuples representing the extracted CTEs. The second element is the remaining SQL text after the CTEs have been stripped.
    """


def get_cte_from_token(tok, pos0):
    cte_name = tok.get_real_name()
    if not cte_name:
        return None

    # Find the start position of the opening parens enclosing the cte body
    idx, parens = tok.token_next_by(Parenthesis)
    if not parens:
        return None

    start_pos = pos0 + token_start_pos(tok.tokens, idx)
    cte_len = len(str(parens))  # includes parens
    stop_pos = start_pos + cte_len

    column_names = extract_column_names(parens)

    return TableExpression(cte_name, column_names, start_pos, stop_pos)


def extract_column_names(parsed):
    # Find the first DML token to check if it's a SELECT or INSERT/UPDATE/DELETE
    idx, tok = parsed.token_next_by(t=DML)
    tok_val = tok and tok.value.lower()

    if tok_val in ('insert', 'update', 'delete'):
        # Jump ahead to the RETURNING clause where the list of column names is
        idx, tok = parsed.token_next_by(idx, (Keyword, 'returning'))
    elif not tok_val == 'select':
        # Must be invalid CTE
        return ()

    # The next token should be either a column name, or a list of column names
    idx, tok = parsed.token_next(idx, skip_ws=True, skip_cm=True)
    return tuple(t.get_name() for t in _identifiers(tok))


def token_start_pos(tokens, idx):
    return sum(len(str(t)) for t in tokens[:idx])


def _identifiers(tok):
    if isinstance(tok, IdentifierList):
        for t in tok.get_identifiers():
            # NB: IdentifierList.get_identifiers() can return non-identifiers!
            if isinstance(t, Identifier):
                yield t
    elif isinstance(tok, Identifier):
        yield tok