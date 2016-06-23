#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import random
from os import curdir, sep, path, getcwd, chdir
import pymongo
import sched, time
from threading import Thread, Lock
from bson import BSON

scheduled_task = sched.scheduler(time.time, time.sleep)

mutex = Lock()

client = pymongo.MongoClient()
db = client.socket_logs
coll = db.tcp_server

result_table = ""

home_dir = path.dirname(path.realpath(__file__))
chdir(home_dir)

def unicode_msg(s):
	try:
		return s.decode('utf8').encode('utf8')
	except Exception as e:
		return "Failed to decode message."

def table_generator(table_content): 
	return """
	<table>
	<tr>
		<th>IP</th>
		<th>Timestamp</th>
		<th>Message</th>
	</tr>
	%s
	</table>
	</div>
	</body>
	</html>
	""" % table_content

def table_row(ip, timestamp, message):
	return u"<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (ip, timestamp, message.decode('utf8')[:30] + " ..." if len(message.decode('utf8')) > 30 else message.decode('utf8'))

def refresh_table(sc):
	mutex.acquire()
	try:
		global coll, result_table
		result_table = ""

		for doc in coll.find().sort([['date', pymongo.DESCENDING]])[:20]:
			ts = doc['date']
			ts_str = "%d/%02d/%02d %02d:%02d:%02d.%03d" % (ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second, int(ts.microsecond/1000))
			msg = ''.join(list(doc['message']))
	
			msg_str = unicode_msg(msg)

			msg_str = msg_str.replace("<", "&#60;").replace(">", "&#62;")

			result_table += table_row(doc['ip'], ts_str, msg_str).encode('utf8')
		sc.enter(1, 1, refresh_table, (sc,))
	finally:
		mutex.release()

class HTTP_Request_Handler(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_GET(self):
		mutex.acquire()
		try:
			global result_table
		finally:
			mutex.release()

			if self.path=="/":
				self.path="/index.html"

			try:
				sendReply = False
				if self.path.endswith(".html"):
					mimetype='text/html'
					sendReply = True
				if self.path.endswith(".jpg"):
					mimetype='image/jpg'
					sendReply = True
				if self.path.endswith(".gif"):
					mimetype='image/gif'
					sendReply = True
				if self.path.endswith(".js"):
					mimetype='application/javascript'
					sendReply = True
				if self.path.endswith(".css"):
					mimetype='text/css'
					sendReply = True

				if sendReply == True:
					f = open(curdir + sep + self.path) 
					self.send_response(200)
					self.send_header('Content-type', mimetype)
					self.end_headers()
					self.wfile.write(f.read())

					if self.path.endswith("index.html"):
						mutex.acquire()
						try:
							self.wfile.write(table_generator(result_table))
						finally:
							mutex.release()
					f.close()
				return

			except IOError:
				self.send_error(404, 'File Not Found: %s' % self.path)

			self._set_headers()
			global home_dir
			f = open("%s%sindex.html" % (home_dir, sep), "r")
			self.wfile.write(f.read())
			f.close()

	def do_HEAD(self):
		self._set_headers()

	def do_POST(self):
		self._set_headers()
		print "in post method"
		self.data_string = self.rfile.read(int(self.headers['Content-Length']))

		self.send_response(200)
		self.end_headers()

		#data = simplejson.loads(self.data_string)
		#with open("test123456.json", "w") as outfile:
		#	simplejson.dump(data, outfile)
		#print "{}".format(data)
		#f = open("for_presen.py")
		self.wfile.write(f.read())
		f.close()
		return

def run_server(server_class=HTTPServer, handler_class=HTTP_Request_Handler, port=7777):
	print "Server running..."
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	print 'Starting httpd...'
	httpd.serve_forever()

if __name__ == "__main__":
	from sys import argv

scheduled_task.enter(1, 1, refresh_table, (scheduled_task,))

t_sched = Thread(target = scheduled_task.run)

if len(argv) == 2:
	t_serv = Thread(target = run_server, kwargs={'port': int(argv[1])})
else:
	t_serv = Thread(target = run_server)

t_sched.start()
t_serv.start()
