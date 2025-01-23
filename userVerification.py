import requests
from random import choice
from time import sleep, time

# ****************************************************************
# NEED TO WORK ON DATABASE VERIFICATION AFTER DATABASE CREATION
# ****************************************************************
from pymongo import MongoClient

# This function call codeforces api to get the user information
def verifyUser(message) -> list[bool,str]:
    handle = message.content.split(" ")[1]
    url = f"https://codeforces.com/api/user.info?handles={handle}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            database_verification_response = verifyUserInDataBase(data['result'][0])
            return database_verification_response
        else:
            return [False,f"Error: {data['comment']}"]
    else:
        # *************************************************************************
        # Need to change this message
        # it Says that the handle is not valid
        # *************************************************************************
        return [False,f"{message.author.mention} \n {handle} is not a valid handle"]


# ****************************************************************
# NEED TO WORK ON DATABASE VERIFICATION AFTER DATABASE CREATION
# ****************************************************************


# This function verifies the user in the database
def verifyUserInDataBase(result:dict) -> list[bool,str]:
    client = MongoClient('localhost', 27017)
    db = client['LockoutBot']
    collection = db['admin']
    cursor = collection.find({'handle' :result['handle']})
    if cursor.to_list().__len__():
        return [False,"User has already registered"]
    else:
        return[True,result['handle']]

# This function generates a random problem for the user
def generateRandomProblem() -> list[bool,list]:
    url = f"https://codeforces.com/api/problemset.problems"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            problems = data['result']['problems']
            problem = choice(problems)
            return_url = f"https://codeforces.com/problemset/problem/{problem['contestId']}/{problem['index']}"
            return [True,[return_url,problem['contestId'],problem['index']]]
        else:
            return [False,[f"Error: {data['comment']}"]]
    else:
        return [False,[f"Error: Unable to fetch data, status code {response.status_code}"]]


def get_user_submissions(handle,from1 = 1,count = 1) -> list[bool,str]:
    url = f"https://codeforces.com/api/user.status?handle={handle}&from={from1}&count={count}"
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            return [True,data['result']]
        else:
            return [False,f"Error: {data['comment']}"]
    else:
        return [False,f"Error: Unable to fetch data, status code {response.status_code}"]

# ****************************************************************
# NEED TO WORK ON DATABASE VERIFICATION AFTER DATABASE CREATION
# ****************************************************************


# def registerUserinDatabase(handle):
#   return




def registerUser(message , problem):
    handle = message.content.split(" ")[1]

    for _ in range(60):
        userSubmissionInformation = get_user_submissions(handle)
        if not userSubmissionInformation[0]:
            print(userSubmissionInformation[1])
            return [False,"User could not be registered. Some error occured on the server side"]
        verdict = get_user_submissions(handle)[1][0]
        if verdict['problem']['contestId'] == problem[1] and verdict['problem']['index'] == problem[2]:
            if verdict['verdict'] == 'COMPILATION_ERROR':
                # ****************************************************************
                # registerUserinDatabase(handle)
                # 
                # ****************************************************************
                return [True , "User has been registered"]
            else:
                # ****************************************************************
                # Need to send a message for wrong submission
                # ****************************************************************

                pass
        sleep(1)
        
    else:
        return [False,"User could not be registered"]








async def userRegistration(message):
    print(message)
    print(" Verificaiton request by ",message.author)
    message_id = await message.channel.send(f"verifyng user {message.author.mention} ...")
    verification_response = verifyUser(message)
    if not verification_response[0]:
        print(verification_response[1])
        await message_id.edit(content = verification_response[1])
        return
    problem = generateRandomProblem()
    if not problem[0]:
        print(problem[1][0])
        await message_id.edit(content = f"Registration could not be completed. Codeforces server is down")
        return
    
    # ****************************************************************
    # Need to enter steps for verification
    # Problem 
    # Compilation error in cpp
    # ****************************************************************
    
    await message_id.edit(content = f"registration in progress. Problem is {problem[1][0]}") 
    userRegisterMessage = registerUser(message , problem[1])
    if userRegisterMessage[0]:
        await message_id.edit(content = f"User has been registered")
    else:
        await message_id.edit(content = userRegisterMessage[1])
    print("User has been registered")
    return

if __name__ == "__main__":
    sol = generateRandomProblem()
    print(sol)
