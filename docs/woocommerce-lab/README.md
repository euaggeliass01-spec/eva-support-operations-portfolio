# Northwind Studio — WooCommerce Support Lab

**Evidence type:** Self-directed technical lab  
**Platform:** WordPress Playground  
**Purpose:** Reproducible WooCommerce configuration and troubleshooting practice

## What the Blueprint creates

- latest WordPress with PHP 8.2;
- Storefront theme;
- WooCommerce;
- four simple products;
- one variable product with A5 and A4 variations;
- a 10% coupon (`WELCOME10`);
- a Germany shipping zone with a €5 flat rate;
- a synthetic pending order;
- a Support Lab Brief page.

## Launch

After this repository is published on GitHub Pages, use the **Launch WooCommerce lab** button on the portfolio homepage. It builds a fresh browser-based WordPress instance from `blueprint.json`.

You can also construct the URL manually:

```text
https://playground.wordpress.net/?blueprint-url=PUBLIC_URL_TO_THIS_BLUEPRINT
```

## Hands-on checklist before claiming this project in an application

Complete these actions yourself and record brief notes:

1. Open Products and verify the four simple products and one variable product.
2. Open the variable product and inspect both variations.
3. Apply `WELCOME10` in a test cart.
4. Enter a German shipping address and verify the €5 flat rate.
5. Inspect the synthetic pending order and its order notes.
6. Temporarily change one variation to out of stock, observe the storefront, and restore it.
7. Disable the flat-rate method, reproduce the missing-shipping symptom, and restore it.
8. Open WooCommerce status/log areas and note where you would collect evidence.
9. Export or screenshot the final working state for the portfolio.
10. Write one paragraph on what surprised you and what you had to troubleshoot.

## Suggested application wording after completing the checklist

> I built a reproducible WooCommerce support lab using WordPress Playground. The Blueprint installs WooCommerce and Storefront, creates products and variations, configures a coupon and a Germany shipping zone, and adds a synthetic order. I used the lab to reproduce and reverse common support problems, including missing shipping methods and variation stock errors. A specific challenge was making the environment repeatable rather than relying on a manually configured site, so I documented the setup as code and added a restoration checklist.

## Limitations

This is a portfolio lab, not professional WordPress support experience. It should be described exactly that way.
