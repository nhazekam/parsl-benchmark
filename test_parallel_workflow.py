import parsl
from parsl.app.app import python_app
from parsl.config import Config
from parsl.executors import ThreadPoolExecutor

import matplotlib.pyplot as plt
import os
import sys
import time

@python_app
def quick_task(limit):
  return 0

@python_app
def long_task(limit):
  # Simple Collatz computation
  xmin = 1
  ymin = 1
  xmax = 640
  ymax = 480
  width = 640
  height = 480
  iterations = 150

  for j in range(height):
    for i in range(width):
      x = xmin + i * (xmax-xmin)/width
      y = ymin + i * (ymax-ymin)/width
      z = x + y
      alpha = 1
      for _ in range(iterations):
        z = z - alpha * ((z ** 2 - 1) / (2*z))
  return 0


class Task():
  def __init__(self, task_id, submit, completed):
    self.id = task_id
    self.submit_time = submit
    self.completed_time = completed


# Sequential start/wait on jobs to test timing.
def run_sequential_workflow(num_processes):
  start_time = time.time()
  for i in range(num_processes):
    f = quick_task(num_processes)
    f.result()
  end_time = time.time()
  return end_time - start_time


# Parallel workflow
def run_parallel_workflow(num_processes):
  jobs = []
  start_time = time.time()
  for i in range(num_processes):
    jobs.append(long_task(num_processes))
  for j in jobs:
    j.result()
  end_time = time.time()
  return end_time - start_time
  

address_str = "condorfe.crc.nd.edu"

local_config=Config(
  executors=[
    ThreadPoolExecutor(
      max_threads=8,
      label='local_threads'
    )
  ]
)

condor_config=Config(
)

if __name__ == "__main__":
  task_batch_sizes = [1, 10, 50, 100, 250]
  configs = [local_config]
  """
  print("Sequential Workload")
  for config in configs:
    parsl.load(config)
    fig, axes = plt.subplots(1, 1)
    sequential_time_by_jobs = []
    for s in task_batch_sizes:
      t = run_sequential_workflow(s)
      print("{} jobs in {}s.".format(s, t))
      sequential_time_by_jobs.append(t)
    print(sequential_time_by_jobs)
    axes.plot(task_batch_sizes, sequential_time_by_jobs)
    plt.savefig("{}_seq_workload.png".format(config.executors[0].label))
    parsl.clear()
  """

  for config in configs:
    parsl.load(config)
    task_batch_sizes = [1, 2, 4, 8, 16]
    print("Parallel Workload")
    fig, axes = plt.subplots(1, 1)
    parallel_time_by_jobs = []
    for s in task_batch_sizes:
      t = run_parallel_workflow(s)
      print("{} jobs in {}s.".format(s, t))
      parallel_time_by_jobs.append(t)
    axes.plot(task_batch_sizes, parallel_time_by_jobs)
    plt.savefig("{}_par_workload.png".format(config.executors[0].label))
