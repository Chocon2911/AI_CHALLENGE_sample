import openai
import argparse
import time 
import re

from dataset import get_data

def get_response(args, user_request, max_len, temp):
    responese = openai.Completion.create(
        engine = args.model_name,
        prompt = user_request,
        max_tokens = max_len,
        n = 1,
        temperature = temp
    )

    return responese

def convert_to_submit_file(api_result: list = []):
    answer_start = api_result.find("Answer: ")
    if answer_start != -1:
        answer_end = api_result.find(",", answer_start)
        answer_part = api_result[answer_start + len("Answer: "):answer_end]

        if any(c.isalpha() for c in answer_part):
            answer = answer_part[0:answer_part.find(")")]  
        else:
            answer = answer_part
        return answer.lower()
    else:
        answer = api_result
        return answer.lower()
    return 'Nan'
            
                

def main(args):
    with open("openai_api_key.txt", "r") as f:
        openai.api_key = f.readline()
        test_examples = get_data(args.data)
        results = []
        with open('./results/results.txt', 'r') as read:
            results = read.readlines()
        curr_indx = 1
        last_indx = len(results)
        print("Last request: ", last_indx)
        with open('./results/results.txt', 'a') as f:
            for problem in test_examples:
                prompt = """
                Ignore all previous instructions, you are a very smart puzzle riddle and math problem solver you will use logic and reasoning to solve hard problems and get answers of this SAT math test in the simplest way.             
                       
            You're also someone who professionally checks spelling, logic, and structural errors. Before answering, If in {options} or {problem} there are some of these errors likes grammatical errors, vocabulary errors, expression errors, logical errors, mathematical errors  in the "Problem", please accurately amend and replace the previous answer in {options} by the new one and The answer must ONLY be in alphabet character (ignore unexpected extra characters and alphabet characters )  or numbers if {option}: "" and the units behind them are banned.
            Try to avoid distracting characters, symbols and numbers in {options} as much as possible,
            Which are banned in the {answers} : Symbols like ")", "(", "{", "}", numbers, rational numbers and their combinations.
            Your {answer} format should be like one of these choices and must not have any others banned stuff: 
            'a' OR 'b' OR 'c' OR 'd' OR 'e'
            If {answer} was not found, please check again until correct to make sure {answer} is not empty and write it in the {answer}
                """
                ques = problem["Problem"]
                max_len = 20
                temp = 0.2
                user_request = prompt + ques
                responese = {}
                if curr_indx > last_indx:
                    while 'id' not in responese:
                        try:
                            t1 = time.time()
                            responese = get_response(args, user_request, max_len, temp)
                            #print(user_request)
                            t2 = time.time()
                            time_request = t2 - t1
                            answer = responese.choices[0].text
                            #results.append([answer, time_request])
                        except:
                            print("Waiting...")
                            time.sleep(20)
                            continue
                    print(f"Time request for {problem['id']}: {time_request}, answer: {answer}")
                    choose = convert_to_submit_file(answer)
                    f.write(choose + '\t' + str(time_request) + '\n')
                    
                curr_indx += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
		"--model_name", type=str, 
		default="text-davinci-003",
        help= "Name to request model from openai"
	)
    parser.add_argument(
		"--data", type=str, 

		default="./data/test.json",
		help="Path to data test"
	)

    args = parser.parse_args()
    main(args)
