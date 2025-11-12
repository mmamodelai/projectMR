-- Leafly Expansion Import SQL
-- Generated: 2025-10-13T21:11:28.629169
-- Strains: 33

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


-- Update products for: Lemon Haze
UPDATE products
SET
    leafly_strain_type = 'Sativa',
    leafly_description = $$Lemon Hazeis asativamarijuana strain that smells and tastes like fresh peeled lemon slices. Lemon Haze is made by crossingLemon SkunkwithSilver Haze. Its buds appear to be green and yellow with amber hairs on the trichomes, giving it the yellow tint.$$,
    leafly_rating = 4.205893464299207,
    leafly_review_count = 2647,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Lemon Skunk","Silver Haze"}'::TEXT[],
    lineage = $$Lemon Skunk x Silver Haze$$,
    image_url = 'https://images.leafly.com/flower-images/defaults/red-orange-amber/strain-4.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/lemon-haze',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%lemon%haze%');


-- Update products for: Pineapple Express
UPDATE products
SET
    leafly_strain_type = 'Sativa',
    leafly_description = $$Pineapple Expressis a sativa-dominanthybrid marijuana strainmade by crossingTrainwreckwithHawaiian. While this strain rose to fame on the silver screen in 2008 amidst the release ofPineapple Express,it is a real strain that you can find on the shelves of dispensaries across the country.Since then, this strain has become a favorite in the hearts and minds of cannabis lovers. Pineapple Express produces long-lastingenergetic effectsthat you can feel right away. Pineapple Express is 20% THC and may make you feelbuzzy,alert, andcreative. The best time to smoke Pineapple Express is in the morning, afternoon, or early evening hours. In terms of flavor, this strain packs a punch to your pallet withbright citrusnotes infused withpineappleandearthypine, thanks to the terpenes ofcaryophyllenelimoneneandOcimene. Medical marijuana patients choose Pineapple Express to relieve symptoms associated withdepression,pain, andfatigue. The average price per gram of Pineapple Express is $20.$$,
    leafly_rating = 4.404226618705036,
    leafly_review_count = 4448,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative","Alert"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Fruity","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Trainwreck","Hawaiian"}'::TEXT[],
    lineage = $$Trainwreck x Hawaiian$$,
    image_url = 'https://images.leafly.com/flower-images/pineapple-express.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/pineapple-express',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%pineapple%express%');


-- Update products for: Wedding Cake
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$Wedding Cake, also known as "Triangle Mints #23," is a potent type ofindica-hybrid marijuana strainmade by crossingTriangle KushwithAnimal Mints. Fun fact: In Canada, this strain is known asPink Cookies. The Wedding Cake strain providesrelaxingandeuphoric effectsthat calm the body and mind. This strain yields a rich and tangy flavor profile with undertones ofearthy pepper. Medical marijuana patients choose Wedding Cake to help relieve symptoms associated withpain,insomniaandappetite loss. Consumers with a low THC tolerance should enjoy this strain with an extra slice of care due to its high THC content. Wedding Cake has soared in popularity over the years and was namedLeafly Strain of the Yearin 2019.$$,
    leafly_rating = 4.553571428571429,
    leafly_review_count = 2632,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative","Calm"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Triangle Kush","Animal Mints"}'::TEXT[],
    lineage = $$Triangle Kush x Animal Mints$$,
    image_url = 'https://leafly-public.imgix.net/strains/photos/m2y50HYRBu0dHY4JSdSx_wedding-cake_jman.jpg?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/wedding-cake',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%wedding%cake%');


-- Update products for: Strawberry Cough
UPDATE products
SET
    leafly_strain_type = 'Sativa',
    leafly_description = $$Known for its sweet smell of fresh strawberries and an expanding sensation that can make even the most seasoned consumer cough,Strawberry Coughis a potentsativamarijuana strain with mysterious genetic origins. However, Strawberry Cough is thought to be a cross ofHazeandStrawberry Fields. The skunky, berry flavors will capture your senses while the cerebral, uplifting effects provide an aura of euphoria that is sure to leave a smile on your face. Strawberry Cough is a great solution in times of elevated stress.$$,
    leafly_rating = 4.32577040298002,
    leafly_review_count = 2953,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Haze","Strawberry Fields"}'::TEXT[],
    lineage = $$Haze x Strawberry Fields$$,
    image_url = 'https://images.leafly.com/flower-images/strawberry-cough.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/strawberry-cough',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%strawberry%cough%');


-- Update products for: Mimosa
UPDATE products
SET
    leafly_strain_type = 'Hybrid',
    leafly_description = $$Mimosa, also known as "Purple Mimosa," is ahybrid marijuana strainmade by crossingClementinewithPurple Punch. In small doses, this strain produceshappy, level-headed effects that will leave you feelingupliftedand motivated enough to take on any mundane task. In large doses, Mimosa may make you feelsleepyandrelaxed. This strain has a strong aroma and flavor that reminds you of its namesake, with notes offruitandcitrusflavors bursting through. Medical marijuana patients choose this strain to help relieve symptoms associated withdepressionandstress. Mimosa is a staple from theTangiefamily. Breeder Symbiotic Genetics has released a refined Mimosa dubbed Mimosa v6.$$,
    leafly_rating = 4.435875216637782,
    leafly_review_count = 1154,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative","Calm"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Clementine","Purple Punch"}'::TEXT[],
    lineage = $$Clementine x Purple Punch$$,
    image_url = 'https://leafly-public.imgix.net/strains/photos/sE4UZNIUQbSxoqEEk0E1_Mimosa.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/mimosa',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%mimosa%');


-- Update products for: Northern Lights
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$Northern Lights, also known as "NL," is anindica marijuana strainmade by crossingAfghaniwithThai. Northern Lights produceseuphoric effectsthat settle in firmly throughout the body,relaxing musclesand easing the mind. Consumers say this strain has apungentlysweet and spicy flavor profile that is smooth on the exhale. Medical marijuana patients choose Northern Lights to help relieve symptoms associated withdepression,stress,painandinsomnia. Growers say this strain features purple and crystal-coated buds and grows best indoors with a flowering time of 45-50 days.$$,
    leafly_rating = 4.439069521543749,
    leafly_review_count = 3783,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Afghani","Thai"}'::TEXT[],
    lineage = $$Afghani x Thai$$,
    image_url = 'https://images.leafly.com/flower-images/northern-lights.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/northern-lights',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%northern%lights%');


-- Update products for: Acapulco Gold
UPDATE products
SET
    leafly_strain_type = 'Sativa',
    leafly_description = $$Acapulco Goldis a raresativa marijuana strain. As one of the most well-known strains, Acapulco Gold has been likened to dinner at a five-star restaurant. This strain produces effects that are motivating andenergizing. This strain comes from the area in and around Acapulco, Mexico, and its orange hairs resemble a gold nugget, with gold, green, and brown colors and plenty of resin on the buds. An aroma of burnt toffee lingers when the bud is broken up.Acapulco Gold has a reputation for being one of the best cannabis strains ever created, and it's becoming more difficult to find.$$,
    leafly_rating = 4.490654205607477,
    leafly_review_count = 856,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Orange","Grapefruit","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://images.leafly.com/flower-images/acapulco.jpg?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/acapulco-gold',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%acapulco%gold%');


-- Update products for: Tangie
UPDATE products
SET
    leafly_strain_type = 'Sativa',
    leafly_description = $$Tangieis asativamarijuana strain made by crossingCalifornia OrangeandSkunk-1. This strain is a popular choice in Amsterdam and is spreading elsewhere. Tangie is a remake of sorts of the popular version ofTangerine Dreamthat was sought-after in the 1990s. The citrus heritage of Tangie is the most evident in its refreshing tangerine aroma. Tangie provides a euphoric yet relaxed effect.$$,
    leafly_rating = 4.447172619047619,
    leafly_review_count = 1344,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"California Orange","Skunk-1"}'::TEXT[],
    lineage = $$California Orange x Skunk-1$$,
    image_url = 'https://leafly-public.imgix.net/strains/photos/8wTMziz0RQaJqNE4juPn_Tangie.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/tangie',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%tangie%');


-- Update products for: Dosidos
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$Dosidos, also known as "Dosi Doe," "Do-Si-Dos," and "Dosi" is an indica-dominanthybrid marijuana strainwith qualities similar to its parent, aGSC-phenotype. With glittering trichomes, bright pistils, and lime green and lavender leaves,Dosidosweed is a feast for the eyes. Its aroma is pungent, sweet, and earthy with slight floral funkiness. These classic OG aromas blend nicely with medical-grade body effects that lean toward the sedative side with the addition ofFace Off OGgenetics. Those who smoke Dosi can enjoy a stoney, in-your-face buzz off the start that melts down over the body, petrifying the consumer with relaxation that emanates outward. The dominant terpene inDosidosislimonene.$$,
    leafly_rating = 4.6368,
    leafly_review_count = 1250,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://leafly-public.imgix.net/jdRI25LqQM6Wavphys2K_nug-dosidos-v1.jpg?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/do-si-dos',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%do-si-dos%' OR name ILIKE '%dosidos%');


-- Update products for: Master Kush
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$Master Kush, also known as "High Rise," "Grandmaster Kush," and "Purple SoCal Master Kush" is a popular indica marijuana strain crossed from twolandracestrains from different parts of the Hindu Kush region by the Dutch White Label Seed Company in Amsterdam. The plant produces a subtle earthy, citrus smell with a hint of incense, which is often described as a vintage flavor. The taste of Master Kush is reminiscent of the famous hard-rubbed charas hash. This strain holds a superb balance of full-body relaxation without mind-numbing effects. Instead, Master Kush offers a sharpened sensory awareness that can bring out the best of any activity.$$,
    leafly_rating = 4.266630016492578,
    leafly_review_count = 1819,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://images.leafly.com/flower-images/defaults/purple/strain-4.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/master-kush',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%master%kush%');


-- Update products for: Cherry Pie
UPDATE products
SET
    leafly_strain_type = 'Hybrid',
    leafly_description = $$Cherry Pie's parents areGranddaddy PurpleandF1 Durb. With buds that are dense and full of orange hairs and a touch of purple, thishybridstrain smells of sweet and sour cherry pie. Leafly reviewers tell us that Cherry Pie’s effects include feelinggiggly,happy, andeuphoric.$$,
    leafly_rating = 4.343521897810219,
    leafly_review_count = 2192,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Fruity","Tropical","Sour","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"are Granddaddy Purple","F1 Durb"}'::TEXT[],
    lineage = $$are Granddaddy Purple x F1 Durb$$,
    image_url = 'https://images.leafly.com/flower-images/cherry-pie.jpg?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/cherry-pie',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%cherry%pie%');


-- Update products for: Grape Ape
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$Grape Ape, propagated by Apothecary Genetics and Barney’s Farm, is a mostlyindicastrain that crossesMendocino Purps,Skunk, andAfghani. Named for its distinctgrape-like smell, this indica is known for providing carefreerelaxationthat can help soothepain,stress, andanxiety. Its dense, compact buds are wreathed in deep purple leaves which darken as this indica reaches full maturation following its 7 to 8 week flowering time.$$,
    leafly_rating = 4.289369210410234,
    leafly_review_count = 2267,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative","Calm"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://leafly-public.imgix.net/strains/photos/KcYDLvLXTE2QIyiiLTRN_grape-ape.jpg?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/grape-ape',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%grape%ape%');


-- Update products for: Granddaddy Purple
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$Granddaddy Purpleis an indica marijuana strain that goes by many different names, including "Grand Daddy Purp," "Granddaddy Purps," "GDP," and "Grandaddy Purple Kush." Popularized in 2003 by Ken Estes, Granddaddy Purple (or GDP) is a famousindicacross ofMendo Purps,Skunk, and Afghanistan. Other people claim it is Big Bud x Purple Urkle. Either way, this California staple inherits a complexgrapeandberryaroma from its Purps and Ghani heritage. GDP flowers bloom in shades of deep purple, a contrasting backdrop for its snow-like dusting of white crystal resin. Its potent effects are clearly detectable in both mind and body, delivering a fusion of cerebraleuphoriaand physicalrelaxation. While your thoughts may float in a dreamy buzz, your body is more likely to find itself fixed in one spot for the duration of GDP’s effects. Granddaddy Purple is typically pulled off the shelf for consumers looking to combatpain,stress,insomnia,appetite loss, andmuscle spasms. GDP blesses growers with massive yields which are ready for harvest following a 60 day flowering time indoors.$$,
    leafly_rating = 4.417033257082527,
    leafly_review_count = 5683,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Sour","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://images.leafly.com/flower-images/granddaddy-purple.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/granddaddy-purple',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%granddaddy%purple%' OR name ILIKE '%gdp%');


-- Update products for: Durban Poison
UPDATE products
SET
    leafly_strain_type = 'Sativa',
    leafly_description = $$This puresativaoriginates from the South African port city of Durban. It has gained popularity worldwide for itssweetsmell andenergetic,upliftingeffects.Durban Poisonis the perfect strain to help you stay productive through a busy day, when exploring the outdoors, or to lend a spark ofcreativity. Growers and concentrate enthusiasts will both enjoy the over-sized resin glands which make this strain a quality choice for concentrate extraction. The buds are round and chunky, and leave a thick coating oftrichomeson almost all areas of the plant.$$,
    leafly_rating = 4.446494464944649,
    leafly_review_count = 3794,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Sour","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Zkittles","Durban Poison"}'::TEXT[],
    lineage = $$Zkittles x Durban Poison$$,
    image_url = 'https://images.leafly.com/flower-images/durban-poison.jpg?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/durban-poison',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%durban%poison%');


-- Update products for: Blueberry
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$Blueberry, also known as "Berry Blue," is anindicamarijuana strain made by crossingPurple ThaiwithThai. A true A-List cannabis strain, Blueberry’s legendary status soared to new heights after claiming theHigh Times’Cannabis Cup 2000 for Best indica. The long history of the strain goes back to the late 1970s when American breeder DJ Short was working with a variety of exoticlandrace strains. However, throughout the decades of Blueberry’s cultivation, the genetics have been passed around, due in large part to DJ Short working with multiple seed banks and breeders. Thesweetflavors of freshblueberriescombine withrelaxingeffects to produce a long-lasting sense ofeuphoria. Many consumers utilize the effects of Blueberry to help contend withpainandstress, while connoisseurs and growers admire the strain for its colorful hues and highTHC content.$$,
    leafly_rating = 4.281135902636917,
    leafly_review_count = 2465,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Purple Thai","Thai"}'::TEXT[],
    lineage = $$Purple Thai x Thai$$,
    image_url = 'https://images.leafly.com/flower-images/blueberry.jpg?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/blueberry',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%blueberry%' AND (name ILIKE '%og%' OR name ILIKE '%kush%'));


-- Update products for: Purple Haze
UPDATE products
SET
    leafly_strain_type = 'Sativa',
    leafly_description = $$Purple Hazeis asativamarijuana strain popularized by Jimi Hendrix’s 1967 classic song, Purple Haze. This strain delivers a dreamy burst ofeuphoriathat brings veteran consumers back to their psychedelic heyday. This nostalgic sativa staple remains cherished for itshigh energycerebral stimulation that awakenscreativityand blissfulcontentmentthroughout the day. Purple Haze is believed to have descended from parent strainsPurple ThaiandHaze, which pass on a mix ofsweetandearthyflavors underscored by notes ofberryand sharpspice. Purple Haze buds typically acquire vibrant hues of lavender that further justify the naming of this strain.$$,
    leafly_rating = 4.2223113964687,
    leafly_review_count = 1246,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"strains Purple Thai","Haze"}'::TEXT[],
    lineage = $$strains Purple Thai x Haze$$,
    image_url = 'https://images.leafly.com/flower-images/defaults/purple/strain-10.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/purple-haze',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%purple%haze%');


-- Update products for: Chemdawg
UPDATE products
SET
    leafly_strain_type = 'Hybrid',
    leafly_description = $$Chemdawg, officially named "Chemdog," is a hybrid marijuana strain grown and spread by the breeder Chemdog since 1991. In a Leafly interview, Chemdog relates how Chemdog came from what was thought to be Northern California bag seed, via a Colorado Grateful Dead concert. Chem 91, Chem 4, and Chem Sis are all variations on Chemdog. The original name Chemdog came from two names for the same bud "Chem" and "Dog bud." Chemdog evolved into the variation 'Chemdawg' over time and distance as other growers and breeders propagated it, with the latter name becoming more dominant. Leafly customers tell us Chemdawg effects includefeelingeuphoric,uplifted, andcreative. Medical marijuana patients often choose Chemdawg when dealing with symptoms associated withstress,anxiety, andpain. Chemdog is a staple strain in cannabis and may be a source of powerhouse strains likeSour DieselandOG Kush, Chemdog is known for its distinct,diesel-like aroma.Pungentand sharp, you’ll be able to smell this strain from a mile away. Cannabis newbies be warned: Chemdog tends to be very potent. Consumers can expect to have a cerebral experience, coupled with a strong heavy-bodied feeling.$$,
    leafly_rating = 4.263916700040048,
    leafly_review_count = 2497,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Fruity","Tropical","Sour","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://images.leafly.com/flower-images/defaults/generic/strain-1.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/chemdawg',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%chemdawg%' OR name ILIKE '%chemdog%');


-- Update products for: Mango Kush
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$TheMango Kushmarijuana strain tastes similar to the actualmangofruit, with a distinct kush flavor and hints ofpineon the exhale. Its buds are covered with orangepistilsand are described as very dense. The plant has an average growth height of 4-5 feet. Flowering is 9-11 weeks and is a favorite with both indoor and outdoor growers. The buds have thick shiny trichomes which are evident when the bud is broken apart. The smell and taste are the same and described as mango and banana.$$,
    leafly_rating = 4.238242097147263,
    leafly_review_count = 1297,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://images.leafly.com/flower-images/mango-kush.jpg?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/mango-kush',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%mango%kush%');


-- Update products for: Clementine
UPDATE products
SET
    leafly_strain_type = 'Sativa',
    leafly_description = $$Clementineis a energizing sativa-dominant strain that is made by crossingTangiewithLemon Skunk. This strain is loved for its sweet taste and citrus aroma. Leafly users say Clementine is perfect for a wake and bake or activating your third eye to increase your focus. Clementine has won awards including the best sativa concentrate in 2015.$$,
    leafly_rating = 4.415929203539823,
    leafly_review_count = 565,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative","Calm"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Strawberry","Nutty","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Tangie","Lemon Skunk"}'::TEXT[],
    lineage = $$Tangie x Lemon Skunk$$,
    image_url = 'https://leafly-public.imgix.net/strains/photos/QNQ0kFSQ9Cf1v5ffgbWl_Clementine.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/clementine',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%clementine%');


-- Update products for: Bubba Kush
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$Bubba Kush, also known as "BK," "Bubba," and "Bubba OG Kush" is anindicamarijuana strain from Florida that has gained notoriety in the US and beyond for its heavy tranquilizing effects. Sweet hashish flavors with subtle notes of chocolate and coffee come through on the exhale, delighting the palate as powerful relaxation takes over. From head to toe, muscles ease with heaviness as dreamy euphoria blankets the mind, crushing stress while bringing happy moods. Bubba Kush exhibits a distinctive, bulky bud structure with hues that range from forest green to pale purple.$$,
    leafly_rating = 4.258739333883843,
    leafly_review_count = 3633,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://images.leafly.com/flower-images/bubba-kush.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/bubba-kush',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%bubba%kush%');


-- Update products for: The Original Z
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$The Original Z(popularly known under an infringing candy name) is anindicahybrid marijuana strain bred from an alleged mix ofGrape ApeandGrapefruitthat is crossed with another undisclosed strain. This sweet, tropical confection-flavored cultivar came to market in the 2010s. According to the story, the cultivar came from an individual dubbed Gas Station Bob. Working as Terp Hogz, the growers Fields and Tony Mendo popularized Z with the help of 3rd Gen Family's Brandon Parker—growing the strain, entering it into contests, and making new crosses. The Original Z won 1st Place at the 2016 Emerald Cup, the 2023 King of Z Hill, and has placed in several Cannabis Cups in San Francisco and Michigan. Both Terp Hogz and 3rd Gen Fam—as well as other breeders—continue to refine the varietal.  In 2023, Terp Hogz announced they will use the name "The Original Z," as part of a settlement with a candy company over alleged trademark infringement.  This strain features medium-sized, spongy greencolasthat with asweet,tropicalblend offruitflavors. The effects of The Original Z are calming, leaving consumersfocused, alert, andhappywhilerelaxingthe body to help unwind any time of day.$$,
    leafly_rating = 4.492610837438423,
    leafly_review_count = 1015,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative","Alert"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Fruity","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://leafly-public.imgix.net/strains/photos/6VF5EvUTjqZPKFVOQAAY_Zkittlez.jpg?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/zkittlez',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%zkittlez%' OR name ILIKE '%skittlez%');


-- Update products for: White Widow
UPDATE products
SET
    leafly_strain_type = 'Hybrid',
    leafly_description = $$White Widowis ahybridweed strain made from a genetic cross between a Braziliansativalandrace and a resin-heavy South Indianindica. This strain is 60% sativa and 40% indica. White Widow is one of the most famous strains worldwide, first bred in the Netherlands by Green House Seeds in the 1990s. Its buds are white with crystal resin, warning you of the potent effects to come. A powerful burst of euphoria and energy breaks through immediately, stimulating both conversation and creativity. White Widow is 15% THC, making this strain an ideal choice for moderate cannabis consumers. Leafly customers tell us White Widow effects include feelingenergetic,talkative, andcreative. Medical marijuana patients often choose White Widow when dealing with symptoms associated withstress,anxiety, andpain. White Widow features flavors likewoody,spicy/herbal, andearthy. The dominant terpenes of this strain aremyrceneandcaryophyllene, though growing conditions and strain phenotypes may impact the exact blend. The average price of White Widow typically ranges from $8-$12 per gram. White Widow is a balanced hybrid that can be enjoyed by both indica and sativa lovers. It has a flowering time of 8-9 weeks and can be grown indoors or outdoors in mild climates. It produces chunky and conical buds with a loose and fluffy texture that are easy to break up despite their stickiness. If you’ve smoked, dabbed, or consumed White Widow, tell us about your experience by leaving a strain review.$$,
    leafly_rating = 4.290030211480363,
    leafly_review_count = 4634,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"a Brazilian sativa landrace","a resin-heavy South Indian indica"}'::TEXT[],
    lineage = $$a Brazilian sativa landrace x a resin-heavy South Indian indica$$,
    image_url = 'https://images.leafly.com/flower-images/white-widow.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/white-widow',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%white%widow%');


-- Update products for: Trainwreck
UPDATE products
SET
    leafly_strain_type = 'Sativa',
    leafly_description = $$Trainwreckis a mind-bending, potentsativawith effects that hit like a freight train.MexicanandThaisativas were bred withAfghaniindicasto produce this Northern California staple, passing on asweetlemonandspicypinearoma. Trainwreck begins its speedy hurtle through the mind with a surge ofeuphoria, awakeningcreativityandhappiness.Migraines,pain, andarthritisare mowed down by Trainwreck’s high-THC content, and many patients also use it for relief ofanxiety,ADD/ADHD, andPTSD.  There are many stories about the origin of the name. Some say growers grew it among a train wreck in Arcata, CA. Others say the plant's sprawling growth resembled a train wreck.$$,
    leafly_rating = 4.211706102117061,
    leafly_review_count = 3212,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://images.leafly.com/flower-images/trainwreck.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/trainwreck',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%trainwreck%');


-- Update products for: Skywalker OG
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$Skywalker OGis an Indica-dominanthybridcannabis strain with a potent THC content ranging from 20% to 30%. It is a cross betweenMazarandBlueberry OGstrains. The dominant terpenes found in Skywalker OG aremyrcene,caryophyllene, andlimonene. Skywalker OG is well-known for itsrelaxingandeuphoriceffects, making it an excellent choice forstressrelief andpainmanagement. This strain is often used to alleviate symptoms ofanxiety,depression, andinsomnia. The strain's name pays homage to the Star Wars franchise, featuring the namesake of Luke Skywalker himself. Skywalker OG's creators chose to name the strain after the Jedi hero due to its potent, "forceful" effects. When it comes to taste and aroma, Skywalker OG has aspicy,herbalflavor with hints ofearthyundertones. The top flavors and aromas includediesel,pine, andspicy herbalnotes.$$,
    leafly_rating = 4.464022662889518,
    leafly_review_count = 1765,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative","Calm"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Mazar","Blueberry OG strains"}'::TEXT[],
    lineage = $$Mazar x Blueberry OG strains$$,
    image_url = 'https://images.leafly.com/flower-images/defaults/long-fluffy-wispy/strain-2.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/skywalker-og',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%skywalker%og%' OR (name ILIKE '%skywalker%' AND name ILIKE '%og%'));


-- Update products for: Headband
UPDATE products
SET
    leafly_strain_type = 'Hybrid',
    leafly_description = $$Headband, also known as simply "HB," is a hybrid marijuana strain and love-child of cannabis’ power couple,OG KushandSour Diesel. The smooth, creamy smoke is accented by flavors oflemonsanddieselwhile the long-lasting effects are great forpainrelief, helping you torelax, and to combat elevatedstresslevels. Many report that the effects create a slight pressure around the crown of their head and feels as though they are wearing a headband. The effects have been known to come on slow, so pace yourself with this potenthybrid.$$,
    leafly_rating = 4.213008748573603,
    leafly_review_count = 2629,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Sour","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://leafly-public.imgix.net/strains/photos/3EbkAKSsTfyyIsmMfygd_Headband_jman_hdr.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/headband',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%headband%');


-- Update products for: Fire OG
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$Fire OG, also known as "Fire OG Kush," is a indica-dominanthybridmarijuana strain made by crossingOG KushandSFV OG Kush. This strain has an aroma similar to Lemon Pledge and has euphoric effects that are potent and long-lasting. Fire OG is one of the strongest OG strains, and is a fan favorite among consumers who have a high THC tolerance. Fire OG gets its name from the frosty red hairs that make the strain appear to look like it is on fire. Fire OG plants typically flower in 9-10 weeks.$$,
    leafly_rating = 4.374800637958533,
    leafly_review_count = 1254,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Fruity","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"OG Kush","SFV OG Kush"}'::TEXT[],
    lineage = $$OG Kush x SFV OG Kush$$,
    image_url = 'https://leafly-public.imgix.net/strains/photos/UILdlZQQuN969injI7OQ_FireOG.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/fire-og',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%fire%og%');


-- Update products for: GG4
UPDATE products
SET
    leafly_strain_type = 'Hybrid',
    leafly_description = $$Original Glue is ahybridweed strain made from a genetic cross between Chem’s Sister,Sour Dubb, andChocolate Diesel. This strain is 37%sativaand 63%indica. Also known as “GG4”, Original Glue is a potent strain that delivers heavy-handed euphoria and relaxation, leaving you feeling “glued” to the couch. Its chunky, resin-covered buds fill the room with pungent earthy and sour aromas inherited from its parent strains. Original Glue is 20% THC, making this strain an ideal choice for experienced cannabis consumers. Leafly customers tell us Original Glue effects include feelingrelaxed,sleepy, andhungry. Medical marijuana patients often choose Original Glue when dealing with symptoms associated withstress,anxiety, andpain. Bred by GG Strains LLC, Original Glue features flavors likepungent,pine, andearthy. The dominant terpene of this strain iscaryophyllene. The average price of Original Glue typically ranges from $10-$15 per gram. Original Glue is a multiple award-winning strain that has taken first place in both the Michigan and Los Angeles 2014 Cannabis Cups, as well as the High Times Jamaican World Cup in 2015. It is a fast-growing strain that produces large yields of sticky buds with a flowering time of 9-10 weeks. If you’ve smoked, dabbed, or consumed Original Glue, tell us about your experience by leaving a strain review.$$,
    leafly_rating = 4.639040348964013,
    leafly_review_count = 5502,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Fruity","Tropical","Sour","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://images.leafly.com/flower-images/gg-4.jpg?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/original-glue',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%gorilla%glue%' OR name ILIKE '%gg4%' OR name ILIKE '%gg #4%');


-- Update products for: Sherbert
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$Sherbert, also known as "Sherbet", "Sherbert OG", "Sunset Sherbet", and "Sunset Sherbert" is an indica-dominant hybrid marijuana strain made by crossingGirl Scout CookieswithPink Panties. This strain exhibits powerful, full-body effects that are elevated by a jolt of cerebral energy and carefree state of mind. Sherbet boasts a THC level of 18% and may be overwhelming to novice cannabis consumers. The high potency of Sherbert makes it an ideal choice for medical marijuana patients seeking relief from symptoms associated withstress,tension, and mood disorders. This strain features a sweet, dessert-like flavor profile with notes of skunky citrus, sweet berry, and candy. The average price per gram of Sherbert is $20, but may vary based on your location. According to growers, Sherbert flowers into oblong fluffy nugs with rich trichome coverage and dark amber hairs throughout light and dark green foliage. This strain was originally bred by Mr. Sherbinski, who bred Sherbert intentionally to inherit the genetic lineage of its parent strain Girl Scout Cookies.$$,
    leafly_rating = 4.548787699586044,
    leafly_review_count = 1691,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative","Calm"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Fruity","Tropical","Sour","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Girl Scout Cookies","Pink Panties"}'::TEXT[],
    lineage = $$Girl Scout Cookies x Pink Panties$$,
    image_url = 'https://images.leafly.com/flower-images/sunset-sherbert.jpg?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/sunset-sherbert',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%sunset%sherbet%' OR name ILIKE '%sherbert%');


COMMIT;
