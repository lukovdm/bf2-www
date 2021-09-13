from django import forms

from socialgraph.models import Relation


class EmptyForm(forms.Form):
    pass


class RelationForm(forms.ModelForm):
    class Meta:
        model = Relation
        exclude = []
