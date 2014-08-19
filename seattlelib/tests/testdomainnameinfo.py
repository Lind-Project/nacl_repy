import repyhelper
repyhelper.translate_and_import('domainnameinfo.repy')

if __name__ == '__main__':

  assert(domainnameinfo_gethostlocation('amazon.uk') == 'United Kingdom')
  assert(domainnameinfo_gethostlocation('microsoft.us') == 'United States')
  # we don't care about what the url contains (except the end)
  assert(domainnameinfo_gethostlocation('asd.fasdf.as.df.asdf.asd.fas.microsoft.us') == 'United States')

  try:
    # invalid, we should get a TypeError
    domainnameinfo_gethostlocation(False)
  except TypeError:
    pass
  else:
    print "Error, didn't get exception when passing in False..."

  try:
    # invalid, we should get a TypeError
    domainnameinfo_gethostlocation('google.com')
  except UnknownHostLocationError:
    pass
  else:
    print "Hmm, can I really locate google.com?"
    
