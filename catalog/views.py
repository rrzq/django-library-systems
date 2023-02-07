from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Author, BookInstance, Genre, Language
from django.views.generic import View, CreateView, DetailView, ListView, TemplateView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.models import User

# Create your views here.


def index(request):

    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available
    }

    return render(request, 'catalog/index.html', context=context)


class BookCreateView(PermissionRequiredMixin, CreateView):  # model_form.html
    permission_required = 'login'
    model = Book
    fields = '__all__'


class BookDetailView(DetailView):  # model_detail.html
    model = Book


@login_required
def my_view(request):
    return render(request, 'catalog/my_view.html')


class SignUpCreateView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'catalog/signup.html'


class CheckoutBookListView(LoginRequiredMixin, ListView):
    # list all book instance filter : based on current user
    model = BookInstance
    template_name = 'catalog/profile.html'
    paginate_by = 5

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user)


class UserListView(PermissionRequiredMixin, ListView):
    permission_required = 'login'
    # model_list.html
    model = User
    context_object_name = 'user_list'


class BookListView(ListView):
    model = Book, Genre
    queryset = Book.objects.order_by('title')
    paginate_by = 10
    context_object_name = 'book_list'


class BorrowBookView(LoginRequiredMixin, View):
    template_name = 'catalog/book_borrow.html'
    model = BookInstance

    def get(self, request, pk):
        book_instance = BookInstance.objects.get(pk=pk)
        book_instance.borrower = request.user
        book_instance.status = 'o'
        book_instance.save()
        return redirect('catalog:profile')

    def post(self, request, *args, **kwargs):
        book_instance = BookInstance.objects.get(pk=pk)
        book_instance.borrower = request.user
        book_instance.status = 'o'
        book_instance.save()
        return HttpResponseRedirect(reverse("catalog:book_detail", kwargs={"pk": self.book_instance.pk}))


class ReturnBookView(View):
    template_name = 'catalog/book_return.html'
    model = BookInstance

    def get(self, request, pk):
        book_instance = BookInstance.objects.get(pk=pk)
        book_instance.borrower = None
        book_instance.status = 'a'
        book_instance.save()
        return redirect('catalog:profile')


class SearchView(ListView):
    model = Book
    template_name = 'catalog/book_search.html'
    context_object_name = 'all_search_results'

    def get_queryset(self):
        result = super(SearchView, self).get_queryset()
        query = self.request.GET.get('search')
        if query:
            postresult = Book.objects.filter(title__contains=query)
            result = postresult
        else:
            result = None
        return result
