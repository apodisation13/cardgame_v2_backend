from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from lib.utils.config.base import BaseConfig
from lib.utils.schemas.events import ActionConfigData

if TYPE_CHECKING:
    from lib.utils.db.pool import Database


class ActionBase(ABC):
    def __init__(
        self,
        config: BaseConfig,
        action_config: ActionConfigData,
        payload: dict,
        db: Database | None = None,
    ):
        self.config = config
        self.action_config = action_config
        self.payload = payload
        self.db = db

    @abstractmethod
    async def execute(self) -> None:
        pass

    def check_conditions(self) -> bool:
        """Проверка условий выполнения действия"""
        conditions = self.action_config.conditions

        if isinstance(conditions, bool):
            return conditions

        return True

        # for condition in conditions:
        #     field_value = context.get(condition['field'])
        #     if not self._check_condition(field_value, condition['operator'], condition['value']):
        #         return False
        # return True

    # def _check_condition(self, field_value: Any, operator: str, value: Any) -> bool:
    #     operators = {
    #         'eq': lambda a, b: a == b,
    #         'ne': lambda a, b: a != b,
    #         'gt': lambda a, b: a > b,
    #         'lt': lambda a, b: a < b,
    #         'contains': lambda a, b: b in a if a else False,
    #     }
    #     return operators[operator](field_value, value)
