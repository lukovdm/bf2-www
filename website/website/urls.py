"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from cms.sitemaps import CMSSitemap
from django.contrib.sitemaps.views import sitemap
from django.views.defaults import page_not_found, server_error

from members.sitemaps import BecomeAMemberSitemap
from members.views import BecomeAMemberView, PasswordSetView

def custom_page_not_found(request):
    return page_not_found(request, None)

def custom_server_error(request):
    return server_error(request)


urlpatterns = (
    [
        path("i18n/", include("django.conf.urls.i18n")),
        path(
            "sitemap.xml",
            sitemap,
            {"sitemaps": {"cmspages": CMSSitemap, "member": BecomeAMemberSitemap}},
        ),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)

urlpatterns += i18n_patterns(
    path("404/", custom_page_not_found),
    path("500/", custom_server_error),
    path("admin/", admin.site.urls),
    path("user/", include("django.contrib.auth.urls")),
    path("become-a-member/", BecomeAMemberView.as_view(), name="become-a-member"),
    path(
        "activate-account/<uidb64>/<token>/",
        PasswordSetView.as_view(),
        name="activate-account",
    ),
    re_path(r"^", include("cms.urls")),
)
