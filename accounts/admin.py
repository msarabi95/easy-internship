from accounts.models import Profile, Intern
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


class InternInline(admin.StackedInline):
    model = Intern
    extra = 0

class ProfileAdmin(admin.ModelAdmin):
    list_display = ["get_ar_full_name", "get_en_full_name", "role"]
    search_fields = ["ar_first_name", "ar_middle_name",
                     "ar_last_name", "en_first_name",
                     "en_middle_name", "en_last_name"]
    inlines = [InternInline, ]

class RoleListFilter(admin.SimpleListFilter):
    # Refer to: https://docs.djangoproject.com/en/1.9/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter
    title = "Role"
    parameter_name = 'role'

    def lookups(self, request, model_admin):
        return (
            (Profile.INTERN, Profile.INTERN.capitalize()),
            (Profile.STAFF, Profile.STAFF.capitalize()),
            ("unknown", "Unknown"),
        )

    def queryset(self, request, queryset):
        if self.value() == Profile.INTERN:
            return queryset.filter(profile__role=Profile.INTERN)
        if self.value() == Profile.STAFF:
            return queryset.filter(profile__role=Profile.STAFF)
        if self.value() == "unknown":
            return queryset.exclude(profile__role=Profile.INTERN).exclude(profile__role=Profile.STAFF)


class ModifiedUserAdmin(UserAdmin):
    search_fields = ["profile__ar_first_name",
                     "profile__ar_middle_name",
                     "profile__ar_last_name",
                     "profile__en_first_name",
                     "profile__en_middle_name",
                     "profile__en_last_name"]

    def get_role(self, instance):
        try:
            profile = instance.profile
            return profile.role.capitalize()
        except ObjectDoesNotExist:
            return "Unknown"
    get_role.short_description = "Role"

    def get_list_display(self, request):
        list_display = super(ModifiedUserAdmin, self).get_list_display(request)
        list_display = list(list_display)
        list_display.append("get_role")
        return tuple(list_display)

    def get_list_filter(self, request):
        list_filter = super(ModifiedUserAdmin, self).get_list_filter(request)
        list_filter = list(list_filter)
        list_filter.append(RoleListFilter)
        return tuple(list_filter)


admin.site.unregister(User)
admin.site.register(User, ModifiedUserAdmin)
admin.site.register(Profile, ProfileAdmin)
