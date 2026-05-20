from services.cron.app.tasks.task_one import TaskOne
from services.cron.app.tasks.task_resend_events import TaskResendEvents
from services.cron.app.tasks.task_two import TaskTwo


TASKS = (
    TaskOne,
    TaskTwo,
    TaskResendEvents,
)
