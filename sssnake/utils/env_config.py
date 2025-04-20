from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

@dataclass(frozen=True)
class ParamEntry:
    name: str
    group: str
    type: type
    value: Any

class EnvConfig:
    def __init__(self, raw_params: Dict[str, Dict[str, Any]]):
        self._entries: Dict[str, ParamEntry] = {}

        for group, items in [("var", raw_params.get("env_variable", {})),
                             ("const", raw_params.get("env_constant", {}))]:
            for key, val in items.items():
                self._entries[key] = ParamEntry(
                    name=key,
                    group=group,
                    type=type(val),
                    value= val if not isinstance(val, list) else tuple(val)
                )

    def get(self, name: str) -> Any:
        return self._entries[name].value

    def entry(self, name: str) -> ParamEntry:
        return self._entries[name]

    def list_params(self) -> List[Tuple[str, str, str, Any]]:
        return [
            (e.name, e.group, e.type.__name__, e.value)
            for e in self._entries.values()
        ]

    def update(self, raw_params: Dict[str, Dict[str, Any]]) -> None:

        for group, items in [
            ("var", raw_params.get("env_variable", {})),
            ("const", raw_params.get("env_constant", {}))
        ]:
            for key, val in items.items():
                if key in self._entries:
                    new_val = tuple(val) if isinstance(val, list) else val
                    self._entries[key] = ParamEntry(
                        name=key,
                        group=group,
                        type=type(val),
                        value=new_val
                    )
                else:
                    pass
