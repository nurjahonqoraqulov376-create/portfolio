from django.views.generic import DetailView, ListView

from .models import Project, Technology


class ProjectListView(ListView):
    """Barcha loyihalar + texnologiya bo'yicha filtr (`?tech=django`)."""

    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 9

    def get_queryset(self):
        queryset = Project.objects.with_tech()
        tech = self.request.GET.get("tech")
        if tech:
            queryset = queryset.filter(technologies__slug=tech)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["technologies"] = Technology.objects.filter(
            projects__isnull=False
        ).distinct()
        context["active_tech"] = self.request.GET.get("tech", "")
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.with_tech()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Bir xil texnologiyaga ega boshqa loyihalar
        tech_ids = self.object.technologies.values_list("id", flat=True)
        context["related_projects"] = (
            Project.objects.with_tech()
            .filter(technologies__in=tech_ids)
            .exclude(pk=self.object.pk)
            .distinct()[:3]
        )
        return context
