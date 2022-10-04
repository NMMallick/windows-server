/**
 * @file ThreadPool.hh
 * @author Nathaniel Mallick (nmm109@pitt.edu)
 * @brief
 * @version 0.1
 * @date 2022-08-26
 *
 * @copyright Copyright (c) 2022
 *
 */

#ifndef TASK_POOL_
#define TASK_POOL_

#include <condition_variable>
#include <mutex>
#include <thread>
#include <queue>
#include <functional>

class TaskPool
{
public:
	void start();
	void launch(const std::function<void()> &);
	void stop();
	bool busy();

private:
	void loop();

	bool should_terminate = false;
	std::mutex queue_mutex;
	std::condition_variable mutex_condition;
	std::vector<std::thread> threads;
	std::queue<std::function<void()>> jobs;
};

#endif