import tornado.websocket
import tornado.concurrent
import tornado.ioloop
import tornado.httpclient
from tornado.websocket import websocket_connect
import functools
import threading
from multiprocessing import Process
import time
import json
import random

class WebsocketStreamingConnectionManager:

	def __init__(self, eventLoop, name,ip,port,database_name,start_etag,strategy):
		threading.Thread.__init__(self)
		self.eventLoop=eventLoop
		self.name = name	
		self.ip = ip
		self.port = port
		self.database_name = database_name	
		self.start_etag=start_etag
		self.strategy=strategy

	@tornado.gen.coroutine
	def connect(self):
		print ("started connection to thread %s", self.name)
		#x = yield websocket_connect("ws://echo.websocket.org",io_loop = self.eventLoop)
		x = yield websocket_connect("ws://192.168.56.1:8080/databases/echo3/subscriptions/echo",io_loop = self.eventLoop)
		print ("connected to thread %s", self.name)
		return x

	def subscription_connect(self):
		createUrl = "http://"+self.ip+":"+self.port+"/databases/"+self.database_name+"/subscriptions/create?startEtag="+self.start_etag


		http_client = tornado.httpclient.AsyncHTTPClient()
		subscription_id = json.loads(yield http_client.fetch(createUrl))['Id']		
		connection_id = random.randrange(1000000000)

		wsUrl = "ws://"+self.ip+":"+self.port+"/databases/"+self.database_name+"/subscriptions/pull?id="+subscription_id + "?conneciton=" +connection_id+"&strategy="+strategy
		x = yield websocket_connect(wsUrl,io_loop = self.eventLoop)
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


@tornado.gen.coroutine
def main(count):

	wsThreads = []
	some_children = []
	for index in range(count):
		newCon = WebsocketStreamingConnectionManager(tornado.ioloop.IOLoop.current(),"Thread#"+str(index),"192.168.56)
		some_children.append(newCon.run())
		wsThreads.append(newCon)

	yield tornado.gen.multi(some_children)

	print ("created threads")

	print ("created threads waiter")

	print ("started threads waiter")

	print ("waiter on ioloop")

def mainMPRunner(processorsCount, requestsAmount):
	proccesses = []
	for index in range(proccessorsCount * 2):
		new_proccess = Process(target=functools.partial(tornado.ioloop.IOLoop().run_sync,functools.partial(main,int(requestsAmount/(proccessorsCount*2)))))
		new_proccess.start()
		proccesses.append(new_proccess)
	
	for cur_proccess in proccesses:
		cur_proccess.join()

def main3SPRunner():
	tornado.ioloop.IOLoop.current().run_sync(functools.partial(main3, 20))


if __name__ == '__main__':
	startTime = time.time()
	proccessorsCount = 4
	requestsAmount = 1000
#	tornado.ioloop.IOLoop.current().run_sync(functools.partial(main,1000))
	mainMPRunner(proccessorsCount, requestsAmount)
	print("end time: %s" % str(time.time() - startTime))

#	mainMultiThreaded()
