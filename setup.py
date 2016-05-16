from distutils.core import setup

setup(name='mppfnet',
      version='1.0',
      description='Multi-Period Version of PFNET',
      author='Martin Zellner',
      author_email='martin.zellner@gmail.com',
      packages=['mppfnet'],
      requires=['scipy',
                'numpy',
                'PFNET',
                'pypvwatts',
                'alpg'])
