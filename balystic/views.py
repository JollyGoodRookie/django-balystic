from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from .client import Client
from .forms import QAQuestionForm, QAAnswerForm
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from .forms import LoginForm


class CommunityUserList(View):
    """
    Displays a list of the users retrieved from 7dhub
    """
    template_name = 'balystic/user_list.html'
    client = Client()

    def get(self, request):
        context = {'users': self.client.get_users()}
        return render(request, self.template_name, context)


class CommunityUserDetail(View):
    """
    Displays the details for the given user
    """
    templat_name = 'balystic/user_detail.html'
    client = Client()

    def get(self, request, username):
        context = {'user': self.client.get_user(username)}
        return render(request, self.template_name, context)


class CommunityBlogListView(View):
    template_name = "balystic/blog_list.html"

    def get(self, request):
        """
        Display the list of all the blogs posts
        in the community (by page)
        """
        page = request.GET.get('page', 1)
        client = Client()
        blog_entries = client.get_blogs(page=page)
        #############################
        if 'blogs' not in blog_entries:
            raise Http404
        blog_entries = blog_entries['blogs']
        #############################
        context = {'blog_entries': blog_entries}
        return render(request, self.template_name, context)


class CommunityBlogDetailView(View):
    template_name = "balystic/blog_detail.html"

    def get(self, request, slug):
        """
        Display detail of the required blog post,
        if it does exists.
        """
        client = Client()
        blog_entry = client.get_blog_detail(slug)
        #########################
        if 'blog' not in blog_entry:
            raise Http404
        blog_entry = blog_entry['blog']
        #########################
        context = {'entry': blog_entry}
        return render(request, self.template_name, context)


class CommunityQAListView(View):
    template_name = "balystic/qa_list.html"

    def get(self, request):
        """
        Display list of all the questions
        inside community
        """
        page = request.GET.get('page', 1)
        client = Client()
        questions = client.get_questions(page=page)
        #############################
        if 'questions' not in questions:
            raise Http404
        questions = questions['questions']
        #############################
        context = {'questions': questions}
        return render(request, self.template_name, context)


class CommunityQADetailView(View):
    template_name = "balystic/qa_detail.html"

    def get(self, request, pk):
        """
        Display detail of the required question,
        if it exists
        """
        client = Client()
        form = QAAnswerForm()
        question = client.get_question_detail(pk)
        #########################
        if 'question' not in question:
            raise Http404
        question = question['question']
        #########################
        context = {'question': question, 'form': form}
        return render(request, self.template_name, context)

    def post(self, request, pk):
        """
        creates an answer for a question
        """
        form = QAAnswerForm(request.POST)
        if form.is_valid():
            client = Client()
            data = form.cleaned_data
            data['user_email'] = request.user.email
            client = Client()
            client.create_answer(pk, data)
            return redirect('balystic_qa_detail', pk=pk)
        context = {'form': form}
        return render(request, self.template_name, context)


class CommunityQACreateQuestionView(LoginRequiredMixin, View):
    template_name = "balystic/qa_create_question.html"

    def get(self, request):
        """
        Display the form for creating a question
        """
        form = QAQuestionForm()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request):
        """
        Creates the question in the qa community
        """
        form = QAQuestionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['user_email'] = request.user.email
            client = Client()
            client.create_question(data)
            return redirect('balystic_qa')
        context = {'form': form}
        return render(request, self.template_name, context)


class CommunityQAQuestionVoteView(LoginRequiredMixin, View):

    def post(self, request, pk):
        client = Client()
        client.vote_answer(pk, data=request.POST)
        return redirect('balystic_qa_detail', pk=pk)


class CommunityQAAnswerVoteView(LoginRequiredMixin, View):

    def post(self, request, pk):
        client = Client()
        client.vote_answer(pk, data=request.POST)
        return redirect('balystic_qa')

class LoginView(View):
    """
    View that handles the authentication form.
    """
    template_name = 'balystic/login.html'

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(settings.LOGIN_REDIRECT_URL)
                else:
                    form.add_error(None, 'Account is not active')
            else:
                form.add_error(None, 'Not able to authenticate with the given credentials')
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    template_name='balystic/logout.html'

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        logout(request)
        return redirect('balystic_login')
