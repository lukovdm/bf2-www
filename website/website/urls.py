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
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from cms.sitemaps import CMSSitemap
from django.contrib.sitemaps.views import sitemap

from members.sitemaps import BecomeAMemberSitemap
from members.views import BecomeAMemberView, PasswordSetView

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    url(
        r"^sitemap\.xml$",
        sitemap,
        {"sitemaps": {"cmspages": CMSSitemap, "member": BecomeAMemberSitemap}},
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("user/", include("django.contrib.auth.urls")),
    path("become-a-member/", BecomeAMemberView.as_view(), name="become-a-member"),
    path(
        "activate-account/<uidb64>/<token>/",
        PasswordSetView.as_view(),
        name="activate-account",
    ),
    url(r"^", include("cms.urls")),
)
