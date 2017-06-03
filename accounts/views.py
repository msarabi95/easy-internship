from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.views.generic.edit import FormView

from userena.models import UserenaSignup
from userena.views import signup, profile_edit, profile_detail
from userena import settings as userena_settings

from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response

from accounts.models import Profile, Intern, University, Batch
from accounts.forms import ChooseUniversityForm, KSAUHSSignupForm, AGUSignupForm, OutsideSignupForm, \
    KSAUHSProfileEditForm, AGUProfileEditForm, OutsideProfileEditForm, ResendForm
from accounts.permissions import IsStaff
from accounts.serializers import ProfileSerializer, InternSerializer, UserSerializer, InternTableSerializer, \
    BatchSerializer
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions

from months.models import Internship
from months.serializers import FullInternshipSerializer2


class SignupWrapper(View):
    def get(self, request, *args, **kwargs):
        context = {'form': ChooseUniversityForm}
        return render(request, 'accounts/signup_start.html', context)

    def get_signup_form(self, university_id):
        if university_id == -1:
            form = OutsideSignupForm
        else:
            university = University.objects.get(id=university_id)
            if university.is_ksauhs:
                form = KSAUHSSignupForm
            elif university.is_agu:
                form = AGUSignupForm
            else:
                form = OutsideSignupForm
        form.university_id = university_id
        return form

    def post(self, request, *args, **kwargs):
        page = request.POST.get('page')
        if int(page) == 1:
            form = ChooseUniversityForm(request.POST)
            if form.is_valid():
                university_id = int(form.cleaned_data.get('university_id'))

                signup_form = self.get_signup_form(university_id)

                request.method = "GET"  # Return the `signup` output as if it were a GET request
                return signup(request, signup_form=signup_form)
            return render(request, 'accounts/signup_start.html', {'form': form})

        elif int(page) == 2:
            university_id = int(request.POST.get('university'))
            signup_form = self.get_signup_form(university_id)
            return signup(request, signup_form=signup_form)


class ProfileDetailWrapper(View):
    def get_template_name(self, user):
        intern_profile = user.profile.intern
        if intern_profile.is_ksauhs_intern:
            return 'accounts/profile_detail/ksauhs.html'
        elif intern_profile.is_agu_intern:
            return 'accounts/profile_detail/agu.html'
        return 'accounts/profile_detail/outside.html'

    def get(self, request, *args, **kwargs):
        user = User.objects.get_by_natural_key(kwargs.get('username'))

        if not hasattr(user.profile, 'intern'):
            raise PermissionDenied

        kwargs['template_name'] = self.get_template_name(user)
        return profile_detail(request, *args, **kwargs)


class ProfileEditWrapper(View):
    def get_profile_edit_form(self, user):
        intern_profile = user.profile.intern
        if intern_profile.is_ksauhs_intern:
            return KSAUHSProfileEditForm
        if intern_profile.is_agu_intern:
            return AGUProfileEditForm
        return OutsideProfileEditForm

    def get_template_name(self, user):
        intern_profile = user.profile.intern
        if intern_profile.is_ksauhs_intern:
            return 'accounts/profile_form/ksauhs.html'
        elif intern_profile.is_agu_intern:
            return 'accounts/profile_form/agu.html'
        return 'accounts/profile_form/outside.html'

    def get(self, request, *args, **kwargs):
        user = User.objects.get_by_natural_key(kwargs.get('username'))
        kwargs['edit_profile_form'] = self.get_profile_edit_form(user)
        kwargs['template_name'] = self.get_template_name(user)
        return profile_edit(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = User.objects.get_by_natural_key(kwargs.get('username'))
        kwargs['edit_profile_form'] = self.get_profile_edit_form(user)
        kwargs['template_name'] = self.get_template_name(user)
        return profile_edit(request, *args, **kwargs)


class ResendConfirmationKey(FormView):
    template_name = "accounts/resend_confirmation_code.html"
    form_class = ResendForm
    success_url = reverse_lazy('resend_activation_complete')

    def form_valid(self, form):
        """
        Issue a new activation if form is valid.
        """
        UserenaSignup.objects.reissue_activation(form.user.userena_signup.activation_key)
        return redirect(self.get_success_url())


class ResendConfirmationKeyComplete(TemplateView):
    template_name = "userena/activate_retry_success.html"

    def get_context_data(self, **kwargs):
        context = super(ResendConfirmationKeyComplete, self).get_context_data(**kwargs)
        context['userena_activation_days'] = userena_settings.USERENA_ACTIVATION_DAYS
        context['SUPPORT_EMAIL_ADDRESS'] = settings.SUPPORT_EMAIL_ADDRESS
        return context


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("accounts.user.view_all"):
            return self.queryset.all()
        return self.queryset.filter(username=self.request.user.username)


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("accounts.profile.view_all"):
            return self.queryset.all()
        return self.queryset.filter(user=self.request.user)


class InternViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InternSerializer
    queryset = Intern.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.has_perm("accounts.intern.view_all"):
            return self.queryset.all()
        return self.queryset.filter(profile__user=self.request.user)

    @list_route(methods=['get'], permission_classes=[permissions.IsAuthenticated, IsStaff])
    def as_table(self, request, *args, **kwargs):
        interns = self.queryset.all().prefetch_related('profile__user', 'internship')
        serialized = InternTableSerializer(interns, many=True)
        return Response(serialized.data)


class BatchViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BatchSerializer
    queryset = Batch.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    @detail_route(methods=['get'], permission_classes=[permissions.IsAuthenticated, IsStaff])
    def interns(self, request, pk, *args, **kwargs):
        batch = get_object_or_404(Batch, id=pk)
        interns = Intern.objects.filter(batch=batch).prefetch_related('profile__user', 'internship')
        serialized = InternTableSerializer(interns, many=True)
        return Response(serialized.data)

    @detail_route(methods=['get'], permission_classes=[permissions.IsAuthenticated, IsStaff])
    def plans(self, request, pk, *args, **kwargs):
        batch = get_object_or_404(Batch, id=pk)
        plans = Internship.objects.filter(intern__batch=batch).prefetch_related(
            'rotation_requests__requested_department__department__hospital',
            'rotation_requests__requested_department__department__specialty',
            'rotations__department__specialty',
            'rotations__department__hospital',
            'intern__profile__user__freezes',
            'intern__profile__user__freeze_requests',
            'intern__profile__user__freeze_cancel_requests',
        )
        serialized = FullInternshipSerializer2(plans, many=True)
        return Response(serialized.data)
