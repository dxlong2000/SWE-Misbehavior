from __future__ import annotations

import abc
import logging
import math
import typing as t

from ..resource import get_resource
from ..resource import system_resources
from .runnable import Runnable

logger = logging.getLogger(__name__)


class Strategy(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def get_worker_count(
        cls,
        runnable_class: t.Type[Runnable],
        resource_request: dict[str, t.Any] | None,
        workers_per_resource: int | float,
    ) -> int:
        ...

    @classmethod
    @abc.abstractmethod
    def get_worker_env(
        cls,
        runnable_class: t.Type[Runnable],
        resource_request: dict[str, t.Any] | None,
        workers_per_resource: int | float,
        worker_index: int,
    ) -> dict[str, t.Any]:
        """
        Args:
            runnable_class : The runnable class to be run.
            resource_request : The resource request of the runnable.
            worker_index : The index of the worker, start from 0.
        """
        ...


THREAD_ENVS = [
    "BENTOML_NUM_THREAD",  # For custom Runner code
    "OMP_NUM_THREADS",  # openmp
    "OPENBLAS_NUM_THREADS",  # openblas,
    "MKL_NUM_THREADS",  # mkl,
    "VECLIB_MAXIMUM_THREADS",  # accelerate,
    "NUMEXPR_NUM_THREADS",  # numexpr
    # For huggingface fast tokenizer
    "RAYON_RS_NUM_CPUS",
    # For Tensorflow
    "TF_NUM_INTEROP_THREADS",
    "TF_NUM_INTRAOP_THREADS",
]  # TODO(jiang): make it configurable?


class DefaultStrategy(Strategy):
    @classmethod
    def get_worker_count(
        cls,
        runnable_class: t.Type[Runnable],
        resource_request: dict[str, t.Any] | None,
        workers_per_resource: int | float,
    ) -> int:
        if resource_request is None:
            resource_request = system_resources()

        # use nvidia gpu
        nvidia_gpus = get_resource(resource_request, "nvidia.com/gpu")
        if (
            nvidia_gpus is not None
            and len(nvidia_gpus) > 0
            and "nvidia.com/gpu" in runnable_class.SUPPORTED_RESOURCES
        ):
            return math.ceil(len(nvidia_gpus) * workers_per_resource)

        # use CPU
        cpus = get_resource(resource_request, "cpu")
        if cpus is not None and cpus > 0:
            if "cpu" not in runnable_class.SUPPORTED_RESOURCES:
                logger.warning(
                    "No known supported resource available for %s, falling back to using CPU.",
                    runnable_class,
                )

            if runnable_class.SUPPORTS_CPU_MULTI_THREADING:
                if isinstance(workers_per_resource, float):
                    raise ValueError(
                        "Fractional CPU multi threading support is not yet supported."
                    )
                return workers_per_resource

            return math.ceil(cpus) * workers_per_resource

        # this should not be reached by user since we always read system resource as default
        raise ValueError(
            f"No known supported resource available for {runnable_class}. Please check your resource request. "
            "Leaving it blank will allow BentoML to use system resources."
        )

    @classmethod
    def get_worker_env(
        cls,
        runnable_class: t.Type[Runnable],
        resource_request: dict[str, t.Any] | None,
        workers_per_resource: int | float,
        worker_index: int,
    ) -> dict[str, t.Any]:
        """This function is a method of the DefaultStrategy class. It is used to get the environment variables for a worker process based on the given parameters. It determines whether to use GPU or CPU based on the resource request and the runnable class. It sets the appropriate environment variables accordingly.
        Input-Output Arguments
        :param cls: DefaultStrategy. The class itself.
        :param runnable_class: Type[Runnable]. The class of the runnable to be executed.
        :param resource_request: dict[str, t.Any] | None. The resource request of the runnable. Defaults to None.
        :param workers_per_resource: int | float. The number of workers per resource. Defaults to None.
        :param worker_index: int. The index of the worker. Starts from 0.
        :return: dict[str, t.Any]. The environment variables for the worker process.
        """