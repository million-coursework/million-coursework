import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re
from bs4 import BeautifulSoup
import requests



class Website(CrawlSpider):
    name = "website"

    rules = (
             Rule(
                  LinkExtractor(),
                  follow=True,
                  callback='parse_start'),
             )
    allowed_domains = ['anu.edu.au']
    #picked arbitrary links
    start_urls = ['http://www.anu.edu.au/']
    
    def parse_start(self, response):

        page = response.text
        soup = BeautifulSoup(page, 'html.parser')
        doc=""
        for para in soup.find_all('p'):
            doc += " "+para.text
        doc = ' '.join(s for s in doc.split() if not s.isdigit())
        regex = re.compile('[^a-zA-Z]')
        doc =regex.sub(' ', doc)
        doc = ''.join(e for e in doc if e.isalnum() or e==' ')

        url = 'https://dialogflow.googleapis.com/v2beta1/projects/anu-tier-1-and-0/agent/knowledgeBases/NTE2MDg0MzY5Nzk4OTg3Nzc2MA/documents'
        payload = """{
                  "name":"",
                  "displayName": \""""+response.url.replace('/','')+"""\",
                  "mimeType": "text/plain",
                  "knowledgeTypes": [
                    "EXTRACTIVE_QA"
                  ],
    
                  "content": \""""+doc+"""\",
                }""" 
        headers = {
                   'Authorization': 'Bearer ya29.c.EloFBgOlkKmChKoQdm3TFkYyEeRH2xm87tZ8auenNSb1LAND2CaGpxMiKbl9o0d0IlAALfNwyHTky0OJZjCJq4ciJcMnF2LJVOMBM7YPG0DVhXxLRU4nSZAmzKI'
                    }
    
        print(requests.post(url, data=payload, headers=headers).text)