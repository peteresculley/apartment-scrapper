import scrapy
import io
from re import sub


class QuotesSpider(scrapy.Spider):
  name = "nekretnine"

  def start_requests(self):
    urls = [
      'https://www.nekretnine.rs/stambeni-objekti/kuce/izdavanje-prodaja/prodaja/lista/po-stranici/20/?order=1',
    ]
    headers = {
      ":authority": "www.nekretnine.rs",
      ":method": "GET",
      ":path": "/stambeni-objekti/kuce/izdavanje-prodaja/prodaja/lista/po-stranici/20/?order=1",
      ":scheme": "https",
      "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
      "accept-encoding": "gzip, deflate, br",
      "accept-language": "en-US,en;q=0.9,es;q=0.8",
      "sec-fetch-dest": "document",
      "sec-fetch-mode": "navigate",
      "sec-fetch-site": "none",
      "upgrade-insecure-requests": "1",
      "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"
    }
    for url in urls:
      yield scrapy.Request(url=url, headers=headers, callback=self.parse)

  def parse(self, response):
    offers = response.css('.row.offer')
    results = []
    for offer in offers:
      location = offer.css('.offer-location::text').get().strip()
      href = 'https://www.nekretnine.rs' + offer.css('.offer-title a::attr(href)').get()
      price = offer.css('.offer-price:not(.offer-price--invert) span::text').get().strip()
      price_per_area = offer.css('.offer-price:not(.offer-price--invert) small::text').get().strip()
      area = offer.css('.offer-price.offer-price--invert span::text').get().strip()

      price = sub("[^0-9.]", "", price.replace(',', '.'))
      area = sub("[^0-9.]", "", area.replace(',', '.'))
      price_per_area = sub("[^0-9.]", "", price_per_area.replace(',', '.'))

      d = ';'

      location_split = location.replace(d, ',').split(',')
      city = ''
      town = ''
      country = ''
      if len(location_split) == 1:
        country = location_split[0].strip()

      if len(location_split) == 2:
        city = location_split[0].strip()
        country = location_split[1].strip()

      if len(location_split) == 3:
        city = location_split[1].strip()
        town = location_split[0].strip()
        country = location_split[2].strip()

      if country == 'Srbija':
        result = town + d + city + d + href + d + price + d + area + d + price_per_area
        results.append(result)

    heading = 'Town;City;Link;Price (EUR);Area (m^2);Price/Area (EUR/m^2)'
    output = heading + '\n' + '\n'.join(results)
    filename = 'selected.csv'
    with io.open(filename, 'w', encoding='utf8') as f:
      f.write(output)
    self.log('Saved file %s' % filename)
