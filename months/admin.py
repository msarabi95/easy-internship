from django.contrib import admin
from django.db.models import Count
from rotations.models import Rotation, RotationRequest
from months.models import Internship


class RotationInline(admin.TabularInline):
    model = Rotation
    extra = 0
    readonly_fields = ['month', 'specialty', 'department']
    exclude = ['rotation_request']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class RotationRequestInline(admin.TabularInline):
    model = RotationRequest
    extra = 0
    readonly_fields = ['month', 'specialty', 'requested_department', 'is_delete']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class CompletePlanFilter(admin.SimpleListFilter):  # Temporary!
    title = "Complete plan?"
    parameter_name = 'complete_plan'

    def lookups(self, request, model_admin):
        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(rr_count=Count("rotation_requests"))
        if self.value() == "yes":
            return queryset.filter(rr_count__gte=12)
        if self.value() == "no":
            return queryset.filter(rr_count__lt=12)


class InternshipAdmin(admin.ModelAdmin):
    search_fields = ["intern__profile__ar_first_name",
                     "intern__profile__ar_father_name",
                     "intern__profile__ar_last_name",
                     "intern__profile__en_first_name",
                     "intern__profile__en_father_name",
                     "intern__profile__en_last_name"]
    inlines = [RotationInline, RotationRequestInline]
    list_filter = [CompletePlanFilter]

admin.site.register(Internship, InternshipAdmin)
