# news-letter
Project for Distributed Systems course on my CS degree

---

# Running

You need the [Python3 interpreter](https://www.python.org/downloads/) installed in your system. This is the only dependency.

Once Python is installed and in the system path, open 3 terminal sessions and go to the `src` folder of this project.

Load the server:

```Bash
$ python init.py server <host> <port>
```

Load the publisher:

```Bash
$ python init.py publisher <server host> <server port>
```

Load the subscriber:

```Bash
$ python init.py subscriber <server host> <server port>
```

The server needs a port and a host to expose the API. The clients need the host and the port used by the server.

To start the on-line comunication between server and subscriber, you need to specify the subscriber's location, which will be sent to the server in order establish the connection. The subscriber app will ask for this information in runtime.

---

# Architeture

The clients are not coupled into the server, so new apps can be written and make use of the full API exposed by the server.

## Server

The server provides resources through a RMI API. This API is designed to be stateless. The server persists and retrieves the data as required by the clients. The persistence is built over SQLite, a lightweight database manager written in the C language and delivered as a Python module.

There are two layers forming the server: the database layer and the RMI layer.

* **Database layer**: The database layer provides useful functions to persist and retrieve data from the disk. No business logic in this layer.
* **RMI layer**: The RMI layer exposes the functions into the network so clients can access them via RMI. This layer contains business logic.

## Client

There are two clients: publisher and subscriber.

### Publisher

The publisher creates subjects and posts. Everytime a publisher creates something it is sent to the server, which will persist it on disk.
Only authenticated users can access the publisher's features. It lets the user create new accounts though.

### Subscriber

The subscriber reads posts created by publishers. Everytime a subscriber wants to read something, it asks to the server for the required information. If the subscriber is authenticated, it can also recieve posts on-line as the publishers create them. Each subscriber should subscribe itself into subjects to recieve on-line posts of these subjects.

## On-line comunication

For this feature to work, the subscriber exposes a small RMI API and informs the server about it. The server can now send new posts to the subscriber in an on-line fashion.
