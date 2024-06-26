import orjson
from sentry_relay.processing import StoreNormalizer

from sentry.db.models import NodeData
from sentry.utils.canonical import CanonicalKeyDict


class EventDict(CanonicalKeyDict):
    """
    Creating an instance of this dictionary will send the event through basic
    (Rust-based) type/schema validation called "re-normalization".

    This is used as a wrapper type for `Event.data` such that creating an event
    object (or loading it from the DB) will ensure the data fits the type
    schema.
    """

    def __init__(self, data, skip_renormalization=False, **kwargs):
        is_renormalized = isinstance(data, EventDict) or (
            isinstance(data, NodeData) and isinstance(data.data, EventDict)
        )

        if not skip_renormalization and not is_renormalized:
            data = dict(data)
            pre_normalize_type = data.get("type")
            normalizer = StoreNormalizer(
                is_renormalize=True, enable_trimming=False, json_dumps=orjson.dumps
            )
            data = normalizer.normalize_event(data, json_loads=orjson.loads)
            # XXX: This is a hack to make generic events work (for now?). I'm not sure whether we
            # should include this in the rust normalizer, since we don't want people sending us
            # these via the sdk.
            if pre_normalize_type == "generic":
                data["type"] = pre_normalize_type

        CanonicalKeyDict.__init__(self, data, **kwargs)
