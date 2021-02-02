#import certifi
# -*- coding: utf-8 -*-

# Scrapy settings for proto_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html



BOT_NAME = 'proto_spider'
FEED_EXPORT_ENCODING = 'utf-8'

SPIDER_MODULES = ['proto_spider.spiders']
NEWSPIDER_MODULE = 'proto_spider.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 5
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
 #  'proto_spider.middlewares.ProtoSpiderDownloaderMiddleware': 543,
 #   'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810

 # }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'proto_spider.middlewares.ProtoSpiderSpiderMiddleware': 543,
#}


# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# ELASTICSEARCH_INDEX = 'furniture'

ITEM_PIPELINES = {
    #'proto_spider.duplicatespipeline.DuplicatesPipeline':100,
    'proto_spider.pipelines.ProtoSpiderPipeline': 300,
    'scrapyelasticsearch.scrapyelasticsearch.ElasticSearchPipeline': 500
}

ELASTICSEARCH_SERVER = 'localhost'
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_TYPE = '_doc'
ELASTICSEARCH_MAPPING = '''{
"settings":{
"analysis" : {
    "analyzer":{
      "my_analyzer":{
        "tokenizer":"standard",
        "filter":["standard","lowercase","porter_stem"]
      }
    }
  }
},
"_doc": {
"properties": {
  "certifications": {
    "properties": {
      "certification": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "title": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "url": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      }
    }
  },
  "description": {"type": "text", "analyzer":"my_analyzer"},
  "image": {"type": "text"},
  "lowestprice": {"type": "float"},
  "price": {"type": "float"},
  "productname": {"type": "text", "analyzer":"my_analyzer"},
  "producturl": {"type": "text"},
  "sitename": {
    "type": "text",
    "analyzer":"my_analyzer",
    "fields": {
      "raw": {
        "type": "keyword"
      }
    }
  }
}
}

}'''

#ELASTICSEARCH_INDEX_DATE_FORMAT = '%Y-%m'
#ELASTICSEARCH_UNIQ_KEY = 'url'  # Custom unique key
# can also accept a list of fields if need a composite key
#ELASTICSEARCH_UNIQ_KEY = ['url', 'id']

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
