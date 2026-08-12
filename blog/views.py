from django.db.models import F
from django.views.generic import DetailView, ListView

from .models import Post


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        queryset = Post.published.prefetch_related("tags")
        tag = self.request.GET.get("tag")
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_tag"] = self.request.GET.get("tag", "")
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.published.prefetch_related("tags")

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        # F() — bazaning o'zida oshiradi, parallel so'rovlarda ham to'g'ri ishlaydi
        Post.objects.filter(pk=post.pk).update(views=F("views") + 1)
        post.views += 1
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_ids = self.object.tags.values_list("id", flat=True)
        context["related_posts"] = (
            Post.published.filter(tags__in=tag_ids)
            .exclude(pk=self.object.pk)
            .distinct()[:3]
        )
        return context
