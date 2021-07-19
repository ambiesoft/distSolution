import sys
import argparse

def testFormat():
  code = '''
  fjewjfowejf
        fwejofwej

        wefjoweijfoewj
      %(aaa)s
      ''' % {"aaa": 'bbb'}

  print(code)


def main():

  parser = argparse.ArgumentParser(prog='MyPythonTest', description='Test ArgumentParser')
  parser.add_argument('-f', 
                      action='store_true',
                      help='do it with force')

  args = parser.parse_args()

  if args.f:
    print('f is set')
  else:
    print('f is not set')

def aaa():
  if not sys.stdin.isatty():
    print("not sys.stdin.isatty")
  else:
    print("is  sys.stdin.isatty")


if __name__ == '__main__':
  main()
