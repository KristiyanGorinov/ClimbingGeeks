from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction, connection
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.template.context_processors import request
from django.urls import reverse_lazy
from django.views.generic import ListView, View, DetailView, CreateView, UpdateView, DeleteView, TemplateView

from SoftUniFinalExam.utils import get_user_obj
from clubs.forms import ClubCreateForm, ClubEditForm, ClubDeleteForm
from competitions.forms import CompetitionCreateForm, CompetitionEditForm, CompetitionDeleteForm
from competitions.models import Competitions
from posts.forms import PostCreateForm, PostsEditForm, PostDeleteForm
from posts.models import Post
from clubs.models import Club
from registration.forms import RegisterBaseForm
from registration.models import Registration
from .decorators import unauthenticated_user, allowed_users, AllowedUsersMixin
from .forms import CreateUserForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from users.models import *


class HomeView(TemplateView):
    template_name = 'public/public-page.html'



class AboutView(ListView):
    model = User
    template_name = 'public/about-me.html'


class PostsView(LoginRequiredMixin, AllowedUsersMixin, ListView):
    model = Post
    template_name = 'user/posts.html'
    context_object_name = 'posts'
    login_url = 'login'
    allowed_roles = ['admin', 'staff', 'user']


class PostDetailView(LoginRequiredMixin, AllowedUsersMixin, DetailView):
    model = Post
    template_name = 'Posts/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = 'login'
    allowed_roles = ['admin', 'staff', 'user']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        related_posts = Post.objects.exclude(id=self.object.id)[:4]
        context['related_posts'] = related_posts

        return context


class PostCreateView(LoginRequiredMixin, AllowedUsersMixin, CreateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'Posts/post_create.html'
    success_url = reverse_lazy('posts')
    context_object_name = 'posts'
    login_url = 'login'
    allowed_roles = ['admin', 'staff', 'user']

    def form_valid(self, form):
        logged_in_user = self.request.user
        try:
            custom_user = Users.objects.get(user=logged_in_user)
        except Users.DoesNotExist:
            raise ValueError("No corresponding Users instance found for the logged-in user.")

        form.instance.user = custom_user
        return super().form_valid(form)


class PostEditView(LoginRequiredMixin, AllowedUsersMixin, UpdateView):
    model = Post
    form_class = PostsEditForm
    template_name = 'Posts/post_edit.html'
    success_url = reverse_lazy('posts')
    context_object_name = 'posts'
    login_url = 'login'
    allowed_roles = ['admin', 'staff', 'user']

    def form_valid(self, form):
        logged_in_user = self.request.user
        try:
            custom_user = Users.objects.get(user=logged_in_user)
        except Users.DoesNotExist:
            raise ValueError("No corresponding Users instance found for the logged-in user.")

        form.instance.user = custom_user
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, AllowedUsersMixin, DeleteView):
    model = Post
    form_class = PostDeleteForm
    template_name = 'Posts/post_delete.html'
    success_url = reverse_lazy('posts')
    context_object_name = 'posts'
    login_url = 'login'
    allowed_roles = ['admin', 'staff', 'user']

    def get_initial(self):
        return self.object.__dict__

    def form_invalid(self, form):
        return self.form_valid(form)


class ClubsView(LoginRequiredMixin, AllowedUsersMixin, ListView):
    model = Club
    template_name = 'user/clubs.html'
    context_object_name = 'clubs'
    login_url = 'login'
    allowed_roles = ['admin', 'staff', 'user']


class ClubDetailView(LoginRequiredMixin, AllowedUsersMixin, DetailView):
    model = Club
    template_name = 'Clubs/club_details.html'
    context_object_name = 'club'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = 'login'
    allowed_roles = ['admin', 'staff', 'user']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        related_clubs = Club.objects.exclude(id=self.object.id)[:4]
        context['related_clubs'] = related_clubs

        return context


class ClubCreateView(LoginRequiredMixin, AllowedUsersMixin, CreateView):
    model = Club
    form_class = ClubCreateForm
    template_name = 'Clubs/club_create.html'
    success_url = reverse_lazy('clubs')
    context_object_name = 'clubs'
    login_url = 'login'
    allowed_roles = ['admin', 'staff']

    def form_valid(self, form):
        logged_in_user = self.request.user
        try:
            custom_user = Users.objects.get(user=logged_in_user)
        except Users.DoesNotExist:
            raise ValueError("No corresponding Users instance found for the logged-in user.")

        form.instance.user = custom_user
        return super().form_valid(form)


class ClubEditView(LoginRequiredMixin, AllowedUsersMixin, UpdateView):
    model = Club
    form_class = ClubEditForm
    template_name = 'Clubs/club_edit.html'
    success_url = reverse_lazy('clubs')
    context_object_name = 'clubs'
    login_url = 'login'
    allowed_roles = ['admin', 'staff']

    def form_valid(self, form):
        logged_in_user = self.request.user
        try:
            custom_user = Users.objects.get(user=logged_in_user)
        except Users.DoesNotExist:
            raise ValueError("No corresponding Users instance found for the logged-in user.")

        form.instance.user = custom_user
        return super().form_valid(form)


class ClubDeleteView(LoginRequiredMixin, AllowedUsersMixin, DeleteView):
    model = Club
    form_class = ClubDeleteForm
    template_name = 'Clubs/club_delete.html'
    success_url = reverse_lazy('clubs')
    context_object_name = 'clubs'
    login_url = 'login'
    allowed_roles = ['admin', 'staff']

    def get_initial(self):
        return self.object.__dict__

    def form_invalid(self, form):
        return self.form_valid(form)


@login_required
@allowed_users(allowed_roles=['admin', 'staff', 'user'])
def join_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    user_id = request.user.id

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM clubs_club_members WHERE club_id = %s AND user_id = %s",
            [club_id, user_id]
        )
        is_member_of_current_club = cursor.fetchone()

    if is_member_of_current_club:
        messages.info(request, "You are already a member of this club!")
    else:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT club_id FROM clubs_club_members WHERE user_id = %s",
                [user_id]
            )
            other_club = cursor.fetchone()

        if other_club:
            messages.error(
                request,
                f"You are already a member of another club. Leave it before joining a new one."
            )
        else:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO clubs_club_members (club_id, user_id) VALUES (%s, %s)",
                    [club_id, user_id]
                )
            messages.success(request, "You have successfully joined the club!")

    return redirect('club_detail', club.slug)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'user', 'staff'])
def leave_club(request):
    user_id = request.user.id

    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM clubs_club_members WHERE user_id = %s",
            [user_id]
        )

    messages.success(request, "You have successfully left the club!")

    return redirect('profile')


class CompetitionsView(LoginRequiredMixin, AllowedUsersMixin, ListView):
    model = Competitions
    template_name = 'user/competitions.html'
    context_object_name = 'competitions'
    login_url = 'login'
    allowed_roles = ['admin', 'staff', 'user']


class CompetitionDetailView(LoginRequiredMixin, AllowedUsersMixin, DetailView):
    model = Competitions
    template_name = 'Competitions/competition_details.html'
    context_object_name = 'competitions'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = 'login'
    allowed_roles = ['admin', 'staff', 'user']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        related_competitions = Competitions.objects.exclude(id=self.object.id)[:4]
        context['related_competitions'] = related_competitions

        return context


class CompetitionCreateView(LoginRequiredMixin, AllowedUsersMixin, CreateView):
    model = Competitions
    form_class = CompetitionCreateForm
    template_name = 'Competitions/competition_create.html'
    success_url = reverse_lazy('competitions')
    context_object_name = 'competitions'
    login_url = 'login'
    allowed_roles = ['admin', 'staff']

    def form_valid(self, form):
        logged_in_user = self.request.user
        try:
            custom_user = Users.objects.get(user=logged_in_user)
        except Users.DoesNotExist:
            raise ValueError("No corresponding Users instance found for the logged-in user.")

        form.instance.user = custom_user
        return super().form_valid(form)


class CompetitionEditView(LoginRequiredMixin, AllowedUsersMixin, UpdateView):
    model = Competitions
    form_class = CompetitionEditForm
    template_name = 'Competitions/competition_edit.html'
    success_url = reverse_lazy('competitions')
    context_object_name = 'competitions'
    login_url = 'login'
    allowed_roles = ['admin', 'staff']

    def form_valid(self, form):
        logged_in_user = self.request.user
        try:
            custom_user = Users.objects.get(user=logged_in_user)
        except Users.DoesNotExist:
            raise ValueError("No corresponding Users instance found for the logged-in user.")

        form.instance.user = custom_user
        return super().form_valid(form)


class CompetitionDeleteView(LoginRequiredMixin, AllowedUsersMixin, DeleteView):
    model = Competitions
    form_class = CompetitionDeleteForm
    template_name = 'Competitions/competition_delete.html'
    success_url = reverse_lazy('competitions')
    context_object_name = 'competitions'
    login_url = 'login'
    allowed_roles = ['admin', 'staff']

    def get_initial(self):
        return self.object.__dict__

    def form_invalid(self, form):
        return self.form_valid(form)


class CompetitionRegisterView(LoginRequiredMixin, AllowedUsersMixin, CreateView):
    model = Registration
    form_class = RegisterBaseForm
    template_name = 'Competitions/competition_register.html'
    success_url = reverse_lazy('profile')
    context_object_name = 'competitions'
    login_url = 'login'
    allowed_roles = ['admin', 'staff', 'user']

    def form_valid(self, form):
        form.instance.user = self.request.user

        competition_slug = self.kwargs.get('slug')
        try:
            competition = Competitions.objects.get(slug=competition_slug)
            form.instance.competition = competition
        except Competitions.DoesNotExist:
            form.add_error(None, "Competition does not exist.")
            return self.form_invalid(form)

        response = super().form_valid(form)

        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM competitions_competitions_participants WHERE user_id = %s AND competitions_id = %s",
                    [self.request.user.id, competition.id]
                )
        except Exception as e:
            print(f"Error deleting row: {e}")

        messages.success(self.request, f"You have successfully registered for the competition: {competition.title}")
        return response


class RegistrationDeleteView(LoginRequiredMixin, AllowedUsersMixin, View):
    login_url = 'login'
    allowed_roles = ['admin', 'staff']

    def post(self, request, pk, *args, **kwargs):
        registration = get_object_or_404(Registration, pk=pk)

        registration.delete()

        messages.success(request,
                         f"Registration for {registration.first_name} {registration.last_name} has been successfully reviewed.")

        return redirect(reverse_lazy('admin-panel'))


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff', 'user'])
def add_competition(request, competitions_id):
    competition = get_object_or_404(Competitions, id=competitions_id)
    user_id = request.user.id

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM competitions_competitions_participants WHERE competitions_id = %s AND user_id = %s",
            [competitions_id, user_id]
        )
        is_member_of_current_competition = cursor.fetchone()

    if is_member_of_current_competition:
        messages.info(request, "You have already added this competition in your profile")
    else:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO competitions_competitions_participants (competitions_id, user_id) VALUES (%s, %s)",
                [competitions_id, user_id]
            )
        messages.success(request, "You have successfuly added this competition to your profile")

    return redirect('competition_detail', competition.slug)


class UserHomeView(LoginRequiredMixin, AllowedUsersMixin, ListView):
    model = Post
    template_name = 'user/user-page.html'
    context_object_name = 'posts'
    login_url = 'login'
    allowed_roles = ['admin', 'staff', 'user']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        posts = Post.objects.all().order_by('uploaded_at')[:4]
        context['posts'] = posts

        return context


@login_required(login_url='login')
def user_profile(request):
    user = request.user
    try:
        profile = user.users
    except Users.DoesNotExist:
        profile = Users.objects.create(
            user=user,
            first_name=user.first_name or "",
            last_name=user.last_name or "",
            email=user.email or f"default_email_{user.pk}@example.com",
            phone="",
            info="",
        )

    user_id = request.user.id
    user_clubs = Club.objects.filter(members=user_id)
    user_competitions = Competitions.objects.filter(participants=user_id)

    if request.method == 'POST':
        if 'leave_club' in request.POST:
            user_id = request.user.id
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM clubs_club_members WHERE user_id = %s",
                    [user_id]
                )
        else:
            form = ProfileUpdateForm(request.POST, instance=user)
            if form.is_valid():
                user = form.save()
                profile.phone = request.POST.get('phone', profile.phone)
                profile.info = request.POST.get('info', profile.info)
                profile.first_name = user.first_name
                profile.last_name = user.last_name
                profile.email = user.email
                profile.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('profile')


    else:
        form = ProfileUpdateForm(instance=user)

    context = {
        'form': form,
        'profile': profile,
        'user_clubs': user_clubs,
        'user_competitions': user_competitions,
    }
    return render(request, 'user/user-profile.html', context)


class BecomeStaffView(LoginRequiredMixin, View):
    login_url = 'login'
    staff_pass_key = "STAFF123"

    def post(self, request, *args, **kwargs):
        staff_key = request.POST.get("staff_key")

        if staff_key == self.staff_pass_key:
            staff_group, created = Group.objects.get_or_create(name="staff")
            request.user.groups.add(staff_group)

            request.user.is_staff = True
            request.user.save()

            messages.success(request, "You have successfully become a staff member!")
        else:
            messages.error(request, "Invalid staff key. Please try again.")

        return redirect("profile")


@unauthenticated_user
def register_user(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            if User.objects.filter(email=email).exists():
                messages.error(request, "This email is already registered in our system.")
                return render(request, 'user/register-user.html', {'form': form})

            if Users.objects.filter(email=email).exists():
                messages.error(request, "This email is already registered in our system.")
                return render(request, 'user/register-user.html', {'form': form})

            try:
                with transaction.atomic():
                    user = form.save()

                    group, created = Group.objects.get_or_create(name='user')
                    user.groups.add(group)

                    existing_users_record = Users.objects.filter(user=user).first()
                    if not existing_users_record:
                        Users.objects.create(
                            user=user,
                            username=user.username,
                            email=email
                        )
                    else:
                        existing_users_record.username = user.username
                        existing_users_record.email = email
                        existing_users_record.save()

                messages.success(request, f'Account created for {form.cleaned_data["username"]}')
                return redirect('login')

            except IntegrityError:
                messages.error(request, "There was an error creating your account. Please try again.")
                return render(request, 'user/register-user.html', {'form': form})


    context = {'form': form}
    return render(request, 'user/register-user.html', context)


@unauthenticated_user
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            return redirect('user-home')
        else:
            messages.info(request, 'Username or Password is incorrect')

    return render(request, 'user/login-user.html')



def logout_user(request):
    logout(request)
    return redirect('home')


class PanelView(LoginRequiredMixin, AllowedUsersMixin, TemplateView):
    model = User
    login_url = 'login'
    allowed_roles = ['admin', 'staff']
    template_name = 'Admins/admin_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        context['posts'] = Post.objects.all()
        context['competitions'] = Competitions.objects.all()
        context['clubs'] = Club.objects.all()
        context['registrations'] = Registration.objects.all()
        return context


class ClubAdminPanelView(LoginRequiredMixin, AllowedUsersMixin, View):
    template_name = 'Admins/admin_club_panel.html'
    allowed_roles = ['admin', 'staff']
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        clubs = Club.objects.prefetch_related(
            'members'
        )

        context = {
            'clubs': clubs
        }
        return render(request, self.template_name, context)


class RemoveUserFromClubView(LoginRequiredMixin, AllowedUsersMixin, View):
    allowed_roles = ['admin', 'staff']
    login_url = 'login'

    def post(self, request, club_id, user_id, *args, **kwargs):
        club = get_object_or_404(Club, id=club_id)
        user = get_object_or_404(User, id=user_id)

        club.members.remove(user)

        messages.success(request, f"{user.username} has been removed from {club.title}.")

        return redirect(reverse_lazy('admin_club_panel'))
@login_required
@allowed_users(allowed_roles=['admin'])
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('admin-panel')

    user.delete()
    messages.success(request, f"User {user.username} has been successfully deleted.")
    return redirect('admin-panel')


@login_required
@allowed_users(allowed_roles=['admin'])
def make_superuser(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user == request.user:
        messages.error(request, "You are already a superuser")
        return redirect('admin-panel')
    if user.is_superuser and user.is_staff:
        messages.error(request, "This user is already a superuser")
        return redirect('admin-panel')

    admin_group, created = Group.objects.get_or_create(name="admin")
    user.groups.add(admin_group)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    messages.success(request, f"User {user.username} has been successfully made a superuser.")
    return redirect('admin-panel')

class RevokeStaffView(LoginRequiredMixin, AllowedUsersMixin, View):
    allowed_roles = ['admin']
    login_url = 'login'

    def post(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)

        if user == request.user:
            messages.error(request, "You cannot revoke yourself")
            return redirect('admin-panel')

        if user.is_staff or user.is_superuser:
            admin_group,  created = Group.objects.get_or_create(name="admin")
            staff_group, created = Group.objects.get_or_create(name="staff")
            user.groups.remove(admin_group,staff_group)
            user.is_staff = False
            user.is_superuser = False
            user.save()
            messages.success(request, f"Staff privileges revoked for {user.username}.")
        else:
            messages.error(request, f"{user.username} is not a staff member.")

        return redirect(reverse_lazy('admin-panel'))