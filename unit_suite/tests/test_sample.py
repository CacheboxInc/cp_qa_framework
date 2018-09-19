import pytest
from assertpy import assert_that
import time
from httmock import all_requests, HTTMock
import requests

@pytest.mark.jira("CP-1907")
def test_1():
    print ("Printing Value Test 1")
    #time.sleep(20)
    assert_that(True).is_true()

@pytest.mark.sanity
def test_2():
    print ("Printing value Test 2")
    #time.sleep(20)
    assert True


def test_dummy():
    print("Printing value:  Dummy Test")
    #time.sleep(20)
    assert True


@all_requests
def response_content(url, request):
	return {'status_code': 200,
	        'content': 'Oh hai'}

@all_requests
def response_content_400(url , request):
        return{'statu_code' : 400,
                'content' : 'Bad request'}

with HTTMock(response_content):
	r = requests.get('https://foo_bar')

def test_200_response():
        with HTTMock(response_content):
            r = requests.get('http://domain.com/')
        print (r.status_code)
        print (r.content)

def test_400_response():
        with HTTMock(response_content_400):
            r = requests.get("http://planning.com") 
        print (r.status_code)
        print (r.content)



