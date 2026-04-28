import pytest
import asyncio
from src.pipeline_queue import PipelineQueue, PipelineItem


class MockDomainTask:
    def __init__(self, domain):
        self.domain = domain


@pytest.mark.asyncio
async def test_pipeline_queue_basic():
    """Queue can put and get items"""
    queue = PipelineQueue()
    task = MockDomainTask("example.com")
    item = PipelineItem(task=task, forms=[], emails=set())

    await queue.put(item)
    result = await queue.get()

    assert result.task.domain == "example.com"
    queue.task_done()


@pytest.mark.asyncio
async def test_pipeline_queue_empty_blocks():
    """Get blocks when empty"""
    queue = PipelineQueue()

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(queue.get(), timeout=0.1)


@pytest.mark.asyncio
async def test_pipeline_queue_done_signal():
    """Queue signals when all done"""
    queue = PipelineQueue(total_items=2)

    assert not queue.all_done()

    await queue.put(PipelineItem(MockDomainTask("a.com")))
    await queue.get()
    queue.task_done()

    assert not queue.all_done()

    await queue.put(PipelineItem(MockDomainTask("b.com")))
    await queue.get()
    queue.task_done()

    assert queue.all_done()
