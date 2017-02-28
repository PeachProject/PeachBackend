# Peach Backend
```
______               _     
| ___ \             | |    
| |_/ /__  __ _  ___| |__  
|  __/ _ \/ _` |/ __| '_ \ 
| | |  __/ (_| | (__| | | |
\_|  \___|\__,_|\___|_| |_|
                BACKEND


License:    LGPLv3
Authors:    Christian Bierstedt
            Henry Müssemann
```

## Peach Concept

Read about the [Peach concept](https://github.com/PeachProject/PeachStandalone)!

## What is the Peach Backend

The Peach Backend Git contains all necessary scripts for hosting a peach backend.
The Peach Backend is the module where the workflows are being executed.

General execution principle looks like this:

A Kafka Event was sent by the frontend and will now be processed by the backend (`$ python run_consumers --c "1"`).
The kafka event contains a binary encoded workflow consisting of several nodes, ports and connections.
The event consumer will convert the binary data into a dask script and save it to a local queue folder.
Furthermore the consumer will upload the given data into a mysql table (find needed sql statements for setting up a peach mysql database in `/sql/*`).
If everything went right the consumer will emit another kafka event that will be consumed by the second consumer (`$ python run_consumers --c "2"`).
This consumer actually executes the generated dask file in a different process.

## Setting up the Peach Backend

### Clone this Git

  1. Clone this git 
  2. Init submodules

  ```
  $ git submodule init
  $ git submodule update
  ```

### Install Prerequisites

  1. Install kafka python

  ```
  sudo pip install kafka-python
  ```

  2. Install dask

  ```
  sudo pip install dask[complete]
  ```

  3. Install mysql python

  ```
  sudo apt-get install python-mysqldb
  ```

### Gather paths

  1. Somewhere on your disk create a folder named something like `queue` or `workflow_script_queue`.
     Make sure to have write and execution permission and remember the path.

  2. Either create your own service hub or clone the [PeachDefaultServiceHub](https://github.com/PeachProject/PeachDefaultServiceHub).
     Please make sure to remember the path.

### Edit configs

  1. Copy `PeachBackend/config/peachBackendConfig.sample.py` to `PeachBackend/config/peachBackendConfig.py`

  ```
  $ cp PeachBackend/config/peachBackendConfig.sample.py PeachBackend/config/peachBackendConfig.py
  ```

  2. Adapt the newly created file (e.g. `$ PeachBackend/config/peachBackendConfig.py`):

  ```
  Replace

  "<current_git>": The directory of this file (e.g. `/home/.../PeachBackend` !<- no ending backslash!)
  "<local_queue_temp>": Your workflow script queue temp directory created in `Gather paths / 1.`
  "<Peach_Service_Hub>": Your service hub directory created in `Gather paths / 2`
  "<Kafka_Server>": The kafka server ip (e.g. `123.456.7.890:9092`)
  "<mysql_*>": The mysql information
  ```

  3. Copy `PeachShared/library/config/peachSharedConfig.sample.py` to `PeachShared/library/config/peachSharedConfig.py`

  ```
  $ cp PeachShared/library/config/peachSharedConfig.sample.py PeachShared/library/config/peachSharedConfig.py
  ```

  4. Adapt the newly created file (e.g. `$ vim PeachShared/library/config/peachSharedConfig.py`):

  ```
  Replace

  "<PeachClient_Git_Repo>": The directory of this file (e.g. /home/peach/PeachClient)
  "<peach_temp_data>": The shared storage (See basic concept)
  "<kafka_server>": The kafka server address (e.g. localhost:9092)
  ```

### Run consumers

#### For gnome-terminal users

Type in terminal

```
$ python run_consumers.py
```

#### Other GUI based Linux stuff

Open two terminals.

In the first one type

```
$ python run_consumers.py --c "1"
```

In the second one type

```
$python run_consumers.py --c "2"
```

#### One-Terminal-Only system
We would suggest to install the screen software for linux:

```
$ sudo apt-get install screen 
```

Then open a session

```
$ screen
```

type in

```
$ python run_consumers.py --c "1"
```

Press "Ctrl" + "A" followed by a "C" and type in 

```
$ python run_consumers.py --c "2"
```

Detach the session by pressing "Ctrl" + "A" followed by a "D".

The two scripts will now run in background. More information on how to use the screen software can be found [here](https://wiki.ubuntuusers.de/Screen/);