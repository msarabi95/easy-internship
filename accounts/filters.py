import rest_framework_filters as filters
from django.db.models.functions import Concat
from django.db.models import CharField, Value

from accounts.models import Profile, Intern
from months.models import Internship


class ProfileFilter(filters.FilterSet):
    en_full_name = filters.CharFilter(name='en_full_name', method='filter_en_full_name')

    def filter_en_full_name(self, queryset, name, value):
        # Construct full field name
        prefix = name.split('en_full_name')[0]
        field_name = "%s%s" % (prefix, "en_full_name")
        lookup = "%s__icontains" % field_name
        # Perform filtering
        return queryset.annotate(
            **{field_name: Concat(
                '%s%s' % (prefix, 'en_first_name'), Value(' '),
                '%s%s' % (prefix, 'en_father_name'), Value(' '),
                '%s%s' % (prefix, 'en_grandfather_name'), Value(' '),
                '%s%s' % (prefix, 'en_last_name'),
                output_field=CharField()
            )}
        ).filter(**{lookup: value})

    class Meta:
        model = Profile
        fields = ['en_full_name']


class InternFilter(filters.FilterSet):
    profile = filters.RelatedFilter(ProfileFilter, name='profile', queryset=Profile.objects.filter(role=Profile.INTERN))

    class Meta:
        model = Intern
        fields = ['id']


class InternshipFilter(filters.FilterSet):
    intern = filters.RelatedFilter(InternFilter, name='intern', queryset=Intern.objects.all())

    class Meta:
        model = Internship
        fields = ['id']
