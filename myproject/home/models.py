from django.db import models
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import (
    FieldPanel, InlinePanel, MultiFieldPanel, FieldRowPanel
)
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from modelcluster.fields import ParentalKey


# ──────────────────────────────────────────────
# STREAMFIELD BLOCKS
# ──────────────────────────────────────────────

class FeatureCardBlock(blocks.StructBlock):
    """Used in the Features section (University Life, Research, Athletics, Academics)"""
    icon = ImageChooserBlock()
    title = blocks.CharBlock(max_length=100)
    text = blocks.TextBlock()
    link_url = blocks.URLBlock(required=False)
    link_label = blocks.CharBlock(max_length=50, default="Learn More")

    class Meta:
        icon = "placeholder"
        label = "Feature Card"


class AboutFeatureBlock(blocks.StructBlock):
    """Two bullet features inside the About section"""
    icon = ImageChooserBlock()
    title = blocks.CharBlock(max_length=100)
    text = blocks.TextBlock()

    class Meta:
        icon = "tick"
        label = "About Feature"


class CounterCardBlock(blocks.StructBlock):
    """Stats counter cards (157+ Programs, 18,250 Faculty, etc.)"""
    icon = ImageChooserBlock()
    number = blocks.CharBlock(max_length=20, help_text="e.g. 157, 18,250, 48k")
    suffix = blocks.CharBlock(max_length=5, required=False, help_text="e.g. +, k")
    label = blocks.CharBlock(max_length=50)

    class Meta:
        icon = "order"
        label = "Counter Stat"


class ProgramCardBlock(blocks.StructBlock):
    """Academic program cards in the slider"""
    image = ImageChooserBlock()
    tag = blocks.CharBlock(max_length=50, help_text="e.g. Media, Science")
    title = blocks.CharBlock(max_length=200)
    rating = blocks.DecimalBlock(max_digits=3, decimal_places=1, help_text="e.g. 4.8")
    description = blocks.TextBlock()
    language = blocks.CharBlock(max_length=50)
    duration = blocks.CharBlock(max_length=50, help_text="e.g. 04 Years")
    link_url = blocks.URLBlock(required=False)

    class Meta:
        icon = "doc-full"
        label = "Program Card"


class TestimonialBlock(blocks.StructBlock):
    """Student story / testimonial cards"""
    photo = ImageChooserBlock()
    name = blocks.CharBlock(max_length=100)
    quote = blocks.TextBlock()
    profile_url = blocks.URLBlock(required=False)

    class Meta:
        icon = "user"
        label = "Student Testimonial"


class EventCardBlock(blocks.StructBlock):
    """Upcoming events"""
    image = ImageChooserBlock()
    day = blocks.CharBlock(max_length=2, help_text="e.g. 15")
    month = blocks.CharBlock(max_length=3, help_text="e.g. Aug")
    title = blocks.CharBlock(max_length=200)
    description = blocks.TextBlock()
    location = blocks.CharBlock(max_length=200)
    date = blocks.DateBlock()
    time_from = blocks.TimeBlock()
    time_to = blocks.TimeBlock()
    link_url = blocks.URLBlock(required=False)

    class Meta:
        icon = "date"
        label = "Event Card"


class FAQBlock(blocks.StructBlock):
    """FAQ accordion items"""
    question = blocks.CharBlock(max_length=300)
    answer = blocks.TextBlock()

    class Meta:
        icon = "help"
        label = "FAQ Item"


class SkillBarBlock(blocks.StructBlock):
    """Chancellor skill progress bars"""
    label = blocks.CharBlock(max_length=100)
    percentage = blocks.IntegerBlock(min_value=0, max_value=100)

    class Meta:
        icon = "bars"
        label = "Skill Bar"


class MarqueeItemBlock(blocks.StructBlock):
    """Scrolling marquee text items"""
    icon = ImageChooserBlock()
    text = blocks.CharBlock(max_length=50)
    link_url = blocks.URLBlock(required=False)

    class Meta:
        icon = "snippet"
        label = "Marquee Item"


class BlogPostBlock(blocks.StructBlock):
    """Blog/news cards shown on homepage"""
    image = ImageChooserBlock()
    category = blocks.CharBlock(max_length=100)
    date = blocks.DateBlock()
    title = blocks.CharBlock(max_length=300)
    author = blocks.CharBlock(max_length=100)
    link_url = blocks.URLBlock(required=False)

    class Meta:
        icon = "edit"
        label = "Blog Post Card"


class AdmissionChecklistBlock(blocks.StructBlock):
    """Two-column checklist in Apply section"""
    items_column_1 = blocks.ListBlock(blocks.CharBlock(max_length=100), label="Left Column Items")
    items_column_2 = blocks.ListBlock(blocks.CharBlock(max_length=100), label="Right Column Items")

    class Meta:
        icon = "list-ul"
        label = "Admission Checklist"


# ──────────────────────────────────────────────
# ORDERABLE INLINE MODELS
# ──────────────────────────────────────────────

class NavMenuItem(Orderable):
    """Top navigation menu items"""
    page = ParentalKey("HomePage", on_delete=models.CASCADE, related_name="nav_items")
    label = models.CharField(max_length=100)
    url = models.CharField(max_length=255, blank=True)

    panels = [
        FieldPanel("label"),
        FieldPanel("url"),
    ]


class SocialLink(Orderable):
    """Social media links used in sidemenu and footer"""
    page = ParentalKey("HomePage", on_delete=models.CASCADE, related_name="social_links")
    PLATFORM_CHOICES = [
        ("facebook", "Facebook"),
        ("twitter", "Twitter"),
        ("pinterest", "Pinterest"),
        ("linkedin", "LinkedIn"),
        ("instagram", "Instagram"),
        ("youtube", "YouTube"),
    ]
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url = models.URLField()

    panels = [
        FieldPanel("platform"),
        FieldPanel("url"),
    ]


class FooterLink(Orderable):
    """Footer bottom links (Privacy Policy, Terms, Disclaimer)"""
    page = ParentalKey("HomePage", on_delete=models.CASCADE, related_name="footer_links")
    label = models.CharField(max_length=100)
    url = models.CharField(max_length=255)

    panels = [
        FieldPanel("label"),
        FieldPanel("url"),
    ]


# ──────────────────────────────────────────────
# MAIN HOME PAGE MODEL
# ──────────────────────────────────────────────

class HomePage(Page):
    """
    Wagtail Page model for the University Homepage (index.html).

    Sections mapped:
      1. SEO / Meta
      2. Header & Navigation
      3. Hero / Banner
      4. Feature Cards
      5. About Section
      6. Counter Stats
      7. Academic Programs (slider)
      8. Student Stories / Testimonials
      9. Events
      10. Apply to Stadum CTA
      11. Chancellor Section
      12. Marquee Strip
      13. Community / Join CTA
      14. FAQ
      15. Blog Posts
      16. Footer
    """

    # ── 1. SEO ──────────────────────────────────
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=300, blank=True)

    # ── 2. Header ───────────────────────────────
    logo = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="logo_image"
    )
    logo_dark = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="logo_dark_image"
    )
    header_phone = models.CharField(max_length=30, blank=True)
    header_email = models.EmailField(blank=True)
    header_address = models.CharField(max_length=200, blank=True)

    # ── 3. Hero / Banner ────────────────────────
    hero_subtitle = models.CharField(max_length=200, blank=True, verbose_name="Hero Sub-label")
    hero_title = models.CharField(max_length=300, blank=True, verbose_name="Hero Headline")
    hero_description = models.TextField(blank=True, verbose_name="Hero Description")
    hero_btn1_label = models.CharField(max_length=50, blank=True, default="Explore Programs")
    hero_btn1_url = models.CharField(max_length=255, blank=True)
    hero_btn2_label = models.CharField(max_length=50, blank=True, default="Watch Video")
    hero_btn2_url = models.CharField(max_length=255, blank=True)
    hero_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="hero_main_image"
    )
    hero_small_image_1 = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="hero_small_img1"
    )
    hero_small_image_2 = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="hero_small_img2"
    )
    hero_badge_text = models.CharField(max_length=100, blank=True, help_text="e.g. '1996 EST * 25 Years Quality Teaching'")
    hero_established_year = models.CharField(max_length=10, blank=True, help_text="e.g. 1996")

    # ── 4. Feature Cards ────────────────────────
    features_section_title = models.CharField(max_length=200, blank=True)
    feature_cards = StreamField(
        [("feature_card", FeatureCardBlock())],
        blank=True, use_json_field=True
    )

    # ── 5. About Section ────────────────────────
    about_subtitle = models.CharField(max_length=100, blank=True)
    about_title = models.CharField(max_length=300, blank=True)
    about_description = models.TextField(blank=True)
    about_image_main = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="about_main"
    )
    about_image_2 = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="about_img2"
    )
    about_image_3 = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="about_img3"
    )
    about_features = StreamField(
        [("about_feature", AboutFeatureBlock())],
        blank=True, use_json_field=True, max_num=2
    )
    about_btn_label = models.CharField(max_length=50, blank=True, default="Learn More")
    about_btn_url = models.CharField(max_length=255, blank=True)

    # ── 6. Counter Stats ────────────────────────
    counter_stats = StreamField(
        [("counter", CounterCardBlock())],
        blank=True, use_json_field=True, max_num=4
    )

    # ── 7. Academic Programs ─────────────────────
    programs_subtitle = models.CharField(max_length=100, blank=True)
    programs_title = models.CharField(max_length=300, blank=True)
    programs_explore_url = models.CharField(max_length=255, blank=True)
    program_cards = StreamField(
        [("program", ProgramCardBlock())],
        blank=True, use_json_field=True
    )

    # ── 8. Student Stories ───────────────────────
    stories_subtitle = models.CharField(max_length=100, blank=True)
    stories_title = models.CharField(max_length=300, blank=True)
    testimonials = StreamField(
        [("testimonial", TestimonialBlock())],
        blank=True, use_json_field=True
    )

    # ── 9. Events ───────────────────────────────
    events_subtitle = models.CharField(max_length=100, blank=True)
    events_title = models.CharField(max_length=300, blank=True)
    events_explore_url = models.CharField(max_length=255, blank=True)
    events = StreamField(
        [("event", EventCardBlock())],
        blank=True, use_json_field=True
    )

    # ── 10. Apply CTA ───────────────────────────
    apply_subtitle = models.CharField(max_length=100, blank=True)
    apply_title = models.CharField(max_length=300, blank=True)
    apply_description = models.TextField(blank=True)
    apply_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="apply_image"
    )
    apply_checklist = StreamField(
        [("checklist", AdmissionChecklistBlock())],
        blank=True, use_json_field=True, max_num=1
    )
    apply_btn_label = models.CharField(max_length=50, blank=True, default="More About Admission")
    apply_btn_url = models.CharField(max_length=255, blank=True)

    # ── 11. Chancellor Section ──────────────────
    chancellor_subtitle = models.CharField(max_length=100, blank=True)
    chancellor_title = models.CharField(max_length=200, blank=True)
    chancellor_description = models.TextField(blank=True)
    chancellor_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="chancellor_photo"
    )
    chancellor_name = models.CharField(max_length=150, blank=True, help_text="e.g. Prof. Dr. Simons Doe, Ph.D")
    chancellor_signature = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="chancellor_sig"
    )
    chancellor_btn_label = models.CharField(max_length=50, blank=True, default="Lecturer at Faculty")
    chancellor_btn_url = models.CharField(max_length=255, blank=True)
    chancellor_skills = StreamField(
        [("skill_bar", SkillBarBlock())],
        blank=True, use_json_field=True
    )

    # ── 12. Marquee ─────────────────────────────
    marquee_items = StreamField(
        [("item", MarqueeItemBlock())],
        blank=True, use_json_field=True
    )

    # ── 13. Community CTA ───────────────────────
    community_subtitle = models.CharField(max_length=100, blank=True)
    community_title = models.CharField(max_length=300, blank=True)
    community_description = models.TextField(blank=True)
    community_bg_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="community_bg"
    )
    community_btn_label = models.CharField(max_length=50, blank=True, default="Join Community")
    community_btn_url = models.CharField(max_length=255, blank=True)

    # ── 14. FAQ ─────────────────────────────────
    faq_subtitle = models.CharField(max_length=100, blank=True)
    faq_title = models.CharField(max_length=200, blank=True)
    faq_description = models.TextField(blank=True)
    faq_image_1 = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="faq_img1"
    )
    faq_image_2 = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="faq_img2"
    )
    faq_image_3 = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="faq_img3"
    )
    faq_items = StreamField(
        [("faq", FAQBlock())],
        blank=True, use_json_field=True
    )

    # ── 15. Blog Posts ───────────────────────────
    blog_subtitle = models.CharField(max_length=100, blank=True)
    blog_title = models.CharField(max_length=300, blank=True)
    blog_explore_url = models.CharField(max_length=255, blank=True)
    blog_posts = StreamField(
        [("post", BlogPostBlock())],
        blank=True, use_json_field=True
    )

    # ── 16. Footer ───────────────────────────────
    footer_logo = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="footer_logo_img"
    )
    footer_about_text = models.TextField(blank=True)
    footer_address = models.CharField(max_length=200, blank=True)
    footer_email = models.EmailField(blank=True)
    footer_copyright_name = models.CharField(max_length=100, blank=True, default="Stadum")
    footer_copyright_year = models.CharField(max_length=10, blank=True, default="2025")

    # ──────────────────────────────────────────────
    # ADMIN PANELS
    # ──────────────────────────────────────────────

    content_panels = Page.content_panels + [

        MultiFieldPanel([
            FieldPanel("meta_description"),
            FieldPanel("meta_keywords"),
        ], heading="🔍 SEO / Meta"),

        MultiFieldPanel([
            FieldPanel("logo"),
            FieldPanel("logo_dark"),
            FieldPanel("header_phone"),
            FieldPanel("header_email"),
            FieldPanel("header_address"),
            InlinePanel("social_links", label="Social Media Links"),
        ], heading="🔗 Header & Branding"),

        MultiFieldPanel([
            FieldPanel("hero_subtitle"),
            FieldPanel("hero_title"),
            FieldPanel("hero_description"),
            FieldRowPanel([
                FieldPanel("hero_btn1_label"),
                FieldPanel("hero_btn1_url"),
            ]),
            FieldRowPanel([
                FieldPanel("hero_btn2_label"),
                FieldPanel("hero_btn2_url"),
            ]),
            FieldPanel("hero_image"),
            FieldPanel("hero_small_image_1"),
            FieldPanel("hero_small_image_2"),
            FieldPanel("hero_badge_text"),
            FieldPanel("hero_established_year"),
        ], heading="🎯 Hero / Banner Section"),

        MultiFieldPanel([
            FieldPanel("features_section_title"),
            FieldPanel("feature_cards"),
        ], heading="⭐ Feature Cards (University Life, Research…)"),

        MultiFieldPanel([
            FieldPanel("about_subtitle"),
            FieldPanel("about_title"),
            FieldPanel("about_description"),
            FieldPanel("about_image_main"),
            FieldPanel("about_image_2"),
            FieldPanel("about_image_3"),
            FieldPanel("about_features"),
            FieldRowPanel([
                FieldPanel("about_btn_label"),
                FieldPanel("about_btn_url"),
            ]),
        ], heading="🏛️ About Section"),

        MultiFieldPanel([
            FieldPanel("counter_stats"),
        ], heading="📊 Counter / Stats Bar"),

        MultiFieldPanel([
            FieldPanel("programs_subtitle"),
            FieldPanel("programs_title"),
            FieldPanel("programs_explore_url"),
            FieldPanel("program_cards"),
        ], heading="🎓 Academic Programs"),

        MultiFieldPanel([
            FieldPanel("stories_subtitle"),
            FieldPanel("stories_title"),
            FieldPanel("testimonials"),
        ], heading="💬 Student Stories / Testimonials"),

        MultiFieldPanel([
            FieldPanel("events_subtitle"),
            FieldPanel("events_title"),
            FieldPanel("events_explore_url"),
            FieldPanel("events"),
        ], heading="📅 Events"),

        MultiFieldPanel([
            FieldPanel("apply_subtitle"),
            FieldPanel("apply_title"),
            FieldPanel("apply_description"),
            FieldPanel("apply_image"),
            FieldPanel("apply_checklist"),
            FieldRowPanel([
                FieldPanel("apply_btn_label"),
                FieldPanel("apply_btn_url"),
            ]),
        ], heading="📋 Apply to Stadum CTA"),

        MultiFieldPanel([
            FieldPanel("chancellor_subtitle"),
            FieldPanel("chancellor_title"),
            FieldPanel("chancellor_description"),
            FieldPanel("chancellor_image"),
            FieldPanel("chancellor_name"),
            FieldPanel("chancellor_signature"),
            FieldPanel("chancellor_skills"),
            FieldRowPanel([
                FieldPanel("chancellor_btn_label"),
                FieldPanel("chancellor_btn_url"),
            ]),
        ], heading="👨‍🏫 Chancellor Section"),

        MultiFieldPanel([
            FieldPanel("marquee_items"),
        ], heading="🔄 Marquee Strip"),

        MultiFieldPanel([
            FieldPanel("community_subtitle"),
            FieldPanel("community_title"),
            FieldPanel("community_description"),
            FieldPanel("community_bg_image"),
            FieldRowPanel([
                FieldPanel("community_btn_label"),
                FieldPanel("community_btn_url"),
            ]),
        ], heading="🤝 Community / Join CTA"),

        MultiFieldPanel([
            FieldPanel("faq_subtitle"),
            FieldPanel("faq_title"),
            FieldPanel("faq_description"),
            FieldPanel("faq_image_1"),
            FieldPanel("faq_image_2"),
            FieldPanel("faq_image_3"),
            FieldPanel("faq_items"),
        ], heading="❓ FAQ Section"),

        MultiFieldPanel([
            FieldPanel("blog_subtitle"),
            FieldPanel("blog_title"),
            FieldPanel("blog_explore_url"),
            FieldPanel("blog_posts"),
        ], heading="📰 Blog / News Section"),

        MultiFieldPanel([
            FieldPanel("footer_logo"),
            FieldPanel("footer_about_text"),
            FieldPanel("footer_address"),
            FieldPanel("footer_email"),
            FieldPanel("footer_copyright_name"),
            FieldPanel("footer_copyright_year"),
            InlinePanel("footer_links", label="Footer Bottom Links"),
        ], heading="🦶 Footer"),
    ]

    class Meta:
        verbose_name = "Home Page"