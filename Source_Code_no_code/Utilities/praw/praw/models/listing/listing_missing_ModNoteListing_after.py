"""Provide the Listing class."""
from typing import Any, Optional

from ..base import PRAWBase


class Listing(PRAWBase):
    """A listing is a collection of :class:`.RedditBase` instances."""

    AFTER_PARAM = "after"
    CHILD_ATTRIBUTE = "children"

    def __getitem__(self, index: int) -> Any:
        """Return the item at position index in the list."""
        return getattr(self, self.CHILD_ATTRIBUTE)[index]

    def __len__(self) -> int:
        """Return the number of items in the Listing."""
        return len(getattr(self, self.CHILD_ATTRIBUTE))

    def __setattr__(self, attribute: str, value: Any):
        """Objectify the ``CHILD_ATTRIBUTE`` attribute."""
        if attribute == self.CHILD_ATTRIBUTE:
            value = self._reddit._objector.objectify(value)
        super().__setattr__(attribute, value)


class FlairListing(Listing):
    """Special Listing for handling flair lists."""

    CHILD_ATTRIBUTE = "users"

    @property
    def after(self) -> Optional[Any]:
        """Return the next attribute or ``None``."""
        return getattr(self, "next", None)


class ModNoteListing(Listing):
    """Special Listing for handling :class:`.ModNote` lists."""

    AFTER_PARAM = "before"
    CHILD_ATTRIBUTE = "mod_notes"

    @property
    def after(self) -> Optional[Any]:
        """This method returns the next attribute or None based on the condition. If the "has_next_page" attribute is False, it returns None. Otherwise, it returns the "end_cursor" attribute.
        Input-Output Arguments
        :param self: ModNoteListing. An instance of the ModNoteListing class.
        :return: Optional[Any]. The next attribute or None.
        """


class ModeratorListing(Listing):
    """Special Listing for handling moderator lists."""

    CHILD_ATTRIBUTE = "moderators"


class ModmailConversationsListing(Listing):
    """Special Listing for handling :class:`.ModmailConversation` lists."""

    CHILD_ATTRIBUTE = "conversations"

    @property
    def after(self) -> Optional[str]:
        """Return the next attribute or ``None``."""
        try:
            return self.conversations[-1].id
        except IndexError:
            return None