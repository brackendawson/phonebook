export PHONE_BOOK_TEST=1
rm phonebook.db
python3 phonebookd.py &
sleep 1
python3 phonebook-tests.py
kill %%
