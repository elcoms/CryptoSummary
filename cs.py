import CMCscraper as scraper
import fire

def scrape(coin="bitcoin", a=False, path=scraper.currentFilePath / "data"):
    if (a):
        scraper.ScrapeAll(path)
    else:
        data = scraper.ScrapePage(scraper.GetCoinPageSource(coin))
        scraper.WriteToFile(data, path, coin)

# class Commands(object):
#     def __init__(self):
#         self.scrape = scrape_cmd
        
if __name__ == "__main__":
    fire.Fire()