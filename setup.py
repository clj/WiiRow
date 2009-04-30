#    WiiRow, a WiiRemote frontend for FrontRow and stuff
#
#    Copyright (C) 2009 Christian L. Jacobsen
#
#    This file is part of WiiRow
#
#    Cloninator is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Cloninator is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Cloninator; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sys, os, re
from setuptools import setup

import distutils.cmd 
import distutils.command.build
from distutils.util import *
import distutils.spawn as d_spawn
import os

import py2app.recipes

# Let python know where the portable source code is
sys.path.insert(0, os.path.abspath('src'))

def sqlalchemyCheck(py2app_cmd, modulegraph):
    name = 'sqlalchemy'
    m = modulegraph.findNode(name)
    if m is None or m.filename is None:
        return None
    from distutils.sysconfig import get_config_h_filename
    import os.path, tempfile
    def path_components(path):
        """ Splits a path into a list of all its components """
        if not path:
            return []
        tail, head = os.path.split(path)
        return path_components(tail) + [head]
    # Get the prefix where python stuff is stored
    PREFIX = os.path.normpath(sys.prefix)
    # Figure out there pyconfig is
    pyconfig_hPath    = get_config_h_filename()
    # Figure out where we want it
    newPyconfig_hPath = pyconfig_hPath[len(PREFIX) + 1:]
    # Need the path and name of the file by themselves
    # FIXME: Make this less crude
    includePath, pyconfig_h = os.path.split(pyconfig_hPath[len(PREFIX) + 1:])
    # A temporary directory that we can pass to py2app to actually include
    # in the distribution
    tempInclude = os.path.join(py2app_cmd.temp_dir, includePath)
    # Make the temporary path, copy the file and let py2app know that it should
    # be included in the distribution
    py2app_cmd.mkpath(tempInclude)
    py2app_cmd.copy_file(pyconfig_hPath, os.path.join(tempInclude, pyconfig_h))
    py2app_cmd.resources.append(
            os.path.join(py2app_cmd.temp_dir, 
            path_components(newPyconfig_hPath)[0]))
    # Need to import all the database engine bits, or they do not get
    # included in the distribution
    # FIXME: import everythign? This will of course not import any of the DB
    # layers, perhaps they are imported if instaled? As the sqlite library
    # correctly handled by py2app, suggesting that something knows it is needed.
    modulegraph.import_hook(name + '.databases', m, ['*'])
    # Need to return a dict so that py2app know that we did stuff
    return dict()


import imp
py2app.recipes.sqlalchemy = imp.new_module('py2app.recipes.sqlalchemy')
py2app.recipes.sqlalchemy.check = sqlalchemyCheck

class build_frameworks(distutils.cmd.Command):
    description = "Builds OS X Frameworks"
    user_options = [
            ('frameworks', None, "A list of frameworks to build"),
            ('target', None, "The target to build (for all frameworks)"),
            ('name', None, 
                "The name of the built framework (ie <name>.framework")]
    def initialize_options(self):
        self.frameworks = None
        self.configuration = 'Release'
        self.target = None
        self.dist_dir = None
        self.bdist_dir = None
        self.framework_dir = None
        self.framework_temp = None
        self.name = None
        self.temp_dir = None
        self.xcodebuild = None
        self.alias = None

    def finalize_options(self):
        # I don't know of a better way of getting this directory other than
        # copying the relevant code from py2app.build_app into here...
        py2app = self.get_finalized_command('py2app')
        py2app.create_directories()
        self.set_undefined_options('py2app', 
                ('dist_dir', 'dist_dir'),
                ('bdist_dir', 'bdist_dir'),
                ('framework_dir', 'framework_dir'),
                ('temp_dir', 'temp_dir'),
                ('alias', 'alias'))
        self.framework_temp = os.path.join(self.temp_dir, 'BuiltFrameworks')
        # I want absolute paths:
        self.framework_dir = os.path.abspath(self.framework_dir)
        self.temp_dir = os.path.abspath(self.temp_dir)
        #self.ensure_dirname(self.frameworks)
        #self.ensure_string(self.target)

    def run(self):
        # Nothing to do?
        if self.frameworks is None:
            return
        frameworks = self.frameworks
        if type(frameworks) is not dict and type(frameworks) is not list:
            frameworks = [dict(framework=frameworks)]
        frameworks = map(lambda i: type(i) is not dict and dict(framework=i) or i,
                         frameworks)
        # Find xcodebuild
        self.xcodebuild = d_spawn.find_executable('xcodebuild')
        if not self.xcodebuild:
            raise DistutilsExecError('Could not find the xcodebuild command, ' \
                  'have you installed Xcode?')
        # Build things
        for framework in frameworks:
            self.execute(self.__build, 
                    [framework],
                    'Building Framework: %s' % (framework['framework']))
        # If we are doing an alias build, we have to get py2app to link in the
        # framework
        if self.alias:
            # (At least some) py2app(s) generate bad symlinks for frameworks in
            # alias builds. Therefore we'll do it ourselves.
            py2app = self.get_finalized_command('py2app')
            app_path = os.path.join(
                    self.dist_dir,
                    py2app.get_appname() + '.app')
            app_framework_path = os.path.join(
                    app_path, 'Contents', 'Frameworks')
            from py2app.util import makedirs
            makedirs(app_framework_path)
            for framework in frameworks:
                # FIXME: Move somewhere else, ie into a Frameworks class, like the
                # Extensions class
                name = framework.get('name', self.name)
                if not name:
                    framework_name = os.path.split(framework['framework'])
                    if framework_name[1] == '':
                        framework_name = os.path.split(framework_name[0])[1]
                    else:
                        framework_name = framework_name[1]
                else:
                    framework_name = name
                framework_name = framework_name + '.framework'    
                src = os.path.join(self.framework_dir, framework_name)
                dst = os.path.join(app_framework_path, framework_name)
                try:
                    os.remove(dst)
                except:
                    pass
                os.symlink( os.path.abspath(src), dst)


    def __build(self, frameworkDict):
        framework = frameworkDict['framework']
        # We need to change into the project directory in order for xcodebuild
        # to do its thing (ie the directory with the .xcodeproj in it)
        cwd = os.getcwd()
        os.chdir(framework)
        cmd = [self.xcodebuild]
        if 'target' in frameworkDict:
            cmd.extend(["-target", frameworkDict['target']])
        elif self.target:
            cmd.extend(["-target", self.target])
        if self.alias:
            cmd.extend(['-configuration', 'Debug'])
        else:
            cmd.extend(['-configuration', 'Release'])
        cmd.extend([    
            'CONFIGURATION_BUILD_DIR=%s' % (self.framework_dir),
            'PROJECT_TEMP_DIR=%s' % (self.framework_temp)])
        self.spawn(cmd)
        # However we MUST also put the cwd back to what it was, as other
        # commands might rely on relative paths
        os.chdir(cwd)
                  

distutils.command.build.build.sub_commands.append(('build_frameworks', None))


def getSVNLastChangedRev(trunk = '/trunk'):
    output = os.popen('svnversion -cn . %s' % (trunk))
    version = output.readline()
    try:
        version = version.split(':')[1]
    except IndexError:
        version = 'Could not determine SVN last changed revision'
    return version

def isAliasBuild():
    return 'py2app' in sys.argv and ('--alias' in sys.argv or '-A' in sys.argv)

def getBundleVersion():
    if isAliasBuild():
        return 'AliasBuild'
    else:
        return getSVNLastChangedRev()

def fileList(path, ext):
    """
    Given a regular path to search for files (NOT recursively) and a regular
    expression will find files (and NOT directories, or symbolic links, or...)
    in that path (and not subdirectories thereof) which match the regular
    expressoin. A regular expression for finding images might look like this:
    '\.(tiff?|png)$'
    Which finds images named *.tiff *.tif or *.png
    """
    r = re.compile(ext)
    return \
        filter(lambda f: os.path.isfile(f),
        map(lambda f: os.path.join(path, f), 
        filter(lambda f: r.search(f), os.listdir(path))))

plist=dict(
        CFBundleName='WiiRow',
        NSHumanReadableCopyright='Copyright 2009 Christian L. Jacobsen',
        CFBundleIdentifier='com.absolutepanic.WiiRow',
        CFBundleVersion='%s' % (getBundleVersion()), # build version
        CFBundleShortVersionString='0.3.0', # release-version-number
        # See:
        # http://developer.apple.com/documentation/MacOSX/Conceptual/BPRuntimeConfig/Articles/PListKeys.html
        LSUIElement=1,
        #LSBackgroundOnly=1,
        #CiMOptions=dict(
        #    VerboseExceptions=isAliasBuild(),
        #    AliasBuild=isAliasBuild(),
        #    ),
        )

# Fix for using Apple's supplied Python2.3 + py2app 0.3.6
if sys.hexversion < 0x02040000:
    version = sys.version[:3]
    # This is required to make the app look for _objc.so (and probably other
    # things) in the right place. From:
    # http://maba.wordpress.com/2006/08/31/ 
    # incredible-2d-images-using-nodebox-universal-binary/
    plist.update(dict(PyResourcePackages=[
        (s % version) for s in [
            u'lib/python%s', 
            u'lib/python%s/lib-dynload',
            u'lib/python%s/site-packages',
            u'lib/python%s/site-packages.zip',
            ]]))


def dataIfExists(file):
    if os.path.exists(file): data_files.append(file)

data_files=[
    'src/English.lproj',
    ]
data_files.extend(fileList('images', '\.(tiff?|png)$'))
data_files.extend(fileList('quartz', '\.qtz$'))
QCC = '/Developer/Examples/Quartz Composer/Compositions/'
qccs = '''\
Core Image/Star Shine.qtz
Core Image/Psychotic.qtz
Conceptual/Noise - 3D.qtz
Conceptual/Lorenz Attractor - JavaScript.qtz 
Conceptual/Flip Clock.qtz 
Conceptual/Random - Nested Iterator.qtz 
Feedback/Fire Drips.qtz 
Feedback/Combed Trail.qtz 
Feedback/Blazed Trail.qtz 
Graphic Animations/Blue.qtz 
Graphic Animations/Cells.qtz
Graphic Animations/Cube Array.qtz 
Graphic Animations/Rings.qtz 
Graphic Animations/Scanner.qtz 
Graphic Animations/Static.qtz 
Particle Systems/Blob.qtz 
Particle Systems/Particle System.qtz
Particle Systems/Explosive.qtz 
Screen Savers/Security.qtz 
'''
for i in qccs.split('\n'):
    i = i.strip()
    if not i: continue
    i = os.path.join(QCC, i)
    print i
    dataIfExists(i)


icon = 'images/WiiRow.icns'
#    data_files.extend()

setup(
    cmdclass={'build_frameworks': build_frameworks},
    app=['src/main.py'],
    setup_requires=['py2app'],
    data_files=data_files,
    options=dict(
        build_frameworks=(dict(
            frameworks=[
                dict(framework='frameworks/WiiRemoteFramework/',
                target='WiiRemoteFramework',
                name='WiiRemote'),
                dict(framework='frameworks/EyeTunes/')])),
        py2app=dict(
            iconfile=icon,
            plist=plist,
        )
    )
)

# vim:ts=4:sw=4:et:
