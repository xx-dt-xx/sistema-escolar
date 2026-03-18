from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Course, CourseGroup, Category
from core.models import MediaAsset


def faq_view(request):
    faq_image = MediaAsset.objects.filter(tag='preguntas', is_active=True).first()
    return render(request, 'faq.html', {'faq_image': faq_image})


def nosotros_view(request):
    valores_images = list(MediaAsset.objects.filter(tag='valores', is_active=True))
    equipo_images = list(MediaAsset.objects.filter(tag='equipo', is_active=True))
    return render(request, 'nosotros.html', {
        'valores_images': valores_images,
        'equipo_images': equipo_images,
    })


def course_list_view(request):
    courses = Course.objects.filter(is_active=True).select_related('category').order_by('category__name', 'name')

    # Filtro por búsqueda
    query = request.GET.get('q', '')
    if query:
        courses = courses.filter(
            Q(name__icontains=query) |
            Q(short_description__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Filtro por categoría
    category_id = request.GET.get('category', '')
    if category_id:
        courses = courses.filter(category__id=category_id)

    # Filtro por turno
    shift = request.GET.get('shift', '')
    if shift:
        courses = courses.filter(groups__shift=shift, groups__status=CourseGroup.OPEN).distinct()

    categories = Category.objects.all()

    context = {
        'courses': courses,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'selected_shift': shift,
        'shift_choices': CourseGroup.SHIFT_CHOICES,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail_view(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    groups = course.groups.filter(
        status__in=[CourseGroup.OPEN, CourseGroup.IN_PROGRESS]
    ).prefetch_related('schedules', 'coursegroupinstructor_set__instructor')
    syllabus = course.syllabus.all()

    gallery_images = course.gallery_images.all()

    context = {
        'course': course,
        'groups': groups,
        'syllabus': syllabus,
        'gallery_images': gallery_images,
    }
    return render(request, 'courses/course_detail.html', context)


def group_detail_view(request, slug, group_id):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    group = get_object_or_404(CourseGroup, id=group_id, course=course)
    schedules = group.schedules.all()
    instructors = group.coursegroupinstructor_set.select_related('instructor__user').all()

    context = {
        'course': course,
        'group': group,
        'schedules': schedules,
        'instructors': instructors,
    }
    return render(request, 'courses/group_detail.html', context)


def home_view(request):
    # Toma 3 cursos activos que tengan al menos un grupo abierto
    featured_courses = Course.objects.filter(
        is_active=True,
        is_featured=True,
        groups__status=CourseGroup.OPEN
    ).distinct().select_related('category')[:3]

    hero_banners = MediaAsset.objects.filter(tag='hero', is_active=True)

    return render(request, 'home.html', {
        'featured_courses': featured_courses,
        'hero_banners': hero_banners,
    })
