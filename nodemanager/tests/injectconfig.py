import persist

# Injects value for the key in the cfile file, defaults to nodeman.cfg
def inject(key, value, cfile="nodeman.cfg"):
  configuration = persist.restore_object(cfile)

  # Inject the dictionary
  configuration[key] = value

  persist.commit_object(configuration, cfile)

# This is a sample dictionary for 'networkrestrictions'
# config = {}
# config['nm_restricted'] = True
# config['nm_user_preference'] = [(True,'192.168.1.128'),(True,'127.0.0.1')]
# config['repy_restricted'] = False
# config['repy_nootherips'] = False
# config['repy_user_preference'] = [(True,'192.168.1.127'),(True,'127.0.0.1')]
