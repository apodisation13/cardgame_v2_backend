from lib.utils.events.action_types import ActionType
from lib.utils.events.actions.action_add_resources import ActionAddResources
from lib.utils.events.actions.action_one import SendSmsAction


ACTION_REGISTRY = {
    ActionType.ADD_RESOURCES: ActionAddResources,
    ActionType.SEND_SMS: SendSmsAction,
    # ActionType.WEBHOOK: WebhookAction,
}
