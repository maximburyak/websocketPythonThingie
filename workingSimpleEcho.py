import tornado.websocket
import tornado.concurrent
import tornado.ioloop
import tornado.httpclient
from tornado import escape
from tornado.websocket import websocket_connect
import functools
import threading
from multiprocessing import Process
import time
import json
import random


class SubscriptionCriteria(object):
	def __init__(self, collection, script=None):
		self.collection=collection
		self.script=script

class SubscriptionConnectionOptions(object):
	def __init__(self, retry_time, strategy, max_docs_per_batch, ignore_subscription_errors, max_batch_size=None, connection_id=None):
		self.retry_time = retru_time
		self.strategy=strategy
		self.max_docs_per_batch=max_docs_per_batch
		self.ignore_subscription_erros = ignore_subscription_erros
		self.max_batch_size = max_batch_size
		SubscriptionConnectionOptions.connections_counter

		connections_counter=connections_counter+1
		if connection_id is None:
			self.connection_id =  random.randrange(1000000000)


	connections_counter=0

class WebsocketStreamingConnectionManager:

	def __init__(self, eventLoop, name,ip,port,database_name, collection,start_etag,strategy,script):
		threading.Thread.__init__(self)
		self.eventLoop=eventLoop
		self.name = name	
		self.ip = ip
		self.port = port
		self.database_name = database_name	
		self.start_etag=start_etag
		self.strategy=strategy
		self.collection=collection
		self.script = script
		self.baseUrl = "http://"+self.ip+":"+str(self.port)+"/databases/"+self.database_name+"/subscriptions/"

	
	@tornado.gen.coroutine
	def create_subscription(self, criteria):
		createUrl = self.baseUrl +  "create?startEtag="+str(self.start_etag)

		http_client = tornado.httpclient.AsyncHTTPClient()
		criteriaAsJson=json.dumps(criteria.__dict__)

		create_subs_request =  tornado.httpclient.HTTPRequest(url=createUrl, method="POST", body=criteriaAsJson)

		create_subs_result = yield http_client.fetch(create_subs_request)
		subscription_id = escape.json_decode(create_subs_result.body)['Id']@tornado.gen.coroutine
		return subscription_id

	@tornado.gen.coroutine
	def subscription_connect(self):
		criteria = SubscriptionCriteria(self.collection, self.script)
		subscription_id=self.create_subscription(criteria)
		connection_id = random.randrange(1000000000)

		wsUrl = self.baseUrl + "pull?id="+subscription_id + "?conneciton=" +connection_id+"&strategy="+strategy
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
		self.conn = yield self.subscription_connect() #self.eventLoop.run_sync(self.connect)

		msg = "Hello!"
		self.conn.write_message(msg)
		response = yield self.receive() # self.eventLoop.run_sync(self.receive)
		print ("%s was received as thread %s" % (response,self.name))		


@tornado.gen.coroutine
def main(count):

	wsThreads = []
	some_children = []
	for index in range(count):
		newCon = WebsocketStreamingConnectionManager(tornado.ioloop.IOLoop.current(),"Thread#"+str(index),"192.168.56.1", 8080, "aaa","Apples",0, 0,None)
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
	proccessorsCount = 1
	requestsAmount = 2
#	tornado.ioloop.IOLoop.current().run_sync(functools.partial(main,1000))
	mainMPRunner(proccessorsCount, requestsAmount)
	print("end time: %s" % str(time.time() - startTime))

#	mainMultiThreaded()
