from entities.entity import Entity
import json


class BBCArticle(Entity):

    def __init__(self, url: str):
        super(BBCArticle, self).__init__(url)
        self.date = self.get_date()

    def get_body(self) -> list:
        body = self.soup.find_all(attrs={'data-component': 'text-block'})
        return [p.text for p in body]

    def get_title(self) -> str:
        return self.soup.find(id="main-heading").text

    def get_date(self) -> str:
        return self.soup.find(attrs={'data-testid': 'timestamp'})['datetime']

    def save_json(self, directory, name=None):
        item = {
            "title": self.title,
            "date": self.date,
            "body": " ".join(self.body)
        }

        if not name:
            name = self.title

        name = "".join([x if x.isalnum() else "_" for x in name])

        with open(directory + "/" + name + ".json", 'w', encoding='utf8') as json_file:
            json.dump(item, json_file, ensure_ascii=False)
