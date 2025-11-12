Exhibit A

Data Usage and Integration Fees

I. Integration Fee
Company shall pay to Blaze the following one-time integration set-up fee: $
II. API Integration Usage Fees
a. API Integration Usage fees are charged to cover costs of API infrastructure and to encourage good
behavior and efficient calls.
b. Company’s Partner Key shall only be utilized with dispensary/developer keys of Company
locations. Another company making calls against this Partner Key can result in the key being
disabled and the immediate termination of this Agreement.
c. Upon the Company’s Partner Key being promoted to production, BLAZE shall begin monitoring
the Company’s API utilization. At the end of each month BLAZE will charge the Company’s
billing account based on the Tier.
d. The Tier will be assigned as the most cost-effective base, after taking overages into consideration.
e. For the initial 90 days in production, overage fees will not be assessed, however the base tier will
still be adjusted as if they were.

Tier Price Per Month Call Limit Overages Per Call
1 $100.00 250,000 0.0006
2 $250.00 1,500,000 0.0002
3 $500.00 10,000,000 0.0001

III. Use of Data
Notwithstanding anything to the contrary in this Agreement, Company agrees to the following restrictions
on the use of data:
a. Blaze reserves the right to restrict access to payment related API’s. Company will not send orders
through Blaze API’s with a payment applied without the express consent of Blaze. All orders sent to
Blaze through Blaze API’s must be submitted without payment applied, unless integrated and utilized
with a Blaze authorized payment solution.
b. Company will not present data to any third party for the purpose of third party’s commercial use or
monetization of the data.
IV. Pagination Rules and Rate Limits: If the Company is accessing or pulling data, the following rules must
be adhered to:
a. Fetching historical transactions shall be done on an hourly or nightly basis.
b. Fetching members shall be done hourly or nightly. Maintain the last sync date and utilize the
modified date to fetch members that have been modified after the last sync time.
c. Fetching inventory shall be done no more than every 5 minutes to be the most up to date. Maintain
the last sync date and utilize the modified date to fetch products that have been modified after the
last sync time.
d. Company call volume shall not exceed 10,000 calls for every 5 minutes. Exceeding that threshold
will result in rate throttling or Company partner key being disabled.