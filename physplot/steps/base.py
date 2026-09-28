"""Base workflow step types."""

from __future__ import annotations

import functools

from .fields import coerce_field, field

MODULE_ID = "physplot.steps.base"
MODULE_VERSION = "1.1.0"
MODULE_REVISION = "2026-09-25-r1"
MODULE_API_VERSION = "1"
MODULE_COMPATIBILITY = "v1"
MODULE_STATUS = "stable"


class WorkflowStep:
    """Base class for replayable workflow steps.

    Subclasses implement ``apply(physplot, allow_column_number_fallback=False)``
    and ``to_code()``. To be editable from the GUI they also implement
    ``_describe_fields()``; ``describe``, ``validate`` and ``update`` then work
    without further code.

    A step with ``enabled = False`` stays in the sequence but does nothing:
    ``apply`` returns ``None`` and sequence runs report it as skipped.
    ``to_code`` should use ``_format_code`` so ``enabled=False`` round-trips
    through exported sequence files; every built-in step accepts ``enabled``
    in its constructor.
    """

    enabled: bool = True
    display_name: str | None = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        apply = cls.__dict__.get("apply")
        if apply is None or getattr(apply, "_physplot_enabled_guard", False):
            return

        @functools.wraps(apply)
        def guarded_apply(self, physplot, *args, **kw):
            if not getattr(self, "enabled", True):
                return None
            return apply(self, physplot, *args, **kw)

        guarded_apply._physplot_enabled_guard = True
        cls.apply = guarded_apply

    def apply(self, physplot, allow_column_number_fallback: bool = False):
        raise NotImplementedError

    def to_code(self) -> str:
        raise NotImplementedError

    # -- Editing -----------------------------------------------------------

    @classmethod
    def step_label(cls) -> str:
        return cls.display_name or cls.__name__

    @classmethod
    def template(cls, columns=()) -> "WorkflowStep":
        """Return a new step with sensible defaults for the given columns."""
        raise NotImplementedError(f"{cls.__name__} has no template.")

    def _describe_fields(self) -> dict:
        return {}

    def describe(self) -> dict:
        """Return the editable fields of this step, in display order."""
        fields = dict(self._describe_fields())
        fields["enabled"] = field(bool(getattr(self, "enabled", True)), "bool", label="Enabled")
        return fields

    def validate(self, **fields) -> dict:
        """Return ``fields`` converted to stored values, or raise ``ValueError``."""
        spec = self.describe()
        unknown = sorted(set(fields) - set(spec))
        if unknown:
            raise ValueError(f"{type(self).__name__} has no editable field(s): {', '.join(unknown)}.")
        return {name: coerce_field(name, spec[name], value) for name, value in fields.items()}

    def update(self, **fields) -> "WorkflowStep":
        """Validate and apply edited field values in place."""
        for name, value in self.validate(**fields).items():
            self._set_field(name, value)
        return self

    def _set_field(self, name: str, value) -> None:
        setattr(self, name, value)

    # -- Code generation ---------------------------------------------------

    def _format_code(self, arguments: list[tuple[str, object]]) -> str:
        """Render ``ClassName(\\n    name=value,\\n)`` with ``enabled`` when off."""
        lines = [f"{type(self).__name__}("]
        lines.extend(f"    {name}={value!r}," for name, value in arguments)
        if not getattr(self, "enabled", True):
            lines.append("    enabled=False,")
        lines.append(")")
        return "\n".join(lines)
