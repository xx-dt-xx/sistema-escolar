from django.contrib import admin
from .models import Category, Instructor, Course, CourseImage, CourseSyllabus, CourseGroup, CourseGroupInstructor, Schedule


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('user', 'speciality', 'years_of_experience')
    search_fields = ('user__first_name', 'user__last_name', 'speciality')


class CourseSyllabusInline(admin.TabularInline):
    model = CourseSyllabus
    extra = 1
    ordering = ['order']


class CourseImageInline(admin.TabularInline):
    model = CourseImage
    extra = 1
    max_num = 2
    ordering = ['order']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'monthly_price', 'duration_weeks', 'is_active', 'is_featured')
    list_editable = ('is_active', 'is_featured')
    list_filter = ('category', 'is_active', 'language')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CourseSyllabusInline, CourseImageInline]


class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 1


class CourseGroupInstructorInline(admin.TabularInline):
    model = CourseGroupInstructor
    extra = 1


@admin.register(CourseGroup)
class CourseGroupAdmin(admin.ModelAdmin):
    list_display = ('course', 'name', 'shift', 'status', 'start_date', 'end_date', 'max_capacity', 'available_spots')
    list_filter = ('shift', 'status', 'course')
    search_fields = ('course__name', 'name')
    inlines = [CourseGroupInstructorInline, ScheduleInline]
