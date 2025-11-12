BEGIN;

-- Update products for: OG Kush
UPDATE products
SET
    leafly_strain_type = 'Hybrid',
    leafly_description = $$OG Kush, also known as "Premium OG Kush," was first cultivated in Florida in the early ‘90s when a marijuana strain from Northern California was supposedly crossed withChemdawg,Lemon Thaiand aHindu Kushplant from Amsterdam. The result was ahybridwith a unique terpene profile that boasts a complex aroma with notes of fuel, skunk, and spice. OG often refers to “Original Gangster,” or "Ocean Grown" indicating either the strain’s authenticity or intensity. Many people have different names for the acronym, but real OG Kush should smell like lemon-pine-fuel with a high-THC, mixed head and body effect. It's often enjoyed in the back half of the day to ease stress.$$,
    leafly_rating = 4.276787290379524,
    leafly_review_count = 5665,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://images.leafly.com/flower-images/og-kush.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/og-kush',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%og%kush%' OR name ILIKE '% og %');



-- Update products for: Blue Dream
UPDATE products
SET
    leafly_strain_type = 'Sativa',
    leafly_description = $$Blue Dreamis a sativa-dominanthybrid marijuana strainmade by crossingBlueberrywithHaze. This strain produces a balanced high, along with effects such as cerebral stimulation andfull-body relaxation. Blue Dream can be more than 20% THC but has a low CBD percentage, making this potent strain a fan favorite of both novice and veteran cannabis consumers. In terms of flavor, Blue Dream is reported to smell and taste like sweetberries. Medical marijuana patients often use Blue Dream to treat symptoms of stress, anxiety anddepression. Blue Dream originated in California and has since achieved legendary status among West Coast strains and has quickly become one of the most-searched-for strains in the Leafly database. The average price per gram of Blue Dream is $20. Strains similar to Blue Dream includeBlue Dream CBD,Double Dream, andBlue Magoo.$$,
    leafly_rating = 4.338508268646642,
    leafly_review_count = 14815,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Blueberry","Haze"}'::TEXT[],
    lineage = $$Blueberry x Haze$$,
    image_url = 'https://images.leafly.com/flower-images/blue-dream.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/blue-dream',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%blue%dream%');



-- Update products for: Maui Wowie
UPDATE products
SET
    leafly_strain_type = 'Sativa',
    leafly_description = $$Maui Wowie, also known as "Maui Waui" and "Mowie Wowie," is a classicsativamarijuana strain made from a cross ofHawaiianand another strain that remains unknown. This strain featurestropicalflavors and stress-relieving qualities that will float you straight to the shores of Hawaii where this strain originally comes from. Since its beginnings in the island’s volcanic soil, Maui Wowie has spread across the world to bless us with its sweetpineappleflavors andhigh-energyeuphoria. Lightweight effects allow your mind to drift away tocreativeescapes, while Maui Wowie’s motivating, active effects may be all you need to get outside and enjoy the sun.$$,
    leafly_rating = 4.331887201735358,
    leafly_review_count = 1844,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative","Alert"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Fruity","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Hawaiian","another strain that remains unknown"}'::TEXT[],
    lineage = $$Hawaiian x another strain that remains unknown$$,
    image_url = 'https://images.leafly.com/flower-images/defaults/generic/strain-18.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/maui-wowie',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%maui%wowie%' OR name ILIKE '%maui%waui%');



-- Update products for: GSC
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$GSC, also known as "Girl Scout Cookies" or simply Cookies, is an indica-dominanthybrid marijuana strainfrom the California breeder Jigga who crossed a sub-type ofOG Kushwith an intermediate strain calledF1 Durban. This popular strain is known for producingeuphoric effects, followed up by waves offull-body relaxation. One hit of GSC will leave you feelinghappy,hungry, and stress-free. This strain features a robust THC level of 25% and is best reserved for experienced cannabis consumers. Those with a low THC tolerance should take it slow with GSC as the effects of the strain may be overwhelming. The high THC content in GSC is beloved by medical marijuana patients looking for quick relief from symptoms associated withchronic pain,nausea, andappetite loss. GSC is famous for its pungent, dessert-like aroma & flavor profile featuring bold notes of mint, sweet cherry, and lemon. The average price per gram of GSC is $11. This strain has won numerous accolades and awards over the years, including a few Cannabis Cups. Because GSC has reached legendary status among the cannabis community at large, you can find many variations of this sought-after strain, includingThin Mint (aka Thin Mint Girl Scout Cookies)andPlatinum GSC (aka Platinum Girl Scout Cookies).$$,
    leafly_rating = 4.428120063191153,
    leafly_review_count = 7596,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Fruity","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://images.leafly.com/flower-images/gsc.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/girl-scout-cookies',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%girl%scout%cookies%' OR name ILIKE '%gsc%');



-- Update products for: Sour Diesel
UPDATE products
SET
    leafly_strain_type = 'Hybrid',
    leafly_description = $$Sour Diesel, also known as "Sour D" and "Sour Deez," is a popularhybrid marijuana strainmade by crossingChemdawgandSuper Skunk. Sour Diesel effects are dreamy, cerebral, fast-acting andenergizing. This strain features apungent flavor profilethat smells likediesel. Medical marijuana patients choose Sour Diesel to help relieve symptoms associated withdepression,pain, andstress. Fun fact: Sour Diesel first became popular in the early 1990s and has been legendary ever since.$$,
    leafly_rating = 4.335435645877132,
    leafly_review_count = 8562,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Sour","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Chemdawg","Super Skunk"}'::TEXT[],
    lineage = $$Chemdawg x Super Skunk$$,
    image_url = 'https://leafly-public.imgix.net/strains/photos/5SPDG4T4TcSO8PgLgWHO_SourDiesel_AdobeStock_171888473.jpg?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/sour-diesel',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%sour%diesel%');




COMMIT;