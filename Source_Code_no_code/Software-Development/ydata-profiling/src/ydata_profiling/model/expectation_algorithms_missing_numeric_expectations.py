from typing import Any, Tuple


def generic_expectations(
    name: str, summary: dict, batch: Any, *args
) -> Tuple[str, dict, Any]:
    batch.expect_column_to_exist(name)

    if summary["n_missing"] == 0:
        batch.expect_column_values_to_not_be_null(name)

    if summary["p_unique"] == 1.0:
        batch.expect_column_values_to_be_unique(name)

    return name, summary, batch


def numeric_expectations(
    name: str, summary: dict, batch: Any, *args
) -> Tuple[str, dict, Any]:
    """It checks the numeric expectations of the given batch and returns the name, summary, and batch.
    Input-Output Arguments
    :param name: str. The name of the column.
    :param summary: dict. The summary of the column.
    :param batch: Any. The batch of data to be checked.
    :param *args: Any. Additional arguments.
    :return: Tuple[str, dict, Any]. The name, summary, and batch.
    ```
    """


def categorical_expectations(
    name: str, summary: dict, batch: Any, *args
) -> Tuple[str, dict, Any]:
    # Use for both categorical and special case (boolean)
    absolute_threshold = 10
    relative_threshold = 0.2
    if (
        summary["n_distinct"] < absolute_threshold
        or summary["p_distinct"] < relative_threshold
    ):
        batch.expect_column_values_to_be_in_set(
            name, set(summary["value_counts_without_nan"].keys())
        )
    return name, summary, batch


def path_expectations(
    name: str, summary: dict, batch: Any, *args
) -> Tuple[str, dict, Any]:
    return name, summary, batch


def datetime_expectations(
    name: str, summary: dict, batch: Any, *args
) -> Tuple[str, dict, Any]:
    if any(k in summary for k in ["min", "max"]):
        batch.expect_column_values_to_be_between(
            name,
            min_value=summary.get("min"),
            max_value=summary.get("max"),
            parse_strings_as_datetimes=True,
        )

    return name, summary, batch


def image_expectations(
    name: str, summary: dict, batch: Any, *args
) -> Tuple[str, dict, Any]:
    return name, summary, batch


def url_expectations(
    name: str, summary: dict, batch: Any, *args
) -> Tuple[str, dict, Any]:
    return name, summary, batch


def file_expectations(
    name: str, summary: dict, batch: Any, *args
) -> Tuple[str, dict, Any]:
    # By definition within our type logic, a file exists (as it's a path that also exists)
    batch.expect_file_to_exist(name)

    return name, summary, batch