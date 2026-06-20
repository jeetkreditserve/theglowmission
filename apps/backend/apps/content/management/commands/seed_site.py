from __future__ import annotations

import os
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from apps.common.image_variants import ensure_image_variants
from apps.campaigns.models import CampaignForm, CampaignFormField
from apps.content.models import BrandSettings, FAQ, GalleryImage, HeroSlide, Page, PageSection, Service, Testimonial


BRAND_STORY = (
    "The Glow Mission is a boutique facial wellness studio built around natural care, calm touch, "
    "and skin that looks quietly refreshed. The practice carries forward a mother's cosmetology wisdom: "
    "simple ingredients, consistent massage, facial movement, and patient hands. Every ritual is designed "
    "to soften visible fatigue, release facial tension, and give you one peaceful hour to feel cared for."
)


class Command(BaseCommand):
    help = "Seed The Glow Mission CMS content and upload provided brand assets to S3."

    def handle(self, *args, **options):
        self.create_admin_user()
        brand = self.seed_brand()
        self.seed_pages()
        campaign = self.seed_campaign()
        self.seed_hero_slides(campaign)
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

    def attach_seed_image(self, instance, field_name: str, filename: str | list[str], storage_name: str):
        field = getattr(instance, field_name)
        if field:
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

    def seed_pages(self):
        pages = [
            ("Home", "home", 0),
            ("About", "about", 1),
            ("Services", "services", 2),
            ("Glow Rituals", "glow-rituals", 3),
            ("Gallery", "gallery", 4),
            ("Contact", "contact", 5),
        ]
        for title, slug, ordering in pages:
            Page.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "status": Page.Status.PUBLISHED,
                    "ordering": ordering,
                    "seo_title": f"{title} | The Glow Mission",
                    "seo_description": "Natural facial massage, face yoga, and glow rituals in a calm boutique spa setting.",
                },
            )

        home = Page.objects.get(slug="home")
        sections = [
            {
                "section_type": PageSection.SectionType.HERO,
                "title": "Natural facial rituals for a softer, calmer glow.",
                "subtitle": "A premium spa wellness experience shaped by facial massage, face yoga, and botanical care.",
                "body": "Come in for one peaceful hour. Leave feeling rested, lifted, and beautifully looked after.",
                "cta_label": "Book a consultation",
                "cta_url": "/campaigns/glow-consultation",
                "ordering": 0,
                "config": {"visual": "luxury-editorial-spa"},
            },
            {
                "section_type": PageSection.SectionType.SERVICES,
                "title": "Rituals designed around touch, tension, and visible radiance",
                "subtitle": "Facial massage, face yoga, botanical textures, and slow care.",
                "body": "Choose a session for glow, sculpting, natural ingredient care, or a seasonal offer. Every treatment can be edited from the CMS as the menu grows.",
                "cta_label": "Explore services",
                "cta_url": "/services",
                "ordering": 1,
            },
            {
                "section_type": PageSection.SectionType.STORY,
                "title": "A legacy carried forward",
                "subtitle": "Inspired by a mother's wisdom in cosmetology and natural care.",
                "body": BRAND_STORY,
                "cta_label": "Read our story",
                "cta_url": "/about",
                "ordering": 2,
                "asset_candidates": ["glow-about-story.webp", "glow-about-story.png"],
            },
            {
                "section_type": PageSection.SectionType.GALLERY,
                "title": "A slower kind of beauty ritual",
                "subtitle": "Champagne warmth, ivory linens, botanicals, and calm hands.",
                "body": "Every visual touchpoint should feel like the treatment itself: warm, refined, natural, and deeply restful.",
                "cta_label": "View gallery",
                "cta_url": "/gallery",
                "ordering": 3,
            },
        ]
        for section in sections:
            asset_candidates = section.pop("asset_candidates", None)
            item, _ = PageSection.objects.update_or_create(
                page=home,
                section_type=section["section_type"],
                ordering=section["ordering"],
                defaults=section,
            )
            if asset_candidates:
                self.attach_seed_image(item, "media", asset_candidates, f"home-section-{item.ordering}.webp")
                item.save()

        for slug in ["about", "services", "glow-rituals", "gallery", "contact"]:
            page = Page.objects.get(slug=slug)
            PageSection.objects.update_or_create(
                page=page,
                section_type=PageSection.SectionType.RICH_TEXT,
                ordering=0,
                defaults={
                    "title": page.title,
                    "subtitle": "Natural facial rituals, crafted with care.",
                    "body": BRAND_STORY if slug == "about" else "Every detail is designed with softness, natural care, premium touch, and visible confidence in mind.",
                    "active": True,
                },
            )

    def seed_hero_slides(self, campaign: CampaignForm):
        slides = [
            {
                "title": "Natural facial rituals for a softer, calmer glow.",
                "subtitle": "Facial massage, face yoga, and botanical care in one peaceful hour.",
                "body": "A luxury spa wellness experience for rested skin, softened tension, and quiet confidence.",
                "offer_label": "Signature consultation",
                "primary_cta_label": "Book a consultation",
                "primary_cta_url": f"/campaigns/{campaign.slug}",
                "secondary_cta_label": "Explore rituals",
                "secondary_cta_url": "/services",
                "ordering": 0,
                "image_alt": "Luxury facial massage ritual in a calm boutique spa setting",
                "asset_candidates": ["glow-hero-signature.webp", "glow-hero-facial-massage.png", "glow-mission-post-1.png"],
            },
            {
                "title": "Limited free glow sessions for new clients.",
                "subtitle": "Create a campaign in the CMS and place it directly on this carousel.",
                "body": "Use this space for seasonal offers, free consultations, launch giveaways, and treatment trials.",
                "offer_label": "Launch offer",
                "primary_cta_label": "Claim the offer",
                "primary_cta_url": f"/campaigns/{campaign.slug}",
                "secondary_cta_label": "See treatment menu",
                "secondary_cta_url": "/glow-rituals",
                "ordering": 1,
                "image_alt": "Premium spa consultation setting for a limited glow session offer",
                "asset_candidates": ["glow-hero-offer.webp", "glow-hero-offer.png", "glow-mission-post-1.png"],
            },
            {
                "title": "A quieter lift through face yoga and touch.",
                "subtitle": "Gentle facial movement, jaw release, and massage for a rested natural contour.",
                "body": "Choose a hands-on ritual designed to soften tension and make your face feel lighter.",
                "offer_label": "Face yoga lift",
                "primary_cta_label": "Book face yoga",
                "primary_cta_url": f"/campaigns/{campaign.slug}",
                "secondary_cta_label": "View ritual menu",
                "secondary_cta_url": "/glow-rituals",
                "ordering": 2,
                "image_alt": "Face yoga lift ritual in a calm boutique spa setting",
                "asset_candidates": ["glow-hero-face-yoga.webp", "glow-service-face-yoga.png", "glow-mission-post-1.png"],
            },
        ]
        for slide in slides:
            asset_candidates = slide.pop("asset_candidates")
            item, _ = HeroSlide.objects.update_or_create(
                ordering=slide["ordering"],
                defaults={**slide, "active": True, "linked_campaign": campaign},
            )
            self.attach_seed_image(item, "image", asset_candidates, f"hero-slide-{item.ordering}.png")
            item.save()

    def seed_services(self, campaign: CampaignForm):
        services = [
            {
                "title": "Signature Glow Ritual",
                "slug": "signature-glow-ritual",
                "short_description": "A complete one-hour facial massage ritual for rested, brighter-looking skin.",
                "description": "Slow cleansing, botanical textures, lymphatic-inspired massage, lifting strokes, and a calming finish for skin that feels cared for without harshness.",
                "duration": "60 minutes",
                "session_count": 1,
                "price_amount": 2500,
                "sale_price_amount": 1999,
                "discount_label": "Introductory glow price",
                "price_note": "Best for first-time glow clients",
                "inclusions": ["Gentle cleanse", "Facial massage", "Botanical mask", "Glow finish"],
                "featured": True,
                "ordering": 0,
                "asset_candidates": ["glow-service-signature.webp", "glow-service-signature.png", "glow-mission-post-1.png"],
            },
            {
                "title": "Face Yoga Lift",
                "slug": "face-yoga-lift",
                "short_description": "Guided facial movement and lifting massage to soften tension and support natural contour.",
                "description": "A sculpting-focused session for facial tightness, tired expressions, jaw tension, and a more awake look.",
                "duration": "45 minutes",
                "session_count": 1,
                "price_amount": 1800,
                "sale_price_amount": None,
                "discount_label": "",
                "price_note": "Available as a standalone ritual or add-on",
                "inclusions": ["Guided face yoga", "Jaw and cheek release", "Lifting massage", "At-home practice tips"],
                "featured": False,
                "ordering": 1,
                "asset_candidates": ["glow-service-face-yoga.webp", "glow-service-face-yoga.png", "glow-mission-post-1.png"],
            },
            {
                "title": "Natural Ingredient Facial",
                "slug": "natural-ingredient-facial",
                "short_description": "A sensory botanical facial inspired by honey, cucumber, citrus, herbs, and soft cream textures.",
                "description": "A gentle seasonal ritual for dullness, dryness, and anyone who wants a natural, comforting facial experience.",
                "duration": "60 minutes",
                "session_count": 1,
                "price_amount": 2200,
                "sale_price_amount": None,
                "discount_label": "Seasonal ritual",
                "price_note": "Ingredients vary by season and skin comfort",
                "inclusions": ["Ingredient consultation", "Botanical mask", "Cooling compress", "Hydrating finish"],
                "featured": False,
                "ordering": 2,
                "asset_candidates": ["glow-service-natural-facial.webp", "glow-service-natural-facial.png", "glow-mission-post-1.png"],
            },
        ]
        for service in services:
            asset_candidates = service.pop("asset_candidates")
            item, _ = Service.objects.update_or_create(
                slug=service["slug"],
                defaults={
                    **service,
                    "image_alt": f"{service['title']} treatment at The Glow Mission",
                    "currency": "INR",
                    "cta_label": "Book this ritual",
                    "cta_url": f"/campaigns/{campaign.slug}",
                    "booking_campaign": campaign,
                    "active": True,
                },
            )
            self.attach_seed_image(item, "image", asset_candidates, f"{item.slug}.png")
            item.save()

    def seed_supporting_content(self):
        faqs = [
            ("What is The Glow Mission?", "The Glow Mission is a boutique facial wellness studio focused on natural facial massage, face yoga, botanical textures, and slow restorative care."),
            ("How long is a session?", "Most signature rituals are 45 to 60 minutes. The CMS service menu can be updated as new treatment lengths are added."),
            ("Is this a medical facial?", "No. The Glow Mission is a wellness and beauty ritual experience, not a medical dermatology service or clinical skin procedure."),
            ("What should I book for my first visit?", "The Signature Glow Ritual is the best first session because it combines consultation, massage, botanical care, and a calm glow finish."),
            ("Can I book a free session offer?", "Yes. When a free session campaign is active, it appears on the homepage carousel and has its own campaign form."),
            ("Do you use harsh peels or machines?", "The current approach is hands-on and gentle: massage, facial movement, natural textures, compresses, and calming skin care."),
            ("Can prices or discounts change?", "Yes. Services have structured pricing and offer fields in the CMS, so prices, sale prices, and discount labels can be changed anytime."),
            ("Can I choose a treatment later?", "Yes. You can submit a consultation form first and choose the right ritual after discussing your goals and comfort level."),
            ("What skin concerns can I mention?", "You can mention dullness, dryness, tension, puffiness, uneven texture, fatigue, or simply that you want a calmer glow."),
            ("How do campaign forms work?", "Each campaign can have custom fields, active dates, success copy, and response export from the admin CMS."),
            ("Will my treatment be customized?", "Every session should be adjusted around comfort, skin feel, time, and the kind of result you want from that visit."),
            ("How should I prepare?", "Arrive with minimal makeup if possible, share any sensitivities, and give yourself a little time after the session before rushing back into the day."),
        ]
        for ordering, (question, answer) in enumerate(faqs):
            FAQ.objects.update_or_create(question=question, defaults={"answer": answer, "active": True, "ordering": ordering})

        testimonials = [
            ("A softer kind of glow", "The ritual felt calm and personal. My skin looked rested and my face felt lighter.", "First glow client"),
            ("Care you can feel", "The whole experience felt gentle, intentional, and beautifully put together.", "Glow client"),
            ("The pause I needed", "It felt like a beauty treatment and a reset at the same time. The massage was the best part.", "Wellness client"),
        ]
        for ordering, (name, quote, role) in enumerate(testimonials):
            Testimonial.objects.update_or_create(name=name, defaults={"quote": quote, "role": role, "active": True, "ordering": ordering})

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
                    "options": ["Signature Glow Ritual", "Face Yoga Lift", "Natural Ingredient Facial"] if key == "preferred_ritual" else [],
                    "ordering": ordering,
                    "active": True,
                },
            )
        return form
