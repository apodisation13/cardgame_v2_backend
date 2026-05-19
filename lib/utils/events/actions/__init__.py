from lib.utils.events.action_types import ActionType
from lib.utils.events.actions.action_add_resources import ActionAddResources
from lib.utils.events.actions.action_send_service_tg import ActionSendServiceTg


ACTION_REGISTRY = {
    ActionType.ADD_RESOURCES: ActionAddResources,
    ActionType.SEND_SERVICE_TG: ActionSendServiceTg,
}
