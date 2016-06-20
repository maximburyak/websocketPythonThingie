import tornado.websocket
import tornado.concurrent
import tornado.ioloop
from tornado.websocket import websocket_connect
import functools
import threading
from multiprocessing import Process
import time

#class WebSocketParallelConnection(multiprocessing.Process):
#	def __init__(self)
#	multiproccessing.Proccess.__init__(self)

class WebsocketStreamingConnectionManager(threading.Thread):

	def __init__(self, eventLoop, name):
		threading.Thread.__init__(self)
		self.eventLoop=eventLoop
		self.name = name	
	
	@tornado.gen.coroutine
	def connect(self):
		print ("started connection to thread %s", self.name)
		#x = yield websocket_connect("ws://echo.websocket.org",io_loop = self.eventLoop)
		x = yield websocket_connect("ws://192.168.56.1:57052/api/values",io_loop = self.eventLoop)
		print ("connected to thread %s", self.name)
		return x

	@tornado.gen.coroutine
	def receive(self):
		x = yield self.conn.read_message()
		return x

	@tornado.gen.coroutine
	def run(self):

		print ("started run for thread %s", self.name)
		self.conn = yield self.connect() #self.eventLoop.run_sync(self.connect)

		msg = "Hello!"
		self.conn.write_message(msg)
		response = yield self.receive() # self.eventLoop.run_sync(self.receive)
		print ("%s was received as thread %s" % (response,self.name))		


class WebsocketStreamingConnectionManager2(threading.Thread):

	def __init__(self, eventLoop, name):
		threading.Thread.__init__(self)
		self.eventLoop=eventLoop
		self.name = name	
	
	@tornado.gen.coroutine
	def connect(self):
		print ("started connection to thread %s", self.name)
		x = yield websocket_connect("ws://echo.websocket.org",io_loop = self.eventLoop)
		print ("connected to thread %s", self.name)
		return x

	@tornado.gen.coroutine
	def receive(self):
		x = yield self.conn.read_message()
		return x


	def run(self):
		self.eventLoop.run_sync(self.innerRun)

	@tornado.gen.coroutine
	def innerRun(self):
		print ("started run for thread %s", self.name)
		self.conn = yield self.connect() #self.eventLoop.run_sync(self.connect)

		msg = "Hello!"
		self.conn.write_message(msg)
		response = yield self.receive() # self.eventLoop.run_sync(self.receive)
		print ("%s was received as thread %s" % (response,self.name))				


def mainMultiThreaded():
	wsThreads = []
	for index in range(20):
		newCon = WebsocketStreamingConnectionManager2(tornado.ioloop.IOLoop(),"Thread#"+str(index))
		newCon.start()		
		wsThreads.append(newCon)

	print ("created threads")

	for curThread in wsThreads:
		curThread.join()

	print ("started threads waiter")

	for cur_thread in wsThreads:
		cur_thread.join()		

	print("end time: {0}".format((time.time() - startTime)))

	


class MyState:
	def __init__(self, eventLoop, count):
		self.count = count
		self.my_lock = threading.Lock()
		self.eventLoop = eventLoop
	def dec(self,something):
		with self.my_lock:
			self.count = self.count -1
			
			if self.count ==0:
				self.eventLoop.stop()
		

@tornado.gen.coroutine
def main():
	myAsyncState = MyState(tornado.ioloop.IOLoop.current(),20)

	wsThreads = []
	for index in range(20):
		newCon = WebsocketStreamingConnectionManager(tornado.ioloop.IOLoop.current(),"Thread#"+str(index))
		newCon.run(callback=myAsyncState.dec)
		wsThreads.append(newCon)

	print ("created threads")

	print ("created threads waiter")

	print ("started threads waiter")

	print ("waiter on ioloop")

@tornado.gen.coroutine
def main3(count):

	wsThreads = []
	some_children = []
	for index in range(count):
		newCon = WebsocketStreamingConnectionManager(tornado.ioloop.IOLoop.current(),"Thread#"+str(index))
		some_children.append(newCon.run())
		wsThreads.append(newCon)

	yield tornado.gen.multi(some_children)

	print ("created threads")

	print ("created threads waiter")

	print ("started threads waiter")

	print ("waiter on ioloop")

def main3MPRunner():
	proccesses = []
	for index in range(4):
		new_proccess = Process(target=functools.partial(tornado.ioloop.IOLoop().run_sync,functools.partial(main3,5)))
		new_proccess.start()
		proccesses.append(new_proccess)
	
	for cur_proccess in proccesses:
		cur_proccess.join()

def main3SPRunner():
	tornado.ioloop.IOLoop.current().run_sync(functools.partial(main3, 20))


if __name__ == '__main__':
	startTime = time.time()
#	main()
#	tornado.ioloop.IOLoop.current().start()
#	tornado.ioloop.IOLoop.current().run_sync(main3)
	main3MPRunner()
	print("end time: %s" % str(time.time() - startTime))

#	mainMultiThreaded()
