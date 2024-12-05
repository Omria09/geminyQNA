# GEMINIQNA

GEMINIQNA is a Python program that asks the gemini model 50 random questions from the dataset and returns the model’s success rate.

**Made in roughly 5 hours.**

# The parts (and success rates)
### PART 1: 
asking the model once and comparing the answers with the answers list.

>**success rate for 50 questions: 64%**

### PART 2: 
asking the model once and if the answer is deemed incorrect, keep asking the revised question and explanation untill it determines the result is correct.

>**success rate for 50 questions: 85%**, up to 100% depending on retry amount (currently set to 2)


### PART 2 Multithreaded:
 Same as part 2, but instead of asking the same model it asks a diffrent instance of gemini. also, invokes the questions in a threads to reduce waiting time between question and answers. also added factorial quota wait to reduce rate limit hits

>**I discontinued this part as the gemini quota block made it kinda useless, thus Its unfinished but I've kept it here if in the future Ill try the paid version**

_note_: when an instance decides the explanation is correct it will increase the correct answers _without_ comparing the the answers list again. 


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install langchain_google_genai and dotenv.

```bash
pip install langchain-google-genai python-dotenv
```

Add a .env file with the following content:
```
GOOGLE_API_KEY=YOUR_API_KEY_HERE
```

## Usage

```python
python Part x.py
