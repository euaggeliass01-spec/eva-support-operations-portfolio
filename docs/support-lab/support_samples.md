# WordPress / WooCommerce Support Simulations

> These cases are synthetic portfolio exercises, not real customer tickets.

## WC-101 — Customer charged, order still Pending payment

**Category:** Payments & orders  
**Priority:** High

### Customer report
A customer says their card was charged, but the WooCommerce order is still marked Pending payment. They need the product dispatched today.

### Investigation plan
- Check WooCommerce order notes and exact timestamp.
- Check gateway dashboard for capture, authorization, failure, or duplicate transaction.
- Confirm webhook delivery and gateway logs.
- Do not manually mark the order paid until settlement is verified.

### First reply

Hi there,

I understand why this is concerning, especially when the payment appears on the card but the order has not moved forward.

Before we change the order status, I would like to verify whether the payment gateway recorded a successful transaction or only a temporary authorization. Please send the order number and, if available, the payment transaction reference shown in your gateway dashboard. You do not need to send full card details.

I will then compare the WooCommerce order notes with the gateway record. If the payment is confirmed, the order can be updated safely. If it is only an authorization or a failed capture, we will avoid dispatching the order until the gateway confirms settlement.

Best,
Eva

### Internal note
Escalate if money was captured but the webhook repeatedly fails. Preserve order and gateway IDs; never request card number or CVV.

### Core lesson
Distinguish a bank authorization from a captured payment before changing order state.

---

## WC-102 — Order emails are not reaching customers

**Category:** Email delivery  
**Priority:** Medium

### Customer report
The store owner receives new-order notifications, but customers do not receive processing or completed-order emails.

### Investigation plan
- Confirm Processing and Completed order emails are enabled.
- Verify recipient address on affected orders.
- Run a controlled test order and inspect email logs.
- Check spam, sending reputation, SPF, DKIM, DMARC, and transactional mail configuration.

### First reply

Hi,

Since the admin notification is arriving, WooCommerce is generating at least some email events. I would first check whether the customer emails are enabled and whether the affected orders contain valid billing email addresses.

Next, I would run a controlled test order and inspect the mail log. If WordPress reports that the message was sent but it never arrives, the issue is likely delivery or authentication rather than the WooCommerce email template itself. At that point, I would verify the site's sending domain, SPF/DKIM configuration, and SMTP or transactional email setup.

Please share one affected order number and the result of a fresh test order. Avoid posting customer email addresses publicly.

Best,
Eva

### Internal note
Separate generation from delivery. A successful wp_mail call does not guarantee inbox delivery.

### Core lesson
Troubleshoot the full path: event → generation → handoff → authentication → mailbox.

---

## WC-103 — German flat-rate shipping is missing at checkout

**Category:** Shipping  
**Priority:** Medium

### Customer report
A merchant created a Germany shipping zone with a €5 flat rate, but customers in Berlin only see Local pickup.

### Investigation plan
- Check the customer's complete shipping address and postcode.
- Review shipping-zone order and matching rules.
- Confirm the flat-rate method is enabled and has a valid cost.
- Check product type, shipping class, and package restrictions.
- Retest with a clean session.

### First reply

Hi,

I would check the zone matching order first. WooCommerce uses the first shipping zone that matches the customer's address, so a broader zone placed above Germany can prevent the Germany-specific rate from being used.

Please confirm that:
1. the customer's full German address is entered at checkout,
2. the Germany zone is above broader European zones,
3. Flat rate is enabled inside that zone,
4. the product is not restricted by a shipping class or virtual-product setting.

After saving the zone, test in a private browser window with a Berlin postcode so cached checkout data does not affect the result.

Best,
Eva

### Internal note
Do not assume the displayed address is the shipping address; billing and shipping can differ.

### Core lesson
Shipping-zone precedence is a common source of configuration errors.

---

## WC-104 — Checkout broke after a plugin update

**Category:** Plugin conflict  
**Priority:** Critical

### Customer report
After updating a discount plugin, the checkout spinner never stops and customers cannot place orders.

### Investigation plan
- Confirm current backup and staging availability.
- Capture console, network, PHP, and WooCommerce logs.
- Disable only the most likely changed component.
- Retest with a default theme and minimal plugin set on staging.
- Roll back or escalate with reproducible evidence.

### First reply

Hi,

Because checkout is currently unavailable, the immediate goal is to restore a working purchase path while preserving evidence for diagnosis.

If a staging site is available, I would reproduce the issue there first. Otherwise, I would place the store in a controlled maintenance window, capture the browser-console error and WooCommerce logs, then temporarily deactivate the recently updated discount plugin. If checkout returns, we have a strong conflict signal and can keep the plugin disabled while testing a rollback or compatibility fix.

Before changing anything, please confirm that a current backup exists. I would avoid updating several plugins at once, because that makes the cause harder to isolate.

Best,
Eva

### Internal note
Revenue-impacting outage. Prioritize restoration, then root-cause analysis. Document every change.

### Core lesson
Change one variable at a time and preserve a rollback path.

---

## WC-105 — Connection is not private after domain change

**Category:** Domain & SSL  
**Priority:** High

### Customer report
The store moved to a new domain. Some visitors see a certificate warning and images still load from the old address.

### Investigation plan
- Verify DNS records and certificate coverage for all active hostnames.
- Check WordPress Address and Site Address.
- Use a serialized-data-safe search and replace after backup.
- Clear caches and inspect mixed-content requests.
- Confirm redirects from the old domain.

### First reply

Hi,

This appears to involve two related layers: the SSL certificate for the new domain and old URLs still stored in the site database or cache.

I would first verify that the new domain and its www/non-www version both point to the correct host and are covered by an active certificate. Once HTTPS is valid, I would check the WordPress Address and Site Address, then run a safe search-and-replace for old-domain URLs using a backup and a tool that handles serialized data correctly.

Finally, I would clear the site, CDN, and browser caches and test for mixed-content requests in the browser console.

Best,
Eva

### Internal note
Never run a raw SQL replace on serialized WordPress data without a safe tool and backup.

### Core lesson
Separate certificate validity, canonical URLs, redirects, and mixed content.

---

## WC-106 — Store became slow after page-builder installation

**Category:** Performance  
**Priority:** Medium

### Customer report
Product and checkout pages became noticeably slower after a new page builder and several add-ons were installed.

### Investigation plan
- Measure response time on consistent URLs.
- Check server resources, logs, scheduled actions, and database load.
- Test add-ons individually on staging.
- Review image sizes, scripts, and third-party requests.
- Exclude cart, checkout, and account pages from unsafe caching.

### First reply

Hi,

I would establish a before-and-after baseline rather than guessing from the plugin list. The most useful first checks are server response time, slow requests, database queries, image weight, and whether the slowdown affects all pages or only builder-generated layouts.

On a staging copy, I would disable the new add-ons one at a time, clear caches between tests, and compare the same product and checkout pages. I would also check scheduled actions and error logs for repeated background jobs.

The checkout should be tested carefully because aggressive caching or optimization can break cart sessions even when a speed score improves.

Best,
Eva

### Internal note
Performance work needs baselines. Do not recommend random optimization plugins without evidence.

### Core lesson
Measure, isolate, change, and retest.

---

## WC-107 — Refund completed, customer has not received funds

**Category:** Refunds  
**Priority:** Medium

### Customer report
WooCommerce shows a completed refund from three days ago, but the customer says the money is not back in their account.

### Investigation plan
- Compare WooCommerce order notes with gateway refund status.
- Confirm whether the refund was automatic or manually recorded.
- Capture the provider refund reference.
- Avoid issuing a duplicate refund.

### First reply

Hi,

A completed WooCommerce refund confirms that the refund action was recorded, but the payment provider and the customer's bank determine when the funds become visible.

I would check the order notes and gateway dashboard for a refund transaction ID and status. If the gateway confirms the refund, I would share the provider reference and advise the customer that bank processing times vary. I would not promise an exact arrival date unless the payment provider publishes one for that transaction.

If WooCommerce shows a refund but the gateway has no matching record, the refund may have been recorded manually and needs further review before any second refund is attempted.

Best,
Eva

### Internal note
Financial-risk case. Human verification is required before repeating any transaction.

### Core lesson
A WooCommerce status and a processor settlement are related but not identical.

---

## WC-108 — Variable product appears out of stock

**Category:** Inventory & variations  
**Priority:** Medium

### Customer report
A variable product says Out of stock on the shop page, although two size variations show stock quantities in the admin.

### Investigation plan
- Check variation enabled status, price, stock status, and quantity.
- Verify attribute combinations and default selection.
- Review parent-level inventory settings.
- Regenerate lookup tables and clear product transients.
- Retest without cache.

### First reply

Hi,

I would check whether each variation is enabled, has a price, and is set to In stock. A variation can have a quantity but still be unavailable if its stock status, price, or attributes are incomplete.

I would also review the parent product's stock-management setting and confirm that every variation has a unique, valid combination of attributes. After saving the variations, I would regenerate product lookup data and clear transients or caches before retesting the product page.

Please share a screenshot of the variation settings with customer information removed.

Best,
Eva

### Internal note
Quantities alone do not guarantee purchasability; price and enabled status matter.

### Core lesson
Inspect both parent and variation-level data.

---

