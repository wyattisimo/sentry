from __future__ import annotations

import abc
from collections.abc import Mapping, Sequence
from typing import Any

from sentry.models.project import Project
from sentry.rules.actions import EventAction


class SentryAppEventAction(EventAction, abc.ABC):
    """Abstract class to ensure that actions in SENTRY_APP_ACTIONS have all required methods"""

    @property
    @abc.abstractmethod
    def actionType(self) -> str:
        pass

    @abc.abstractmethod
    def get_custom_actions(self, project: Project) -> Sequence[Mapping[str, Any]]:
        pass

    @abc.abstractmethod
    def self_validate(self) -> None:
        pass
