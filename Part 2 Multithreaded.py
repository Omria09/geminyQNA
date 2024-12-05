from langchain_google_genai import ChatGoogleGenerativeAI
import json
import random
from dotenv import load_dotenv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Globals
load_dotenv()
google_key = os.getenv("GOOGLE_API_KEY")
secondry_google_key = os.getenv("SECONDRY_API_KEY")
sampleCount = 20 # Sample count
max_tries = 2 # Maximum tries to get the correct result
dataSet = 'train.jsonl'

def parseAnswers():
    """
        open the answers lst file and add answers to answers list

        Returns:
            list: answsers list
    """
    answers = []  
    with open('train-labels.lst') as f:
        for line in f:
            answers.append(line.replace('\n',''))
    return answers

def parseQuestions(dataSet):
    """
    open jsonl dataset, add index to every line and save in data list 

    Args:
        dataSet (string): dataset location
    
    Returns:
        list: questions list
    """
    data = []
    index = 0
    with open(dataSet) as f:
        for line in f:
            indexer = {"index":str(index)}
            line = json.loads(line)
            line.update(indexer)
            data.append(line)
            index += 1
    return data

def askGoogle(llm, fullPrompt):
    """
    invoke the full prompt to the provided llm

    Args:
        llm (ChatGoogleGenerativeAI object): the llm used
        fullPrompt (string): the full query
    Returns:
        response object: res
    """
    factor = 3
    attempt = 0
    max_attempts = 5
    while attempt < max_attempts:
        try:
            res = llm.invoke(fullPrompt)
            return res
        except Exception as e:
            attempt += 1
            waitTime = factor ** attempt
            print(f"error: {str(e)}")
            print(f"Rate limit hit. Retrying in {waitTime} seconds...")
            if (waitTime > 60):
                return None
            time.sleep(waitTime)
        return None


def checkResultForQuestion(llm,item, answers, max_tries, optionA, optionB):
    flag = False
    tries = 0
    correctAnsCount = 0
    templatePrompt = "I will give you a question or sentence to complete and two possible answers. Please answer either A or B, depending on which answer is better. You must write down your reasoning but please write your final answer (either A or B) between the <answer> and </answer> tags"

    while (tries < max_tries and not flag):
        prompt = f"{templatePrompt} {str(item)}"
        res = askGoogle(llm, prompt)
        print(res.content)
        if ('<correct>' in res.content):
            correctAnsCount += 1
            flag = True
        elif (res is None):
            print('couldnt find an answer')
            flag = True
        elif (optionA in res.content and answers[int(item['index'])] == '0'):
            correctAnsCount += 1
            flag = True
        elif (optionB in res.content and answers[int(item['index'])] == '1'):
            correctAnsCount += 1
            flag = True
        else:
            print('incorrect, trying again')
            prompt = (f"I will provide you with a question and its associated explanation. "
            f"Your task is to evaluate whether the explanation correctly supports the answer to the question. "
            f"If the explanation is correct, respond with '<correct>'. "
            f"If the explanation is incorrect, provide a revised answer along with an updated explanation. "
            f"Here is the question: {str(item['goal'])} \n"
            f"And here is the explanation: {res.content}")
            #swap to other instance to escape quota block from free plan
            llm = ChatGoogleGenerativeAI( 
                model="gemini-pro",
                google_api_key=secondry_google_key,
            )
        tries += 1
    return correctAnsCount

def checkResult(prompts, answers):
    """
    Ask gemini (Google) the questions and then compare to our answers 

    Args:
        prompts (list): list of questions.
        answers (list): list of answers.

    Returns:
        int: the count of correct answers
    """
    correctAnsCount = 0
    # answer options
    optionA = '<answer>A</answer>'
    optionB = '<answer>B</answer>'
    # default prompts before any question
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=google_key,
    )

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures=[]
        for item in prompts:
            future = executor.submit(checkResultForQuestion, llm, item, answers, max_tries, optionA, optionB)
            futures.append(future)
        for futures in as_completed(futures):
            correctAnsCount += future.result()
        return correctAnsCount

def main():
    answers = parseAnswers()
    questions = parseQuestions(dataSet)

    # Take (int)'sampleCount' random questions
    randomFifty = random.sample(questions, sampleCount, counts=None)

    correctAnsCount = checkResult(randomFifty, answers)

    succRate = (correctAnsCount / sampleCount) * 100
    print (succRate, '% success rate')

if __name__=="__main__":
    main()