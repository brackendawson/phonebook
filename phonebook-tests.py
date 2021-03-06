import unittest
import requests, json

URL = "http://localhost:8000/"

class PhoneBookTest(unittest.TestCase):

	def test_0_list_all(self):
		#an empty database is an empty 204 response
		r = requests.get(URL)
		assert r.status_code == 204
		assert r.text == ""

		#one entry
		text = json.dumps({"surname": "Prefect", "firstname": "Ford", "number": "01818118181", "address": "Betelgeuse"})
		r = requests.post(URL + "create", data=text)
		r = requests.get(URL)
		assert r.status_code == 200
		backdata = json.loads(r.text)
		assert backdata == [{"surname": "Prefect", "firstname": "Ford", "number": "01818118181", "address": "Betelgeuse"}]

		#more entres are returned alphabetically by surname
		text = json.dumps({"surname": "Dent", "firstname": "Arthur", "number": "01818118181"})
		r = requests.post(URL + "create", data=text)
		assert 200 <= r.status_code < 300
		r = requests.get(URL)
		assert 200 <= r.status_code < 300
		backdata = json.loads(r.text)
		assert backdata == [{"surname": "Dent", "firstname": "Arthur", "number": "01818118181", "address": ""},
			{"surname": "Prefect", "firstname": "Ford", "number": "01818118181", "address": "Betelgeuse"}]


	def test_1_add_entry(self):
		#add an antry and check it's in the output
		entry = {"surname": "Beeblebrox", "firstname": "Zaphod", "number": "01818118182", "address": "Betelgeuse, Milky Way"}
		text = json.dumps(entry)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 201
		r = requests.get(URL)
		assert r.status_code == 200 
		backdata = json.loads(r.text)
		assert entry in backdata

		#add an entry with different json formatting
		entry = {"surname": "Watney", "firstname": "Mark", "number": "01818118183", "address": "Mars\nSol\nMilky Way"}
		text = json.dumps(entry, sort_keys=True, indent=4)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 201
		r = requests.get(URL)
		assert r.status_code == 200
		backdata = json.loads(r.text)
		assert entry in backdata

		#test optional fields
		#must fail
		r = requests.get(URL, data=text)
		assert r.status_code == 200
		count = len(json.loads(r.text))
		text = json.dumps({"surname": "Hadfield", "firstname": "Chris", "number": "", "address": "Earth, Sol, Milky Way"})
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 400
		assert r.text == "Missing compulsory field."
		text = json.dumps({"surname": "", "firstname": "Chris", "number": "01818118184", "address": "Earth, Sol, Milky Way"})
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 400
		assert r.text == "Missing compulsory field."
		text = json.dumps({"surname": "Hadfield", "number": "01818118184", "address": "Earth, Sol, Milky Way"})
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 400
		assert r.text == "Missing compulsory field."
		r = requests.get(URL)
		assert r.status_code == 200
		assert count == len(json.loads(r.text)) #the above generated no additional entries in the phonebook
		#must succeed
		entry = {"surname": "Hadfield", "firstname": "Chris", "number": "+11818118184"}
		text = json.dumps(entry)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 201
		r = requests.get(URL)
		assert r.status_code == 200
		backdata = json.loads(r.text)
		entry = {"surname": "Hadfield", "firstname": "Chris", "number": "+11818118184", "address": ""}
		assert entry in backdata
		entry = {"surname": "Armstrong", "firstname": "Neil", "number": "01818118185", "address": ""}
		text = json.dumps(entry)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 201
		r = requests.get(URL)
		assert r.status_code == 200
		backdata = json.loads(r.text)
		assert entry in backdata

		#test duplicate entry
		entry = {"surname": "Aldrin", "firstname": "Buzz", "number": "01818118186"}
		text = json.dumps(entry)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 201
		r = requests.get(URL, data=text)
		assert r.status_code == 200
		count = len(json.loads(r.text))
		entry = {"surname": "Aldrin", "firstname": "Buzz", "number": "01818118186", "address": ""} #I consider these duplicates
		text = json.dumps(entry)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 409
		assert r.text == "Duplicate entry."
		r = requests.get(URL, data=text)
		assert r.status_code == 200
		assert count == len(json.loads(r.text)) #the duplicate cause no additional entry in the phonebook
		entry = {"surname": "Aldrin", "firstname": "Buzz", "number": "01818118186", "address": "The Moon"} #Not a duplicate
		text = json.dumps(entry)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 201
		r = requests.get(URL, data=text)
		assert r.status_code == 200
		count = len(json.loads(r.text))
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 409
		assert r.text == "Duplicate entry."

	def test_1_remove_entry(self):
		#there is no key and you need to say the whole entry you want to delete exactly right
		#delete an nonexistant entry
		entry = {"surname": "Gagarin", "firstname": "Uri", "number": "01818118187", "address": ""}
		text = json.dumps(entry)
		r = requests.post(URL + "remove", data=text)
		assert r.status_code == 404
		assert r.text == "No such entry."
		r = requests.get(URL)
		assert r.status_code == 200
		backdata = json.loads(r.text)
		assert not entry in backdata
		
		#delete an entry that exists
		entry = {"surname": "Gagarin", "firstname": "Uri", "number": "01818118187"}
		text = json.dumps(entry)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 201
		#test compulory fields
		entry = {"surname": "Gagarin", "firstname": "Uri", "number": "01818118187"}
		text = json.dumps(entry)
		r = requests.post(URL + "remove", data=text)
		assert r.status_code == 400
		assert r.text == "Missing compulsory field."
		entry = {"surname": "Gagarin", "firstname": "Uri", "address": ""}
		text = json.dumps(entry)
		r = requests.post(URL + "remove", data=text)
		assert r.status_code == 400
		assert r.text == "Missing compulsory field."
		entry = {"surname": "Gagarin", "number": "01818118187", "address": ""}
		text = json.dumps(entry)
		r = requests.post(URL + "remove", data=text)
		assert r.status_code == 400
		assert r.text == "Missing compulsory field."
		entry = {"firstname": "Uri", "number": "01818118187", "address": ""}
		text = json.dumps(entry)
		r = requests.post(URL + "remove", data=text)
		assert r.status_code == 400
		assert r.text == "Missing compulsory field."
		#test a good deletion now
		entry = {"surname": "Gagarin", "firstname": "Uri", "number": "01818118187", "address": ""}
		text = json.dumps(entry)
		r = requests.post(URL + "remove", data=text)
		assert r.status_code == 201 #tricky one, but I'm saying 201 because it yeilds a change
		r = requests.get(URL)
		assert r.status_code == 200
		backdata = json.loads(r.text)
		assert not entry in backdata
	
	def test_1_update_entry(self):
		#update an non-existing entry
		entry = {"surname": "collins", "firstname": "michael ", "number": "01818118188", "address": "",
			"newsurname": "Collins", "newfirstname": "Michael", "newnumber": "01818118189", "newaddress": "Other side of the moon."}
		text = json.dumps(entry)
		r = requests.post(URL + "update", data=text)
		assert r.status_code == 404
		assert r.text == "No such entry."

		#update an existing entry
		entry = {"surname": "collins", "firstname": "michael ", "number": "01818118188", "address": ""}
		text = json.dumps(entry)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 201
		entry = {"surname": "collins", "firstname": "michael ", "number": "01818118188", "address": "",
			"newsurname": "Collins", "newfirstname": "Michael", "newnumber": "01818118189", "newaddress": "Other side of the moon."}
		text = json.dumps(entry)
		r = requests.post(URL + "update", data=text)
		assert r.status_code == 201
		r = requests.get(URL)
		assert r.status_code == 200
		backdata = json.loads(r.text)
		entry = {"surname": "Collins", "firstname": "Michael", "number": "01818118189", "address": "Other side of the moon."}
		assert entry in backdata

		#invalidate an entry - thank you other applicant for leaving your code on github
		entry = {"surname": "Collins", "firstname": "Michael", "number": "01818118189", "address": "Other side of the moon.",
			"newsurname": ""}
		text = json.dumps(entry)
		r = requests.post(URL + "update", data=text)
		assert r.status_code == 400
		assert r.text == "Missing compulsory field."
		entry = {"surname": "Collins", "firstname": "Michael", "number": "01818118189", "address": "Other side of the moon.",
			"newfirstname": ""}
		text = json.dumps(entry)
		r = requests.post(URL + "update", data=text)
		assert r.status_code == 400
		assert r.text == "Missing compulsory field."
		entry = {"surname": "Collins", "firstname": "Michael", "number": "01818118189", "address": "Other side of the moon.",
			"newnumber": ""}
		text = json.dumps(entry)
		r = requests.post(URL + "update", data=text)
		assert r.status_code == 400
		assert r.text == "Missing compulsory field."

	def test_1_search_surname(self):
		entry1 = {"surname": "Lovell", "firstname": "Jim", "number": "01818118190", "address": ""}
		text = json.dumps(entry1)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 201
		entry2 = {"surname": "Lovell", "firstname": "Marilyn", "number": "01818118190", "address": ""}
		text = json.dumps(entry2)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 201
		entry3 = {"surname": "Mattingly", "firstname": "Ken", "number": "01818118191", "address": ""}
		text = json.dumps(entry3)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 201
		entry4 = {"surname": "Haise", "firstname": "Fred", "number": "01818118192", "address": ""}
		text = json.dumps(entry4)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 201
				
		#test a search that returns one entry
		entry = {"surname": "hais"}
		text = json.dumps(entry)
		r = requests.post(URL + "search", data=text)
		assert r.status_code == 200
		backdata = json.loads(r.text)
		assert len(backdata) == 1
		assert entry4 in backdata

		#test a search that returns more than one entry
		entry = {"surname": "LOVELL"}
		text = json.dumps(entry)
		r = requests.post(URL + "search", data=text)
		assert r.status_code == 200
		backdata = json.loads(r.text)
		assert len(backdata) == 2
		assert entry1 in backdata
		assert entry2 in backdata

		#test a search that returns no entries
		entry = {"surname": "Dawson"}
		text = json.dumps(entry)
		r = requests.post(URL + "search", data=text)
		assert r.status_code == 404
		assert r.text == ""

		#test a search on an unsupported field
		entry = {"firstname": "Bracken"}
		text = json.dumps(entry)
		r = requests.post(URL + "search", data=text)
		assert r.status_code == 400
		assert r.text == "Missing compulsory field." or r.text == "Unsupported field."

		#test an entry including an unspported field
		entry = {"surname": "Lovell", "firstname": "Jack"}
		text = json.dumps(entry)
		r = requests.post(URL + "search", data=text)
		assert r.status_code == 400
		assert r.text == "Unsupported field."

	def test_1_bad_url(self):
		entry = {"surname": "Lovell", "firstname": "Jack"}
		text = json.dumps(entry)
		r = requests.post(URL + "add", data=text)
		assert r.status_code == 404
		assert r.text == "Unknown action."

	def test_1_http_head(self):
		r = requests.head(URL)
		assert r.status_code == 200
		assert r.headers['content-type'] == "application/json"
		r = requests.get(URL)
		assert 200 <= r.status_code < 300
		assert r.headers['content-type'] == "application/json"

	'''def test_1_non_utf_8(self):
		# "þÿ" (fe ff) is not valid in any utf-8 string
		entry = {"surname": "kosþÿme", "firstname": "κόσμε", "number": "01818118193", "address": ""}
		text = json.dumps(entry)
		r = requests.post(URL + "create", data=text)
		print(r.status_code)
		print(r.text)
		assert r.status_code == 400
		assert r.text == "Bad request data."
		entry = {"surname": "kosme", "firstname": "κόσþÿμε", "number": "01818118193", "address": ""}
		text = json.dumps(entry)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 400
		assert r.text == "Bad request data."
		entry = {"surname": "kosme", "firstname": "κόσμε", "number": "þÿ01818118193", "address": ""}
		text = json.dumps(entry)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 400
		assert r.text == "Bad request data."
		entry = {"surname": "kosme", "firstname": "κόσμε", "number": "01818118193", "address": "þÿ"}
		text = json.dumps(entry)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 400
		assert r.text == "Bad request data."
		
		#A good one for luck
		entry = {"surname": "kosme", "firstname": "κόσμε", "number": "01818118193", "address": ""}
		text = json.dumps(entry)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 201		
		r = requests.get(URL)
		assert r.sttus_code == 200
		backdata = json.loads(r.text)
		assert entry in backdata
		#now update it badly
		entry = {"surname": "kosme", "firstname": "κόσμε", "number": "01818118193", "address": "", "newsurname": "þÿ"}
		text = json.dumps(entry)
		r = requests.post(URL + "update", data=text)
		assert r.status_code == 400
		assert r.text == "Bad request data."
		#and search badly
		entry = {"surname": "kosþÿme"}
		text = json.dumps(entry)
		r = requests.post(URL + "search", data=text)
		assert r.status_code == 400
		assert r.text == "Bad request data."'''
	
	def test_1_truncate_json(self):
		entry = {"surname": "Bowman", "name": "David", "number": "01818118194", "address": ""}
		text = json.dumps(entry)
		r = requests.post(URL + "create", data=text[0:10])
		assert r.status_code == 400
		assert r.text == "Bad request data."
		r = requests.post(URL + "remove", data=text[0:3])
		assert r.status_code == 400
		assert r.text == "Bad request data."
		r = requests.post(URL + "update", data=text[0:14])
		assert r.status_code == 400
		assert r.text == "Bad request data."
		r = requests.post(URL + "search", data="")
		assert r.status_code == 400
		assert r.text == "Bad request data."

	def test_1_not_json(self):
		r = requests.post(URL + "create", data="One wonders if one is writing too many tests.")
		assert r.status_code == 400
		assert r.text == "Bad request data."
		r = requests.post(URL + "remove", data="One cannot have too many tests.")
		assert r.status_code == 400
		assert r.text == "Bad request data."
		r = requests.post(URL + "update", data="Well, you can, but I don't think this is it.")
		assert r.status_code == 400
		assert r.text == "Bad request data."
		r = requests.post(URL + "search", data="lks{ejr}fl: ;iuwejrlkasjflkjSF")
		assert r.status_code == 400
		assert r.text == "Bad request data."

	def test_1_bobby_tables(self):
		#try to inject SQL
		entry = {"surname": "Heywood", "firstname": "Floyd", "number": "01818118196", "address": ""}
		text = json.dumps(entry)
		r = requests.post(URL + "create", data=text)
		assert r.status_code == 201
		entry = {"surname": "Heywood'); DROP TABLE phonebook;", "firstname": "Floyd; DROP TABLE phonebook;", "number": "01818118196; DROP TABLE phonebook;", "address": ";DROP TABLE phonebook;"}
		text = json.dumps(entry)
		r = requests.post(URL + "remove", data=text)
		r = requests.get(URL)
		assert r.status_code == 200 #not 204

		entry = {"surname": "Poole'); DROP TABLE phonebook;", "firstname": "Frank; DROP TABLE phonebook;", "number": "01818118195'; DROP TABLE phonebook;", "address": ";DROP TABLE phonebook;"}
		text = json.dumps(entry)
		r = requests.post(URL + "create", data=text)
		r = requests.get(URL)
		assert r.status_code == 200 #not 204

		entry = {"surname": "'); DROP TABLE phonebook;"}
		text = json.dumps(entry)
		r = requests.post(URL + "search", data=text)
		r = requests.get(URL)
		assert r.status_code == 200 #not 204

if __name__ == '__main__':
	unittest.main()
