# ADAPTACIO PER TV3 OLEEEEEEEEEEEEEEEEE  
#code copied from the tutorial https://www.zenrows.com/blog/article-scraper#extract-all-articles-data
#functioning for gamestop :)
# original version i need to adapt


# import the required libraries
from bs4 import BeautifulSoup
import requests
import json
import html
from time import strftime, localtime,  gmtime
import time

import emoji
from cleaning_tools import tv3_r2c, gen_r2c, corpus_to_data




#this is the adapted tfg for the post 17.09.25 tv3 layout
def article_scraper(article_url):
    # create a new dictionary for each article
    data = {}  
    try:
        response = requests.get(article_url)
 
        soup = BeautifulSoup(response.content, 'html.parser')
        #with open("soup"+article_url.replace("/", "_")+".txt", "w") as f:
        #    f.write(str(soup))

        #data['article_url'] = article_url
        title_element = soup.find('title')
        data['title'] = title_element.text.strip() if title_element else ''
 
        # extract published date, handle NoneType
        published_date_element = soup.find('time')
        data['published_date'] = published_date_element['datetime'] if published_date_element else ''
 
        # extract author, handle NoneType
        author_element = soup.find('span', class_='byline-author')
        data['author'] = author_element.text.strip() if author_element else ''
 
        # extract content, handle NoneType
        #content_element = soup.find('div', class_='content-entity-body')
        #data["text"] = content_element.text.strip() if content_element else ''
        
        #in the new version of the tv3 news website, text is found in the second ld-json object! 
        #!in the website prior to 17.09.25 it was the first object
        if len(soup.find_all("script", type="application/ld+json"))<2:
            print("no content in url found", article_url)
            return 0
        else:
            json_ld= soup.find_all("script", type="application/ld+json")[1]
            jason= json.loads(json_ld.string, strict=False)
            contingut_element= jason.get('articleBody')
            #print("CONTENT OF THE ARTICLE", contingut_element)
            data["text"]= contingut_element if contingut_element else ''

            #save url
            url_element = jason.get('url')
            data['url'] = url_element if url_element else ''

                #taste the soup, figure out its ingredients
                #for keys, values in json.loads(j, strict=False).items():
                #    print(keys, values)
        
    except requests.RequestException as e:
        print(f'Error fetching article data for {article_url}: {e}')
    if data["text"]:
        return data
    else:
        return 0
        
def links_getter(base_URL, category_URL):
    response = requests.get(category_URL)

    #getting news links
    data_links  = []
     
    if response.status_code == 200:
 
        # parse HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
    
        #  get link cards
        article_links = soup.find_all('a', class_='media-object')
 
            # iterate through link cards to get article unique hrefs
        for link in article_links:
            href = link.get('href')
                    
            # merge article's unique URL with base URL and append to the empty array
            data_links.append(base_URL+href)
        
        #print('end')
        return data_links
    else:
        return None







def tv3_text_cleaner_v2(html_text):
    #html_text = html_text.replace(".&amp;nbsp;", ".\n")
    if not html_text:
        return
    #the text will be html.unescaped at the end again
    html_text= html.unescape(html.unescape(html_text))
    html_text = html_text.replace("&nbsp;", " ")
    html_text = html_text.replace("\u00a0", " ")
    #for i in range(6):
    #    html_text= html_text.replace("\n\n", "\n")
    html_text_stripped= html_text.split("\n")
    clean_text1 = ""
    j=0
    for line in html_text_stripped:
        j+=1
        #print(j, line)
        # remove empty lines
        if not line:
            continue
        if len(line) < 2 or line.isspace():
            continue
        # superbad strings -> if string in paragraph, paragraph gets removed
        bad_strings = ["!function()", "twitter.", "&#", "@", "&&", "¿", "¡", "#"]
        flag = 0
        for s in bad_strings:
            if s in line:
                flag = 1
                break
        if flag == 1:
            continue
        # If paragraph ends in these characters, i remove the whole paragraph
        bad_characters = ['"', "“", "”", ")"]
        flag = 0
        for character in bad_characters:
            for i in range(4):
                if len(line) < i:
                    break
                if line[-i] == character:
                    # print(line, "removed")
                    flag = 1
                    break
        if flag == 1:
            # remove end of the line
            continue
        # remove enumerations?
        if line[0] in ["-"]:
            # print("remove", line)
            continue
        #remove emojis
        if emoji.emoji_count(line)>0:
            #print("\temoji found :)", emoji.emoji_list(line))
            continue

        # bad but not critical
        # if paragraph ends in a "bad way", remove until the last sentence ". "
        flag=0
        bad_chars = [":", "!", "?"]
        if line[-1].isalnum() or line.strip()[-1].isalnum():
            flag =1
        if line[-1] in bad_chars or line[-2] in bad_chars:
            flag=1
        if flag == 1:
            split_line= line.split(". ")
            if len(split_line) <=1:
                continue
            else:
                line= ". ".join(split_line[:-1]) + ". "

        if not clean_text1:
            clean_text1 = line
            continue
        #print(j, line)
        clean_text1 = clean_text1 + "\n" + line

    # PARAGRAPHS ARE PRESERVED
    # clean_text1 = clean_text1.replace("\n", " ")
    cleanest= ""
    # we re sadly forced to remove : from all sentences bc spacy cant handle them
    for sent in clean_text1.split(". "):
        if ":" in sent:
            continue
        else:
            if not cleanest:
                cleanest = sent
            else:
                cleanest = cleanest + ". " + sent

    return cleanest


            
#returns list of news w infos etc
def tv3_pipeline(tema, desired_articles, pages_to_check, last_page=100):
 
    # get the news category
    
    #The website to check the news from(hell to paginate):
    base_URL = 'https://www.3cat.cat'
    #category_URL = f'{base_URL}/324/incendis/tema/incendis/'
    
    #this is the easy to paginate url to get the news from: 
    #cool_url = "https://www.3cat.cat/Comu/standalone/324_item_tema/contenidor/contenidorNoticiesStandAlone/114/incendis/"
    cool_url_base= "https://www.3cat.cat/Comu/standalone/324_item_tema/contenidor/contenidorNoticiesStandAlone/"
    
    #getting links
    data_list=[]
    data_links=[]
    data_links_all=[]
    url_tema= "/"+tema+"/"

    for i in range(pages_to_check):
        links=links_getter(base_URL, cool_url_base + str(last_page - i) + url_tema)
        if links:
            data_links= data_links + links
        else:
            print("Err no links for topic", tema)
            return 0
    #check that the link hasnt been already collected under another tag
    print("data_links collected", len(data_links), tema)
    data_links= [link for link in data_links if link not in data_links_all]
    data_links_all = data_links_all + data_links
    print("data_links without repetition", len(data_links))
    #print("Data linkks for topic", tema)
    print(data_links)
    # execute the scraping function for each link
    for i, article_url in enumerate(data_links):

        scraped_article = article_scraper(article_url)
        if scraped_article:
            print(f"adding new nr. {i}: {scraped_article['title']}")
            #print(scraped_article.keys())
            if scraped_article["published_date"] > "2022-11-29":
                print("Date of ChatGPT-3-publishment erreicht at article", i , scraped_article["published_date"])
                break
            #skip article if its cleant version is too short
            # it is necessary to do here two step cleaning?
            # cleaned_article= clean_text_conllu(tv3_text_cleaner_v2(scraped_article["text"]))
            cleaned_article = tv3_r2c(gen_r2c(scraped_article["text"]))
            if cleaned_article:
                if len(cleaned_article.split(".")) <= 5:
                    print(f"err corpus text {i} is too short, will be skipped")
                    continue
            if scraped_article['title'].endswith(" - 3CatInfo"):
                scraped_article['title'] = scraped_article['title'][:-len(" - 3CatInfo")]
            else:
                print(f"cleaning article {i} for the corpus made it empty")
                continue
            scraped_article["url"] = article_url
            data_list.append(scraped_article)
            if len(data_list) >= desired_articles:
                print(f"nr of articles about {tema} reached", desired_articles)
                break
        else:
            print("link skipped:", i, article_url)
            continue
    
    # adding batch id with timestamp, cleaning the content
    now = time.time()
    date= strftime('%Y-%m-%d %H:%M:%S', localtime(now))
    l= len(data_list)
    for number, data_set in enumerate(data_list):
        data_set["batch_id"]= f"{date}_{tema}_{l}"
        data_set["custom_id"]= data_set["batch_id"]+"_tv3_"+f"{str(number).zfill(3)}"
        # corpus: full text, cleant
        data_set["corpus"] = tv3_r2c(gen_r2c(data_set["text"]))
        # 2-step cleaning
        # QC-volltext: dataset, only declarative sentences, etc
        data_set["QC_volltext"]=corpus_to_data(data_set["corpus"])

        data_set["QC_text"]=  ".".join(data_set["QC_volltext"].split(".")[3:])
    # purge out news whose clean version is under 100 words
    #data_list = [data_set for data_set in data_list if len(data_set["QC_text"].split(" ")) > 100]
    return data_list


# def tfg
# llista temes is a dictionary of the kind {"meteorologia":325}, this is, topic + starting page
# desired articles and pages to check are positive int, pages to check is a multiple of 10 and bigger than 10*desired articles
# codi is a string
def tv3_scraper(codi, llista_temes, desired_articles, pages_to_check):
    if not isinstance(llista_temes, dict):
        raise TypeError("llista_temes must be a dictionary")
    if not isinstance(desired_articles, int) or desired_articles <= 0:
        raise TypeError("desired_articles must be a positive integer")
    if not isinstance(pages_to_check, int) or pages_to_check <= 0:
        raise TypeError("pages_to_check must be a positive integer")
    codi = str(codi)

    t0 = time.time()
    start_date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    # ask for the tv3 data, print the tv3 data
    print("Starting at ", start_date)
    for tema, l_page in llista_temes.items():
        scraped_data = tv3_pipeline(tema, desired_articles, pages_to_check, last_page = l_page)
        corpusfile = f"{codi}tv3_corpus_{len(scraped_data)}_{tema}.json"
        corpuspath = "data/" + corpusfile
        # corpus_list.append(corpusfile)
        # print the tv3 corpus file
        with open(corpuspath, "w") as f:
            print("Printing to", corpuspath)
            json.dump(scraped_data, f)
    print("Finished in ", time.time() - t0)
    return 0
