A simple phone book server
==========================

A HTTP phone book back end like many others.

API
---
Use GET to list all entries. Returns a json array of dictionaries sorted
alphabetically by surname representing all entries in the database.

Create:
Use POST to url/create create an entry with a json dictionary containing:
-surname - Mandatory text field.
-firstname - Mandatory text field.
-number - Mandatory text field.
-address - Optional text field.

Remove:
POST to url/remove with the entire entry you wish to delete as is so in
create, including any blank address field, to delete that entry from the
database.

Update:
POST to url/update with the entire entry you widh to change as is so in
remove, including any blank address field. Replace data with the following
fields in the same dictionary:
-newsurname - Mandatory text field.
-newfirstname - Mandatory text field.
-newnumber - Mandatory text field.
-newaddress - Optional text field.

Search:
POST to url/search with a case insensitive surname or fragment you wish to
serch with.
-surname - Mandatory text field for search string.
Returns an json array of dictionaries representing matching entries.

WTFPL - © 2015 Bracken Dawson
