# Samuda Chemical Complex Limited — Website

A static, multi-page corporate website for SCCL, built from `samuda_chemical_website_ui_ux_blueprint.md` and the homepage mock-up (`Untitled.png`).

## Structure

```
src/
  layout.html          shared <head>, utility bar, header, mega-menu, footer
  pages/*.html         page bodies (front-matter comment sets title / description / active nav)
  data/products.json   product catalogue — single source for cards, menus, filters and detail pages
build.py               generates the site from src/
site/                  deployable output (upload this folder to any web host)
  assets/css/styles.css  design system
  assets/js/main.js      navigation, animations, catalogue filters, inquiry list, form validation
  assets/img/            optimised WebP images + favicon
  products/*.html        one generated page per product
```

## Build and preview

```bash
python build.py
```

```bash
python -m http.server 8090 --directory site
```

Then open http://localhost:8090. Edit files in `src/` (or `site/assets/`) and run `python build.py` again. Don't edit the generated `.html` files in `site/`; they are overwritten on every build.

## Pages

Home, About, Products (catalogue + 18 product pages), **Our Plants**, Industries, Manufacturing, Quality & Sustainability, **Company Policies**, Global Reach, News, Careers, Contact, Privacy.

## Adding or editing products

Edit `src/data/products.json` and rebuild. Required fields: `slug`, `name`, `formula`, `category` (`basic`, `performance` or `calcium`), `chemical`, `form`, `short`, `overview` (list of paragraphs) and `industries`. Optional fields add sections to the product page: `image` (file name in `site/assets/img/products/`, without `.webp`), `features`, `properties` (key/value rows), `tables` (titled spec tables), `dosage`, `usage`, `applications`, `capacity`, `capacityShort`, `packaging`, `technology` and `storage`. The catalogue, mega-menu, quote-form product list, industry pages, sitemap and detail pages all update automatically.

## Forms

The quote, general-inquiry and careers forms validate in the browser and generate a reference number (e.g. `SCCL-RFQ-20261027-AB12`). **There is no backend yet.** To receive submissions, set `data-endpoint="https://…"` on each `<form>` in `src/pages/contact.html` and `src/pages/careers.html`. The form then POSTs `multipart/form-data` (including `reference` and `submittedAt`) to that URL. Until an endpoint is set, a successful submission is simulated.

## Before launch: confirm with Samuda

Based on the blueprint's content-governance rules, check these items with the company before publishing:

| Item | Where it appears | Status |
|---|---|---|
| Logo | Header, footer, favicon | Vector **recreation** of the S mark. Replace `LOGO_MARK` in `build.py` with the official SVG |
| Photography | Site-wide | Real Samuda photos from `products.docx` and `Plants.docx` are used for products, plants and the lab. The homepage hero (aerial tanks) and a few page banners still use the first supplied images. Replace them with real high-resolution (1920 px+) Samuda photos if available |
| Email `info@scclbd.com` | Utility bar, footer, contact | Confirm the address. No phone numbers are published yet |
| Head office: T.K. Bhaban, 13 Karwan Bazar, Dhaka-1215 | Footer, About, Contact | Confirm floor and current address |
| Factory: Sikirgaon, Gazaria, Munshiganj | Footer, About, Contact | Confirm. The mock-up also mentions a Chattogram (Chandgaon) site, which has been left out until verified |
| Established 2006, T.K. Group concern | Home, About | Confirm with company records |
| "30+ export countries" and regions (Asia, Africa, Europe) | Home, Global Reach | From a 2024 article and the mock-up. Confirm the current figure |
| Product data (18 products) | Catalogue and detail pages | Taken from `products.docx`. Obvious typos were corrected (e.g. "Carbon Loren" → Carbone Lorraine, "Tarloskar" → Kirloskar, "Deuse" → Dense, density unit g/lm → g/ml) |
| Hydrochloric acid capacity | HCl page, Plants page | The source says "Monthly production capacity of HCl = 150-180 MT/Day". Shown as **150–180 MT/day**. Confirm the unit |
| Calcium carbonate (uncoated/coated) specs | CaCO₃ page | The source's property table and packaging text were copied from CPW/HCl, so they are **omitted**. Supply the real CaCO₃ specification table |
| Production capacities | Product pages, Plants page, Home | Published as stated in `products.docx` / `Plants.docx` |
| "One of the largest caustic soda & hydrogen peroxide producers in Bangladesh" | Home hero, About, footer | Wording from `Plants.docx` |
| Labour Rights policy (English) | `policies.html` | English text is a translation of the Bengali original from `Company Policy.docx`. Have HR review the translation |
| Policy manual PDF | `policies.html` (download) | The full 81-page 2020 PDF is published for download. Confirm it is approved for public release, or remove `site/assets/docs/` and the download card |
| Mission, vision and values | About | Draft wording. Needs approval |
| Quality, safety and sustainability statements | Quality and Manufacturing pages | Kept general, with no certifications or figures. Add verified certificates (name, scope, issuer, validity) |
| Privacy Policy | `privacy.html` | Template. Needs legal review |

## Next phases (from the blueprint)

- Backend and admin panel: products, documents (TDS/SDS), inquiry management and roles.
- Full Bangla language version (the Labour Rights policy already has an English/বাংলা toggle).
- Real TDS and SDS downloads once documents are approved.
