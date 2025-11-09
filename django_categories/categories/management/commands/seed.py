from django.core.management.base import BaseCommand
import random
from categories.models import Category

MODE_REFRESH = 'refresh'
MODE_CLEAR = 'clear'

class Command(BaseCommand):
    help = 'Seed the database with categories'

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help='Mode', choices=[MODE_REFRESH, MODE_CLEAR])

    def handle(self, *args, **options):
        mode = options['mode']
        if mode == MODE_REFRESH:
            self.stdout.write('Seeding categories...')
            self.refresh_categories()
        elif mode == MODE_CLEAR:
            self.stdout.write('Clearing categories...')
            self.clear_categories()

        self.stdout.write('Done')

    def refresh_categories(self):
        self.clear_categories()
        self.create_categories()
        # self.create_similarities()

    def clear_categories(self):
        Category.objects.all().delete()

    def create_categories(self):
        # Create 2000 categories
        # first 100 are root, in depth = 0
        all_categories = []

        for i in range(1, 2001):
            parent = None
            if i > 100:
                parent = random.choice(all_categories[:i])

            all_categories.append(Category.objects.create(
                name=f'Seeded Category {i}',
                description=f'Description for Seeded Category {i}',
                image=f'/image/path/to/category/{i}.png',
                parent=parent,
            ))

        self.stdout.write('Creating similarities...')
        self.stdout.write(f'Found {len(all_categories)} categories')
        for i in range(1, 200001):
            category1 = random.choice(all_categories)
            category2 = random.choice(all_categories)

            if category1 == category2:
                category2 = random.choice(all_categories)

            category1.mark_similar_to(category2)

    def create_similarities(self):
        all_categories = Category.objects.all()
