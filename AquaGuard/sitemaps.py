# AquaGuard/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class PublicViewSitemap(Sitemap):
    """
    Sitemap for public pages that should be indexed by search engines.
    Only includes homepage and login page for SEO purposes.
    """
    # Set the priority for your most important page (the Homepage)
    # Homepage gets the highest priority (1.0), Login is slightly lower.
    priority = 0.8
    
    # Indicate how often these pages might change
    changefreq = "daily" 

    def items(self):
        """
        Return the URL names for public pages that should be in the sitemap.
        These correspond to the 'name' arguments in your urls.py file.
        """
        return [
            'public_home',  # Homepage (root path)
            'login',        # Login page
        ]

    def location(self, item):
        """
        This function takes the name (item) and converts it to the full URL path.
        """
        return reverse(item)
