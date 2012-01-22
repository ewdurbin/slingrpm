slingrpm
========

setup your environment
----------------------

create a python virtualenv
`virtualenv ~/python/envs/slingrpm --no-site-packages`

jump in
`source ~/python/envs/slingrpm/bin/activate`

install requirements
`pip install -r requirements/development.txt`

get yourself setup for sling
`source bin/sling`

make sure tests run
`konira`

get the hell out of dev environment
-----------------------------------

unload sling stuff
`desling`

deactivate virtualenv
`deactivate`

basic concept for architecture
-----------------------------
`    
               +----------------+
               | YumRepoUpdater |
               |----------------|
               |p               |
               |                |
               |   Queue/Lock   |
               +----------------+
                  +          ^ +
                  |update    | | status
                  v          + v
      +--------------+   +--------------+            +------------------+
      |   YumRepo    |   |CatchRPMDaemon|            |CatcherFilePuller |
      |--------------|   |--------------|            |------------------|
      |http          |   |d             |   status   |p                 |
      |              |   |              |<----------+|                  |
      |.slingrpm.conf|   |              |+---------->|                  |
      +--------------+   +--------------+   host     +------------------+
        ^+                        ^         port         ^
        ||                        |         file         |    repo server
     +--||------------------------|----------------------|---------------+
        ||                        |                      |            tcp
     +--||------------------------|----------------------|---------------+
        ||                        |                      |   build server
        ||     +--------------+   |                      |
        ||     |    Slinger   |   |rpm to publish        |
        ||     |--------------|   |server to get from    |file transfer
        ||     |cli           |   |                      |
        ||     |              |+--+                      v
        ||     |              |        port         +-------------------+
        |+---->| admin port   |<------------------+ | SlingerFileServer |
        +-----+| repo url     |+------------------> |-------------------|
               +--------------+      servedir       |p                  |
                                                    |                   |
                                                    |                   |
                                                    +-------------------+
`
