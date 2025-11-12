#!/usr/bin/env python3
from conductor_integration import ConductorIntegration

c = ConductorIntegration()
customers = c.get_real_customer_data(limit=3)
print(f'\nFound {len(customers)} customers:')
for i, customer in enumerate(customers, 1):
    print(f'{i}. {customer["name"]} - {customer["phone"]} - {customer["segment"]} - ${customer["ltv"]:.2f} - {customer["total_visits"]} visits')




