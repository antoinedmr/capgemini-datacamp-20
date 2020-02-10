# Logging packages
import sys
import logging
import logzero
from logzero import logger

# Scrapy packages
import scrapy
from TA_scrapy.items import ReviewRestoItem     # you can use it if you want but it is not mandatory
from TA_scrapy.spiders import get_info          # package where you can write your own functions 

class RestoReviewSpider(scrapy.Spider):
    name = "RestoReviewSpider"

    def __init__(self, *args, **kwargs): 
        super(RestoReviewSpider, self).__init__(*args, **kwargs)

        # Set logging level
        logzero.loglevel(logging.WARNING)

        # To track the evolution of scrapping
        self.main_nb = 0
        self.resto_nb = 0
        self.review_nb = 0
        self.resto_price = 0
        self.resto_type = []
        
    def start_requests(self):
        """
        Give the urls to follow to scrapy
        - function automatically called when using "scrapy crawl my_spider"
        """

        # Basic restaurant page on TripAdvisor GreaterLondon
        url = 'https://www.tripadvisor.co.uk/Restaurants-g191259-Greater_London_England.html'
        yield scrapy.Request(url=url, callback=self.parse)
   
    def parse(self, response):
        """
        MAIN PARSING : Start from a classical restaurant page
        - Usually there are 30 restaurants per page
        """

        # Display a message in the console
        logger.warn(' > PARSING NEW MAIN PAGE OF RESTO ({})'.format(self.main_nb))
        self.main_nb += 1

        # Get the list of the 30 restaurants of the page
        xpath = '//div[@class="wQjYiB7z"]//a '
        restaurant_urls = response.xpath(xpath).css('::attr(href)').extract()   # get_info.get_urls_resto_in_main_search_page(response)
        

        # For each url : follow restaurant url to get the reviews
        for restaurant_url in restaurant_urls:
            logger.warn('> New restaurant detected : {}'.format(restaurant_url))
            yield response.follow(url=restaurant_url, callback=self.parse_resto)

        # Get next page information
        next_page, next_page_number = get_info.get_urls_next_list_of_restos(response)
        
        # Follow the page if we decide to
        if get_info.go_to_next_page(next_page, next_page_number, max_page=10):
            yield response.follow(next_page, callback=self.parse)

    def parse_resto(self, response):
        """
        SECOND PARSING : Given a restaurant, get each review url and get to parse it
        - Usually there are 10 comments per page
        """
        logger.warn(' > PARSING NEW RESTO PAGE ({})'.format(self.resto_nb))
        self.resto_nb += 1

        ## Get Restaurant Info
        xpath = '//div[@class="header_links"]/a/text()'
        self.resto_price = response.xpath(xpath).extract()[0]
        self.resto_type = response.xpath(xpath).extract()[1:]

        # Get the list of reviews on the restaurant page
        urls_review = response.xpath('//div[@class="quote"]//a/@href').extract()

        # For each review open the link and parse it into the parse_review method
        for url_review in urls_review:
             yield response.follow(url=url_review, callback=self.parse_review)
        
        next_page, next_page_number = get_info.get_urls_next_list_of_reviews(response)

        if get_info.go_to_next_page(next_page, next_page_number, max_page=10):
            yield response.follow(next_page, callback=self.parse_resto)
        
    def parse_review(self, response):
        """
        FINAL PARSING :
        Open a specific page with review and client opinion
        - Read these data and store them
        - Get all the data you can find and that you believe interesting
        """

        logger.warn(' > PARSING NEW REVIEW PAGE ({})'.format(self.review_nb))
        # Count the number of review scrapped
        self.review_nb += 1

        ## Initialize Storing Object
        review_item = ReviewRestoItem()
        
        ## Restaurant Information
        # Name
        xpath = '//a[@class="HEADING"]/text()'
        review_item['resName'] = response.xpath(xpath).extract_first()
        # Address
        xpath = '//span[@class="street-address"]/text()'
        review_item['resAddress'] = response.xpath(xpath).extract_first()
        # Neighborhood
        xpath = '//span[@class="extended-address"]/text()'
        review_item['resNeighborhood'] = response.xpath(xpath).extract_first()
        # Price Range
        review_item['resPrice'] = self.resto_price
        # Restaurant Type
        review_item['resType'] = self.resto_type
        
        ## Review Information
        # Title
        xpath = '//div[@id="PAGEHEADING"]/text()'
        review_item['reviewTitle'] = response.xpath(xpath).extract_first()
        # Content
        xpath = '//p[@class="partial_entry"]/text()'
        review_item['reviewContent'] = response.xpath(xpath).extract_first()
        # Rating
        xpath = ['//span[@class="ui_bubble_rating bubble_50"]/@alt', 
                '//span[@class="ui_bubble_rating bubble_40"]/@alt',
                '//span[@class="ui_bubble_rating bubble_30"]/@alt',
                '//span[@class="ui_bubble_rating bubble_20"]/@alt',
                '//span[@class="ui_bubble_rating bubble_10"]/@alt']
        for path in xpath:
            rating = response.xpath(path).extract_first()
            if rating:
                review_item['reviewRating'] = rating[0]
        # Date of Visit
        xpath = '//span[@class="ratingDate relativeDate"]/@title'
        review_item['reviewDate'] = response.xpath(xpath).extract_first()
        # Date of Visit
        xpath = '//div[@class="prw_rup prw_reviews_stay_date_hsx"]/text()'
        review_item['visitDate'] = response.xpath(xpath).extract_first()
        
        ## User Information
        # Name
        xpath = '//span[@class="expand_inline scrname"]/text()'
        review_item['userName'] = response.xpath(xpath).extract_first()
        # Location
        xpath = '(//div[@class="member_info"]/div)[1]/div[@class="location"]/span/text()'
        review_item['userLocation'] = response.xpath(xpath).extract_first()
        # Total Contributions
        xpath = '(//div[@class="member_info"]/div)[2]/div/span[@class="badgetext"][1]/text()'
        review_item['userContrib'] = response.xpath(xpath).extract_first()
        # Helpful Contributions
        xpath = '(//div[@class="member_info"]/div)[2]/div/span[@class="badgetext"][2]/text()'
        review_item['userHelpful'] = response.xpath(xpath).extract_first()

        yield review_item

        
