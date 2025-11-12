BEGIN;

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




COMMIT;