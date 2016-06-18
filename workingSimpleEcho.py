import tornado.websocket
import tornado.concurrent
from tornado.websocket import websocket_connect
import functools

@tornado.gen.coroutine
def connect(eventLoop):
	x = yield websocket_connect("ws://echo.websocket.org",io_loop = eventLoop)
	return x

@tornado.gen.coroutine
def receive(conn):
	x = yield conn.read_message()
	return x

def main():
	eventLoop = tornado.ioloop.IOLoop.current()
	conn = eventLoop.run_sync(functools.partial(connect, eventLoop))

	msg = "Hello!"
	conn.write_message(msg)

	while (msg != "Q"):
		result = eventLoop.run_sync(functools.partial(receive,conn))
		print ("%s was received"% result)
		msg = input("Then you said:\n")
		conn.write_message(msg)

if __name__ == '__main__':
	main()
