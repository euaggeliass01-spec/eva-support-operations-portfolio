# Hands-On WooCommerce Troubleshooting

**Evidence type:** Self-directed hands-on technical lab  
**Environment:** WordPress Playground, WooCommerce, Storefront  
**Scope:** Three controlled incidents reproduced, diagnosed, restored, and verified

## Method

For each exercise I recorded a known-good baseline, introduced one controlled change, reproduced the customer-visible symptom, isolated the cause, restored the configuration, verified the result, and documented a customer reply and internal note.

## Case 1 — German flat-rate shipping missing at checkout

**Customer impact:** A customer with a complete German address could not select delivery.  
**Root cause:** The Germany shipping zone existed, but its Flat rate method was disabled.  
**Resolution:** Restored the zone region to Germany, enabled Flat rate with a €5 cost, and retested using postcode 10115 Berlin.  
**Result:** Checkout displayed `Flat rate — €5.00` again.

## Case 2 — One variation out of stock while another remained available

**Customer impact:** The A5 format could not be purchased, while A4 remained available.  
**Root cause:** A5 stock quantity was zero and backorders were disabled.  
**Resolution:** Restored A5 quantity to 15.  
**Result:** Add to cart returned for A5; A4 remained unaffected.

## Case 3 — Checkout blocked because no payment method was available

**Customer impact:** Products and shipping calculated correctly, but checkout could not be completed.  
**Root cause:** No payment gateway was enabled.  
**Resolution:** Enabled Direct Bank Transfer and repeated the checkout in a clean session.  
**Result:** Order #21 was created for €23 and remained On hold pending payment verification.

## Additional finding

Repeated failed checkout attempts produced a stock-availability conflict in one disposable session. I restarted from a clean baseline rather than continue diagnosing a state altered by previous tests.
