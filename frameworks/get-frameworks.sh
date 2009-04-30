#!/bin/bash
svn co \
https://darwiin-remote.svn.sourceforge.net/svnroot/darwiin-remote/WiiRemoteFramework/tags/version-0.6 \
WiiRemoteFramework
#  -r221 \
#  https://darwiin-remote.svn.sourceforge.net/svnroot/darwiin-remote/WiiRemoteFramework/trunk \
#  WiiRemoteFramework
svn co -r270 http://eyetunes.googlecode.com/svn/EyeTunes/trunk/ EyeTunes
