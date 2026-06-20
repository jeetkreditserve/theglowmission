from __future__ import annotations

import os
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from apps.common.image_variants import ensure_image_variants
from apps.campaigns.models import CampaignForm, CampaignFormField
from apps.content.models import BrandSettings, FAQ, GalleryImage, HeroSlide, Page, PageSection, Service, SiteNavigationItem, Testimonial


BRAND_STORY = (
    "The Glow Mission is a boutique facial wellness studio built around natural care, calm touch, "
    "and skin that looks quietly refreshed. The practice carries forward a mother's cosmetology wisdom: "
    "simple ingredients, consistent massage, facial movement, and patient hands. Every ritual is designed "
    "to soften visible fatigue, release facial tension, and give you a protected stretch of time to feel cared for."
)

RITUAL_SERVICES = [
    {
        "title": "The Face Lift Ritual",
        "slug": "the-face-lift-ritual",
        "short_description": "A quick sculpting ritual to lift, refresh, and energise the skin.",
        "description": "A focused 40-minute ritual for facial tension, visible fatigue, and a naturally lifted look through restorative massage, gua sha, cooling therapy, and a nourishing glow pack.",
        "duration": "40 MINS",
        "price_amount": 3599,
        "price_note": "Hero ingredients: Milk, Aloe Vera, Multani Mitti",
        "inclusions": [
            "Gentle Skin Cleanse",
            "Lifting & Restorative Face Massage",
            "Gua Sha Sculpt Massage",
            "Fine-Line Ice Roller Therapy",
            "Nourishing Glow Pack",
        ],
        "ordering": 0,
        "asset_candidates": ["glow-service-face-yoga.webp", "glow-service-face-yoga.png", "glow-gallery-massage-detail.webp"],
    },
    {
        "title": "The Glow Cleanse",
        "slug": "the-glow-cleanse",
        "short_description": "A comforting reset to refresh, soften, and awaken tired skin.",
        "description": "A soft cleansing ritual for dullness and tired skin, with breathwork, relaxation touch, warm steam, exfoliation massage, facial uplift, cooling therapy, and a nourishing glow pack.",
        "duration": "45 MINS",
        "price_amount": 4999,
        "price_note": "Hero ingredients: Banana, Milk, Honey",
        "inclusions": [
            "Grounding Breathwork",
            "Head & Feet Relaxation Touch",
            "Gentle Skin Cleanse",
            "Warm Steam Therapy",
            "Glow Polish Exfoliation Massage",
            "Facial Uplift & Calming Massage",
            "Fine-Line Ice Roller Therapy",
            "Nourishing Glow Pack",
        ],
        "ordering": 1,
        "asset_candidates": ["glow-service-natural-facial.webp", "glow-gallery-botanicals.webp", "glow-service-natural-facial.png"],
    },
    {
        "title": "The Occasion Glow Ritual",
        "slug": "the-occasion-glow-ritual",
        "short_description": "A brightening ritual for special moments and naturally radiant skin.",
        "description": "A radiance-focused ritual for occasions, photographs, and important days, combining relaxation touch, under-eye cooling, steam, brightening exfoliation, calming massage, radiance pack, and gua sha sculpting.",
        "duration": "55 MINS",
        "price_amount": 5999,
        "price_note": "Hero ingredients: Papaya, Orange, Aloe Vera",
        "inclusions": [
            "Grounding Breathwork",
            "Hands & Feet Relaxation Touch",
            "Under-Eye Ice Cloth Therapy",
            "Gentle Skin Cleanse",
            "Warm Steam Therapy",
            "Brightening Exfoliation Massage",
            "Uplift & Calming Massage",
            "Radiance Glow Pack",
            "Gua Sha Sculpting Lift",
        ],
        "ordering": 2,
        "asset_candidates": ["glow-gallery-post-treatment.webp", "glow-hero-offer.webp", "glow-mission-post-1.png"],
    },
    {
        "title": "The Rest & Reset Ritual",
        "slug": "the-rest-reset-ritual",
        "short_description": "A deeper restorative ritual to calm the skin and bring back a rested glow.",
        "description": "A longer restorative ritual for tired skin and a tired nervous system, with grounding breathwork, relaxation touch, steam, skin renewal, nourishment, facial uplift, light therapy, and a restorative glow pack.",
        "duration": "75 MINS",
        "price_amount": 7999,
        "price_note": "Hero ingredients: Papaya, Aloe Vera, Banana",
        "inclusions": [
            "Grounding Breathwork",
            "Head & Feet Relaxation Touch",
            "Gentle Skin Cleanse",
            "Warm Steam Therapy",
            "Skin Renewal Exfoliation",
            "Resting Nourishment Mask",
            "Uplift & Calming Massage",
            "Glow-Boost Light Therapy",
            "Restorative Glow Pack",
        ],
        "ordering": 3,
        "asset_candidates": ["glow-gallery-warm-towel.webp", "glow-gallery-treatment-room.webp", "glow-about-story.png"],
    },
    {
        "title": "The Glow Mission Signature",
        "slug": "the-glow-mission-signature",
        "short_description": "A complete signature ritual for lifting, sculpting, glow, and deep renewal.",
        "description": "The complete Glow Mission experience, designed for clients who want lifting, sculpting, radiance, and deep renewal through massage, gua sha, light therapy, cooling eye care, and a signature glow pack.",
        "duration": "95 MINS",
        "price_amount": 8999,
        "price_note": "Hero ingredients: Saffron, Honey, Aloe Vera",
        "inclusions": [
            "Grounding Breathwork",
            "Head & Feet Relaxation Touch",
            "Gentle Skin Cleanse",
            "Warm Steam Therapy",
            "Glow Polish Exfoliation",
            "Uplift & Relaxing Face Massage",
            "Gua Sha Sculpt Massage",
            "Glow-Boost Light Therapy",
            "Cooling Eye Therapy",
            "Signature Glow Pack",
        ],
        "ordering": 4,
        "asset_candidates": ["glow-service-signature.webp", "glow-service-signature.png", "glow-gallery-massage-detail.webp"],
    },
]

RITUAL_NAMES = [service["title"] for service in RITUAL_SERVICES]
OLD_PLACEHOLDER_SERVICE_SLUGS = ["signature-glow-ritual", "face-yoga-lift", "natural-ingredient-facial"]


class Command(BaseCommand):
    help = "Seed The Glow Mission CMS content and upload provided brand assets to S3."

    def handle(self, *args, **options):
        self.create_admin_user()
        brand = self.seed_brand()
        self.seed_navigation()
        self.seed_pages()
        campaign = self.seed_campaign()
        complimentary_campaign = self.seed_complimentary_campaign()
        self.seed_hero_slides(campaign, complimentary_campaign)
        self.seed_services(campaign)
        self.seed_supporting_content()
        self.stdout.write(self.style.SUCCESS(f"Seeded CMS content for {brand.site_title}."))

    def create_admin_user(self):
        email = os.environ.get("ADMIN_EMAIL", "admin@theglowmission.local")
        password = os.environ.get("ADMIN_PASSWORD")
        if not password:
            raise CommandError("ADMIN_PASSWORD must be set before seeding the CMS admin user.")

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=email,
            defaults={"email": email, "is_staff": True, "is_superuser": True},
        )
        if created:
            user.set_password(password)
            user.save()
        else:
            changed = False
            if user.email != email:
                user.email = email
                changed = True
            if not user.is_staff or not user.is_superuser:
                user.is_staff = True
                user.is_superuser = True
                changed = True
            if changed:
                user.save()

    def seed_brand(self):
        brand, _ = BrandSettings.objects.get_or_create(pk=1)
        brand.site_title = "The Glow Mission"
        brand.tagline = "Natural facial rituals for a softer, calmer glow."
        brand.essence = "A boutique spa wellness experience for rested skin, lifted-feeling features, and a quieter mind."
        brand.mission_statement = BRAND_STORY
        brand.primary_color = "#C9A46A"
        brand.background_color = "#FBF4EA"
        brand.surface_color = "#F4E7D8"
        brand.muted_color = "#BBA08E"
        brand.accent_color = "#D8C7A4"
        brand.text_color = "#251D18"
        brand.heading_font = "Cormorant Garamond"
        brand.body_font = "Montserrat"
        brand.cta_style = {"radius": "2px", "case": "uppercase", "tracking": "0.12em"}
        brand.contact_email = "hello@theglowmission.com"
        brand.instagram_handle = "@theglowmission"
        brand.social_links = {"instagram": "https://instagram.com/theglowmission"}

        self.attach_seed_image(brand, "logo_image", "glow-mission-logo-3d.png", "glow-mission-logo-3d.png")
        self.attach_seed_image(brand, "favicon", "glow-mission-logo-3d.png", "glow-mission-favicon.png")
        brand.save()
        return brand

    def attach_seed_image(self, instance, field_name: str, filename: str | list[str], storage_name: str, *, force: bool = False):
        field = getattr(instance, field_name)
        if field and not force:
            ensure_image_variants(field)
            return
        filenames = filename if isinstance(filename, list) else [filename]
        source = None
        for candidate in filenames:
            path = Path(settings.BASE_DIR) / "seed_assets" / candidate
            if path.exists():
                source = path
                break
        if source is None:
            raise CommandError(f"Missing seed asset. Tried: {', '.join(filenames)}")
        with source.open("rb") as handle:
            field.save(storage_name, File(handle), save=False)
        ensure_image_variants(field)

    def seed_navigation(self):
        SiteNavigationItem.objects.filter(label__iexact="Services").delete()
        SiteNavigationItem.objects.filter(url="/services").delete()

        items = [
            ("Home", "/", SiteNavigationItem.Placement.HEADER, SiteNavigationItem.Style.LINK, 0),
            ("Glow Rituals", "/glow-rituals", SiteNavigationItem.Placement.HEADER, SiteNavigationItem.Style.LINK, 1),
            ("About", "/about", SiteNavigationItem.Placement.HEADER, SiteNavigationItem.Style.LINK, 2),
            ("Gallery", "/gallery", SiteNavigationItem.Placement.HEADER, SiteNavigationItem.Style.LINK, 3),
            ("Contact", "/contact", SiteNavigationItem.Placement.HEADER, SiteNavigationItem.Style.LINK, 4),
            ("Book", "/campaigns/glow-consultation", SiteNavigationItem.Placement.HEADER_CTA, SiteNavigationItem.Style.PRIMARY, 0),
            ("Glow Rituals", "/glow-rituals", SiteNavigationItem.Placement.FOOTER, SiteNavigationItem.Style.LINK, 0),
            ("About", "/about", SiteNavigationItem.Placement.FOOTER, SiteNavigationItem.Style.LINK, 1),
            ("Gallery", "/gallery", SiteNavigationItem.Placement.FOOTER, SiteNavigationItem.Style.LINK, 2),
            ("Contact", "/contact", SiteNavigationItem.Placement.FOOTER, SiteNavigationItem.Style.LINK, 3),
            ("Book a consultation", "/campaigns/glow-consultation", SiteNavigationItem.Placement.FOOTER_CTA, SiteNavigationItem.Style.SECONDARY, 0),
            ("Instagram", "https://instagram.com/theglowmission", SiteNavigationItem.Placement.SOCIAL, SiteNavigationItem.Style.LINK, 0),
        ]
        for label, url, placement, style, ordering in items:
            SiteNavigationItem.objects.update_or_create(
                label=label,
                placement=placement,
                defaults={"url": url, "style": style, "ordering": ordering, "active": True, "open_in_new_tab": url.startswith("http")},
            )

    def seed_pages(self):
        Page.objects.filter(slug="services").delete()

        pages = [
            ("Home", "home", 0),
            ("About", "about", 1),
            ("Glow Rituals", "glow-rituals", 2),
            ("Gallery", "gallery", 3),
            ("Contact", "contact", 4),
        ]
        for title, slug, ordering in pages:
            Page.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "status": Page.Status.PUBLISHED,
                    "ordering": ordering,
                    "seo_title": f"{title} | The Glow Mission",
                    "seo_description": "Luxury natural facial rituals, sculpting massage, botanical care, and deeply restful glow treatments at The Glow Mission.",
                },
            )

        home = Page.objects.get(slug="home")
        sections = [
            {
                "section_type": PageSection.SectionType.HERO,
                "title": "Natural facial rituals for a softer, calmer glow.",
                "subtitle": "A premium spa wellness experience shaped by facial massage, sculpting touch, and botanical care.",
                "body": "Choose a 40 to 95 minute ritual and leave feeling rested, lifted, and beautifully looked after.",
                "cta_label": "Book a consultation",
                "cta_url": "/campaigns/glow-consultation",
                "ordering": 0,
                "config": {"visual": "luxury-editorial-spa"},
            },
            {
                "section_type": PageSection.SectionType.SERVICES,
                "title": "Rituals designed around touch, tension, and visible radiance",
                "subtitle": "Sculpting massage, glow packs, botanical textures, and slow restorative care.",
                "body": "Choose from five real glow rituals ranging from ₹3,599 to ₹8,999 and 40 to 95 minutes. Each treatment is shaped around your skin comfort, facial tension, and the way you want to feel when you leave.",
                "cta_label": "Explore glow rituals",
                "cta_url": "/glow-rituals",
                "ordering": 1,
                "eyebrow": "Glow Rituals",
            },
            {
                "section_type": PageSection.SectionType.STORY,
                "title": "A legacy carried forward",
                "subtitle": "Inspired by a mother's wisdom in cosmetology and natural care.",
                "body": BRAND_STORY,
                "cta_label": "Read our story",
                "cta_url": "/about",
                "ordering": 2,
                "eyebrow": "Founder-led care",
                "media_alt": "Natural facial ritual tools prepared with oils, towels, and botanical textures",
                "asset_candidates": ["glow-gallery-still-life.webp", "glow-gallery-warm-towel.webp"],
                "force_asset": True,
            },
            {
                "section_type": PageSection.SectionType.GALLERY,
                "title": "A slower kind of beauty ritual",
                "subtitle": "Champagne warmth, ivory linens, botanicals, and calm hands.",
                "body": "Every visual touchpoint should feel like the treatment itself: warm, refined, natural, and deeply restful.",
                "cta_label": "View gallery",
                "cta_url": "/gallery",
                "ordering": 3,
                "eyebrow": "In the studio",
            },
        ]
        for section in sections:
            asset_candidates = section.pop("asset_candidates", None)
            force_asset = section.pop("force_asset", False)
            item, _ = PageSection.objects.update_or_create(
                page=home,
                section_type=section["section_type"],
                ordering=section["ordering"],
                defaults=section,
            )
            if asset_candidates:
                self.attach_seed_image(item, "media", asset_candidates, f"home-section-{item.ordering}.webp", force=force_asset)
                item.save()

        self.seed_page_sections()

    def seed_page_sections(self):
        page_sections = {
            "about": [
                {
                    "section_type": PageSection.SectionType.HERO,
                    "ordering": 0,
                    "eyebrow": "Our story",
                    "title": "A boutique ritual shaped by natural care, calm touch, and patient hands.",
                    "subtitle": "The Glow Mission is founder-led in spirit: personal, warm, and built around one careful hour of facial wellness.",
                    "body": BRAND_STORY,
                    "cta_label": "Book a consultation",
                    "cta_url": "/campaigns/glow-consultation",
                    "media_alt": "Natural facial ritual tools arranged with oils, towels, and botanical textures",
                    "asset_candidates": ["glow-gallery-still-life.webp", "glow-gallery-warm-towel.webp"],
                    "force_asset": True,
                },
                {
                    "section_type": PageSection.SectionType.RICH_TEXT,
                    "ordering": 1,
                    "eyebrow": "Why it feels different",
                    "title": "A slower, softer approach to visible radiance.",
                    "body": "The experience is intentionally hands-on and unhurried. Gentle massage, facial movement, natural textures, warm compresses, and attentive conversation come together to help your face feel lighter and your skin feel cared for.",
                    "cta_label": "Explore glow rituals",
                    "cta_url": "/glow-rituals",
                },
            ],
            "glow-rituals": [
                {
                    "section_type": PageSection.SectionType.HERO,
                    "ordering": 0,
                    "eyebrow": "Glow Rituals",
                    "title": "Choose the way you want to feel after one quiet ritual.",
                    "subtitle": "Rested, lifted, brighter, softer, or simply cared for.",
                    "body": "Each glow ritual is shaped around natural facial massage, sculpting touch, botanical textures, and your comfort on the day.",
                    "cta_label": "Book a consultation",
                    "cta_url": "/campaigns/glow-consultation",
                    "media_alt": "Luxury facial massage ritual with warm spa lighting",
                    "asset_candidates": ["glow-hero-signature.webp", "glow-hero-facial-massage.png"],
                },
                {
                    "section_type": PageSection.SectionType.SERVICES,
                    "ordering": 1,
                    "eyebrow": "Treatment menu",
                    "title": "Five natural facial rituals, priced clearly and easy to book.",
                    "body": "Rituals range from ₹3,599 to ₹8,999 and 40 to 95 minutes, from a quick sculpting lift to the complete Glow Mission Signature.",
                },
                {
                    "section_type": PageSection.SectionType.FAQS,
                    "ordering": 2,
                    "eyebrow": "Before you book",
                    "title": "Questions before your first glow ritual",
                    "subtitle": "Simple answers for choosing the right session.",
                },
            ],
            "gallery": [
                {
                    "section_type": PageSection.SectionType.HERO,
                    "ordering": 0,
                    "eyebrow": "Gallery",
                    "title": "The visual language of a slower glow ritual.",
                    "subtitle": "Ivory linens, warm towels, botanical textures, and quiet treatment room details.",
                    "body": "Every image is selected to feel like the ritual itself: warm, refined, natural, and deeply restful.",
                },
                {
                    "section_type": PageSection.SectionType.GALLERY,
                    "ordering": 1,
                    "eyebrow": "In the studio",
                    "title": "A calm look inside The Glow Mission",
                    "body": "Browse the textures, treatment details, and quiet moments that shape the experience.",
                },
            ],
            "contact": [
                {
                    "section_type": PageSection.SectionType.HERO,
                    "ordering": 0,
                    "eyebrow": "Contact",
                    "title": "Begin with the ritual your skin is asking for.",
                    "subtitle": "Tell us what you want to feel: rested, lifted, brighter, softer, or simply cared for.",
                    "body": "We will guide you toward the right glow ritual, offer, or consultation based on your goals and comfort.",
                    "cta_label": "Book a consultation",
                    "cta_url": "/campaigns/glow-consultation",
                    "media_alt": "Premium glow consultation setup with towels, oils, and natural spa tools",
                    "asset_candidates": ["glow-consultation.webp", "glow-hero-offer.webp"],
                },
                {
                    "section_type": PageSection.SectionType.RICH_TEXT,
                    "ordering": 1,
                    "layout_variant": "contact_details",
                    "eyebrow": "Reach out",
                    "title": "Tell us what your skin and face need next.",
                    "body": "Share your goal, preferred time, and any sensitivities. The first conversation is calm, practical, and personal.",
                },
                {
                    "section_type": PageSection.SectionType.CTA,
                    "ordering": 2,
                    "eyebrow": "Personal guidance",
                    "title": "Not sure which glow ritual to choose?",
                    "body": "Begin with a consultation request and share what your skin and face have been asking for. We will help you choose the calmest next step.",
                    "cta_label": "Request my consultation",
                    "cta_url": "/campaigns/glow-consultation",
                },
            ],
        }

        for slug, sections in page_sections.items():
            page = Page.objects.get(slug=slug)
            PageSection.objects.filter(page=page, section_type=PageSection.SectionType.RICH_TEXT, ordering=0, title=page.title).update(active=False)
            for section in sections:
                asset_candidates = section.pop("asset_candidates", None)
                force_asset = section.pop("force_asset", False)
                item, _ = PageSection.objects.update_or_create(
                    page=page,
                    section_type=section["section_type"],
                    ordering=section["ordering"],
                    defaults={**section, "active": True},
                )
                if asset_candidates:
                    self.attach_seed_image(item, "media", asset_candidates, f"{slug}-section-{item.ordering}.webp", force=force_asset)
                    item.save()

    def seed_hero_slides(self, campaign: CampaignForm, complimentary_campaign: CampaignForm):
        slides = [
            {
                "title": "Natural facial rituals for a softer, calmer glow.",
                "subtitle": "Facial massage, sculpting touch, and botanical care from 40 to 95 minutes.",
                "body": "A luxury spa wellness experience for rested skin, softened tension, and quiet confidence.",
                "offer_label": "Signature consultation",
                "primary_cta_label": "Book a consultation",
                "primary_cta_url": f"/campaigns/{campaign.slug}",
                "secondary_cta_label": "Explore rituals",
                "secondary_cta_url": "/glow-rituals",
                "ordering": 0,
                "image_alt": "Luxury facial massage ritual in a calm boutique spa setting",
                "asset_candidates": ["glow-hero-signature.webp", "glow-hero-facial-massage.png", "glow-mission-post-1.png"],
                "linked_campaign": campaign,
            },
            {
                "title": "Limited free glow sessions for new clients.",
                "subtitle": "A soft launch invitation for first-time clients who want to experience natural facial care.",
                "body": "Claim a consultation-led glow session and discover the ritual that suits your skin, tension, and pace.",
                "offer_label": "Launch offer",
                "primary_cta_label": "Claim the offer",
                "primary_cta_url": f"/campaigns/{complimentary_campaign.slug}",
                "secondary_cta_label": "See treatment menu",
                "secondary_cta_url": "/glow-rituals",
                "ordering": 1,
                "image_alt": "Premium spa consultation setting for a limited glow session offer",
                "asset_candidates": ["glow-hero-offer.webp", "glow-hero-offer.png", "glow-mission-post-1.png"],
                "linked_campaign": complimentary_campaign,
            },
            {
                "title": "A sculpted lift in 40 calm minutes.",
                "subtitle": "The Face Lift Ritual refreshes tired skin with restorative massage, gua sha, and cooling therapy.",
                "body": "A focused sculpting ritual for a lifted, energised look when your face needs a quick reset.",
                "offer_label": "The Face Lift Ritual",
                "primary_cta_label": "Book the ritual",
                "primary_cta_url": f"/campaigns/{campaign.slug}",
                "secondary_cta_label": "View ritual menu",
                "secondary_cta_url": "/glow-rituals",
                "ordering": 2,
                "image_alt": "The Face Lift Ritual in a calm boutique spa setting",
                "asset_candidates": ["glow-hero-face-yoga.webp", "glow-service-face-yoga.png", "glow-mission-post-1.png"],
                "linked_campaign": campaign,
            },
        ]
        for slide in slides:
            asset_candidates = slide.pop("asset_candidates")
            linked_campaign = slide.pop("linked_campaign")
            item, _ = HeroSlide.objects.update_or_create(
                ordering=slide["ordering"],
                defaults={**slide, "active": True, "linked_campaign": linked_campaign, "schedule_enabled": False, "starts_at": None, "ends_at": None},
            )
            self.attach_seed_image(item, "image", asset_candidates, f"hero-slide-{item.ordering}.png")
            item.save()

    def seed_services(self, campaign: CampaignForm):
        Service.objects.filter(slug__in=OLD_PLACEHOLDER_SERVICE_SLUGS).update(active=False)

        for service in RITUAL_SERVICES:
            asset_candidates = service["asset_candidates"]
            service_data = {key: value for key, value in service.items() if key != "asset_candidates"}
            item, _ = Service.objects.update_or_create(
                slug=service["slug"],
                defaults={
                    **service_data,
                    "image_alt": f"{service['title']} treatment at The Glow Mission",
                    "currency": "INR",
                    "sale_price_amount": None,
                    "discount_label": "",
                    "featured": False,
                    "session_count": 1,
                    "cta_label": "Book this ritual",
                    "cta_url": f"/campaigns/{campaign.slug}",
                    "booking_campaign": campaign,
                    "active": True,
                },
            )
            self.attach_seed_image(item, "image", asset_candidates, f"{item.slug}.webp")
            item.save()

    def seed_supporting_content(self):
        faqs = [
            ("What is The Glow Mission?", "The Glow Mission is a boutique facial wellness studio focused on natural facial massage, sculpting touch, botanical textures, glow packs, and slow restorative care."),
            ("How long is a session?", "Glow rituals range from 40 to 95 minutes, with enough time for calm preparation, skin work, massage, and a slow finish."),
            ("Is this a medical facial?", "No. The Glow Mission is a wellness and beauty ritual experience, not a medical dermatology service or clinical skin procedure."),
            ("What should I book for my first visit?", "If you want a quick sculpting reset, choose The Face Lift Ritual. If you want the complete experience, choose The Glow Mission Signature."),
            ("Can I book a launch offer or free session?", "Yes. When a launch offer is available, you can request it through the featured consultation form and we will confirm availability."),
            ("Do you use harsh peels or machines?", "The current approach is hands-on and gentle: massage, facial movement, natural textures, compresses, and calming skin care."),
            ("What do the rituals cost?", "The current ritual menu ranges from ₹3,599 to ₹8,999, depending on duration, flow, and depth of care."),
            ("Can prices or offers change?", "Yes. Seasonal rituals, introductory prices, and limited offers may change over time. The current ritual menu will show the latest available details."),
            ("Can I choose a treatment later?", "Yes. You can submit a consultation form first and choose the right ritual after discussing your goals and comfort level."),
            ("What skin concerns can I mention?", "You can mention dullness, dryness, tension, puffiness, uneven texture, fatigue, or simply that you want a calmer glow."),
            ("What happens after I submit a consultation request?", "Your request is reviewed and you will be guided toward the ritual, time, or offer that best fits your skin goals and schedule."),
            ("Will my treatment be customized?", "Every session should be adjusted around comfort, skin feel, time, and the kind of result you want from that visit."),
            ("How should I prepare?", "Arrive with minimal makeup if possible, share any sensitivities, and give yourself a little time after the session before rushing back into the day."),
        ]
        for ordering, (question, answer) in enumerate(faqs):
            FAQ.objects.update_or_create(question=question, defaults={"answer": answer, "active": True, "ordering": ordering})

        testimonials = [
            ("Anonymous client note", "The ritual felt calm and personal. My skin looked rested and my face felt lighter.", "First glow ritual"),
            ("Anonymous client note", "The whole experience felt gentle, intentional, and beautifully put together.", "Glow ritual feedback"),
            ("Anonymous client note", "It felt like a beauty treatment and a reset at the same time. The massage was the best part.", "Wellness feedback"),
        ]
        Testimonial.objects.filter(name__in=["A softer kind of glow", "Care you can feel", "The pause I needed"]).update(active=False)
        for ordering, (name, quote, role) in enumerate(testimonials):
            Testimonial.objects.update_or_create(
                name=f"{name} {ordering + 1}",
                defaults={"quote": quote, "role": role, "is_anonymized": True, "active": True, "ordering": ordering},
            )

        gallery_items = [
            ("Treatment room calm", "Prepared boutique spa treatment bed with ivory linens", "A quiet room prepared for slow facial care.", 0, ["glow-gallery-treatment-room.webp", "glow-about-story.png"]),
            ("Warm towel ritual", "Warm towel compress prepared for a facial ritual", "Soft towels, warm hands, and a slower pace.", 1, ["glow-gallery-warm-towel.webp", "glow-mission-post-1.png"]),
            ("Signature massage detail", "Luxury facial massage treatment detail", "A quiet hour of massage, touch, and rest.", 2, ["glow-gallery-massage-detail.webp", "glow-service-signature.png"]),
            ("Botanical ritual textures", "Natural facial ingredients prepared in ceramic bowls", "Honey, cucumber, citrus, herbs, and warm towels for a sensory ritual.", 3, ["glow-gallery-botanicals.webp", "glow-service-natural-facial.png"]),
            ("Post-treatment glow", "Rested client after a natural facial ritual", "Skin that feels rested, soft, and cared for.", 4, ["glow-gallery-post-treatment.webp", "glow-mission-post-1.png"]),
            ("Quiet spa still life", "Elegant spa still life with natural care tools", "A personal practice shaped by care, consistency, and gentle hands.", 5, ["glow-gallery-still-life.webp", "glow-about-story.png"]),
        ]
        for title, alt_text, caption, ordering, assets in gallery_items:
            gallery, _ = GalleryImage.objects.update_or_create(
                title=title,
                defaults={"alt_text": alt_text, "caption": caption, "active": True, "ordering": ordering},
            )
            self.attach_seed_image(gallery, "image", assets, f"gallery-{ordering}.png")
            gallery.save()

    def seed_campaign(self):
        form, _ = CampaignForm.objects.update_or_create(
            slug="glow-consultation",
            defaults={
                "title": "Glow Consultation",
                "status": CampaignForm.Status.PUBLISHED,
                "summary": "Tell us what you would love your skin and face to feel like. We will help you choose the right ritual or offer.",
                "offer_label": "New client consultation",
                "button_label": "Request my consultation",
                "submitting_label": "Sending your request...",
                "empty_select_label": "Choose a glow ritual",
                "checkbox_label": "Yes, this feels right",
                "error_message": "Please check the highlighted fields and try again.",
                "schedule_enabled": False,
                "starts_at": None,
                "ends_at": None,
                "success_message": "Thank you. Your glow consultation request has been received.",
                "seo_title": "Book a Glow Consultation | The Glow Mission",
                "seo_description": "Tell us about your skin and preferred glow ritual.",
                "hero_image_alt": "Luxury spa consultation setup for The Glow Mission",
            },
        )
        self.attach_seed_image(form, "hero_image", ["glow-consultation.webp", "glow-hero-offer.png", "glow-mission-post-1.png"], "glow-consultation-campaign.webp")
        form.save()
        fields = [
            ("Full name", "full_name", CampaignFormField.FieldType.TEXT, True, 0, "Your name"),
            ("Email", "email", CampaignFormField.FieldType.EMAIL, True, 1, "you@example.com"),
            ("Phone", "phone", CampaignFormField.FieldType.PHONE, False, 2, "+91"),
            ("Preferred ritual", "preferred_ritual", CampaignFormField.FieldType.SELECT, True, 3, ""),
            ("Preferred day", "preferred_day", CampaignFormField.FieldType.TEXT, False, 4, "Weekday morning, weekend evening..."),
            ("What would you like help with?", "skin_goal", CampaignFormField.FieldType.TEXTAREA, False, 5, "Dullness, tension, puffiness, unevenness, dryness..."),
        ]
        for label, key, field_type, required, ordering, placeholder in fields:
            CampaignFormField.objects.update_or_create(
                form=form,
                key=key,
                defaults={
                    "label": label,
                    "field_type": field_type,
                    "placeholder": placeholder,
                    "required": required,
                    "options": RITUAL_NAMES if key == "preferred_ritual" else [],
                    "ordering": ordering,
                    "active": True,
                },
            )
        return form

    def seed_complimentary_campaign(self):
        form, _ = CampaignForm.objects.update_or_create(
            slug="complimentary-facial-session",
            defaults={
                "title": "Complimentary Facial Session",
                "status": CampaignForm.Status.PUBLISHED,
                "summary": "Selected clients can apply for a complimentary natural facial session. The Glow Mission team will review your details and contact you to confirm availability and fit.",
                "offer_label": "Limited complimentary facial",
                "button_label": "Apply for my complimentary session",
                "submitting_label": "Sending your application...",
                "empty_select_label": "Select one",
                "checkbox_label": "I consent to optional filming and social media use",
                "error_message": "Please check the highlighted fields and try again.",
                "schedule_enabled": False,
                "starts_at": None,
                "ends_at": None,
                "success_message": "Thank you. Your complimentary facial session application has been received.",
                "seo_title": "Complimentary Facial Session | The Glow Mission",
                "seo_description": "Apply for a limited complimentary natural facial session at The Glow Mission.",
                "hero_image_alt": "Premium spa setup for a complimentary facial session offer",
            },
        )
        self.attach_seed_image(
            form,
            "hero_image",
            ["glow-hero-offer.webp", "glow-consultation.webp", "glow-hero-offer.png", "glow-mission-post-1.png"],
            "complimentary-facial-session-campaign.webp",
        )
        form.save()
        phone_pattern = r"(?:\+91[\s-]?)?[6-9]\d(?:[\s-]?\d){8}"
        fields = [
            {
                "label": "Full name",
                "key": "full_name",
                "field_type": CampaignFormField.FieldType.TEXT,
                "required": True,
                "ordering": 0,
                "placeholder": "Your full name",
                "validation": {"min_length": 2},
            },
            {
                "label": "Phone",
                "key": "phone",
                "field_type": CampaignFormField.FieldType.PHONE,
                "required": True,
                "ordering": 1,
                "placeholder": "+91",
                "validation": {"pattern": phone_pattern},
            },
            {
                "label": "Email",
                "key": "email",
                "field_type": CampaignFormField.FieldType.EMAIL,
                "required": True,
                "ordering": 2,
                "placeholder": "you@example.com",
                "validation": {},
            },
            {
                "label": "Address",
                "key": "address",
                "field_type": CampaignFormField.FieldType.TEXTAREA,
                "required": True,
                "ordering": 3,
                "placeholder": "Your address",
                "validation": {},
            },
            {
                "label": "Filming and social media consent",
                "key": "filming_consent",
                "field_type": CampaignFormField.FieldType.CHECKBOX,
                "required": False,
                "ordering": 4,
                "help_text": "The facial process may be filmed and the footage may be used on The Glow Mission social media.",
                "validation": {},
            },
            {
                "label": "Skin type",
                "key": "skin_type",
                "field_type": CampaignFormField.FieldType.RADIO,
                "required": True,
                "ordering": 5,
                "options": ["Dry", "Oily", "Combination"],
                "validation": {},
            },
            {
                "label": "Age",
                "key": "age",
                "field_type": CampaignFormField.FieldType.NUMBER,
                "required": True,
                "ordering": 6,
                "placeholder": "Age",
                "validation": {"min": 1, "max": 120},
            },
            {
                "label": "Do you need a consultation?",
                "key": "needs_consultation",
                "field_type": CampaignFormField.FieldType.RADIO,
                "required": True,
                "ordering": 7,
                "options": ["Yes", "No", "Not sure"],
                "validation": {},
            },
            {
                "label": "Allergies",
                "key": "allergies",
                "field_type": CampaignFormField.FieldType.TEXTAREA,
                "required": True,
                "ordering": 8,
                "placeholder": "Please write none if no known allergies.",
                "validation": {},
            },
        ]
        for field in fields:
            CampaignFormField.objects.update_or_create(
                form=form,
                key=field["key"],
                defaults={
                    "label": field["label"],
                    "field_type": field["field_type"],
                    "placeholder": field.get("placeholder", ""),
                    "help_text": field.get("help_text", ""),
                    "required": field["required"],
                    "options": field.get("options", []),
                    "validation": field["validation"],
                    "ordering": field["ordering"],
                    "active": True,
                },
            )
        return form
