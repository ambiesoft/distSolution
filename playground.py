import sys

def testFormat():
  code = '''
  fjewjfowejf
        fwejofwej

        wefjoweijfoewj
      %(aaa)s
      ''' % {"aaa": 'bbb'}

  print(code)


def main():
  if not sys.stdin.isatty():
    print("not sys.stdin.isatty")
  else:
    print("is  sys.stdin.isatty")


if __name__ == '__main__':
  main()
