from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from members.models import Member
from socialgraph.forms import EmptyForm, RelationForm
from socialgraph.models import Relation


class RelationListView(ListView):
    model = Relation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class RelationView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect("/")

    def post(self, request, *args, **kwargs):
        form = RelationForm(request.POST)

        if form.is_valid():
            form.save()
            return self._render_graph(request)

        form = EmptyForm(request.POST)

        if form.is_valid():
            return self._render_graph(request)

        return HttpResponseRedirect("/")

    def _render_graph(self, request):
        mem_1_list = Relation.objects.values_list("member_1_id", flat=True)
        mem_2_list = Relation.objects.values_list("member_2_id", flat=True)
        members = Member.objects.filter(id__in=list(mem_1_list) + list(mem_2_list))
        context = {
            "edges": Relation.objects.all(),
            "vertices": members,
            "form": RelationForm(),
        }
        return render(request, "socialgraph/graph.html", context)
