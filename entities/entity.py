from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup as bs


class Entity(ABC):
    def __init__(self, url: str):
        article = requests.get(url)
        self.soup = bs(article.content, "html.parser")
        self.body = self.get_body()
        self.title = self.get_title()

    @abstractmethod
    def get_body(self) -> list:
        return

    @abstractmethod
    def get_title(self) -> str:
        return
