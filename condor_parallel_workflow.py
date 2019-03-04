import os
import parsl
from parsl.app.app import python_app
from parsl.executors import HighThroughputExecutor
from parsl.providers import CondorProvider
from parsl.config import Config
from parsl.channels import LocalChannel

path_str = os.environ["PATH"]
# TODO: find a way to compute this.
#worker_script_path = "/afs/crc.nd.edu/user/d/dsmith47/.local/bin"
#worker_script_path = "/afs/crc.nd.edu/user/d/dsmith47/Documents/Parsl/parsl/parsl"
worker_script_path = "/afs/crc.nd.edu/user/d/dsmith47/Documents/Parsl/parsl/build/lib/parsl/executors/high_throughput/"
# TODO: find a way to determine this
address_str = "condorfe.crc.nd.edu"

config = Config(
  executors=[
    HighThroughputExecutor(
      label='condor_hte',
      provider=CondorProvider(
        project="condor_hte",
        channel=LocalChannel(),
        worker_init="export HOME=$PWD",
        environment={"PATH": path_str+":"+worker_script_path},
        requirements = "process_worker_pool.py"
      ),
      address = address_str,
      working_dir=os.getcwd(),
    )
  ]
)

parsl.load(config)

@python_app
def generate(limit):
  from random import randint
  return randint(1,limit)

rand_nums = []
for _ in range(5):
  rand_nums.append(generate(10))

outputs = [i.result() for i in rand_nums]
print(outputs)
