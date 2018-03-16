from django.shortcuts import render
from .models import Book, User
from cadmin.utils.pager import Pagination
# Create your views here.


def index(request):
    all_books = Book.objects.all()

    page_num = request.GET.get('page', 1)
    total_count = all_books.count()
    base_url = request.path_info
    params = request.GET

    page = Pagination(page_num, total_count, base_url, params, items_per_page=1, max_pages_count=11)
    book_list = all_books[page.start:page.end]
    page_html = page.page_html()

    return render(request, 'cadmin/show_view.html', {'page_html':page_html})
