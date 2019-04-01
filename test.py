#! /usr/bin/env python3

import parsl
from parsl.app.app import python_app
from parsl.config import Config
from parsl.executors import ThreadPoolExecutor, HighThroughputExecutor
from parsl.executors import WorkQueueExecutor
from parsl.channels import LocalChannel
from parsl.providers import CondorProvider

import argparse
import matplotlib.pyplot as plt
import os
import sys
import time

@python_app
def quick_task(limit):
  a = 1+1
  return 0


@python_app
def long_task(limit):
  xmin = 1
  ymin = 1
  xmax = 640
  ymax = 480
  width = 640
  height = 480
  iterations = 50

  for j in range(height):
    for i in range(width):
      x = xmin + i * (xmax-xmin)/width
      y = ymin + i * (ymax-ymin)/width
      z = x + y
      alpha = 1
      for _ in range(iterations):
        z = z - alpha * ((z ** 2 - 1) / (2*z))
  return 0

@python_app
def run_mandelbrot():
  import subprocess
  subprocess.call(['python3', 'mandelbrot.py'])
  return 0

@python_app
def data_rw(limit):
  f = open("/dev/zero")
  for _ in range(10):
    f.read(10 ** 7)

class Task():
  def __init__(self, task_id, submit, completed):
    self.id = task_id
    self.submit_time = submit
    self.completed_time = completed


# Sequential start/wait on jobs to test timing.
def run_sequential_workflow(num_processes, task=quick_task):
  start_time = time.time()
  for i in range(num_processes):
    #TODO: change that back
    f = task(num_processes)
    f.result()
  end_time = time.time()
  return end_time - start_time


# Parallel workflow
def run_parallel_workflow(num_processes, task=long_task):
  jobs = []
  start_time = time.time()
  for i in range(num_processes):
    jobs.append(task(num_processes))
  for j in jobs:
    j.result()
  end_time = time.time()
  return end_time - start_time


# Parallel workflow, local-only variant
def run_local_parallel_workflow(num_processes):
  jobs = []
  start_time = time.time()
  for i in range(num_processes):
    jobs.append(run_mandelbrot())
  for j in jobs:
    j.result()
  end_time = time.time()
  return end_time - start_time


local_config=Config(
  executors=[
    ThreadPoolExecutor(
      max_threads=8,
      label='local_threads'
    )
  ]
)

address_str = "condorfe.crc.nd.edu"
path_str = os.environ["PATH"]

condor_config=Config(
  executors=[
    HighThroughputExecutor(
      label='condor_hte',
      provider=CondorProvider(
        project="condor_hte",
        channel=LocalChannel(),
        worker_init="export HOME=$PWD",
        environment={"PATH": path_str}
      ),
      address = address_str,
      working_dir = os.getcwd(),
    ),
  ]
)

#TODO: This port number needs to be configurable so that a script can specify
# the port here and when spinning up workers.
wq_config=Config(
  executors=[
    WorkQueueExecutor(
      label='wq_exec',
      project_name='wq_benchmark',
      env={"PATH": path_str},
      init_command="export HOME=$PWD",
      port=9000
    )
  ]
)

def test_local_sequential(task_batch_sizes):
  print("Local Sequential Workload")
  test_parsl_config("local_sequential_workflow.png", local_config,
                    run_sequential_workflow, task_batch_sizes)


def test_local_parallel(task_batch_sizes):
  print("Local Parallel Workload")
  test_parsl_config("local_parallel_workflow.png", local_config,
                    run_local_parallel_workflow, task_batch_sizes)


def test_condor_sequential(task_batch_sizes):
  print("Condor Sequential Workload")
  test_parsl_config("condor_sequential_workflow.png", condor_config,
                    run_sequential_workflow, task_batch_sizes)


def test_condor_parallel(task_batch_sizes):
  print("Condor Parallel Workload...")
  test_parsl_config("condor_parallel_workflow.png", condor_config,
                    run_parallel_workflow, task_batch_sizes)


def test_wq_sequential(task_batch_sizes):
  print("WorkQueue Sequential Workload")
  test_parsl_config("wq_sequential_workflow.png", wq_config,
                    run_sequential_workflow, task_batch_sizes)


def test_wq_parallel(task_batch_sizes):
  print("WorkQueue Sequential Workload")
  test_parsl_config("wq_parallel_workflow.png", wq_config,
                    run_parallel_workflow, task_batch_sizes)


def test_parsl_config(plot_label, config, timing_function, task_batch_sizes):
  parsl.load(config)
  fig, axes = plt.subplots(1, 1)
  axes.set_xlabel("Number of tasks")
  axes.set_ylabel("Time elapsed (s)")
  parallel_time_by_jobs = []
  for s in task_batch_sizes:
    print("Starting to execute {} tasks".format(s))
    t = timing_function(s)
    print("{} jobs in {}s.".format(s, t))
    parallel_time_by_jobs.append(t)
  axes.plot(task_batch_sizes, parallel_time_by_jobs)
  plt.tight_layout()
  plt.savefig(plot_label)
  parsl.clear()


def test_parsl(plot_label, config, timing_function, task_function,
               task_batch_sizes):
  parsl.load(config)
  fig, axes = plt.subplots(1, 1)
  axes.set_xlabel("Number of tasks")
  axes.set_ylabel("Time elapsed (s)")
  parallel_time_by_jobs = []
  for s in task_batch_sizes:
    print("Starting to execute {} tasks".format(s))
    t = timing_function(s, task_function)
    print("{} jobs in {}s.".format(s, t))
    parallel_time_by_jobs.append(t)
  axes.plot(task_batch_sizes, parallel_time_by_jobs)
  plt.tight_layout()
  plt.savefig(plot_label)
  parsl.clear()


def select_config(config_str):
  if config_str == "condor":
    return condor_config
  if config_str == "wq":
    return wq_config
  return local_config


def select_function(function_str):
  if function_str == "cpu_long":
    return long_task
  return quick_task

def select_parallelization(parallelization_str):
  if parallelization_str == "parallel":
    return run_parallel_workflow
  return run_sequential_workflow


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Testing benchmark for parsl lib.")
  
  parser.add_argument('num_task_list', type=int, metavar='N',
                    nargs='+', help="list of task integers.")
  
  parser.add_argument('--test_local_sequential', dest="test_local_sequential",
                    action="store_const", const=test_local_sequential,
                    default=None)
  parser.add_argument('--test_local_parallel', dest="test_local_parallel", action="store_const",
                    const=test_local_parallel, default=None)
  parser.add_argument('--test_condor_sequential', dest="test_condor_sequential", action="store_const",
                    const=test_condor_sequential, default=None)
  parser.add_argument('--test_condor_parallel', dest="test_condor_parallel", action="store_const",
                    const=test_condor_parallel, default=None)
  
  parser.add_argument('--test_wq_sequential', dest="test_wq_sequential", action="store_const",
                    const=test_wq_sequential, default=None)
  parser.add_argument('--test_wq_parallel', dest="test_wq_parallel", action="store_const",
                    const=test_wq_parallel, default=None)

  parser.add_argument('--config', dest='config', default='',
                      help='Parsl configuration to apply.')
  parser.add_argument('--function', dest='function', default='',
                      help='Testing function to apply.')
  parser.add_argument('--parallelization', dest='parallelization',
			default='',
                        help='Run test in parallel or sequence')
 
  parser.add_argument('-o', dest='output_filename', default='out.png',
                       help='output filename') 
  args = parser.parse_args()

  #task_batch_sizes = list(map(int, args.num_task_list.split(",")))
  task_batch_sizes = args.num_task_list
  print(task_batch_sizes)

  config_obj = select_config(args.config)
  function_obj = select_function(args.function)
  parallelization_obj = select_parallelization(args.parallelization)

  test_parsl(args.output_filename, config_obj,
             parallelization_obj, function_obj, task_batch_sizes)

  if args.test_local_sequential:
    args.test_local_sequential(task_batch_sizes)
  if args.test_local_parallel:
    args.test_local_parallel(task_batch_sizes)
  if args.test_condor_sequential:
    args.test_condor_sequential(task_batch_sizes)
  if args.test_condor_parallel:
    args.test_condor_parallel(task_batch_sizes)
  if args.test_wq_sequential:
    args.test_wq_sequential(task_batch_sizes)
  if args.test_wq_parallel:
    args.test_wq_parallel(task_batch_sizes)
