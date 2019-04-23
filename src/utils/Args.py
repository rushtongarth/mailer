
import argparse

p = argparse.ArgumentParser(
  description='Process some emails.'
)
p.add_argument(
  '--test','-t',
  action='store_true',
  help='enable testing mode'
)
p.add_argument(
  '--config','-c',
  help='Use a config file',
  nargs  = 1,
  default=conffile,
)
