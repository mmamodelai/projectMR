# MotaBot AI Workflows - TODO List

## Overview
We need to create 4 specialized chatbots for different customer segments, plus the existing REX (Receipt Cleaner) system.

## ✅ COMPLETED
- **REX** - Receipt cleaner system (already working)

## 🚧 IN PROGRESS
- **XC** - External Customers (Discovery Bot - 80% complete)

## 📋 TODO - Workflow Development

### 1. XC - External Customers (Discovery Bot)
**Status**: 80% Complete - Needs testing and refinement

**Purpose**: Get to know external customers who buy Mota products at 3rd party stores

**Key Features**:
- ✅ Consumption method discovery (edibles, vapes, flower)
- ✅ Use case discovery (creative, relax, work out, socialize, sleep)
- ✅ Leverages existing customer data (dispensary location, account info)
- ✅ Deal notification promises
- ✅ Preference storage in database

**Tools Needed**:
- ✅ Customer Profile Tool (get existing account info)
- ✅ Mota Products Database (11,515+ products with Leafly data)
- ✅ Product Search Tool (by effects, consumption methods)
- ✅ Calculator (for points/recommendations)
- ✅ Preference Storage (customer_preferences table)

**Next Steps**:
- [ ] Test XC bot with real customer data
- [ ] Refine conversation flow based on testing
- [ ] Add product recommendation logic
- [ ] Implement deal notification system

---

### 2. XB - External Budtenders (Sales Incentive Bot)
**Status**: 0% Complete - Needs full development

**Purpose**: Court budtenders at 3rd party stores, offer points/rewards for selling Mota products

**Key Features**:
- [ ] Budtender identification and verification
- [ ] Sales performance tracking
- [ ] Point/reward system for Mota product sales
- [ ] Training material delivery
- [ ] Incentive program management
- [ ] Performance analytics

**Tools Needed**:
- [ ] Budtender Database Tool (3rd party budtender info)
- [ ] Sales Tracking Tool (Mota product sales by budtender)
- [ ] Rewards Calculator (points earned per sale)
- [ ] Training Content Tool (product knowledge, sales tips)
- [ ] Performance Analytics Tool (sales metrics, rankings)
- [ ] Incentive Management Tool (rewards, bonuses, recognition)

**Conversation Flow**:
1. Identify budtender and verify credentials
2. Explain Mota rewards program for budtenders
3. Provide product training and sales materials
4. Track sales performance and award points
5. Send performance updates and incentives
6. Offer advanced training and recognition

**Database Tables Needed**:
- [ ] `external_budtenders` (budtender info, store, credentials)
- [ ] `budtender_sales` (sales tracking, points earned)
- [ ] `budtender_rewards` (incentives, bonuses, recognition)
- [ ] `training_materials` (product info, sales tips, training content)

---

### 3. IC - Internal Customers (Store Loyalty Bot)
**Status**: 0% Complete - Needs full development

**Purpose**: Serve customers who shop at Mota's Silverlake retail store

**Key Features**:
- [ ] Store-specific promotions and inventory alerts
- [ ] VIP status management
- [ ] In-store experience optimization
- [ ] Personal budtender connections
- [ ] Loyalty program management
- [ ] Store events and promotions

**Tools Needed**:
- [ ] Store Inventory Tool (real-time Silverlake inventory)
- [ ] VIP Status Tool (customer tier management)
- [ ] Budtender Assignment Tool (personal budtender connections)
- [ ] Store Events Tool (promotions, events, special offers)
- [ ] Loyalty Points Tool (points balance, redemption)
- [ ] Store Analytics Tool (visit history, preferences)

**Conversation Flow**:
1. Greet by name with VIP status
2. Check recent visits and preferences
3. Offer store-specific promotions
4. Connect with personal budtender
5. Provide inventory updates
6. Manage loyalty points and rewards

**Database Tables Needed**:
- [ ] `store_inventory` (Silverlake inventory levels)
- [ ] `vip_status` (customer tier, benefits)
- [ ] `budtender_assignments` (personal budtender connections)
- [ ] `store_events` (promotions, events, special offers)

---

### 4. IB - Internal Budtenders (Employee Support Bot)
**Status**: 0% Complete - Needs full development

**Purpose**: Support Mota's own budtenders at Silverlake store

**Key Features**:
- [ ] Product knowledge and training
- [ ] Customer service support
- [ ] Sales performance tracking
- [ ] Internal communications
- [ ] Training material access
- [ ] Performance feedback

**Tools Needed**:
- [ ] Employee Database Tool (budtender info, schedules, performance)
- [ ] Product Knowledge Tool (comprehensive product database)
- [ ] Customer Service Tool (customer support, issue resolution)
- [ ] Training Management Tool (training materials, progress tracking)
- [ ] Performance Analytics Tool (sales metrics, customer feedback)
- [ ] Internal Communications Tool (announcements, updates)

**Conversation Flow**:
1. Identify budtender and check schedule
2. Provide product knowledge and training
3. Offer customer service support
4. Track performance and provide feedback
5. Deliver internal communications
6. Manage training progress

**Database Tables Needed**:
- [ ] `internal_budtenders` (employee info, schedules, performance)
- [ ] `training_progress` (training completion, certifications)
- [ ] `performance_metrics` (sales, customer feedback, ratings)
- [ ] `internal_communications` (announcements, updates, policies)

---

## 🛠️ Technical Requirements

### Database Schema Updates
- [ ] Create `customer_preferences` table for XC bot
- [ ] Create `external_budtenders` table for XB bot
- [ ] Create `store_inventory` table for IC bot
- [ ] Create `internal_budtenders` table for IB bot
- [ ] Create `budtender_sales` table for XB bot
- [ ] Create `vip_status` table for IC bot
- [ ] Create `training_progress` table for IB bot

### n8n Workflow Structure
- [ ] XC Discovery Bot (80% complete)
- [ ] XB Sales Incentive Bot (0% complete)
- [ ] IC Store Loyalty Bot (0% complete)
- [ ] IB Employee Support Bot (0% complete)

### AI Tools and Integrations
- [ ] Customer segmentation logic
- [ ] Product recommendation engine
- [ ] Performance analytics dashboard
- [ ] Training content management
- [ ] Deal notification system
- [ ] Rewards calculation engine

## 📊 Success Metrics

### XC Bot (External Customers)
- [ ] Customer preference discovery rate
- [ ] Deal notification engagement
- [ ] Product recommendation conversion
- [ ] Customer satisfaction scores

### XB Bot (External Budtenders)
- [ ] Budtender enrollment rate
- [ ] Sales performance improvement
- [ ] Training completion rates
- [ ] Incentive program participation

### IC Bot (Internal Customers)
- [ ] VIP customer retention
- [ ] Store visit frequency
- [ ] Loyalty point redemption
- [ ] Personal budtender connections

### IB Bot (Internal Budtenders)
- [ ] Training completion rates
- [ ] Performance improvement
- [ ] Customer service quality
- [ ] Employee satisfaction

## 🎯 Next Priority Actions

1. **Complete XC Bot** - Test and refine external customer discovery
2. **Develop XB Bot** - Start with budtender identification and rewards system
3. **Create IC Bot** - Focus on store-specific features and VIP management
4. **Build IB Bot** - Employee support and training management

## 📝 Notes
- All bots should use existing Supabase database
- Leverage existing customer data where possible
- Maintain consistent Luis persona across all bots
- Focus on SMS communication (150 char limit, no emojis)
- Use polling architecture (30-second intervals)
- Store all preferences and interactions for analytics

