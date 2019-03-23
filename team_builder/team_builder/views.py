from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView, View)
from rules.contrib.views import PermissionRequiredMixin

from .forms import (PositionFormSet, SkillCreateForm, UserCreateForm,
                    UserProfileUpdateForm)
from .models import Participant, Position, Project, Skill, User


class SignUpView(SuccessMessageMixin, CreateView):
    form_class = UserCreateForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('home')
    success_message = 'User created! Please log in.'


class SignInView(LoginView):
    template_name = 'registration/signin.html'
    success_url = reverse_lazy('home')


class ProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = 'profile.html'
    queryset = User.objects.all()

    def get_object(self, queryset=None):
        profile = get_object_or_404(User, pk=self.kwargs['profile_id'])
        return profile

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        user_projects = Project.objects.filter(
            position__in=self.request.user.position_set.all()).distinct()
        context['user_projects'] = user_projects
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserProfileUpdateForm
    template_name = 'profile_update.html'
    success_message = 'Profile updated!'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('profile',
                            kwargs={'profile_id': self.request.user.id})


class HomeView(ListView):
    template_name = 'index.html'

    def get_queryset(self):
        return Project.objects.all().prefetch_related('position_set')


class ProjectView(ListView):
    template_name = 'index.html'
    queryset = Project.objects.all()

    def get_queryset(self):
        '''
        Filtering the queryset based on type of filter requested or no filter
        :return: queryset
        '''

        is_member_query = Position.objects.filter(
            participant__in=Participant.objects.filter(
                user=self.request.user, status='member'))

        can_join_query = (~Q(position__in=is_member_query) &
                          ~Q(owner=self.request.user))

        if 'filter_type' in self.kwargs:
            filter_type = self.kwargs['filter_type']
            if filter_type == 'own':
                return self.queryset.filter(owner=self.request.user)
            elif filter_type == 'member':
                return self.queryset.filter(position__in=is_member_query
                                            ).exclude(owner=self.request.user)
            elif filter_type == 'join':
                return self.queryset.filter(can_join_query)
            else:
                raise Http404('No such view')
        else:
            return self.queryset


class ProjectCreateView(LoginRequiredMixin, CreateView):
    template_name = 'projects/project_create.html'
    model = Project
    fields = ['name', 'description', 'url',]

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        position_form = PositionFormSet()
        return self.render_to_response(
            self.get_context_data(form=form,
                                  position_form=position_form))

    def form_valid(self, form, *args, **kwargs):
        new_project = form.instance
        new_project.owner = self.request.user
        new_project.save()
        return super(ProjectCreateView, self).form_valid(form)


class ProjectDetailView(DetailView):
    template_name = 'projects/project_detail.html'
    queryset = Project.objects.all()

    def get_object(self, queryset=None):
        obj = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        user = self.request.user
        position_list = Position.objects.filter(project=project)
        if user == project.owner:
            # If owner, return entire user list including non-approved
            participant_list = Participant.objects.filter(
                position__in=position_list
            )
        elif user != project.owner and user.is_authenticated:
            non_owner_query = (Q(position__in=position_list) & (
                        Q(user=user) | Q(status='member')))
            participant_list = Participant.objects.filter(non_owner_query)
        else:
            participant_list = Participant.objects.filter(status='member')
        context['participant_list'] = participant_list
        return context


class ProjectUpdateView(LoginRequiredMixin,
                        PermissionRequiredMixin,
                        UpdateView):
    template_name = 'projects/project_update.html'
    model = Project
    fields = ['name', 'description', 'url',]
    queryset = Project.objects.all()
    permission_required = 'team_builder.edit_project'

    def get_object(self, queryset=None):
        obj = self.queryset.filter(pk=self.kwargs['project_id']).first()
        return obj

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        skill_form = PositionFormSet(instance=self.object)
        return self.render_to_response(self.get_context_data(
            form=form,
            skill_form=skill_form))


class PositionAddView(LoginRequiredMixin, CreateView):
    template_name = 'positions/position_create.html'
    model = Position
    fields = ['position_name', 'head_count', 'related_skills',]

    def form_valid(self, form, *args, **kwargs):
        new_position = form.instance
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        new_position.project = project
        new_position.save()
        return super(PositionAddView, self).form_valid(form)


class PositionDetailView(DetailView):
    template_name = 'positions/position_detail.html'
    model = Position
    queryset = Position.objects.all()

    def get_object(self, queryset=None):
        obj = get_object_or_404(Position, pk=self.kwargs['position_id'])
        return obj


class PositionUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'positions/position_update.html'
    model = Position
    fields = ['position_name', 'head_count', 'related_skills',]
    queryset = Position.objects.all()

    def get_object(self, queryset=None):
        obj = get_object_or_404(Position, pk=self.kwargs['position_id'])
        return obj


class PositionDeleteView(LoginRequiredMixin, DeleteView):
    model = Position
    fields = ['position_name', 'related_skills',]
    queryset = Position.objects.all()
    template_name = 'positions/position_confirm_delete.html'

    def get_object(self, queryset=None):
        obj = get_object_or_404(Position, pk=self.kwargs['position_id'])
        return obj

    def get_success_url(self):
        position = self.object
        return reverse_lazy('project_update',
                            kwargs={'project_id': position.project.id})


class ParticipantCreateView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        position_id = kwargs['position_id']
        position = get_object_or_404(Position, pk=position_id)
        user = request.user
        participant, created = Participant.objects.get_or_create(
            position=position, user=user)
        return HttpResponseRedirect(reverse('position_detail',
                                            args=[position_id]))


@login_required
@require_POST
def participant_update_view(request, **kwargs):
        pk = kwargs['participant_id']
        participant = get_object_or_404(Participant, pk=pk)
        action = kwargs['action']
        if action == 'approve':
            participant.status = 'member'
            participant.start_date = timezone.now()
            participant.save()
            return HttpResponseRedirect(
                reverse('project_detail',
                        kwargs={'project_id': participant.position.project.id}))
        elif action == 'reject':
            participant.status = 'rejected'
            participant.save()
            return HttpResponseRedirect(
                reverse('project_detail',
                        kwargs={'project_id': participant.position.project.id}))
        elif action == 'retire':
            participant.status = 'retired'
            participant.save()
            return HttpResponseRedirect(
                reverse('project_detail',
                        kwargs={'project_id': participant.position.project.id}))
        else:
            return Http404('Unknown Action')


class ParticipantDeleteView(LoginRequiredMixin, DeleteView):
    model = Participant

    def get_object(self, queryset=None):
        position = Position.objects.get(pk=self.kwargs['position_id'])
        user = self.request.user
        return get_object_or_404(Participant, position=position, user=user)

    def get_success_url(self):
        position_id = self.object.position.id
        return reverse('position_detail', kwargs={'position_id': position_id})


class NotificationView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'notifications.html'


class SkillDetailView(DetailView):
    model = Skill
    template_name = 'skills/skill_detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Skill, pk=self.kwargs['skill_id'])


class SkillCreateView(CreateView):
    model = Skill
    template_name = 'skills/skill_add.html'
    form_class = SkillCreateForm

    def form_valid(self, form, *args, **kwargs):
        new_skill = form.instance
        new_skill.save()
        referrer = self.kwargs['referrer']
        referrer_id = self.kwargs['referrer_id']
        if referrer == 'user':
            user = get_object_or_404(User, pk=referrer_id)
            user.skills.add(new_skill)
            user.save()
        elif referrer == 'position':
            position = get_object_or_404(Position, pk=referrer_id)
            position.related_skills.add(new_skill)
            position.save()
        else:
            return Http404('Unknown referrer')
        return super(SkillCreateView, self).form_valid(form)

    def get_success_url(self):
        referrer = self.kwargs['referrer']
        referrer_id = self.kwargs['referrer_id']
        if referrer == 'user':
            return reverse('profile', kwargs={'profile_id': referrer_id})
        elif referrer == 'position':
            return reverse('position_detail',
                           kwargs={'position_id': referrer_id})
        else:
            return Http404('Unknown referrer')


class SearchView(ListView):
    model = Project
    template_name = 'search.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        search_terms = self.request.GET['search_q']
        if search_terms:
            project_list = Project.objects.all()
            position_list = Position.objects.all()
            user_list = User.objects.all()
            search_terms = search_terms.split(' ')
            for term in search_terms:
                project_list = project_list.filter(
                    Q(name__icontains=term)|
                    Q(description__icontains=term)
                ).distinct()
                position_list = position_list.filter(
                    Q(position_name__icontains=term)|
                    Q(related_skills__name__icontains=term)
                ).distinct()
                user_list = user_list.filter(
                    Q(username__icontains=term)|
                    Q(skills__name__icontains=term)
                ).distinct()
            context['project_results'] = project_list
            context['position_results'] = position_list
            context['user_results'] = user_list
        context['search_terms'] = search_terms
        return context
