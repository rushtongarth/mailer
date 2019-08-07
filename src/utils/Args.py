
import argparse


parser = argparse.ArgumentParser(
  description='Read emails convert them to digestible html format'
)
parser.add_argument(
  '--pagebuild','-p',
  action='store_true',
  help='build webpage'
)
parser.add_argument(
  '--allbuild','-a',
  action='store_true',
  help='build webpage and send email'
)

parser.add_argument(
  '--test','-t',
  action='store_true',
  help='enable testing mode'
)
parser.add_argument(
  '--config','-c',
  help='Use a config file',
  nargs  = 1
)
