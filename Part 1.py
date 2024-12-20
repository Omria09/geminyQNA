from langchain_google_genai import ChatGoogleGenerativeAI
import json
import random
from dotenv import load_dotenv
import os

load_dotenv()
google_key = os.getenv("GOOGLE_API_KEY")

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

def askGoogle(prompts, answers):
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
    templatePrompt = "I will give you a question or sentence to complete and two possible answers. Please answer either A or B, depending on which answer is better. You may write down your reasoning but please write your final answer (either A or B) between the <answer> and </answer> tags"
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=google_key,
    )

    for item in prompts:
        try:
            res = llm.invoke(templatePrompt + str(item))
            if (optionA in res.content and answers[int(item['index'])] == '0'):
                correctAnsCount += 1
            elif (optionB in res.content and answers[int(item['index'])] == '1'):
                correctAnsCount += 1
            else:
                print("false")
        except Exception as e:
            print(f"error: {str(e)}")
            continue
    return correctAnsCount

def main():
    sampleCount = 50 # Count of queries to make
    succRate = 0 # starting success rate 0%
    dataSet = 'train.jsonl'

    answers = parseAnswers()
    questions = parseQuestions(dataSet)

    # Take (int)'sampleCount' random questions
    randomFifty = random.sample(questions, sampleCount, counts=None)

    correctAnsCount = askGoogle(prompts=randomFifty, answers=answers)

    succRate = (correctAnsCount / sampleCount) * 100
    print (succRate, '% success rate')

    # Optional rounded answer
    ## print (f'{round(succRate,0):g}', '% success rate')

if __name__=="__main__":
    main()