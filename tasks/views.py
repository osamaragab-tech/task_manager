from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime, timedelta
from .models import Task
from .forms import TaskForm
import json


def task_list(request):
    """عرض المهام مع تحديد حالتها الزمنية"""
    tasks = Task.objects.all().order_by('due_date')
    now = timezone.now()  # التاريخ والوقت معًا

    for task in tasks:
        if task.due_date:
            # ✅ توحيد النوعين (date أو datetime)
            if isinstance(task.due_date, datetime):
                due_datetime = task.due_date
            else:
                due_datetime = datetime.combine(
                    task.due_date,
                    datetime.min.time(),
                    tzinfo=timezone.get_current_timezone()
                )

            # فرق الأيام بين الموعدين
            diff_days = (due_datetime.date() - now.date()).days

            if diff_days < 0:
                task.status_label = "overdue"     # متأخرة
                task.color = "danger"              # أحمر
            elif diff_days == 0:
                task.status_label = "today"        # اليوم
                task.color = "warning"             # أصفر
            else:
                task.status_label = "upcoming"     # قادمة
                task.color = "success"             # أخضر
        else:
            task.status_label = "no_date"
            task.color = "secondary"

    # تجهيز البيانات لجافاسكريبت (للتنبيهات)
    tasks_json = json.dumps(
        [
            {
                "title": task.title,
                "due_date": task.due_date.isoformat() if task.due_date else None,
            }
            for task in tasks
        ],
        cls=DjangoJSONEncoder,
    )

    context = {
        "tasks": tasks,
        "tasks_json": tasks_json,
        "now": now,
    }
    return render(request, "tasks/task_list.html", context)


def task_add(request):
    """إضافة مهمة جديدة"""
    form = TaskForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("task_list")

    return render(request, "tasks/task_form.html", {
        "form": form,
        "title": "Add Task"
    })


def task_edit(request, task_id):
    """تعديل مهمة"""
    task = get_object_or_404(Task, id=task_id)
    form = TaskForm(request.POST or None, instance=task)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("task_list")

    return render(request, "tasks/task_form.html", {
        "form": form,
        "title": "Edit Task"
    })


def task_delete(request, task_id):
    """حذف مهمة مع تأكيد"""
    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        task.delete()
        return redirect("task_list")

    return render(request, "tasks/task_delete.html", {"task": task})
