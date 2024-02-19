# Instagram-Scraper
This project is made for web and Instagram scraping using [BeautifulSoup](https://github.com/wention/BeautifulSoup4) and [Instaloader](https://github.com/instaloader/instaloader).

[DISCLAIMER: This project is intended for educational purposes only.]

## About
Instagram is a gold mine of data for many sectors like fashion, furniture, restaurants and many more. But Instagram puts quite an effort to prevent web scrapers and crawlers from seeking it's data. 

During this project, we explored scraping Instagram which took a long time to get right.



## Process

### 1. Scraping Profiles
To start off, we needed a list of profiles to scrape to. So, we found a [website](https://starngage.com/plus/en-us/) that contained list of influential profiles on Instagram with various attributes using BeautifulSoup library.


![ScrapingProfiles](media/profiles_scraped.png?raw=true)



### 2. Scraping Instagram
Once the list was ready, we used Instaloader to access the posts in each profile. Each post returns a json containing the post's images/videos along with metadata like comments, time signature, etc.

![ScrapingInsta](media/instagram_scraping.png?raw=true)


### 3. Logging
As we started scraping a larger amount of profiles, a need to track the scraping process seemed necessary. We log the scraping status onto Google Sheets using API calls. 

![logging](media/logging.png?raw=true)

  
## Acknowledgment
This project was made in collaboration with [Nazim Girach](https://github.com/ulfimlg)
