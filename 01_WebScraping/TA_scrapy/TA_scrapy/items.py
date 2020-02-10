# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import pandas as pd

class ReviewRestoItem(scrapy.Item):        
    Name = scrapy.Field()
    Address = scrapy.Field()
    Neighborhood = scrapy.Field()
    Price = scrapy.Field()
    Type = scrapy.Field()
    Rating = scrapy.Field()
    Review = scrapy.Field()
    Date = scrapy.Field()

pass