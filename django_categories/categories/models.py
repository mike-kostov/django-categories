from django.db import models

# Create your models here.
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Category(TimestampedModel):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    image = models.TextField(blank=False, null=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)
    depth = models.PositiveIntegerField(default=0)

    @property
    def similar(self):
        similar_categories = CategorySimilarity.objects.filter(
            models.Q(category_a=self) | models.Q(category_b=self)
        )

        similar_ids = [
            similarity.category_a.id if similarity.category_a != self else similarity.category_b.id
            for similarity in similar_categories
        ]

        return Category.objects.filter(id__in=similar_ids)

    def mark_similar_to(self, other_category):
        if self.id == other_category.id:
            raise ValueError("Cannot mark a category as similar to itself")

        pk_a = self.id
        pk_b = other_category.id
        cat_a = self
        cat_b = other_category

        if pk_a > pk_b:
            pk_a, pk_b = pk_b, pk_a
            cat_a, cat_b = cat_b, cat_a

        similarity, created = CategorySimilarity.objects.get_or_create(
            category_a=cat_a,
            category_b=cat_b
        )

        return similarity, created

    def unmark_similar_to(self, other_category):
        if self.id == other_category.id:
            raise ValueError("Cannot unmark a category as similar to itself")

        pk_a = self.id
        pk_b = other_category.id

        if pk_a > pk_b:
            pk_a, pk_b = pk_b, pk_a

        deleted_count, _ = CategorySimilarity.objects.filter(
            category_a=pk_a,
            category_b=pk_b
        ).delete()

        return deleted_count > 0

    def save(self, *args, **kwargs):
        is_new = self.id is None
        old_parent_id = None

        if not is_new:
            try:
                old_parent_id = Category.objects.values_list('parent_id', flat=True).get(id=self.id)
            except Category.DoesNotExist:
                pass

        if self.parent:
            self.depth = self.parent.depth + 1
        elif not self.parent:
            self.depth = 0

        super().save(*args, **kwargs)

        parent_changed = (is_new and self.parent_id is not None) or (self.parent_id != old_parent_id)

        if parent_changed and self.id is not None:
            self.update_children_depth()

    def update_children_depth(self):
        def recursive_update(parent_id, new_depth):
            children = Category.objects.filter(parent_id=parent_id)
            if children.exists():
                children.update(depth=new_depth)

                for child in children:
                    recursive_update(child.id, new_depth + 1)

        recursive_update(self.id, self.depth + 1)

class CategorySimilarity(TimestampedModel):
    category_a = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='similarities_a')
    category_b = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='similarities_b')

    def save(self, *args, **kwargs):
        pk_a = self.category_a.id
        pk_b = self.category_b.id

        if pk_a is not None and pk_b is not None and pk_a > pk_b:
            self.category_a, self.category_b = self.category_b, self.category_a

        super().save(*args, **kwargs)

    class Meta:
        unique_together = (('category_a', 'category_b'),)

        indexes = [
            models.Index(fields=['category_a', 'category_b']),
        ]
