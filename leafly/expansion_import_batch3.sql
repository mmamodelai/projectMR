BEGIN;

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




COMMIT;