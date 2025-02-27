from datetime import datetime


class Job:
    def __init__(self, title, company, location, link, source):
        self.title = title
        self.company = company
        self.location = location
        self.link = link
        self.date_scraped = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.source = source


class Jobs:
    def __init__(self):
        self.postings = []

    def add_posting(self, job: Job) -> None:
        self.postings.append(job)

    def get_postings(self) -> list:
        return self.postings
