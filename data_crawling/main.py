from typing import Any, Dict

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from data_crawling import lib
from data_crawling.crawlers import GithubCrawler, LinkedInCrawler
from data_crawling.db.documents import UserDocument
from data_crawling.dispatcher import CrawlerDispatcher

logger = Logger(service="nnaemeka/crawler")
_dispatcher = CrawlerDispatcher()
_dispatcher.register("linkedin", LinkedInCrawler)
_dispatcher.register("github", GithubCrawler)


def handler(event, context: LambdaContext) -> Dict[str, Any]:
    first_name, last_name = lib.user_to_names(event.get("user"))

    user = UserDocument.get_or_create(first_name=first_name, last_name=last_name)

    link = event.get("link")
    crawler = _dispatcher.get_crawler(link)

    try:
        crawler.extract(link=link, user=user)

        return {"statusCode": 200, "body": "Link processed successfully"}
    except Exception as e:
        return {"statusCode": 500, "body": f"An error occurred: {str(e)}"}


if __name__ == "__main__":
    event = {"user": "Nnaemeka Ohakim", "link": "https://www.linkedin.com/in/nnaemeka-ohakim/"}

    handler(event, None)
