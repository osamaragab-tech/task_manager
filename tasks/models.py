from django.db import models
from django.utils import timezone


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('done', 'Done'),
    ]

    title = models.CharField(max_length=200, verbose_name="Title")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    due_date = models.DateTimeField(blank=True, null=True, verbose_name="Due Date & Time")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )

    def __str__(self):
        """عرض اسم المهمة مع حالتها"""
        return f"{self.title} ({self.get_status_display()})"

    @property
    def is_overdue(self):
        """إرجاع True لو المهمة تأخرت"""
        return self.due_date and self.due_date < timezone.now()

    @property
    def is_due_today(self):
        """إرجاع True لو تاريخ الاستحقاق اليوم"""
        if not self.due_date:
            return False
        now = timezone.localtime(timezone.now()).date()
        return self.due_date.date() == now

    class Meta:
        ordering = ['due_date']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
