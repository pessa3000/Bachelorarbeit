import os
import copy
import json, csv
import math
import os.path
import html

#Reading the prompts file and making the batch file
def tv3_to_batch(infile, outfile, model):
    with open(infile, "r") as in_file:
        data_list = json.load(in_file)
    #enunciat='Redacta una notícia escrita de tv3 amb el títol seguent: '
    #enunciat= "Completa el text de la següent notícia:"
    prompts=[]
    for num, data_set in enumerate(data_list):

        if len(data_set["corpus"].split(".")) <=5:
            print(f"err tv3 corpus article {data_set['custom_id']} is too short, will be skipped")
            continue
        if data_set['title'].endswith(" - 3CatInfo"):
            data_set['title']=data_set['title'][:-len(" - 3CatInfo")]
        #next_prompt= enunciat + "\nTítol: " + data_set["title"] + "\n" + "' d'unes " + str(len(data_set["QC_text"].split(" "))) + " paraules, sense enumeracions"
        #data_set["prompt"]=f"{data_set['title']} \n {''.join([sent+'.' for sent in data_set['QC_volltext'].split('.')[0:3]]) }"
        t= data_set["corpus"].replace(".\n", ". ")
        data_set["prompt"] = f"{data_set['title']} \n {''.join([sent + '. ' for sent in t.split('. ')[0:3]])}"

    dict1={"custom_id": "request-1", "body": {"model": "gpt-3.5-turbo-0125", "input": "Hello world!"},"max_tokens": 1000}
    requests_list = []

    for number, data_set in enumerate(data_list):
        data_dict = copy.deepcopy(dict1)

        if "prompt" in data_set.keys():
            data_dict["body"]["input"] = data_set["prompt"]
        else:
            continue
        batch_id= data_set["batch_id"]
        data_dict["body"]["model"] = model
        data_dict["batch_id"] = batch_id
        data_dict["custom_id"] = data_set["custom_id"].replace("tv3", f"KI_{model}")
        data_dict["url"] = data_set["url"]
        rest_length = sum(len(sent.split(" ")) for sent in data_set["corpus"].split(".")[3:] )
        data_dict["max_tokens"] = rest_length*6
        requests_list.append(data_dict)

    with open(outfile, 'w') as out_file:
        for entry in requests_list:
            json.dump(entry, out_file, ensure_ascii = False)
            out_file.write('\n')
    return 0