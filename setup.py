from distutils.core import setup

setup(name='jarmeplease',
      version=str(swork.RELEASE),
      description=(
        'A shell enviroment manager. Allows you to easily manage the shell enviroment for'
        'working on various projects.'
      ),
      author='Tim Henderson',
      author_email='tim.tadh@gmail.com',
      license='GPLv2',
      packages=['conf'],
      scripts=['bin/jarmeplease'],
      py_modules=['jarmeplease'],
      platforms=['unix'],
)

