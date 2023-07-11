import requests 
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from langdetect import detect
from negspacy.negation import Negex
from negspacy.termsets import termset
from spacy.matcher import DependencyMatcher
from textblob import TextBlob
from lexicalrichness import LexicalRichness
from nltk.stem import WordNetLemmatizer

value = "https://www.metacritic.com/game/playstation-4/call-of-duty-modern-warfare/critic-reviews"
url = "https://www.metacritic.com/game/playstation-4/call-of-duty-modern-warfare/critic-reviews"
url = url[32:]
div = url.find('/')
platform = url[:div]
url = url[div+1:]
div = url.find('/')
game = url[:div]
url = url[div+1:]
div = url.find('/')
reviewer = url[:]

try:
	reviews = pd.read_csv(game+'_'+reviewer+'_'+platform+'.csv', lineterminator='\n')
	reviews = reviews.drop(columns=['Unnamed: 0'])
	#reviews.to_csv('dashboard.csv')
	#print('dashboard.csv updated ('+game+'_'+reviewer+'_'+platform+'.csv)')
	print(game+'_'+reviewer+'_'+platform+'.csv')

	aspects = pd.read_csv('aspects-'+game+'_'+reviewer+'_'+platform+'.csv', lineterminator='\n')
	aspects = aspects.drop(columns=['Unnamed: 0'])
	#aspects.to_csv('aspects-dashboard.csv')
	#print('aspects-dashboard.csv updated (aspects-'+game+'_'+reviewer+'_'+platform+'.csv)')
	print('aspects-'+game+'_'+reviewer+'_'+platform+'.csv')

except:
	print('web scraping')
	review_dict = {'name':[], 'date':[], 'rating':[], 'review':[]}
	page = 0

	url = value + '?page='+str(page)
	user_agent = {'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"}
	response  = requests.get(url, headers = user_agent)
	soup = BeautifulSoup(response.text, 'html.parser')

	while((reviewer == 'user-reviews' and (nextPage(soup) or page == 0)) or (reviewer == 'critic-reviews' and page == 0)):
		print("page " + str(page))
		for review in soup.find_all('div', class_='review_content'):
			#if review.find('div', class_='name') == None:
			if review == None:
				break

			if(reviewer == 'user-reviews'):
				if review.find('span', class_='blurb blurb_expanded'):
					rv = review.find('span', class_='blurb blurb_expanded').text
				else:
					if(review.find('div', class_='review_body').find('span') is None):
						rv = ''
					else:
						rv = review.find('div', class_='review_body').find('span').text
			else:
				if(review.find('div', class_='review_body') is None):
					rv = ''
				else:
					rv = review.find('div', class_='review_body').text

			try:
				language = detect(rv)
			except:
				continue

			if(language == 'en'):
				try:
					if(reviewer == 'user-reviews'):
						name = review.find('div', class_='name').find('a').text
						rating = int(review.find('div', class_='review_grade').find_all('div')[0].text)
					else:
						name = review.find('div', class_='source').find('a').text
						rating = int(review.find('div', class_='review_grade').find_all('div')[0].text)
						rating = round(rating/10)

					date = review.find('div', class_='date').text
				except:
					continue

				lex = LexicalRichness(rv)
				words = lex.words
				mattr = lex.mattr(window_size=max(1,int(lex.words/2)))
                
				if(words >= 50 and mattr >= 0.75):
					review_dict['name'].append(name)
					review_dict['date'].append(date)
					review_dict['rating'].append(rating)
					review_dict['review'].append(rv)

		page += 1
		url = value+'?page='+str(page)
		user_agent = {'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"}
		response  = requests.get(url, headers = user_agent)
		soup = BeautifulSoup(response.text, 'html.parser')

	print('saving ' + game+'_'+reviewer+'_'+platform+'.csv')
	reviews = pd.DataFrame(review_dict)
	reviews.to_csv(game+'_'+reviewer+'_'+platform+'.csv')
	#reviews.to_csv('dashboard.csv')