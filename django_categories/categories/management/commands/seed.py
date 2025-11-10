from django.core.management.base import BaseCommand
import random
from categories.models import Category, CategorySimilarity

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

    def clear_categories(self):
        Category.objects.all().delete()

    def create_categories(self, num_categories=2000, num_roots=100):
        # examples from task desc
        cat_a = Category.objects.create(
            name='A',
            description='Desc A',
            image='A.png',
        )
        cat_b = Category.objects.create(
            name='B',
            description='Desc B',
            image='B.png',
        )
        cat_c = Category.objects.create(
            name='C',
            description='Desc C',
            image='C.png',
        )
        cat_d = Category.objects.create(
            name='D',
            description='Desc D',
            image='D.png',
        )
        cat_e = Category.objects.create(
            name='E',
            description='Desc E',
            image='E.png',
        )
        cat_f = Category.objects.create(
            name='F',
            description='Desc F',
            image='F.png',
        )

        cat_a.mark_similar_to(cat_b)
        cat_a.mark_similar_to(cat_d)

        cat_b.mark_similar_to(cat_c)
        cat_b.mark_similar_to(cat_d)

        cat_e.mark_similar_to(cat_f)

        root_categories = []
        for i in range(1, num_roots + 1):
            root_categories.append(Category(
                name=f'Seeded Category {i}',
                description=f'Description for Seeded Category {i}',
                image=f'/image/path/to/category/{i}.png',
                parent=None,
                depth=0,
            ))
        Category.objects.bulk_create(root_categories)

        all_categories = list(Category.objects.filter(id__gt=6))
        for i in range(num_roots + 1, num_categories + 1):
            parent = None
            if i > num_roots:
                parent = random.choice(all_categories)

            new_cat = Category.objects.create(
                name=f'Seeded Category {i}',
                description=f'Description for Seeded Category {i}',
                image=f'/image/path/to/category/{i}.png',
                parent=parent,
            )
            all_categories.append(new_cat)

        all_categories = root_categories + all_categories
        self.create_similarities(all_categories)

    def create_similarities(self, all_categories, num_groups=20, total_similarities=200000):
        self.stdout.write('Creating similarities...')
        category_map = {cat.id: cat for cat in all_categories}
        all_ids = sorted(category_map.keys())

        categories_per_group = len(all_ids) // num_groups

        similarity_records = set()
        for _ in range(total_similarities):
            # Choose a random group (island) index
            group_index = random.randrange(num_groups)

            # Determine the ID range for this group
            start_index = group_index * categories_per_group
            # Ensure the last group gets any remainder
            end_index = start_index + categories_per_group
            if group_index == num_groups - 1:
                end_index = len(all_ids)

            # Slice the IDs belonging to this group
            group_ids = all_ids[start_index:end_index]

            if len(group_ids) < 2:
                continue # Skip if the group is too small

            # Choose two distinct categories from WITHIN the selected group
            pk_a, pk_b = random.sample(group_ids, 2)

            # Enforce lower ID first
            if pk_a > pk_b:
                pk_a, pk_b = pk_b, pk_a

            similarity_records.add((pk_a, pk_b))

        unique_similarity_records = [
            CategorySimilarity(category_a_id=a, category_b_id=b)
            for a, b in similarity_records
        ]

        CategorySimilarity.objects.bulk_create(unique_similarity_records, ignore_conflicts=True)
        self.stdout.write(f'Intended similarities: {total_similarities}. Actual unique similarities created: {len(unique_similarity_records)} across {num_groups} islands.')
