"""Storage policy."""
from typing import TYPE_CHECKING, Dict, Optional, Sequence, Type, Union

from wandb.sdk.lib.paths import FilePathStr, URIStr

if TYPE_CHECKING:
    from wandb.filesync.step_prepare import StepPrepare
    from wandb.sdk.artifacts.artifact import Artifact
    from wandb.sdk.artifacts.artifact_manifest_entry import ArtifactManifestEntry
    from wandb.sdk.internal.progress import ProgressFn


class StoragePolicy:
    @classmethod
    def lookup_by_name(cls, name: str) -> Type["StoragePolicy"]:
        """This function looks up a storage policy by its name. It iterates through the subclasses of the class and returns the subclass with the matching name. If no matching subclass is found, it raises a NotImplementedError.
        Input-Output Arguments
        :param cls: Class. The class instance.
        :param name: String. The name of the storage policy to look up.
        :return: Type["StoragePolicy"]. The subclass of the StoragePolicy with the matching name.
        """

    @classmethod
    def name(cls) -> str:
        raise NotImplementedError

    @classmethod
    def from_config(cls, config: Dict) -> "StoragePolicy":
        raise NotImplementedError

    def config(self) -> Dict:
        raise NotImplementedError

    def load_file(
        self, artifact: "Artifact", manifest_entry: "ArtifactManifestEntry"
    ) -> FilePathStr:
        raise NotImplementedError

    def store_file_sync(
        self,
        artifact_id: str,
        artifact_manifest_id: str,
        entry: "ArtifactManifestEntry",
        preparer: "StepPrepare",
        progress_callback: Optional["ProgressFn"] = None,
    ) -> bool:
        raise NotImplementedError

    async def store_file_async(
        self,
        artifact_id: str,
        artifact_manifest_id: str,
        entry: "ArtifactManifestEntry",
        preparer: "StepPrepare",
        progress_callback: Optional["ProgressFn"] = None,
    ) -> bool:
        """Async equivalent to `store_file_sync`."""
        raise NotImplementedError

    def store_reference(
        self,
        artifact: "Artifact",
        path: Union[URIStr, FilePathStr],
        name: Optional[str] = None,
        checksum: bool = True,
        max_objects: Optional[int] = None,
    ) -> Sequence["ArtifactManifestEntry"]:
        raise NotImplementedError

    def load_reference(
        self,
        manifest_entry: "ArtifactManifestEntry",
        local: bool = False,
    ) -> Union[FilePathStr, URIStr]:
        raise NotImplementedError