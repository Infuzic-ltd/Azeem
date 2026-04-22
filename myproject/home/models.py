"""
models.py — Wagtail CMS for homepage.html (Educiza Home 3)

Sections covered:
  1.  Navbar        — logo, phone number
  2.  Banner        — heading, subtext, CTA button, logo icon
  3.  Choose / Why Us — section intro + 4 feature boxes
  4.  About         — images, video URL, heading, bullets, mission box
  5.  Courses       — section heading + Course items (tab-filtered)
  6.  Benefits      — 4 counter stats
  7.  Journey CTA   — sub-heading, heading, CTA button
  8.  Testimonials  — carousel of student reviews
  9.  Articles/Blog — carousel of blog post teasers
  10. Footer        — about text, social links, useful links, explore links,
                      contact details, newsletter label, copyright

Image storage:
  All ImageField / image fields use Cloudinary (free tier) via
  cloudinary_storage.  Images are uploaded to Cloudinary and the CDN URL
  is stored in the DB and rendered directly in the template.

Installation:
  pip install wagtail django-cloudinary-storage cloudinary

settings.py additions:
  INSTALLED_APPS += [
      'cloudinary',
      'cloudinary_storage',
  ]
  DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
  CLOUDINARY_STORAGE = {
      'CLOUD_NAME': '<your-cloud-name>',
      'API_KEY':    '<your-api-key>',
      'API_SECRET': '<your-api-secret>',
  }
  # (all free — sign up at https://cloudinary.com/users/register/free)
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.snippets.models import register_snippet


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class CloudinaryImageField(models.ImageField):
    """
    Thin subclass that documents intent: these fields use
    django-cloudinary-storage as DEFAULT_FILE_STORAGE so every upload goes
    straight to Cloudinary and `.url` returns the CDN URL automatically.
    No extra code is needed — just set DEFAULT_FILE_STORAGE in settings.py.
    """
    pass


# ---------------------------------------------------------------------------
# Snippets  (reusable pieces not tied to a single page)
# ---------------------------------------------------------------------------

@register_snippet
class SocialLink(models.Model):
    """
    A single social-media link that appears in the footer.
    e.g.  Facebook → https://facebook.com/educiza  (fa-brands fa-facebook-f)
    """
    PLATFORM_CHOICES = [
        ('fa-brands fa-facebook-f', 'Facebook'),
        ('fa-brands fa-x-twitter',  'X / Twitter'),
        ('fa-brands fa-youtube',    'YouTube'),
        ('fa-brands fa-instagram',  'Instagram'),
        ('fa-brands fa-linkedin-in','LinkedIn'),
    ]
    platform   = models.CharField(max_length=60, choices=PLATFORM_CHOICES)
    url        = models.URLField()
    sort_order = models.PositiveIntegerField(default=0)

    panels = [FieldPanel('platform'), FieldPanel('url'), FieldPanel('sort_order')]

    class Meta:
        ordering = ['sort_order']
        verbose_name        = 'Social Link'
        verbose_name_plural = 'Social Links'

    def __str__(self):
        return f"{self.get_platform_display()} → {self.url}"


# ---------------------------------------------------------------------------
# Inline child models  (attached to HomePage via ParentalKey)
# ---------------------------------------------------------------------------

class HomePageFeatureBox(Orderable):
    """
    'Why Choose Us' grid — 4 boxes (Academic Program, Expert Faculty, etc.)
    """
    STYLE_CHOICES = [
        ('box1', 'Box 1 (top-left / light bg)'),
        ('box2', 'Box 2 (top-right / accent)'),
        ('box3', 'Box 3 (bottom-left / dark)'),
        ('box4', 'Box 4 (bottom-right / accent)'),
    ]
    page       = ParentalKey('HomePage', related_name='feature_boxes', on_delete=models.CASCADE)
    icon_image = CloudinaryImageField(upload_to='homepage/features/', blank=True, null=True,
                                      help_text='Icon image (e.g. choose3-icon1.png)')
    title      = models.CharField(max_length=120)
    description= models.TextField(max_length=300)
    link_url   = models.CharField(max_length=255, default='./course.html',
                                  help_text='URL the arrow-link points to')
    box_style  = models.CharField(max_length=10, choices=STYLE_CHOICES, default='box1')

    panels = [
        FieldPanel('box_style'),
        FieldPanel('icon_image'),
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('link_url'),
    ]

    class Meta(Orderable.Meta):
        verbose_name = 'Feature Box'


class HomePageAboutBullet(Orderable):
    """
    Tick-list items in the About section.
    """
    page = ParentalKey('HomePage', related_name='about_bullets', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    panels = [FieldPanel('text')]

    class Meta(Orderable.Meta):
        verbose_name = 'About Bullet Point'


class HomePageCourse(Orderable):
    """
    A single course card shown in the 'Explore Our Courses' section.
    Belongs to one or more tab categories (stored as a comma-separated string
    so the template can add CSS classes like `all design` etc.).
    """
    CATEGORY_CHOICES = [
        ('design',      'Design'),
        ('data-science','Data Science'),
        ('marketing',   'Marketing'),
        ('development', 'Development'),
    ]
    page          = ParentalKey('HomePage', related_name='courses', on_delete=models.CASCADE)
    image         = CloudinaryImageField(upload_to='homepage/courses/')
    lessons_count = models.PositiveIntegerField(default=8)
    students_count= models.PositiveIntegerField(default=70)
    title         = models.CharField(max_length=200)
    price         = models.DecimalField(max_digits=8, decimal_places=2)
    enroll_url    = models.CharField(max_length=255, default='./course.html')
    category      = models.CharField(
        max_length=40, choices=CATEGORY_CHOICES,
        help_text='Which tab this course appears under (it always appears in "All")'
    )
    # Modal popup content
    modal_description  = models.TextField(blank=True)
    modal_bullet_1     = models.CharField(max_length=200, blank=True)
    modal_bullet_2     = models.CharField(max_length=200, blank=True)
    modal_bullet_3     = models.CharField(max_length=200, blank=True)
    modal_extra_text   = models.TextField(blank=True)

    panels = [
        FieldPanel('category'),
        FieldPanel('image'),
        FieldPanel('title'),
        FieldPanel('price'),
        FieldPanel('lessons_count'),
        FieldPanel('students_count'),
        FieldPanel('enroll_url'),
        MultiFieldPanel([
            FieldPanel('modal_description'),
            FieldPanel('modal_bullet_1'),
            FieldPanel('modal_bullet_2'),
            FieldPanel('modal_bullet_3'),
            FieldPanel('modal_extra_text'),
        ], heading='Modal Popup Content'),
    ]

    class Meta(Orderable.Meta):
        verbose_name = 'Course'


class HomePageStat(Orderable):
    """
    Counter stats in the 'Benefits' section (95% Satisfied Students, etc.)
    """
    STYLE_CHOICES = [
        ('box1', 'Box 1'),
        ('box2', 'Box 2'),
        ('box3', 'Box 3'),
        ('box4', 'Box 4'),
    ]
    page       = ParentalKey('HomePage', related_name='stats', on_delete=models.CASCADE)
    number     = models.PositiveIntegerField(help_text='Counter end-value, e.g. 95')
    suffix     = models.CharField(max_length=5, default='+',
                                  help_text='Symbol after number, e.g. % or +')
    label      = models.CharField(max_length=80, help_text='e.g. Satisfied Students')
    box_style  = models.CharField(max_length=10, choices=STYLE_CHOICES, default='box1')

    panels = [
        FieldPanel('box_style'),
        FieldPanel('number'),
        FieldPanel('suffix'),
        FieldPanel('label'),
    ]

    class Meta(Orderable.Meta):
        verbose_name = 'Stat Counter'


class HomePageTestimonial(Orderable):
    """
    Student review carousel item.
    """
    page         = ParentalKey('HomePage', related_name='testimonials', on_delete=models.CASCADE)
    person_image = CloudinaryImageField(upload_to='homepage/testimonials/')
    review_text  = models.TextField(max_length=500)
    name         = models.CharField(max_length=100)
    role         = models.CharField(max_length=100, default='Happy Client')
    rating       = models.PositiveSmallIntegerField(default=5,
                       choices=[(i, f'{i} Stars') for i in range(1, 6)])

    panels = [
        FieldPanel('person_image'),
        FieldPanel('name'),
        FieldPanel('role'),
        FieldPanel('rating'),
        FieldPanel('review_text'),
    ]

    class Meta(Orderable.Meta):
        verbose_name = 'Testimonial'


class HomePageArticle(Orderable):
    """
    Blog post teaser in the 'Latest Blog Posts' carousel.
    """
    page        = ParentalKey('HomePage', related_name='articles', on_delete=models.CASCADE)
    image       = CloudinaryImageField(upload_to='homepage/articles/')
    date        = models.DateField()
    comment_count = models.PositiveIntegerField(default=0)
    title       = models.CharField(max_length=200)
    excerpt     = models.TextField(max_length=300)
    link_url    = models.CharField(max_length=255, default='single-blog.html')

    panels = [
        FieldPanel('image'),
        FieldPanel('date'),
        FieldPanel('comment_count'),
        FieldPanel('title'),
        FieldPanel('excerpt'),
        FieldPanel('link_url'),
    ]

    class Meta(Orderable.Meta):
        verbose_name = 'Blog Article'


class HomePageFooterUsefulLink(Orderable):
    """Footer > Useful Links column."""
    page  = ParentalKey('HomePage', related_name='footer_useful_links', on_delete=models.CASCADE)
    label = models.CharField(max_length=80)
    url   = models.CharField(max_length=255)

    panels = [FieldPanel('label'), FieldPanel('url')]
    class Meta(Orderable.Meta):
        verbose_name = 'Useful Link'


class HomePageFooterExploreLink(Orderable):
    """Footer > Explore column."""
    page  = ParentalKey('HomePage', related_name='footer_explore_links', on_delete=models.CASCADE)
    label = models.CharField(max_length=80)
    url   = models.CharField(max_length=255)

    panels = [FieldPanel('label'), FieldPanel('url')]
    class Meta(Orderable.Meta):
        verbose_name = 'Explore Link'


# ---------------------------------------------------------------------------
# Main Page Model
# ---------------------------------------------------------------------------

class HomePage(Page):
    """
    Wagtail Page model for homepage.html (Educiza Home 3 / index2.html).

    Template: templates/homepage.html
    """

    # ------------------------------------------------------------------
    # 1. NAVBAR
    # ------------------------------------------------------------------
    nav_logo        = CloudinaryImageField(upload_to='homepage/nav/',
                          help_text='Main navbar logo (logo.png)')
    nav_phone       = models.CharField(max_length=30, default='+5689 2589 6325')

    # ------------------------------------------------------------------
    # 2. BANNER
    # ------------------------------------------------------------------
    banner_logo_icon    = CloudinaryImageField(upload_to='homepage/banner/',
                              help_text='Small icon above banner heading (journey-logoicon.png)')
    banner_heading      = models.CharField(max_length=200,
                              default='Leading Global Program Premier University')
    banner_subtext      = models.TextField(max_length=400)
    banner_cta_text     = models.CharField(max_length=60, default='View Courses')
    banner_cta_url      = models.CharField(max_length=255, default='./course.html')
    # Decorative images (optional — can leave blank to use static originals)
    banner_left_top_curve   = CloudinaryImageField(upload_to='homepage/banner/', blank=True, null=True)
    banner_right_bottom_curve = CloudinaryImageField(upload_to='homepage/banner/', blank=True, null=True)
    banner_circle_image     = CloudinaryImageField(upload_to='homepage/banner/', blank=True, null=True)
    banner_cross_image      = CloudinaryImageField(upload_to='homepage/banner/', blank=True, null=True)
    banner_dropdown_image   = CloudinaryImageField(upload_to='homepage/banner/', blank=True, null=True)

    # ------------------------------------------------------------------
    # 3. CHOOSE / WHY US  (inline: feature_boxes)
    # ------------------------------------------------------------------
    choose_eyebrow      = models.CharField(max_length=80, default='Our Features')
    choose_heading      = models.CharField(max_length=200,
                              default='Why Choose Educiza University')
    choose_text1        = models.TextField(max_length=500)
    choose_text2        = models.TextField(max_length=500)
    choose_cta_text     = models.CharField(max_length=60, default='Get Started')
    choose_cta_url      = models.CharField(max_length=255, default='./course.html')

    # ------------------------------------------------------------------
    # 4. ABOUT
    # ------------------------------------------------------------------
    about_image1        = CloudinaryImageField(upload_to='homepage/about/',
                              help_text='Large left image (about3-image1.jpg)')
    about_image2        = CloudinaryImageField(upload_to='homepage/about/',
                              help_text='Smaller overlay image with play button (about3-image2.jpg)')
    about_video_url     = models.URLField(
                              default='https://video-previews.elements.envatousercontent.com/h264-video-previews/79b865eb-60f3-41d7-8240-5beebaa70664/11687174.mp4',
                              help_text='URL opened by the play-button popup')
    about_play_icon     = CloudinaryImageField(upload_to='homepage/about/', blank=True, null=True,
                              help_text='Play-button icon overlay (about3-playicon.png)')
    about_eyebrow       = models.CharField(max_length=80, default='About Us')
    about_heading       = models.CharField(max_length=200,
                              default='Cultivate Your Skills and Knowledge')
    about_text          = models.TextField(max_length=600)
    # about_bullets → inline (HomePageAboutBullet)
    about_mission_icon  = CloudinaryImageField(upload_to='homepage/about/', blank=True, null=True,
                              help_text='Icon inside the mission box (about3-icon.png)')
    about_mission_text  = models.CharField(max_length=200,
                              default='Our Mission is to Drive Knowledge and Innovation')

    # ------------------------------------------------------------------
    # 5. COURSES  (inline: courses)
    # ------------------------------------------------------------------
    courses_eyebrow     = models.CharField(max_length=80, default='Popular Courses')
    courses_heading     = models.CharField(max_length=200, default='Explore Our Courses')

    # ------------------------------------------------------------------
    # 6. BENEFITS (inline: stats)
    # ------------------------------------------------------------------
    benefits_eyebrow    = models.CharField(max_length=80, default='Our Expertise')
    benefits_heading    = models.CharField(max_length=200,
                              default='Benefits of Learning With Us')

    # ------------------------------------------------------------------
    # 7. JOURNEY CTA
    # ------------------------------------------------------------------
    journey_logo_icon   = CloudinaryImageField(upload_to='homepage/journey/', blank=True, null=True,
                              help_text='Small icon above journey heading')
    journey_eyebrow     = models.CharField(max_length=80, default='Duis Aute Irure')
    journey_heading     = models.CharField(max_length=200,
                              default='Empower Your Learning Journey with Our Expertise')
    journey_cta_text    = models.CharField(max_length=60, default='Get Started')
    journey_cta_url     = models.CharField(max_length=255, default='./contact.html')

    # ------------------------------------------------------------------
    # 8. TESTIMONIALS  (inline: testimonials)
    # ------------------------------------------------------------------
    testimonials_eyebrow    = models.CharField(max_length=80, default='Reviews')
    testimonials_heading    = models.CharField(max_length=200,
                                  default="Student's Say About Us")
    testimonial_quote_image = CloudinaryImageField(upload_to='homepage/testimonials/', blank=True, null=True,
                                  help_text='Quote icon shown at top of every testimonial card')

    # ------------------------------------------------------------------
    # 9. ARTICLES  (inline: articles)
    # ------------------------------------------------------------------
    articles_eyebrow    = models.CharField(max_length=80, default='News & Articles')
    articles_heading    = models.CharField(max_length=200, default='Latest Blog Posts')

    # ------------------------------------------------------------------
    # 10. FOOTER
    # ------------------------------------------------------------------
    footer_logo         = CloudinaryImageField(upload_to='homepage/footer/',
                              help_text='Footer logo (footer-logo.png)')
    footer_about_text   = models.TextField(max_length=500)
    # social_links → via SocialLink snippet (separate admin section)
    # footer_useful_links → inline
    # footer_explore_links → inline
    footer_phone        = models.CharField(max_length=30, default='+61 3 8376 6284')
    footer_email        = models.EmailField(default='info@educiza.com')
    footer_address      = models.TextField(max_length=300,
                              default='21 King Street Melbourne, 3000, Australia')
    footer_address_url  = models.URLField(blank=True,
                              help_text='Google Maps URL for the address link')
    footer_newsletter_label = models.CharField(max_length=100,
                              default='Sign up for the newsletter:')
    footer_copyright    = models.CharField(max_length=200,
                              default='Copyright 2025, educiza.com All Rights Reserved.')
    footer_right_image  = CloudinaryImageField(upload_to='homepage/footer/', blank=True, null=True,
                              help_text='Decorative right image (footer-rightimage.png)')

    # ------------------------------------------------------------------
    # Wagtail admin panels
    # ------------------------------------------------------------------

    navbar_panels = [
        MultiFieldPanel([
            FieldPanel('nav_logo'),
            FieldPanel('nav_phone'),
        ], heading='Navbar'),
    ]

    banner_panels = [
        MultiFieldPanel([
            FieldPanel('banner_logo_icon'),
            FieldPanel('banner_heading'),
            FieldPanel('banner_subtext'),
            FieldPanel('banner_cta_text'),
            FieldPanel('banner_cta_url'),
        ], heading='Banner Content'),
        MultiFieldPanel([
            FieldPanel('banner_left_top_curve'),
            FieldPanel('banner_right_bottom_curve'),
            FieldPanel('banner_circle_image'),
            FieldPanel('banner_cross_image'),
            FieldPanel('banner_dropdown_image'),
        ], heading='Banner Decorative Images (optional)'),
    ]

    choose_panels = [
        MultiFieldPanel([
            FieldPanel('choose_eyebrow'),
            FieldPanel('choose_heading'),
            FieldPanel('choose_text1'),
            FieldPanel('choose_text2'),
            FieldPanel('choose_cta_text'),
            FieldPanel('choose_cta_url'),
        ], heading='Section Text'),
        InlinePanel('feature_boxes', label='Feature Box', min_num=4, max_num=4),
    ]

    about_panels = [
        MultiFieldPanel([
            FieldPanel('about_image1'),
            FieldPanel('about_image2'),
            FieldPanel('about_video_url'),
            FieldPanel('about_play_icon'),
        ], heading='About Images & Video'),
        MultiFieldPanel([
            FieldPanel('about_eyebrow'),
            FieldPanel('about_heading'),
            FieldPanel('about_text'),
        ], heading='About Text'),
        InlinePanel('about_bullets', label='Bullet Point'),
        MultiFieldPanel([
            FieldPanel('about_mission_icon'),
            FieldPanel('about_mission_text'),
        ], heading='Mission Box'),
    ]

    courses_panels = [
        MultiFieldPanel([
            FieldPanel('courses_eyebrow'),
            FieldPanel('courses_heading'),
        ], heading='Section Heading'),
        InlinePanel('courses', label='Course'),
    ]

    benefits_panels = [
        MultiFieldPanel([
            FieldPanel('benefits_eyebrow'),
            FieldPanel('benefits_heading'),
        ], heading='Section Heading'),
        InlinePanel('stats', label='Stat Counter', min_num=4, max_num=4),
    ]

    journey_panels = [
        FieldPanel('journey_logo_icon'),
        FieldPanel('journey_eyebrow'),
        FieldPanel('journey_heading'),
        FieldPanel('journey_cta_text'),
        FieldPanel('journey_cta_url'),
    ]

    testimonials_panels = [
        MultiFieldPanel([
            FieldPanel('testimonials_eyebrow'),
            FieldPanel('testimonials_heading'),
            FieldPanel('testimonial_quote_image'),
        ], heading='Section Heading & Quote Icon'),
        InlinePanel('testimonials', label='Testimonial'),
    ]

    articles_panels = [
        MultiFieldPanel([
            FieldPanel('articles_eyebrow'),
            FieldPanel('articles_heading'),
        ], heading='Section Heading'),
        InlinePanel('articles', label='Blog Article'),
    ]

    footer_panels = [
        MultiFieldPanel([
            FieldPanel('footer_logo'),
            FieldPanel('footer_right_image'),
            FieldPanel('footer_newsletter_label'),
            FieldPanel('footer_copyright'),
        ], heading='Footer Branding'),
        MultiFieldPanel([
            FieldPanel('footer_about_text'),
        ], heading='About Column'),
        InlinePanel('footer_useful_links', label='Useful Link'),
        InlinePanel('footer_explore_links', label='Explore Link'),
        MultiFieldPanel([
            FieldPanel('footer_phone'),
            FieldPanel('footer_email'),
            FieldPanel('footer_address'),
            FieldPanel('footer_address_url'),
        ], heading='Contact Details'),
    ]

    # Tabbed interface in the Wagtail admin
    edit_handler = TabbedInterface([
        ObjectList(navbar_panels,       heading='Navbar'),
        ObjectList(banner_panels,       heading='Banner'),
        ObjectList(choose_panels,       heading='Why Choose Us'),
        ObjectList(about_panels,        heading='About'),
        ObjectList(courses_panels,      heading='Courses'),
        ObjectList(benefits_panels,     heading='Benefits / Stats'),
        ObjectList(journey_panels,      heading='Journey CTA'),
        ObjectList(testimonials_panels, heading='Testimonials'),
        ObjectList(articles_panels,     heading='Blog Articles'),
        ObjectList(footer_panels,       heading='Footer'),
        ObjectList(Page.promote_panels, heading='SEO / Promote'),
        ObjectList(Page.settings_panels,heading='Settings'),
    ])

    # Tells Wagtail which template to use
    template = 'homepage.html'

    class Meta:
        verbose_name        = 'Home Page'
        verbose_name_plural = 'Home Pages'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Pass social links snippet into context
        context['social_links'] = SocialLink.objects.all()

        # Group courses by category for the tab panels
        all_courses = self.courses.all()
        context['courses_all']          = all_courses
        context['courses_design']       = all_courses.filter(category='design')
        context['courses_data_science'] = all_courses.filter(category='data-science')
        context['courses_marketing']    = all_courses.filter(category='marketing')
        context['courses_development']  = all_courses.filter(category='development')

        return context
