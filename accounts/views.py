from django.shortcuts import render
from django.views.generic import View
from userena.views import signup

from rest_framework.decorators import list_route
from rest_framework.response import Response

from accounts.models import Profile, Intern, University
from accounts.forms import ChooseUniversityForm, KSAUHSSignupForm, AGUSignupForm, OutsideSignupForm
from accounts.permissions import IsStaff
from accounts.serializers import ProfileSerializer, InternSerializer, UserSerializer, InternTableSerializer
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions


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
