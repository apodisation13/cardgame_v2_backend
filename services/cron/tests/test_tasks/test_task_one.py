import pytest

from services.cron.app.tasks import TaskOne


@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_database")
async def test_task_one_execution(
    config,
    db,
    event_sender_mock,
):
    task = TaskOne(config, db)

    # Запускаем задачу
    await task.do()

    call_args = event_sender_mock.call_args_list
    print(call_args)
    call_args = event_sender_mock.call_args
    print(call_args)
