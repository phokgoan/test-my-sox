# Test My Sox

This package is used for establishing TCP/UDP socket server and generating report logs of the received sockets.

The service can be run on either public or internal IP. It can be used for observing and testing the socket sending behavior of your TCP/UDP client.

### Build Your TCP Server/Client Executables

```sh
$ SERVICE_IP=[your IP] SERVICE_TCP_PORT=[your port] make
```

### Run Your Servers in System Background

```sh
$ daemon --name=http_server [your path]/test-my-sox/http_server/http_server.py
$ daemon --name=tcp_server [your path]/test-my-sox/tcp_server
```

