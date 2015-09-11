import http.server, socketserver
import os, traceback
import sqlite3, json

HOST = ""
PORT = 8000
DATABASE = "phonebook.db"

class PhoneBook():
	
	@classmethod
	def handle_get(cls):
		#there is only one get
		return cls.list_all()

	@classmethod
	def handle_post(cls, path, data):
		cmd = path.split("/")[1]
		if cmd == "create":
			return cls.create(data)
		if cmd == "remove":
			return cls.remove(data)
		if cmd == "update":
			return cls.update(data)
		if cmd == "search":
			return cls.search(data)
		return(404, "Unknown action.");

	@staticmethod
	def list_all():
		c = db.execute("SELECT surname, firstname, number, address FROM phonebook ORDER BY surname ASC;")
		data = []
		for row in c:
			data.append({"surname": row[0], "firstname": row[1], "number": row[2], "address": row[3]})
		if len(data) == 0:
			return(204, "")
		return(200, json.dumps(data))

	@staticmethod
	def create(data):
		try:
			entry = json.loads(data)
		except ValueError:
			return(400, "Bad request data.")
		if not type(entry) is dict:
			return(400, "Bad request data.")
		try:
			surname = entry["surname"]
			firstname = entry["firstname"]
			number = entry["number"]
		except KeyError:
			return(400, "Missing compulsory field.")
		if not surname or not firstname or not number:
			return(400, "Missing compulsory field.")
		address = ""
		if "address" in entry.keys():
			address = entry["address"]
		
		#check for dupes
		c = db.execute("SELECT EXISTS(SELECT 1 FROM phonebook WHERE surname=? AND firstname=? AND number=? AND address=? LIMIT 1);", (surname, firstname, number, address))
		if not c.fetchone() == (0,):
			return(409, "Duplicate entry.");

		c = db.execute("INSERT INTO phonebook (surname, firstname, number, address) VALUES (?, ?, ?, ?);", (surname, firstname, number, address))
		return(201, "")

	@staticmethod
	def remove(data):
		try:
			entry = json.loads(data)
		except ValueError:
			return(400, "Bad request data.")
		if not type(entry) is dict:
			return(400, "Bad request data.")
		try:
			surname = entry["surname"]
			firstname = entry["firstname"]
			number = entry["number"]
		except KeyError:
			return(400, "Missing compulsory field.")
		if not surname or not firstname or not number:
			return(400, "Missing compulsory field.")
		address = ""
		if "address" in entry.keys():
			address = entry["address"]
		
		#check entry exists
		c = db.execute("SELECT EXISTS(SELECT 1 FROM phonebook WHERE surname=? AND firstname=? AND number=? AND address=? LIMIT 1);", (surname, firstname, number, address))
		if not c.fetchone() == (1,):
			return(404, "No such entry.");

		c = db.execute("DELETE FROM phonebook WHERE surname=? AND firstname=? AND number=? AND address=?;", (surname, firstname, number, address))
		return(201, "")
	
	@staticmethod
	def search(data):
		try:
			entry = json.loads(data)
		except ValueError:
			return(400, "Bad request data.")
		if not type(entry) is dict:
			return(400, "Bad request data.")
		try:
			surname = entry.pop("surname")
		except KeyError:
			return(400, "Missing compulsory field.")
		if not surname:
			return(400, "Missing compulsory field.")
		if len(entry) > 0:
			return(400, "Unsupported field.")
		
		#search
		c = db.execute("SELECT surname, firstname, number, address FROM phonebook WHERE surname LIKE '%' || ? || '%' ORDER BY surname ASC;", (surname,))
		data = []
		for row in c:
			data.append({"surname": row[0], "firstname": row[1], "number": row[2], "address": row[3]})
		if len(data) == 0:
			return(404, "")
		return(200, json.dumps(data))
		

class PhoneBookHTTPHandler(http.server.BaseHTTPRequestHandler):

	def do_HEAD(self):
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()
	
	def do_GET(self):
		try:
			(response, data) = PhoneBook.handle_get()
		except:
			response = 500
			data = "Server Error"
			print(traceback.format_exc())
		self.send_response(response)
		self.send_header("Content-type", "application/json")
		self.send_header('Content-Length', str(len(data)))
		self.end_headers()
		self.wfile.write(bytes(data, "utf-8"))

	def do_POST(self):
		data = self.rfile.read(int(self.headers.get("Content-Length"))).decode("utf-8")
		try:
			(response, data) = PhoneBook.handle_post(self.path, data)
		except:
			response = 500
			data = "Server Error"
			print(traceback.format_exc())
		self.send_response(response)
		self.send_header("Content-type", "application/json")
		self.send_header('Content-Length', str(len(data)))
		self.end_headers()
		self.wfile.write(bytes(data, "utf-8"))

db = sqlite3.connect(DATABASE)
c = db.execute("SELECT SQLITE_VERSION()")
print("SQLite version: " + str(c.fetchone()))
c = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='phonebook'")
if not c.fetchone():
	print("Initialising database.")
	db.execute('''CREATE TABLE phonebook ( 
		surname TEXT NOT NULL,
		firstname TEXT NOT NULL,
		number TEXT NOT NULL,
		address TEXT NOT NULL)''')
	
#not protected from stray packets in test mode
if os.getenv('PHONE_BOOK_TEST'):
	socketserver.TCPServer.allow_reuse_address = True

httpd = socketserver.TCPServer((HOST, PORT), PhoneBookHTTPHandler)
httpd.serve_forever()
