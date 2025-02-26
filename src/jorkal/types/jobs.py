from datetime import datetime


class Job:
    def __init__(self, title, company, location, url):
        self.title = title
        self.company = company
        self.location = location
        self.link = url
        self.date_scraped = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Jobs:
    def __init__(self):
        self.postings = []

    def add_posting(self, job: Job) -> None:
        self.postings.append(job)

    def get_postings(self) -> list:
        return self.postings
