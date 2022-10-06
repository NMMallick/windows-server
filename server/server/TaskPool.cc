#include "TaskPool.hh"
#include <stdlib.h>

void TaskPool::start() {
	const uint32_t num_threads = std::thread::hardware_concurrency(); // Max # of threads the system supports
	threads.resize(num_threads);
	printf("initiating %d threads\n", threads.size());

	for (uint32_t i = 0; i < num_threads; i++)
	{
		threads.at(i) = std::thread(&TaskPool::loop, this);
	}
}

void TaskPool::loop()
{
	while (true)
	{
		std::function<void()> job;
		{
			std::unique_lock<std::mutex> lock(queue_mutex);
			mutex_condition.wait(lock, [this] {
				return !jobs.empty() || should_terminate;
			});
			if (should_terminate)
				return;

			job = jobs.front();
			jobs.pop();
		}

		job();
	}
}

void TaskPool::launch(const std::function<void()>&  job)
{
	{
		std::unique_lock<std::mutex> lock(queue_mutex);
		jobs.push(job);
	}
	mutex_condition.notify_one();
}

bool TaskPool::busy()
{
	bool poolbusy;
	{
		std::unique_lock<std::mutex> lock(queue_mutex);
		poolbusy = jobs.empty();
	}
	return poolbusy;
}

void TaskPool::stop()
{
	{
		std::unique_lock<std::mutex> lock(queue_mutex);
		should_terminate = true;
	}

	mutex_condition.notify_all();
	for (std::thread& active_thread : threads)
	{
		active_thread.join();
	}

	threads.clear();
}