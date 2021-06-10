import json

from django.core.management import BaseCommand
from django.db.transaction import atomic
from progress.bar import Bar

from book.models import Book, Genre


class Command(BaseCommand):
    help = 'import books data'

    def add_arguments(self, parser):
        pass

    @atomic
    def handle(self, *args, **options):
        json_data = open('./data/books.json')
        book_data = json.load(json_data)

        bar = Bar('Import Books', max=len(book_data))
        for item_data in book_data:
            try:

                new_item = {
                    'title': item_data.get('title'),
                    'author': item_data.get('author'),
                    'genre': Genre.objects.get_or_create(
                        title=item_data.get('genre'),
                        defaults={"title": item_data.get('genre')}
                    )[0],
                }
                book, _ = Book.objects.get_or_create(
                    title=item_data.get('title'),
                    defaults=new_item
                )
                item_data['pk'] = book.pk
                item_data['model'] = 'book.book'
                bar.next()
            except Exception as e:
                print(e)
                bar.next()
        bar.finish()
        bar = Bar('Add prerequisites', max=len(book_data))
        for item_data in book_data:
            try:
                book = Book.get_by_pk(item_data['pk'])
                for prerequisite in item_data.get('prerequisites'):
                    pr = Book.get_by_title(prerequisite)
                    book.prerequisite.add(pr)
                bar.next()
            except Exception as e:
                print(e)
                bar.next()
        bar.finish()
