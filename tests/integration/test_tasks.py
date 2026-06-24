import pytest
from faker import Faker

from retail_client import RetailClient, TaskStatus

pytestmark = pytest.mark.integration

_fake = Faker()


def test_created_task_appears_in_workers_task_list(client: RetailClient, workers, tasks) -> None:
    worker = workers()
    task = tasks(worker.id, title=_fake.sentence(nb_words=4))

    listed = client.list_user_tasks(worker.id)

    assert task.id in {t.id for t in listed}


def test_task_starts_pending_and_can_be_completed(client: RetailClient, workers, tasks) -> None:
    worker = workers()
    task = tasks(worker.id, title=_fake.sentence(nb_words=4))

    assert task.status is TaskStatus.pending

    completed = client.complete_task(task.id)

    assert completed.id == task.id
    assert completed.status is TaskStatus.completed
